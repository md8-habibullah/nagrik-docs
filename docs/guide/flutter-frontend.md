# Flutter App — Full Implementation\n\n## Project Structure

```
nagrik_ai/
├── lib/
│   ├── main.dart
│   ├── app.dart                    # GoRouter + Riverpod setup
│   ├── core/
│   │   ├── constants/
│   │   │   ├── api_endpoints.dart
│   │   │   ├── bd_helplines.dart   # 999, 333, 109, 16123 etc.
│   │   │   └── app_colors.dart
│   │   ├── services/
│   │   │   ├── background_service.dart
│   │   │   ├── location_service.dart
│   │   │   └── notification_service.dart
│   │   └── utils/
│   │       ├── permission_handler.dart
│   │       └── connectivity_checker.dart
│   ├── features/
│   │   ├── auth/
│   │   │   ├── presentation/       # login, register screens
│   │   │   ├── providers/
│   │   │   └── repository/
│   │   ├── agent/                  # Voice AI agent
│   │   │   ├── presentation/
│   │   │   │   ├── agent_screen.dart
│   │   │   │   ├── widgets/
│   │   │   │   │   ├── voice_orb_widget.dart
│   │   │   │   │   ├── reasoning_ticker_widget.dart
│   │   │   │   │   ├── live_form_widget.dart
│   │   │   │   │   └── confirm_action_sheet.dart
│   │   │   ├── providers/
│   │   │   │   ├── agent_state_provider.dart
│   │   │   │   └── voice_provider.dart
│   │   │   └── repository/
│   │   ├── maps/                   # Maps + nearby places
│   │   ├── emergency/              # Panic button + routing
│   │   ├── news/                   # Bangladesh news
│   │   ├── law/                    # BD Law AI
│   │   ├── profile/                # User profile
│   │   └── reports/                # Past civic reports
│   └── shared/
│       ├── widgets/
│       └── models/
├── android/
│   ├── app/src/main/
│   │   ├── AndroidManifest.xml     # Permissions
│   │   └── res/
│   │       └── drawable/           # Notification icons
└── ios/
    └── Runner/
        └── Info.plist              # iOS permissions
```

---

## pubspec.yaml — All Required Packages

```yaml
name: nagrik_ai
description: AI-Driven Voice Civic Agent for Bangladesh
version: 1.0.0+1

environment:
  sdk: ">=3.0.0 <4.0.0"
  flutter: ">=3.16.0"

dependencies:
  flutter:
    sdk: flutter

  # State Management
  flutter_riverpod: ^2.5.0
  riverpod_annotation: ^2.3.3

  # Navigation
  go_router: ^13.0.0

  # Network
  dio: ^5.4.0
  retrofit: ^4.1.0

  # Database (local)
  drift: ^2.16.0
  drift_sqflite: ^2.1.0
  sqflite: ^2.3.0

  # Auth & Backend
  supabase_flutter: ^2.3.4

  # Voice & STT
  speech_to_text: ^6.6.0
  permission_handler: ^11.3.0
  record: ^5.1.0              # audio recording for panic

  # Maps
  flutter_map: ^6.1.0
  latlong2: ^0.9.0
  flutter_map_cache: ^1.1.0   # offline tile caching
  geolocator: ^11.0.0
  geocoding: ^3.0.0

  # Background Services
  flutter_background_service: ^5.0.5
  workmanager: ^0.5.2
  background_locator_2: ^2.1.0

  # Notifications
  firebase_messaging: ^14.9.1
  flutter_local_notifications: ^17.0.0

  # Emergency / Panic
  shake: ^2.2.0               # shake gesture detection
  url_launcher: ^6.2.5        # for phone calls
  just_audio: ^0.9.37         # panic alarm sound

  # UI & Animations
  lottie: ^3.0.0
  animated_text_kit: ^4.2.2
  flutter_animate: ^4.5.0
  cached_network_image: ^3.3.1

  # PDF & Forms
  pdf: ^3.11.1
  printing: ^5.13.1
  open_file: ^3.3.2

  # Storage
  flutter_secure_storage: ^9.0.0
  shared_preferences: ^2.2.2
  path_provider: ^2.1.2

  # Utils
  connectivity_plus: ^6.0.2
  package_info_plus: ^7.0.0
  intl: ^0.19.0
  uuid: ^4.3.3
  logger: ^2.2.0

  # Firebase (crash reporting)
  firebase_core: ^2.29.0
  firebase_crashlytics: ^3.5.1
  firebase_analytics: ^10.10.1

dev_dependencies:
  flutter_test:
    sdk: flutter
  build_runner: ^2.4.8
  riverpod_generator: ^2.3.9
  retrofit_generator: ^8.1.0
  drift_dev: ^2.16.0
  flutter_lints: ^4.0.0
```

