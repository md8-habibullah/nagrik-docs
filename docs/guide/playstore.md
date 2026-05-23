# Google Play Store — Full Submission Guide\n\n## Pre-submission Checklist

- [ ] App tested on Android 8.0+ (API 26+)
- [ ] All permissions have user-facing explanations
- [ ] Privacy policy URL live (required)
- [ ] Terms of service URL live
- [ ] App icon (512×512 PNG, no alpha)
- [ ] Feature graphic (1024×500 PNG)
- [ ] Screenshots (minimum 2, max 8 per device type)
- [ ] Release APK/AAB signed with keystore

---

## Build Release APK

```bash
# 1. Generate signing keystore (one time only)
keytool -genkey -v \\
  -keystore nagrik-ai.keystore \\
  -alias nagrik-ai \\
  -keyalg RSA \\
  -keysize 2048 \\
  -validity 10000

# 2. Add to android/key.properties
storePassword=YOUR_STORE_PASSWORD
keyPassword=YOUR_KEY_PASSWORD
keyAlias=nagrik-ai
storeFile=../nagrik-ai.keystore

# 3. Update android/app/build.gradle
# (Add signingConfigs block)

# 4. Build release AAB (App Bundle — preferred for Play Store)
flutter build appbundle --release

# Output: build/app/outputs/bundle/release/app-release.aab

# 5. Build APK (for direct distribution)
flutter build apk --release --split-per-abi
```

---

## android/app/build.gradle (Signing Config)

```groovy
def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}

android {
    compileSdkVersion 34

    defaultConfig {
        applicationId "ai.nagrik.app"
        minSdkVersion 26
        targetSdkVersion 34
        versionCode 1
        versionName "1.0.0"
    }

    signingConfigs {
        release {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile keystoreProperties['storeFile'] ?
                file(keystoreProperties['storeFile']) : null
            storePassword keystoreProperties['storePassword']
        }
    }

    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android.txt'),
                'proguard-rules.pro'
        }
    }
}
```

---

## Play Store Listing Content

```
App Name: NagrikAI - নাগরিক সহায়ক

Short Description (80 chars max):
বাংলাদেশের প্রথম AI ভয়েস সিভিক এজেন্ট ও ইমার্জেন্সি রাউটার

Full Description:
NagrikAI হল বাংলাদেশের নাগরিকদের জন্য একটি AI-চালিত ভয়েস সহায়ক।
শুধু বলুন — বাকিটা NagrikAI করবে।

✅ ভয়েস দিয়ে সিভিক অভিযোগ দাখিল করুন
✅ জরুরি পরিস্থিতিতে স্বয়ংক্রিয় হেল্পলাইন রাউটিং (999, 333, 109)
✅ কাছের পুলিশ, হাসপাতাল, অ্যাম্বুলেন্স খুঁজুন
✅ বাংলাদেশের আইন সম্পর্কে প্রশ্ন করুন
✅ ঝুঁকিপূর্ণ এলাকায় স্বয়ংক্রিয় সতর্কতা
✅ প্যানিক বাটন — শেক করুন বা বলুন "সাহায্য করো"
✅ সরকারি ফর্ম স্বয়ংক্রিয় পূরণ ও PDF ডাউনলোড
✅ বাংলাদেশের সর্বশেষ সংবাদ

Category: Productivity / Social
Content Rating: Everyone
Price: Free

Tags: civic, bangladesh, emergency, AI, bangla, safety
```

---

## Play Store Required Policies

```
1. Privacy Policy (REQUIRED — host on website)
   Mention:
   - Location data collection and purpose
   - Microphone usage
   - Data stored in Supabase (EU servers)
   - No data sold to third parties
   - User data deletion option

2. Permissions Declaration (Play Console)
   For each sensitive permission, explain:
   - ACCESS_BACKGROUND_LOCATION:
     "Background location is used to alert users when
     they enter high-risk zones, even when the app
     is not actively open."

   - RECORD_AUDIO:
     "Microphone is used only for voice civic reporting
     and emergency recording. Audio is not stored
     without explicit user confirmation."

   - CALL_PHONE:
     "Used exclusively for one-tap emergency helpline
     calling (999, 333, 109) during panic situations."

3. Data Safety Section (Play Console)
   Fill out truthfully:
   - Location: Collected, shared with your backend
   - Personal info: Name, email, phone collected
   - Audio: Collected on explicit user action only
   - Financial info: None
   - Encryption: Yes (HTTPS + AES storage)
```

---

## Internal Testing → Beta → Production

```
Week 1-2: Internal testing
  → Upload AAB to Internal Testing track
  → Share with team (max 100 testers)
  → Fix crashes from Firebase Crashlytics

Week 3-4: Open Beta
  → Move to Open Testing track
  → Share opt-in link publicly
  → Get real user feedback
  → Monitor ANR/crash rates (target < 1%)

Week 5+: Production
  → 20% rollout first
  → Monitor ratings + crash rate
  → 100% rollout if stable
```\n\n