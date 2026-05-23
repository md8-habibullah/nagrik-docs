# Panic Button System\n\n## Panic Trigger Methods

Three simultaneous trigger methods - any one activates panic mode:

1. **Physical:** Volume Down × 3 rapid presses
2. **Gesture:** Phone shake (3 seconds continuous)
3. **Voice keyword:** "সাহায্য করো" / "বাঁচাও" / "help me"

---

## Panic Actions (On Trigger)

```
1. Play loud alarm sound (even if phone muted)
2. Send SMS to all emergency contacts with GPS location
3. Start background audio recording
4. Auto-call 999 after 5 second countdown (cancellable)
5. Upload location + audio to server for evidence
6. Notify app admin dashboard
```

---

## Panic Service Implementation

```dart
// lib/features/emergency/services/panic_service.dart

import 'package:shake/shake.dart';
import 'package:just_audio/just_audio.dart';
import 'package:url_launcher/url_launcher.dart';

class PanicService {
  static final PanicService _instance = PanicService._internal();
  factory PanicService() => _instance;
  PanicService._internal();

  ShakeDetector? _shakeDetector;
  final AudioPlayer _alarmPlayer = AudioPlayer();
  bool _panicActive = false;

  // Initialize all panic triggers
  Future<void> initialize(WidgetRef ref) async {
    _initShakeDetector(ref);
    _initVolumeButtonListener(ref);
    _preloadAlarm();
  }

  void _initShakeDetector(WidgetRef ref) {
    _shakeDetector = ShakeDetector.autoStart(
      onPhoneShake: () {
        if (!_panicActive) {
          triggerPanic(ref, trigger: 'shake');
        }
      },
      shakeThresholdGravity: 2.7,
      shakeSlopTimeMS: 500,
      shakeCountResetTime: 3000,
      minimumShakeCount: 3,
    );
  }

  void _initVolumeButtonListener(WidgetRef ref) {
    // Uses android_intent_plus or platform channel
    // Monitor volume button presses via MethodChannel
    const channel = MethodChannel('nagrik_ai/volume_buttons');
    channel.setMethodCallHandler((call) async {
      if (call.method == 'volumeDownTriplePress') {
        triggerPanic(ref, trigger: 'volume_button');
      }
    });
  }

  Future<void> _preloadAlarm() async {
    await _alarmPlayer.setAsset('assets/audio/emergency_alarm.mp3');
  }

  Future<void> triggerPanic(WidgetRef ref, {
    required String trigger,
  }) async {
    if (_panicActive) return;
    _panicActive = true;

    // 1. Play alarm immediately
    await _alarmPlayer.setVolume(1.0);
    await _alarmPlayer.play();

    // 2. Get current location
    final position = await Geolocator.getCurrentPosition(
      desiredAccuracy: LocationAccuracy.high,
    );

    final location = '${position.latitude},${position.longitude}';
    final mapsLink = 'https://maps.google.com/?q=\$location';

    // 3. Start audio recording
    _startEmergencyRecording();

    // 4. Send SMS to emergency contacts
    final contacts = ref.read(emergencyContactsProvider);
    for (final contact in contacts) {
      await _sendEmergencySMS(
        phone: contact.phone,
        message: '🆘 NagrikAI EMERGENCY ALERT\\n'
                 '\${contact.ownerName} needs help!\\n'
                 'Location: \$mapsLink\\n'
                 'Time: \${DateTime.now()}\\n'
                 'Trigger: \$trigger',
      );
    }

    // 5. Upload to server
    await _uploadPanicEvent(
      lat: position.latitude,
      lng: position.longitude,
      trigger: trigger,
    );

    // 6. Show countdown dialog → auto-call 999
    // This is shown in the UI layer
    ref.read(panicStateProvider.notifier).activate(
      position: position,
      countdownSeconds: 5,
    );
  }

  Future<void> _sendEmergencySMS({
    required String phone,
    required String message,
  }) async {
    final uri = Uri(
      scheme: 'sms',
      path: phone,
      queryParameters: {'body': message},
    );
    await launchUrl(uri);
  }

  Future<void> callEmergency(String number) async {
    final uri = Uri(scheme: 'tel', path: number);
    await launchUrl(uri);
  }

  Future<void> cancelPanic() async {
    _panicActive = false;
    await _alarmPlayer.stop();
    await _stopEmergencyRecording();
  }
}
```

