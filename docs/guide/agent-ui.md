# Agent Visual UI - Live Sandbox Screen

## The Core UX Concept

The "Agent Sandbox" is the most important screen. When a user taps the microphone:

```
State Machine:
IDLE → LISTENING → TRANSCRIBING → REASONING → EXTRACTING → REVIEW → CONFIRMED
```

Each state has distinct visual feedback so the user always knows what the AI is doing.

---

## Agent State Model

```dart
// lib/features/agent/providers/agent_state_provider.dart

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'agent_state_provider.g.dart';

enum AgentPhase {
  idle,
  listening,
  transcribing,
  reasoning,
  extracting,
  review,
  confirmed,
  error,
}

class AgentState {
  final AgentPhase phase;
  final String transcript;
  final List<String> reasoningSteps;   // live "thinking" messages
  final CivicReport? extractedData;
  final String? errorMessage;

  const AgentState({
    this.phase = AgentPhase.idle,
    this.transcript = '',
    this.reasoningSteps = const [],
    this.extractedData,
    this.errorMessage,
  });

  AgentState copyWith({...}) => AgentState(...);
}

class CivicReport {
  final String category;
  final String subCategory;
  final String location;
  final String severity;       // low | medium | high | critical
  final String description;
  final bool isEmergency;
  final double? lat;
  final double? lng;
  final String? suggestedHelpline;

  const CivicReport({...});

  factory CivicReport.fromJson(Map<String, dynamic> json) => CivicReport(
    category: json['category'] ?? '',
    subCategory: json['sub_category'] ?? '',
    location: json['location'] ?? '',
    severity: json['severity'] ?? 'medium',
    description: json['description'] ?? '',
    isEmergency: json['is_emergency'] ?? false,
    lat: json['lat']?.toDouble(),
    lng: json['lng']?.toDouble(),
    suggestedHelpline: json['suggested_helpline'],
  );
}

@riverpod
class AgentNotifier extends _\$AgentNotifier {
  @override
  AgentState build() => const AgentState();

  void setPhase(AgentPhase phase) =>
    state = state.copyWith(phase: phase);

  void appendTranscript(String text) =>
    state = state.copyWith(transcript: text);

  void addReasoningStep(String step) =>
    state = state.copyWith(
      reasoningSteps: [...state.reasoningSteps, step]
    );

  void setExtractedData(CivicReport report) =>
    state = state.copyWith(
      extractedData: report,
      phase: AgentPhase.review,
    );

  void reset() => state = const AgentState();
}
```

---

## Voice Orb Widget (Animated Microphone)

```dart
// lib/features/agent/presentation/widgets/voice_orb_widget.dart

class VoiceOrbWidget extends ConsumerWidget {
  const VoiceOrbWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final phase = ref.watch(agentNotifierProvider).phase;

    return GestureDetector(
      onTap: () => ref.read(voiceProviderProvider.notifier).toggleListening(),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        width: phase == AgentPhase.listening ? 100 : 80,
        height: phase == AgentPhase.listening ? 100 : 80,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: _getOrbColor(phase),
          boxShadow: phase == AgentPhase.listening
            ? [BoxShadow(
                color: Colors.red.withOpacity(0.4),
                blurRadius: 20,
                spreadRadius: 10,
              )]
            : [],
        ),
        child: Center(
          child: phase == AgentPhase.listening
            ? Lottie.asset('assets/lottie/pulse.json', width: 60)
            : const Icon(Icons.mic, color: Colors.white, size: 36),
        ),
      ).animate(
        onPlay: (ctrl) => phase == AgentPhase.listening
          ? ctrl.repeat()
          : ctrl.stop(),
      ).scale(
        begin: const Offset(1, 1),
        end: const Offset(1.05, 1.05),
        duration: 600.ms,
        curve: Curves.easeInOut,
      ),
    );
  }

  Color _getOrbColor(AgentPhase phase) => switch (phase) {
    AgentPhase.idle => Colors.blue.shade700,
    AgentPhase.listening => Colors.red.shade600,
    AgentPhase.transcribing => Colors.orange.shade600,
    AgentPhase.reasoning => Colors.purple.shade600,
    AgentPhase.extracting => Colors.teal.shade600,
    AgentPhase.review => Colors.green.shade600,
    AgentPhase.confirmed => Colors.green.shade800,
    AgentPhase.error => Colors.red.shade900,
  };
}
```

---

## Reasoning Ticker Widget (Live AI Thinking)

