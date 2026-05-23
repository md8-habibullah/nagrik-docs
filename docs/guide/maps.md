# Maps, Places & Navigation

## Maps Strategy

**Primary:** \`flutter_map\` + OpenStreetMap tiles (FREE, no quota)
**Facilities search:** Google Places API (via backend proxy)
**Offline tiles:** Cached using \`flutter_map_cache\` package

---

## Flutter Map Setup

```dart
// lib/features/maps/presentation/map_screen.dart

import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

class MapScreen extends ConsumerStatefulWidget {
  const MapScreen({super.key});

  @override
  ConsumerState<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends ConsumerState<MapScreen> {
  final MapController _mapController = MapController();
  List<Marker> _markers = [];

  @override
  Widget build(BuildContext context) {
    final userLocation = ref.watch(userLocationProvider);
    final nearbyPlaces = ref.watch(nearbyPlacesProvider);
    final riskZones = ref.watch(riskZonesProvider);

    return Scaffold(
      body: Stack(
        children: [
          FlutterMap(
            mapController: _mapController,
            options: MapOptions(
              initialCenter: userLocation ?? const LatLng(23.8103, 90.4125),
              initialZoom: 14,
              onTap: (_, point) => _onMapTap(point),
            ),
            children: [
              // Base map tiles (OpenStreetMap - FREE)
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'com.nagrik.ai',
                tileProvider: CachedTileProvider(), // offline support
              ),

              // Risk zones overlay
              PolygonLayer(
                polygons: riskZones.map((zone) => Polygon(
                  points: zone.boundary,
                  color: zone.level == 'high'
                    ? Colors.red.withOpacity(0.3)
                    : Colors.orange.withOpacity(0.2),
                  borderColor: zone.level == 'high'
                    ? Colors.red
                    : Colors.orange,
                  borderStrokeWidth: 2,
                )).toList(),
              ),

              // User location
              if (userLocation != null)
                MarkerLayer(markers: [
                  Marker(
                    point: userLocation,
                    child: const Icon(
                      Icons.my_location,
                      color: Colors.blue,
                      size: 30,
                    ),
                  ),
                ]),

              // Nearby places markers
              MarkerLayer(
                markers: nearbyPlaces.map((place) => Marker(
                  point: LatLng(place.lat, place.lng),
                  child: GestureDetector(
                    onTap: () => _showPlaceDetails(place),
                    child: _buildPlaceMarker(place.type),
                  ),
                )).toList(),
              ),
            ],
          ),

          // Category filter chips at top
          Positioned(
            top: 48, left: 16, right: 16,
            child: _buildCategoryFilter(),
          ),

          // Direction card at bottom
          Positioned(
            bottom: 16, left: 16, right: 16,
            child: _buildNearbyList(),
          ),
        ],
      ),
    );
  }

  Widget _buildPlaceMarker(String type) {
    final (icon, color) = switch (type) {
      'police' => (Icons.local_police, Colors.blue),
      'hospital' => (Icons.local_hospital, Colors.red),
      'ambulance' => (Icons.emergency, Colors.orange),
      'school' => (Icons.school, Colors.green),
      'pharmacy' => (Icons.medical_services, Colors.teal),
      'tourist' => (Icons.camera_alt, Colors.purple),
      _ => (Icons.place, Colors.grey),
    };

    return Container(
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: color,
        shape: BoxShape.circle,
        border: Border.all(color: Colors.white, width: 2),
      ),
      child: Icon(icon, color: Colors.white, size: 16),
    );
  }
}
```

---

## Nearby Places - Backend Service

```typescript
// src/routes/places.ts

router.get('/nearby', async (req, res) => {
  const { lat, lng, type, radius = 2000 } = req.query;

  // Google Places API call
  const response = await fetch(
    \`https://maps.googleapis.com/maps/api/place/nearbysearch/json?\` +
    new URLSearchParams({
      location: \`\${lat},\${lng}\`,
      radius: radius.toString(),
      type: mapPlaceType(type as string),
      key: process.env.GOOGLE_PLACES_API_KEY!,
      language: 'bn',  // Bengali results
    })
  );

  const data = await response.json();

  // Transform for app
  const places = data.results.map((p: any) => ({
    id: p.place_id,
    name: p.name,
    lat: p.geometry.location.lat,
    lng: p.geometry.location.lng,
    type: type,
    rating: p.rating,
    distance: calculateDistance(
      Number(lat), Number(lng),
      p.geometry.location.lat, p.geometry.location.lng
    ),
    address: p.vicinity,
    openNow: p.opening_hours?.open_now,
    phone: p.formatted_phone_number,
  }));

  // Sort by distance
  places.sort((a: any, b: any) => a.distance - b.distance);

  res.json({ places });
});

function mapPlaceType(type: string): string {
  const map: Record<string, string> = {
    police: 'police',
    hospital: 'hospital',
    pharmacy: 'pharmacy',
    school: 'school',
    tourist: 'tourist_attraction',
    fire: 'fire_station',
    bank: 'bank',
    mosque: 'mosque',
  };
  return map[type] ?? 'point_of_interest';
}
```

---

## Bangladesh Police Stations - Static Database

````typescript
// src/data/bd_police_stations.ts
// Static JSON seeded at startup - no external API cost

export const DHAKA_POLICE_STATIONS = [
  {
    id: 'dhanmondi-ps',
    name: 'ধানমন্ডি থানা',
    name_en: 'Dhanmondi Police Station',
    phone: '02-9671234',
    division: 'Dhaka',
    district: 'Dhaka',
    thana: 'Dhanmondi',
    lat: 23.7461,
    lng: 90.3742,
    address: 'Road 8A, Dhanmondi, Dhaka-1209',
    oc_name: 'Contact OC',
  },
  {
    id: 'mirpur-ps',
    name: 'মিরপুর থানা',
    name_en: 'Mirpur Police Station',
    phone: '02-9001234',
    division: 'Dhaka',
    district: 'Dhaka',
    thana: 'Mirpur',
    lat: 23.8103,
    lng: 90.3551,
    address: 'Mirpur-10, Dhaka-1216',
    oc_name: 'Contact OC',
  },
  // ... all 64 Dhaka police stations
  // Source: Bangladesh Police official directory
];

export const BD_HELPLINES = {
  emergency: '999',           // National emergency
  info: '333',                // Government info line
  health: '16000',            // Health emergency
  women_abuse: '109',         // Women & children helpline
  anti_corruption: '16700',   // Anti-corruption
  consumer: '16123',          // Consumer rights
  fire: '02-9555555',         // Fire service
  coast_guard: '02-9557001',  // Coast guard
  rapid_action: '01769-691100', // RAB
};
```\n\n
````
