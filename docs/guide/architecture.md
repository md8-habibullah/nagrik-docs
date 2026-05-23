# Tech Stack - Final Decisions

## Why These Choices?

Every choice below is optimized for: **1-2 month MVP timeline**, **4-5 person team**, **Bangla language support**, **competition demo quality**, and **real production scalability**.

---

## Frontend

```
Flutter (Dart)
├── State Management:    Riverpod (best for async/streaming)
├── Navigation:          GoRouter
├── HTTP Client:         Dio + Retrofit
├── Local DB:            Drift (SQLite wrapper, type-safe)
├── Maps:                flutter_map + OpenStreetMap tiles (FREE)
│                        OR Google Maps Flutter (paid but better)
├── Voice/STT:           flutter_speech_to_text (device STT, free)
│                        + Google STT API (fallback, accurate Bangla)
├── Background:          flutter_background_service
│                        + Workmanager (periodic tasks)
├── Location:            geolocator + background_locator_2
├── Push Notifications:  firebase_messaging (FCM)
├── Local Notifications: flutter_local_notifications
├── Audio:               just_audio (panic alarm sound)
├── Shake detect:        shake (for panic trigger)
├── PDF generation:      pdf (dart package) + printing
└── Secure Storage:      flutter_secure_storage
```

---

## Backend

```
Node.js + Express
├── Language:            TypeScript (strict mode)
├── ORM:                 Prisma (Supabase PostgreSQL)
├── Auth:                Supabase Auth (JWT + OAuth)
├── File Storage:        Supabase Storage (audio, images)
├── Realtime:            Supabase Realtime (risk zone updates)
├── Caching:             Redis (Upstash - free tier)
├── Queue:               BullMQ (emergency job queue)
├── Validation:          Zod
├── Logging:             Winston + Sentry
└── Testing:             Vitest + Supertest
```

---

## Database

```
Supabase (PostgreSQL)
├── Primary:             Cloud PostgreSQL (Supabase)
├── Local (on device):   Drift/SQLite (offline cache)
├── Sessions:            Supabase Auth
└── Files:               Supabase Storage Buckets
```

---

## AI / Intelligence

```
OpenRouter API (via backend proxy - NEVER call from app)
├── Primary Model:       google/gemini-1.5-pro (best Bangla, cheapest)
├── Reasoning Model:     anthropic/claude-3.5-sonnet (complex tasks)
├── Fallback:            google/gemini-flash-1.5 (fast, cheap)
├── Speech-to-Text:      Google Cloud STT (Bangla-BD locale)
├── News:                RSS feeds (no cost)
└── Maps Places:         Google Places API (for facility search)
```

---

## DevOps & Deployment

```
├── Backend hosting:     Railway.app (easy, free tier)
│                        OR Render.com
├── Database:            Supabase (free 500MB tier)
├── CI/CD:               GitHub Actions
├── App distribution:    Firebase App Distribution (beta)
├── Crash reporting:     Firebase Crashlytics
├── Analytics:           Firebase Analytics + Mixpanel
└── Secrets:             GitHub Secrets + Railway env vars
```

---

## Why Flutter over Kotlin Native?

1. **Single codebase** → Android + iOS simultaneously
2. **Faster development** → your team can ship in 1-2 months
3. **Dart is simpler** than Kotlin for rapid prototyping
4. **Same performance** for your use case (no 3D rendering)
5. **Strong package ecosystem** for all needed features

> ⚠️ **Important:** The hackathon proposal said Kotlin. Flutter is the right call for your team size and timeline. The core thesis is unchanged - only the implementation language changes.

