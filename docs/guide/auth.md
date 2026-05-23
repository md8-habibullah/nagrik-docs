# Auth & User Profiles\n\n## Authentication Flow

```
Registration:
User fills form → Supabase Auth creates account
  → Email/SMS OTP verification
  → User completes profile (name, NID area, phone)
  → JWT issued → stored in flutter_secure_storage

Login:
Email + Password → Supabase Auth
  → JWT access token (1 hour expiry)
  → Refresh token (30 days)
  → Both stored securely on device

Phone Login (alternative):
Phone number → OTP via SMS (Supabase Twilio integration)
  → Verify OTP → JWT issued
```

---

## Supabase Auth Setup (Flutter)

```dart
// lib/core/config/supabase_config.dart

Future<void> initSupabase() async {
  await Supabase.initialize(
    url: Env.supabaseUrl,
    anonKey: Env.supabaseAnonKey,
    authOptions: const FlutterAuthClientOptions(
      authFlowType: AuthFlowType.pkce,
      autoRefreshToken: true,
    ),
    storageOptions: const StorageClientOptions(
      retryAttempts: 3,
    ),
  );
}

// Auth Provider
@riverpod
class AuthNotifier extends _\$AuthNotifier {
  @override
  AsyncValue<User?> build() {
    return AsyncValue.data(
      Supabase.instance.client.auth.currentUser
    );
  }

  Future<void> signUpWithEmail({
    required String email,
    required String password,
    required String nameBn,
    required String phone,
  }) async {
    state = const AsyncValue.loading();

    final response = await Supabase.instance.client.auth.signUp(
      email: email,
      password: password,
      data: {
        'name_bn': nameBn,
        'phone': phone,
      },
    );

    if (response.user != null) {
      // Create user profile in our DB
      await Supabase.instance.client
        .from('users')
        .insert({
          'id': response.user!.id,
          'email': email,
          'name_bn': nameBn,
          'phone': phone,
        });
    }

    state = AsyncValue.data(response.user);
  }

  Future<void> signInWithPhone(String phone) async {
    await Supabase.instance.client.auth.signInWithOtp(
      phone: '+880\${phone.replaceAll(RegExp(r'^0'), '')}',
    );
  }

  Future<void> verifyOTP(String phone, String otp) async {
    final response = await Supabase.instance.client.auth.verifyOTP(
      phone: '+880\${phone.replaceAll(RegExp(r'^0'), '')}',
      token: otp,
      type: OtpType.sms,
    );
    state = AsyncValue.data(response.user);
  }

  Future<void> signOut() async {
    await Supabase.instance.client.auth.signOut();
    state = const AsyncValue.data(null);
  }
}
```

---

## User Profile Screen

```dart
// Collect at onboarding - saves to Supabase:
// ✅ নাম (Bengali + English)
// ✅ NID area / District
// ✅ Phone number
// ✅ Permanent address
// ✅ Emergency contacts (up to 5)
// ✅ Profile photo (Supabase Storage)
// ✅ Preferred language (Bangla / English)
// ✅ Notification preferences

class OnboardingProfileScreen extends ConsumerStatefulWidget {
  // Multi-step form:
  // Step 1: Basic info (name, phone)
  // Step 2: Location (division/district/thana dropdown - BD specific)
  // Step 3: Emergency contacts
  // Step 4: Permissions (location, mic, notifications)
}
```

---

## Bangladesh Division/District/Thana Dropdown

```dart
// Bundled in app - no API needed
// assets/data/bd_geo.json

{
  "divisions": [
    {
      "id": "dhaka",
      "name_bn": "ঢাকা",
      "name_en": "Dhaka",
      "districts": [
        {
          "id": "dhaka_city",
          "name_bn": "ঢাকা",
          "name_en": "Dhaka",
          "thanas": [
            { "id": "dhanmondi", "name_bn": "ধানমন্ডি", "name_en": "Dhanmondi" },
            { "id": "mirpur", "name_bn": "মিরপুর", "name_en": "Mirpur" },
            // ... all thanas
          ]
        }
      ]
    }
    // ... all 8 divisions → 64 districts → all thanas
  ]
}
```\n\n