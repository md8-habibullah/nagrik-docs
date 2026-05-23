# Apple App Store — Full Submission Guide\n\n## Requirements

- **Mac computer** required for iOS builds
- **Apple Developer Account** ($99/year)
- **Xcode 15+**
- iOS 14.0+ target (covers 95%+ of devices)

---

## iOS Build Setup

```bash
# 1. In Xcode, set Bundle Identifier
# ai.nagrik.app

# 2. Set minimum iOS version
# ios/Podfile → platform :ios, '14.0'

# 3. Install pods
cd ios && pod install && cd ..

# 4. Set up signing in Xcode
# Xcode → Runner → Signing & Capabilities
# → Team: your Apple Developer account
# → Bundle ID: ai.nagrik.app

# 5. Build for App Store
flutter build ipa --release

# Output: build/ios/ipa/nagrik_ai.ipa
```

---

## Info.plist — All Required Keys

```xml
<!-- Location (REQUIRED — very detailed explanation) -->
<key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
<string>
NagrikAI ব্যাকগ্রাউন্ডে আপনার লোকেশন ব্যবহার করে:
১) ঝুঁকিপূর্ণ এলাকায় প্রবেশ করলে সতর্কতা পাঠাতে
২) প্যানিক বাটন চাপলে আপনার অবস্থান পাঠাতে
৩) কাছের হাসপাতাল ও পুলিশ খুঁজে দিতে
লোকেশন কখনো তৃতীয় পক্ষের কাছে বিক্রি করা হয় না।
</string>

<!-- Microphone -->
<key>NSMicrophoneUsageDescription</key>
<string>
NagrikAI ভয়েস রিপোর্ট করতে এবং ইমার্জেন্সিতে অডিও রেকর্ড করতে
মাইক্রোফোন ব্যবহার করে। অডিও শুধুমাত্র আপনার অনুমতিতে সেভ হয়।
</string>

<!-- Camera -->
<key>NSCameraUsageDescription</key>
<string>
সিভিক রিপোর্টে ছবি সংযুক্ত করতে ক্যামেরা ব্যবহার করা হয়।
</string>

<!-- Contacts (for emergency contacts import) -->
<key>NSContactsUsageDescription</key>
<string>
ইমার্জেন্সি কনট্যাক্ট যোগ করতে আপনার ফোনবুক ব্যবহার করা হতে পারে।
</string>
```

---

## App Store Review — Common Rejection Reasons to Avoid

```
❌ Crash on launch
   Fix: Test on real device, not just simulator

❌ Location used without justification
   Fix: Show location permission prompt at right moment
        (when user first uses a location feature, not on launch)

❌ Empty states / incomplete features
   Fix: Ensure all listed features actually work

❌ Privacy policy missing or generic
   Fix: Write Bangladesh-specific privacy policy, mention Supabase

❌ Metadata doesn't match app
   Fix: Screenshots must match actual app UI exactly

❌ Calls API without user action
   Fix: Never auto-call. Always show confirmation dialog

❌ Background location not clearly explained
   Fix: Add detailed justification in review notes
```

---

## App Store Listing Content

```
Name: NagrikAI
Subtitle: Bangladesh Civic AI Agent

Keywords (100 chars max):
bangladesh,civic,emergency,bangla,AI,safety,police,hospital,law,নাগরিক

Description:
[Same as Play Store but adjust formatting for App Store style]

Category: Utilities
Secondary Category: Productivity

Age Rating: 4+ (no objectionable content)
Price: Free

Privacy Policy URL: https://nagrik.ai/privacy
Support URL: https://nagrik.ai/support
Marketing URL: https://nagrik.ai
```

---

## TestFlight → Production

```
1. Upload IPA via Xcode or Transporter app
2. Add internal testers (team, max 25 internal)
3. External TestFlight beta (up to 10,000 testers, needs review)
4. Submit for App Review (1-3 business days average)
5. Phased release: 1% → 2% → 5% → 10% → 50% → 100%
   (each phase monitored for crash rate)
```\n\n