# Offline Mode Implementation\n\n## Phase 1 Offline Strategy

For your 1-2 month MVP: **cached maps + risk zones + helplines**.
Full offline voice AI comes in a later phase (requires ~2GB on-device model).

---

## What Works Offline

| Feature | Offline Support | How |
|---|---|---|
| Map display | ✅ Yes | Cached OSM tiles (flutter_map_cache) |
| Risk zones | ✅ Yes | Cached in SQLite, updated on connect |
| Helpline directory | ✅ Yes | Bundled in app assets |
| Police/hospital list | ✅ Yes | Cached in SQLite |
| Past reports | ✅ Yes | SQLite |
| Panic button (SMS) | ✅ Yes | Works without internet |
| Voice AI agent | ❌ No | Requires OpenRouter API |
| News feed | ❌ No | Requires internet |
| Live places search | ❌ No | Requires Google Places API |

---

## Connectivity-Aware UI

```dart
// lib/core/utils/connectivity_checker.dart

@riverpod
Stream<bool> isOnline(IsOnlineRef ref) async* {
  final connectivity = Connectivity();

  yield* connectivity.onConnectivityChanged.map((result) =>
    result != ConnectivityResult.none
  );
}

// In any widget:
class ConnectivityBanner extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final online = ref.watch(isOnlineProvider).valueOrNull ?? true;

    if (online) return const SizedBox.shrink();

    return Container(
      width: double.infinity,
      color: Colors.orange,
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: const Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.wifi_off, color: Colors.white, size: 16),
          SizedBox(width: 8),
          Text(
            'অফলাইন মোড — সীমিত ফিচার উপলব্ধ',
            style: TextStyle(color: Colors.white, fontSize: 12),
          ),
        ],
      ),
    );
  }
}
```

---

## Offline Map Tiles

```dart
// lib/features/maps/services/tile_cache_service.dart

// flutter_map_cache handles this automatically.
// Pre-cache Dhaka area tiles on first launch:

Future<void> preCacheDhakaTiles() async {
  // Cache zoom levels 10-16 for Dhaka area
  // Approx bounding box: Dhaka metro area
  const bounds = LatLngBounds(
    LatLng(23.6850, 90.3350),  // SW
    LatLng(23.9050, 90.5050),  // NE
  );

  // Use flutter_map_cache to download tiles
  // Estimated size: ~50MB for zoom 10-16 Dhaka
  await TileCacheService.downloadArea(
    bounds: bounds,
    minZoom: 10,
    maxZoom: 16,
  );
}
```

---

## Offline Queue — Submit When Back Online

```dart
// When offline, store reports locally and sync when connected

class OfflineQueueService {
  final AppDatabase _db;
  final AgentService _agentService;

  Future<void> queueReport(CivicReport report) async {
    await _db.pendingReports.insertOne(
      PendingReport(
        id: const Uuid().v4(),
        reportJson: jsonEncode(report.toJson()),
        createdAt: DateTime.now(),
        synced: false,
      ),
    );
  }

  // Called when connectivity restored
  Future<void> syncPendingReports() async {
    final pending = await _db.pendingReports
      .filter((r) => r.synced.equals(false))
      .get();

    for (final item in pending) {
      try {
        final report = CivicReport.fromJson(
          jsonDecode(item.reportJson)
        );
        await _agentService.submitReport(report);
        await _db.pendingReports.filter(
          (r) => r.id.equals(item.id)
        ).delete();
      } catch (_) {
        // Will retry next time
      }
    }
  }
}
```\n\n