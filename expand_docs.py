import os

def append_to_file(filepath, content):
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(content)

def expand_architecture():
    content = """
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
   - *Pros*: Firebase Auth and Crashlytics are industry standard.
   - *Cons*: Firestore geographical queries require complex workarounds (GeoHashes). Supabase uses PostGIS, which natively supports `ST_Distance` queries for mapping risk zones.
2. **Python (FastAPI) instead of Node.js?**
   - *Pros*: Python has better native AI/ML libraries if we want to run local NLP models.
   - *Cons*: Slower API routing overhead. Since we are using an API (OpenRouter) instead of hosting our own AI models, Node.js is faster for I/O proxying.
"""
    append_to_file('docs/guide/architecture.md', content)

def expand_flutter():
    content = """
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
"""
    append_to_file('docs/guide/flutter-frontend.md', content)

def expand_ai():
    content = """
## Bit-by-Bit Implementation: AI Proxying

Never put your API keys (OpenRouter, Google Maps, etc.) inside the Flutter app. If someone decompiles your APK, they will steal the keys and drain your budget.

### Step-by-Step Logic
1. **Flutter App**: Records voice, converts to text (using device STT), and sends a JSON payload `{ "transcript": "aami mohammadpur e accident dekhechi" }` to your Node.js backend.
2. **Node Backend (`/api/agent`)**: Receives the transcript. It holds the `OPENROUTER_API_KEY` securely in `.env`.
3. **System Prompting**: The Node backend wraps the transcript in a massive "System Prompt" (defining the JSON schema we want).
4. **OpenRouter**: Forwards the prompt to Gemini 1.5 Pro.
5. **Streaming**: As Gemini generates the JSON, Node.js streams it back to Flutter so the user sees the "Reasoning..." happening live.

## Alternative Approaches to Consider
1. **Direct API calls from Flutter?**
   - *Pros*: Faster to implement initially (no backend needed).
   - *Cons*: MASSIVE security risk. You will definitely lose your API keys.
2. **Local On-Device AI Models?**
   - *Pros*: Works 100% offline, costs $0 in API fees.
   - *Cons*: Running a 3B parameter model on a low-end Android phone in Bangladesh will drain the battery instantly and make the phone overheat. Not viable for Phase 1.
"""
    append_to_file('docs/guide/ai-core.md', content)

def expand_safety():
    content = """
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
"""
    append_to_file('docs/guide/safety-features.md', content)

def expand_offline():
    content = """
## Bit-by-Bit Implementation: Offline Capabilities

For users without internet, we must ensure basic functionality works.

### Step-by-Step Logic
1. **Map Tiles**: Use `flutter_map_cache`. When the user is on WiFi, the app downloads OpenStreetMap tiles for Dhaka (zoom levels 10-15). These are stored as `.png` files in the app's local directory.
2. **Local Database**: Use `sqlite3` (via the Drift package in Flutter). Store the polygons (coordinates) of known "Red Zones".
3. **Location Polling**: When offline, the app still gets GPS pings. It queries the local SQLite DB: `SELECT * FROM risk_zones WHERE ST_Contains(geom, user_location)`. If true, trigger a local notification.

## Alternative Approaches to Consider
1. **Google Maps SDK instead of flutter_map?**
   - *Pros*: Google Maps has higher quality POI data.
   - *Cons*: Google Maps SDK does not allow you to cache map tiles for true offline use without internet, and it costs money. `flutter_map` (OpenStreetMap) is 100% free and allows aggressive offline caching.
"""
    append_to_file('docs/guide/offline.md', content)

def main():
    expand_architecture()
    expand_flutter()
    expand_ai()
    expand_safety()
    expand_offline()
    print("Documentation expanded successfully!")

if __name__ == '__main__':
    main()
