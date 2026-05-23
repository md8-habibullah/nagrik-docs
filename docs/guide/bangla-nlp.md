# Bangla NLP & Dialect Handling

## The Challenge

Bangladesh has major dialect variations:

- Standard Bangla (ঢাকা / formal)
- Chittagong dialect (চট্টগ্রামের ভাষা) - heavily modified phonetics
- Sylhet dialect (সিলেটি) - distinct vocabulary
- Noakhali dialect (নোয়াখালীর ভাষা)
- Rajshahi/Rangpur (উত্তরবঙ্গ) - different vowels

---

## Two-Step Pipeline

```
Step 1: STT (Speech → Raw Text)
   Input: Audio with dialect/noise
   Output: Raw text (may have wrong words)

   Priority:
   1. flutter_speech_to_text (bn-BD locale) - free, instant
   2. Google Cloud STT v1p1beta1 - paid but better dialects
      Model: "latest_long" for Bangla
      Alternative phrases: true (captures dialect variations)

Step 2: LLM Normalization (Raw Text → Canonical Data)
   Input: Raw transcript (possibly dialect-heavy)
   Output: Structured JSON with standard Bangla
```

---

## Google STT Bangla Configuration

```typescript
// src/services/google-stt.service.ts

async function transcribeWithGoogleSTT(audioBase64: string): Promise<string> {
  const client = new SpeechClient();

  const [response] = await client.recognize({
    config: {
      encoding: "LINEAR16",
      sampleRateHertz: 16000,
      languageCode: "bn-BD", // Bengali Bangladesh
      alternativeLanguageCodes: ["bn-IN"], // Also try India Bengali
      model: "latest_long",
      useEnhanced: true,
      enableAutomaticPunctuation: true,
      enableWordTimeOffsets: false,
      speechContexts: [
        {
          phrases: [
            // Civic terms (boost recognition)
            "রাস্তা",
            "ড্রেন",
            "পানি",
            "বিদ্যুৎ",
            "আগুন",
            "পুলিশ",
            "হাসপাতাল",
            "থানা",
            "গর্ত",
            "নালা",
            // Common misspoken civic terms
            "হানী",
            "পাতি",
            "বিদুত",
            // Area names in Dhaka
            "মিরপুর",
            "গুলশান",
            "মতিঝিল",
            "ধানমন্ডি",
            "বনানী",
            "উত্তরা",
            "মোহাম্মদপুর",
            "রামপুরা",
          ],
          boost: 15.0, // Boost probability for civic terms
        },
      ],
    },
    audio: { content: audioBase64 },
  });

  return (
    response.results
      ?.map((r) => r.alternatives?.[0]?.transcript)
      .filter(Boolean)
      .join(" ") ?? ""
  );
}
```

---

## Dialect Normalization Prompt Engineering

```typescript
// Few-shot examples embedded in system prompt

const DIALECT_EXAMPLES = \`
## Dialect normalization examples:

Input (Chittagong): "আমার বাড়ির সামনে হানী আহে না"
Normalized: "আমার বাড়ির সামনে পানি আসে না"
Category: water, Sub: supply_problem

Input (Sylheti): "রাস্তার উপরে বড় খাল অইছে"
Normalized: "রাস্তায় বড় গর্ত হয়েছে"
Category: road_damage, Sub: pothole

Input (Noakhali): "নালাতে ময়লা জমছে, পাউনি যাইতে পারতেছে না"
Normalized: "নালায় ময়লা জমেছে, পানি যেতে পারছে না"
Category: drainage, Sub: clogged_drain

Input (Rangpur): "ইলেকট্রিকের তার ঝুলি আছে, বিপজ্জনক"
Normalized: "বিদ্যুতের তার ঝুলছে, বিপজ্জনক"
Category: electricity, Sub: dangerous_wire
\`;
```

---

## Text-to-Speech (TTS) - AI Response in Bangla

````dart
// For AI responses that should be spoken back to user
// Use Google TTS or device TTS

import 'package:flutter_tts/flutter_tts.dart';

class TTSService {
  final FlutterTts _tts = FlutterTts();

  Future<void> initialize() async {
    await _tts.setLanguage('bn-BD');
    await _tts.setSpeechRate(0.8);  // Slightly slower for clarity
    await _tts.setVolume(1.0);
    await _tts.setPitch(1.0);
  }

  Future<void> speak(String text) async {
    await _tts.speak(text);
  }

  Future<void> stop() async {
    await _tts.stop();
  }
}
```\n\n
````