```dart
// lib/features/agent/presentation/widgets/reasoning_ticker_widget.dart

class ReasoningTickerWidget extends ConsumerWidget {
  const ReasoningTickerWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(agentNotifierProvider);

    if (state.phase == AgentPhase.idle ||
        state.phase == AgentPhase.confirmed) {
      return const SizedBox.shrink();
    }

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.black87,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.purple.shade700, width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 8, height: 8,
                decoration: const BoxDecoration(
                  color: Colors.purple,
                  shape: BoxShape.circle,
                ),
              ).animate(onPlay: (c) => c.repeat())
               .scaleXY(end: 0.5, duration: 600.ms)
               .then()
               .scaleXY(end: 1.0, duration: 600.ms),
              const SizedBox(width: 8),
              Text(
                'AI Agent - ${_phaseLabel(state.phase)}',
                style: const TextStyle(
                  color: Colors.purple,
                  fontSize: 11,
                  fontFamily: 'monospace',
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          // Live transcript if listening
          if (state.transcript.isNotEmpty)
            Text(
              '"${state.transcript}"',
              style: TextStyle(
                color: Colors.white.withOpacity(0.7),
                fontSize: 13,
                fontStyle: FontStyle.italic,
              ),
            ),
          const SizedBox(height: 4),
          // Reasoning steps
          ...state.reasoningSteps.asMap().entries.map((e) =>
            Text(
              '> ${e.value}',
              style: TextStyle(
                color: e.key == state.reasoningSteps.length - 1
                  ? Colors.greenAccent
                  : Colors.white.withOpacity(0.5),
                fontSize: 12,
                fontFamily: 'monospace',
              ),
            ).animate().fadeIn(duration: 300.ms),
          ),
        ],
      ),
    );
  }

  String _phaseLabel(AgentPhase phase) => switch (phase) {
    AgentPhase.listening => 'LISTENING...',
    AgentPhase.transcribing => 'TRANSCRIBING...',
    AgentPhase.reasoning => 'REASONING...',
    AgentPhase.extracting => 'EXTRACTING DATA...',
    AgentPhase.review => 'AWAITING REVIEW',
    _ => 'PROCESSING...',
  };
}
```

---

## Live Form Auto-fill Widget

````dart
// lib/features/agent/presentation/widgets/live_form_widget.dart

class LiveFormWidget extends ConsumerStatefulWidget {
  const LiveFormWidget({super.key});

  @override
  ConsumerState<LiveFormWidget> createState() => _LiveFormWidgetState();
}

class _LiveFormWidgetState extends ConsumerState<LiveFormWidget> {
  late TextEditingController _categoryCtrl;
  late TextEditingController _locationCtrl;
  late TextEditingController _descCtrl;

  @override
  void initState() {
    super.initState();
    _categoryCtrl = TextEditingController();
    _locationCtrl = TextEditingController();
    _descCtrl = TextEditingController();
  }

  @override
  Widget build(BuildContext context) {
    final report = ref.watch(agentNotifierProvider).extractedData;

    // Animate fill when data arrives
    ref.listen(agentNotifierProvider, (prev, next) {
      if (next.extractedData != null && prev?.extractedData == null) {
        _animateFill(next.extractedData!);
      }
    });

    if (report == null) return const SizedBox.shrink();

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          _buildField('Category', _categoryCtrl, Icons.category),
          const SizedBox(height: 12),
          _buildField('Location', _locationCtrl, Icons.location_on),
          const SizedBox(height: 12),
          _buildSeverityChip(report.severity),
          const SizedBox(height: 12),
          _buildField('Description', _descCtrl, Icons.description,
            maxLines: 3),
          const SizedBox(height: 20),
          // Emergency banner
          if (report.isEmergency)
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.red.shade50,
                border: Border.all(color: Colors.red),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  const Icon(Icons.warning, color: Colors.red),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Emergency detected! Routing to: \${report.suggestedHelpline}',
                      style: const TextStyle(color: Colors.red, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  // Simulate typewriter fill animation
  Future<void> _animateFill(CivicReport report) async {
    await _typewriterFill(_categoryCtrl,
      '\${report.category} → \${report.subCategory}');
    await _typewriterFill(_locationCtrl, report.location);
    await _typewriterFill(_descCtrl, report.description);
  }

  Future<void> _typewriterFill(
    TextEditingController ctrl, String text) async {
    ctrl.clear();
    for (int i = 0; i <= text.length; i++) {
      await Future.delayed(const Duration(milliseconds: 30));
      ctrl.text = text.substring(0, i);
    }
  }

  Widget _buildField(String label, TextEditingController ctrl,
    IconData icon, {int maxLines = 1}) {
    return TextFormField(
      controller: ctrl,
      maxLines: maxLines,
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        fillColor: Colors.blue.shade50,
        filled: true,
      ),
    );
  }

  Widget _buildSeverityChip(String severity) {
    final color = switch (severity) {
      'critical' => Colors.red,
      'high' => Colors.orange,
      'medium' => Colors.yellow.shade700,
      _ => Colors.green,
    };

    return Row(
      children: [
        const Text('Severity: ', style: TextStyle(fontWeight: FontWeight.bold)),
        Chip(
          label: Text(severity.toUpperCase()),
          backgroundColor: color.withOpacity(0.2),
          side: BorderSide(color: color),
          labelStyle: TextStyle(color: color, fontWeight: FontWeight.bold),
        ),
      ],
    );
  }
}
```\n\n
````