## System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER DEVICE                               │
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │  Voice   │    │  Maps    │    │  Panic   │    │  News    │  │
│  │  Agent   │    │ & Places │    │  Button  │    │  Feed    │  │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘  │
│       │               │               │               │         │
│  ┌────▼───────────────▼───────────────▼───────────────▼──────┐ │
│  │              Flutter App Core (Riverpod State)              │ │
│  │         Drift SQLite Cache | FCM | Background Service       │ │
│  └────────────────────────┬───────────────────────────────────┘ │
│                           │ HTTPS                               │
└───────────────────────────┼─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                    NODE.JS BACKEND (Railway)                      │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │  /auth   │  │  /agent  │  │/emergency│  │  /locations  │   │
│  │  router  │  │  router  │  │  router  │  │    router    │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘   │
│       │              │              │               │            │
│  ┌────▼──────────────▼──────────────▼───────────────▼─────────┐ │
│  │                    Service Layer                             │ │
│  │  AuthService | AgentService | EmergencyService | GeoService  │ │
│  └────────────────────────┬────────────────────────────────────┘ │
│                           │                                      │
│  ┌────────────────────────▼────────────────────────────────────┐ │
│  │                  External API Calls                          │ │
│  │  OpenRouter API | Google STT | Google Places | News RSS     │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                       SUPABASE                                   │
│   PostgreSQL DB | Auth | Storage Buckets | Realtime Channels     │
└──────────────────────────────────────────────────────────────────┘
```

---

## Data Flow - Voice Report Submission

```
User speaks (Bangla)
        │
        ▼
[Flutter STT plugin] - device-native, zero latency
        │ raw text transcript
        ▼
[Backend /agent/process]
        │
        ├──▶ [Google STT API] - high-accuracy Bangla fallback
        │
        ▼
[OpenRouter - Gemini 1.5 Pro]
        │ structured JSON extraction
        ▼
{
  "category": "road_damage",
  "sub_category": "pothole",
  "location": "Mirpur 10, Dhaka",
  "severity": "high",
  "description": "বড় গর্ত রাস্তায়, দুর্ঘটনার আশঙ্কা",
  "emergency": false
}
        │
        ▼
[Flutter UI] - live form auto-fill animation
        │
        ▼
[User reviews + edits] - human-in-the-loop
        │
        ▼
[Confirm & Submit]
        │
        ├──▶ [Supabase DB] - store report
        ├──▶ [API/Webhook] - notify relevant authority
        └──▶ [User gets report ID]
```

---

## Security Architecture

```
App ─── HTTPS ──▶ Backend (JWT verify) ──▶ Supabase RLS
                         │
                         ├── OpenRouter key: SERVER SIDE ONLY
                         ├── Google APIs key: SERVER SIDE ONLY
                         └── Supabase service key: SERVER SIDE ONLY

Device stores:
  - JWT access token (flutter_secure_storage, AES encrypted)
  - Refresh token (secure storage)
  - Cached map tiles (read-only, public data)
  - User profile cache (encrypted)
```

> ⛔ Never put API keys in Flutter code. Always proxy through your Node.js backend.\n\n

## Bit-by-Bit Implementation: Why This Stack?

For a team of 4-5 developers building an MVP in 1-2 months, **velocity** and **type-safety** are the most critical metrics.

### Why Flutter?

- **Single Codebase**: Writing separate Android (Kotlin) and iOS (Swift) apps would double development time. Flutter compiles to native ARM code, ensuring high performance (60fps) for animations like the Voice Orb.
- **Rich UI**: Flutter's declarative UI makes building the "Live Agent Sandbox" extremely fast.

### Why Node.js + Express?

- **JavaScript Everywhere**: If your team knows JS/Dart, Node is much faster to iterate on than Python/Django or Go.
- **Async I/O**: Node is inherently non-blocking, which is perfect for proxying requests to OpenRouter and Google STT simultaneously.

### Why Supabase (PostgreSQL)?

- **Zero Backend Configuration**: Setting up a custom Postgres server, Auth system, and Row Level Security (RLS) takes weeks. Supabase gives you this out-of-the-box in 1 day.
- **Relational Integrity**: Civic reports need strict schemas (Users -> Reports -> Locations). NoSQL (like Firebase/Firestore) makes complex geographical querying (e.g., finding all reports within a 5km radius) very difficult and expensive.

## Alternative Approaches to Consider

1. **Firebase instead of Supabase?**
   - _Pros_: Firebase Auth and Crashlytics are industry standard.
   - _Cons_: Firestore geographical queries require complex workarounds (GeoHashes). Supabase uses PostGIS, which natively supports `ST_Distance` queries for mapping risk zones.
2. **Python (FastAPI) instead of Node.js?**
   - _Pros_: Python has better native AI/ML libraries if we want to run local NLP models.
   - _Cons_: Slower API routing overhead. Since we are using an API (OpenRouter) instead of hosting our own AI models, Node.js is faster for I/O proxying.