---

## Volume Button Native Channel (Android)

```kotlin
// android/app/src/main/kotlin/MainActivity.kt

import android.view.KeyEvent
import io.flutter.embedding.android.FlutterActivity
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    private val CHANNEL = "nagrik_ai/volume_buttons"
    private var volumeDownCount = 0
    private var lastVolumePress = 0L

    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {
        if (keyCode == KeyEvent.KEYCODE_VOLUME_DOWN) {
            val now = System.currentTimeMillis()
            if (now - lastVolumePress < 500) {
                volumeDownCount++
                if (volumeDownCount >= 3) {
                    // Triple press detected
                    flutterEngine?.dartExecutor?.binaryMessenger?.let { messenger ->
                        MethodChannel(messenger, CHANNEL)
                            .invokeMethod("volumeDownTriplePress", null)
                    }
                    volumeDownCount = 0
                }
            } else {
                volumeDownCount = 1
            }
            lastVolumePress = now
            return true
        }
        return super.onKeyDown(keyCode, event)
    }
}
```

---

## Panic Screen UI

```dart
class PanicScreen extends ConsumerStatefulWidget {
  // Full-screen red alert with countdown
  // Shows:
  // - Big "EMERGENCY" text
  // - Countdown timer (5 → 0 → calls 999)
  // - Cancel button
  // - "Calling 999..." status
  // - Location shared confirmation
  // - "SMS sent to X contacts" confirmation
}
```

---

## Voice Keyword Detection

```dart
// During active listening, check for panic keywords

const List<String> PANIC_KEYWORDS = [
  'সাহায্য করো', 'বাঁচাও', 'help me',
  'আমাকে বাঁচাও', 'emergency', 'ইমার্জেন্সি',
  'আগুন', 'ডাকাত', 'ধর্ষণ', 'আক্রমণ',
];

bool containsPanicKeyword(String transcript) {
  final lower = transcript.toLowerCase();
  return PANIC_KEYWORDS.any((kw) => lower.contains(kw));
}
```\n\n## Location Tracking & Risk Zones\n\n## Location Architecture

```
Foreground (app open):
  geolocator → high accuracy → update every 30 seconds
  → show on map in real-time

Background (app minimized/closed):
  flutter_background_service → foreground service (Android)
  WorkManager → periodic task every 15 minutes
  → store in SQLite + sync to Supabase when online

Risk zone checking:
  On each location update → check if inside any risk zone polygon
  → if entered risk zone → trigger notification
```

---

## Background Location Service

```dart
// lib/core/services/background_service.dart

import 'package:flutter_background_service/flutter_background_service.dart';

Future<void> initBackgroundService() async {
  final service = FlutterBackgroundService();

  await service.configure(
    androidConfiguration: AndroidConfiguration(
      onStart: onStart,
      autoStart: true,
      isForegroundMode: true,           // Required for background location
      notificationChannelId: 'nagrik_location',
      initialNotificationTitle: 'NagrikAI সক্রিয়',
      initialNotificationContent: 'আপনার নিরাপত্তা পর্যবেক্ষণ করছে...',
      foregroundServiceNotificationId: 888,
      foregroundServiceTypes: [
        AndroidForegroundType.location,  // Android 14+ required
      ],
    ),
    iosConfiguration: IosConfiguration(
      autoStart: true,
      onForeground: onStart,
      onBackground: onIosBackground,
    ),
  );

  await service.startService();
}

@pragma('vm:entry-point')
void onStart(ServiceInstance service) async {
  DartPluginRegistrant.ensureInitialized();

  // Update notification
  service.on('setAsForeground').listen((event) {
    service.setAsForegroundService();
  });

  // Location tracking loop
  Timer.periodic(const Duration(minutes: 15), (timer) async {
    await _captureAndCheckLocation(service);
  });
}

Future<void> _captureAndCheckLocation(ServiceInstance service) async {
  try {
    final position = await Geolocator.getCurrentPosition(
      desiredAccuracy: LocationAccuracy.balanced,
      timeLimit: const Duration(seconds: 10),
    );

    // Store locally
    final db = await getDatabase();
    await db.insert('location_snapshots', {
      'lat': position.latitude,
      'lng': position.longitude,
      'captured_at': DateTime.now().toIso8601String(),
    });

    // Check risk zones
    await _checkRiskZones(position.latitude, position.longitude);

    // Sync to server if online
    final isConnected = await Connectivity()
      .checkConnectivity() != ConnectivityResult.none;
    if (isConnected) {
      await _syncLocationToServer(position);
    }

  } catch (e) {
    // Silent fail - battery optimization may block
    debugPrint('Background location error: \$e');
  }
}
```