---

## AndroidManifest.xml — Critical Permissions

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

  <!-- Internet -->
  <uses-permission android:name="android.permission.INTERNET"/>
  <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>

  <!-- Location (foreground + background) -->
  <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
  <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>
  <uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION"/>
  <uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
  <uses-permission android:name="android.permission.FOREGROUND_SERVICE_LOCATION"/>

  <!-- Microphone -->
  <uses-permission android:name="android.permission.RECORD_AUDIO"/>

  <!-- Phone calls (panic button) -->
  <uses-permission android:name="android.permission.CALL_PHONE"/>
  <uses-permission android:name="android.permission.SEND_SMS"/>

  <!-- Notifications -->
  <uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
  <uses-permission android:name="android.permission.VIBRATE"/>
  <uses-permission android:name="android.permission.WAKE_LOCK"/>

  <!-- Camera (for report photo attachment) -->
  <uses-permission android:name="android.permission.CAMERA"/>

  <!-- Boot (restart background service after reboot) -->
  <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>

  <application
    android:label="NagrikAI"
    android:name="\${applicationName}"
    android:icon="@mipmap/ic_launcher"
    android:enableOnBackInvokedCallback="true">

    <!-- Background location service -->
    <service
      android:name="com.ryanheise.audioservice.AudioServiceIsolateService"
      android:foregroundServiceType="location"
      android:exported="false"/>

    <receiver
      android:name="com.it_nomads.flutterSecureStorage.ciphers.StorageCipherFactory"
      android:exported="false"/>

  </application>
</manifest>
```

---

## iOS Info.plist — Required Permissions

```xml
<!-- Add to ios/Runner/Info.plist -->
<key>NSMicrophoneUsageDescription</key>
<string>NagrikAI ব্যবহারকারীর ভয়েস ইনপুট এবং ইমার্জেন্সি রেকর্ডিংয়ের জন্য মাইক্রোফোন প্রয়োজন।</string>

<key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
<string>NagrikAI আপনার নিরাপত্তার জন্য লোকেশন ট্র্যাক করে এবং কাছের পুলিশ/হাসপাতাল খুঁজে দেয়।</string>

<key>NSLocationWhenInUseUsageDescription</key>
<string>NagrikAI কাছের সেবা এবং ঝুঁকি সতর্কতার জন্য আপনার অবস্থান প্রয়োজন।</string>

<key>NSLocationAlwaysUsageDescription</key>
<string>NagrikAI পটভূমিতে ঝুঁকিপূর্ণ এলাকা সতর্কতার জন্য লোকেশন প্রয়োজন।</string>

<key>NSCameraUsageDescription</key>
<string>সিভিক রিপোর্টে ছবি সংযুক্ত করার জন্য ক্যামেরা প্রয়োজন।</string>

<key>UIBackgroundModes</key>
<array>
  <string>location</string>
  <string>fetch</string>
  <string>remote-notification</string>
  <string>audio</string>
</array>
```\n\n
## Bit-by-Bit Implementation: State Management

We use **Riverpod** because it is compile-safe and handles asynchronous state (like waiting for API calls or voice streams) gracefully using `AsyncValue`.

### Step-by-Step Logic for the Agent Sandbox
1. **The Provider (`AgentNotifier`)**: Holds the current phase of the UI (Listening, Transcribing, Reasoning, etc).
2. **The Mic Button**: When tapped, it triggers `ref.read(agentNotifierProvider.notifier).setPhase(AgentPhase.listening)`.
3. **The Voice Stream**: As `flutter_speech_to_text` yields partial words, we call `appendTranscript(text)`.
4. **The UI Reaction**: The UI is simply a `ConsumerWidget` that listens to `AgentNotifier`. If `phase == listening`, the microphone pulses red. If `phase == reasoning`, a loading ticker appears.

## Alternative Approaches to Consider
1. **BLoC instead of Riverpod?**
   - *Pros*: BLoC is extremely structured and great for massive enterprise apps.
   - *Cons*: Highly boilerplate-heavy. For a 1-month MVP, creating Events, States, and Blocs for every tiny feature will slow the team down. Riverpod offers the safety of BLoC with the simplicity of Provider.
