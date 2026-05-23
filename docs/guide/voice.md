# Voice Pipeline - STT + AI Processing

## Voice Processing Architecture

```
User speaks
    │
    ▼
[flutter speech_to_text] ──▶ Device STT (Bengali locale: bn-BD)
    │                         Free, works offline, fast
    │ (if accuracy poor)
    ▼
[Google Cloud STT API] ──▶ High accuracy Bangla + dialects
    │                       Cost: $0.006 per 15 seconds
    │
    ▼
[Node.js Backend /agent/process]
    │
    ▼
[OpenRouter → Gemini 1.5 Pro]
    │ System prompt + few-shot examples
    ▼
[Structured JSON response]
    │
    ▼
[Flutter UI - live form fill]
```

---

## Voice Provider (Flutter)

```dart
// lib/features/agent/providers/voice_provider.dart

import 'package:speech_to_text/speech_to_text.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'voice_provider.g.dart';

@riverpod
class VoiceProvider extends _\$VoiceProvider {
  final SpeechToText _stt = SpeechToText();
  bool _sttAvailable = false;

  @override
  void build() {}

  Future<void> initialize() async {
    _sttAvailable = await _stt.initialize(
      onStatus: _onStatus,
      onError: _onError,
    );
  }

  Future<void> startListening() async {
    if (!_sttAvailable) {
      await initialize();
    }

    ref.read(agentNotifierProvider.notifier).setPhase(AgentPhase.listening);

    await _stt.listen(
      onResult: (result) {
        // Live transcript as user speaks
        ref.read(agentNotifierProvider.notifier)
           .appendTranscript(result.recognizedWords);

        if (result.finalResult) {
          _processTranscript(result.recognizedWords);
        }
      },
      listenFor: const Duration(seconds: 60),
      pauseFor: const Duration(seconds: 3),
      localeId: 'bn_BD',           // Bengali Bangladesh
      cancelOnError: false,
      partialResults: true,        // Live transcription
      listenMode: ListenMode.confirmation,
    );
  }

  Future<void> stopListening() async {
    await _stt.stop();
  }

  Future<void> toggleListening() async {
    if (_stt.isListening) {
      await stopListening();
    } else {
      await startListening();
    }
  }

  Future<void> _processTranscript(String transcript) async {
    if (transcript.isEmpty) return;

    final notifier = ref.read(agentNotifierProvider.notifier);

    // Add reasoning steps (shown in UI)
    notifier.setPhase(AgentPhase.reasoning);
    notifier.addReasoningStep('ভয়েস ট্র্যান্সক্রিপ্ট বিশ্লেষণ করছি...');
    notifier.addReasoningStep('অবস্থান শনাক্ত করার চেষ্টা করছি...');
    notifier.addReasoningStep('সমস্যার ধরন নির্ধারণ করছি...');
    notifier.addReasoningStep('ইমার্জেন্সি মাত্রা যাচাই করছি...');

    try {
      // Call backend AI agent
      final agentService = ref.read(agentServiceProvider);
      final report = await agentService.processVoiceReport(
        transcript: transcript,
        userLocation: await _getUserLocation(),
      );

      notifier.addReasoningStep('✓ ডেটা এক্সট্র্যাকশন সম্পন্ন');
      notifier.setExtractedData(report);

      // If emergency detected - immediate routing
      if (report.isEmergency) {
        ref.read(emergencyRouterProvider.notifier)
           .handleEmergency(report);
      }
    } catch (e) {
      notifier.setPhase(AgentPhase.error);
    }
  }

  void _onStatus(String status) {
    if (status == 'done') {
      ref.read(agentNotifierProvider.notifier)
         .setPhase(AgentPhase.transcribing);
    }
  }

  void _onError(dynamic error) {
    ref.read(agentNotifierProvider.notifier)
       .setPhase(AgentPhase.error);
  }

  Future<Map<String, double>?> _getUserLocation() async {
    // Get current location for context
    final pos = await Geolocator.getCurrentPosition();
    return {'lat': pos.latitude, 'lng': pos.longitude};
  }
}
```

---

## AI Agent Service (Backend call)

```dart
// lib/features/agent/repository/agent_service.dart

class AgentService {
  final Dio _dio;

  AgentService(this._dio);

  Future<CivicReport> processVoiceReport({
    required String transcript,
    Map<String, double>? userLocation,
  }) async {
    final response = await _dio.post(
      '/agent/process',
      data: {
        'transcript': transcript,
        'location': userLocation,
        'language': 'bn',
      },
    );

    return CivicReport.fromJson(response.data['report']);
  }
}
```

---

## Backend Agent Handler (Node.js)

````typescript
// src/routes/agent.ts

import { Router } from 'express';
import { OpenAI } from 'openai';

const router = Router();

const openrouter = new OpenAI({
  baseURL: 'https://openrouter.ai/api/v1',
  apiKey: process.env.OPENROUTER_API_KEY!,
});

const SYSTEM_PROMPT = \`
You are NagrikAI, a civic assistant for Bangladesh citizens.
Extract structured data from Bangla voice transcripts.

DIALECT NORMALIZATION:
- পানি = হানী = water
- ড্রেন = নালা = drainage
- রাস্তা = পথ = road
- হাসপাতাল = ডাক্তারখানা = hospital

Return ONLY valid JSON matching this schema:
{
  "category": "road_damage|drainage|electricity|water|crime|fire|medical|flood|other",
  "sub_category": "string",
  "location": "string (extracted from speech or 'GPS-based')",
  "severity": "low|medium|high|critical",
  "description": "short Bangla summary max 100 chars",
  "is_emergency": boolean,
  "suggested_helpline": "999|333|109|16123|null",
  "lat": number or null,
  "lng": number or null
}

EMERGENCY RULES:
- Fire → is_emergency: true, helpline: 999
- Crime in progress → is_emergency: true, helpline: 999
- Medical emergency → is_emergency: true, helpline: 999
- Flood/disaster → is_emergency: true, helpline: 333
\`;

router.post('/process', async (req, res) => {
  const { transcript, location } = req.body;

  const locationContext = location
    ? \`User GPS: lat=\${location.lat}, lng=\${location.lng}\`
    : 'GPS not available';

  const response = await openrouter.chat.completions.create({
    model: 'google/gemini-1.5-pro',
    messages: [
      { role: 'system', content: SYSTEM_PROMPT },
      { role: 'user', content: \`
        Transcript: "\${transcript}"
        \${locationContext}
        Extract the civic report data.
      \` },
    ],
    temperature: 0.1,
    max_tokens: 500,
    response_format: { type: 'json_object' },
  });

  const report = JSON.parse(
    response.choices[0].message.content!
  );

  // Enrich with actual GPS if available
  if (location && !report.lat) {
    report.lat = location.lat;
    report.lng = location.lng;
  }

  res.json({ report });
});

export default router;
```\n\n
````