---

## Risk Zone Detection

```dart
Future<void> _checkRiskZones(double lat, double lng) async {
  final riskZones = await _getCachedRiskZones();

  for (final zone in riskZones) {
    if (_isPointInPolygon(lat, lng, zone.boundary)) {
      if (!_wasAlreadyNotified(zone.id)) {
        // Trigger notification
        await _sendRiskZoneAlert(zone);
        _markNotified(zone.id);
      }
    }
  }
}

// Point-in-polygon algorithm (ray casting)
bool _isPointInPolygon(
  double lat, double lng,
  List<LatLng> polygon
) {
  bool inside = false;
  int n = polygon.length;

  for (int i = 0, j = n - 1; i < n; j = i++) {
    final xi = polygon[i].latitude, yi = polygon[i].longitude;
    final xj = polygon[j].latitude, yj = polygon[j].longitude;

    final intersect = ((yi > lng) != (yj > lng)) &&
        (lat < (xj - xi) * (lng - yi) / (yj - yi) + xi);

    if (intersect) inside = !inside;
  }

  return inside;
}
```

---

## Dhaka Risk Zones Database (Initial Data)

```typescript
// Initial Dhaka risk zones - manually curated
// Seed via Prisma seed script

const DHAKA_RISK_ZONES = [
  {
    id: 'dhaka-old-town-flood',
    name_bn: 'পুরান ঢাকা বন্যা ঝুঁকি',
    level: 'high',
    type: 'flood',
    boundary: [/* GeoJSON coordinates */],
    description: 'বর্ষাকালে জলাবদ্ধতার উচ্চ ঝুঁকি',
  },
  {
    id: 'mirpur-crime-zone',
    name_bn: 'মিরপুর ছিনতাই সতর্কতা',
    level: 'medium',
    type: 'crime',
    boundary: [/* polygon */],
    description: 'রাতে চলাচলে সতর্ক থাকুন',
  },
  // ... more zones
];
```

---

## Battery Optimization Warning (Android)

```dart
// On first launch, ask user to disable battery optimization

Future<void> requestBatteryOptimizationExclusion() async {
  if (Platform.isAndroid) {
    // Check if already excluded
    final isIgnoring = await Permission.ignoreBatteryOptimizations.isGranted;

    if (!isIgnoring) {
      showDialog(
        context: context,
        builder: (_) => AlertDialog(
          title: const Text('ব্যাকগ্রাউন্ড সার্ভিস'),
          content: const Text(
            'NagrikAI সঠিকভাবে কাজ করতে ব্যাটারি অপ্টিমাইজেশন বন্ধ রাখুন। '
            'Settings → Battery → NagrikAI → "Don\'t optimize"'
          ),
          actions: [
            TextButton(
              onPressed: () async {
                await Permission.ignoreBatteryOptimizations.request();
              },
              child: const Text('সেটিংস খুলুন'),
            ),
          ],
        ),
      );
    }
  }
}
```\n\n## Emergency Routing System\n\n## Emergency Detection - Automatic

AI automatically detects emergencies from voice:

```
Critical keywords/intent → is_emergency: true
  ↓
Severity: "critical"
  ↓
App shows RED banner: "জরুরি সাহায্য দরকার?"
  ↓
Two options:
  [হ্যাঁ, এখনই কল করুন] [না, রিপোর্ট পাঠান]
  ↓
If YES → Direct call to appropriate helpline
```

---

## Bangladesh Helpline Directory

```dart
// lib/core/constants/bd_helplines.dart

class BdHelplines {
  static const Map<String, HelplineInfo> all = {
    'national_emergency': HelplineInfo(
      number: '999',
      nameBn: 'জাতীয় জরুরি সেবা',
      nameEn: 'National Emergency',
      description: 'পুলিশ, ফায়ার, অ্যাম্বুলেন্স',
      icon: Icons.emergency,
      color: Colors.red,
      categories: ['crime', 'fire', 'medical'],
    ),
    'govt_info': HelplineInfo(
      number: '333',
      nameBn: 'সরকারি তথ্য ও অভিযোগ',
      nameEn: 'Govt Info & Complaints',
      description: 'সরকারি সেবা অভিযোগ',
      categories: ['civic', 'disaster'],
    ),
    'women_children': HelplineInfo(
      number: '109',
      nameBn: 'নারী ও শিশু নির্যাতন',
      nameEn: 'Women & Children Helpline',
      categories: ['crime', 'abuse'],
    ),
    'health': HelplineInfo(
      number: '16000',
      nameBn: 'স্বাস্থ্য সহায়তা',
      nameEn: 'Health Emergency',
      categories: ['medical'],
    ),
    'consumer': HelplineInfo(
      number: '16123',
      nameBn: 'ভোক্তা অধিকার',
      nameEn: 'Consumer Rights',
      categories: ['consumer'],
    ),
    'anti_corruption': HelplineInfo(
      number: '16700',
      nameBn: 'দুর্নীতি দমন',
      nameEn: 'Anti-Corruption (ACC)',
      categories: ['corruption'],
    ),
    'fire': HelplineInfo(
      number: '02-9555555',
      nameBn: 'ফায়ার সার্ভিস',
      nameEn: 'Fire Service',
      categories: ['fire'],
    ),
    'railway': HelplineInfo(
      number: '131',
      nameBn: 'বাংলাদেশ রেলওয়ে',
      nameEn: 'Bangladesh Railway',
      categories: ['transport'],
    ),
    'legal_aid': HelplineInfo(
      number: '16430',
      nameBn: 'জাতীয় আইনি সহায়তা',
      nameEn: 'Legal Aid',
      categories: ['legal'],
    ),
  };

  static String getForCategory(String category) {
    for (final entry in all.entries) {
      if (entry.value.categories.contains(category)) {
        return entry.value.number;
      }
    }
    return '999'; // Default to national emergency
  }
}
```

---

## Emergency Call Routing

```dart
// Immediately call emergency number
Future<void> callHelpline(String number) async {
  final uri = Uri(scheme: 'tel', path: number);

  if (await canLaunchUrl(uri)) {
    await launchUrl(uri);
  } else {
    // Fallback: show number for manual dial
    Clipboard.setData(ClipboardData(text: number));
    showSnackBar('নম্বরটি কপি করা হয়েছে: \$number');
  }
}
```

---

## Emergency Adapter (No-API Fallback)

```typescript
// When no official API available for a department:
// Send structured email/webhook instead

export class EmergencyAdapter {

  async routeReport(report: CivicReport): Promise<void> {
    const department = this.getDepartment(report.category);

    if (department.apiAvailable) {
      await this.sendViaApi(department.apiUrl, report);
    } else if (department.email) {
      await this.sendViaEmail(department.email, report);
    } else {
      await this.sendViaWebhook(department.webhookUrl, report);
    }
  }

  private async sendViaEmail(
    email: string, report: CivicReport
  ): Promise<void> {
    // Use Supabase Edge Function or SendGrid
    await emailService.send({
      to: email,
      subject: \`[NagrikAI] \${report.category} - \${report.location}\`,
      html: this.buildEmailTemplate(report),
    });
  }
}
```\n\n
## Bit-by-Bit Implementation: Panic Button

The panic button must work even if the app is closed (running in the background).

### Step-by-Step Logic
1. **Permissions**: Request `ACCESS_BACKGROUND_LOCATION` and `SEND_SMS` on Android.
2. **Shake Detection**: Use the `shake` Flutter package. When acceleration exceeds a threshold (e.g., 3.0g), trigger the event.
3. **Action Execution**:
   - Get current GPS coordinate via `geolocator`.
   - Reverse geocode to get a readable address (e.g., "Dhaka University Area").
   - Format SMS: "URGENT! I am in danger at [Location]. [Google Maps Link]".
   - Send SMS silently using `telephony` package.

## Alternative Approaches to Consider
1. **Volume Button Intercept instead of Shake?**
   - *Pros*: Less accidental triggers than shaking.
   - *Cons*: Android/iOS strictly forbid overriding hardware buttons when the app is in the background. It will likely get rejected from the Play Store. Shake detection relies on accelerometer data, which is permitted in the background.
