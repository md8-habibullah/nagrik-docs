# Database Schema (Supabase / Prisma)\n\n## Prisma Schema

```prisma
// prisma/schema.prisma

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider  = "postgresql"
  url       = env("DATABASE_URL")
  directUrl = env("DIRECT_URL")
}

// ─── Users & Auth ───────────────────────────────────────────

model User {
  id            String   @id @default(uuid())
  email         String   @unique
  phone         String?
  nameEn        String?
  nameBn        String?
  nidArea       String?  // NID region code
  address       String?
  divisionCode  String?
  districtCode  String?
  thanaCode     String?
  avatarUrl     String?
  isVerified    Boolean  @default(false)
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt

  reports           CivicReport[]
  emergencyContacts EmergencyContact[]
  deviceTokens      DeviceToken[]
  locationHistory   LocationSnapshot[]

  @@map("users")
}

model EmergencyContact {
  id      String @id @default(uuid())
  userId  String
  name    String
  phone   String
  relation String  // পরিবার | বন্ধু | সহকর্মী

  user User @relation(fields: [userId], references: [id])

  @@map("emergency_contacts")
}

model DeviceToken {
  id        String   @id @default(uuid())
  userId    String
  token     String   @unique  // FCM token
  platform  String   // android | ios
  updatedAt DateTime @updatedAt

  user User @relation(fields: [userId], references: [id])

  @@map("device_tokens")
}

// ─── Civic Reports ───────────────────────────────────────────

model CivicReport {
  id          String   @id @default(uuid())
  userId      String
  category    String   // road_damage | drainage | electricity ...
  subCategory String
  location    String   // Human-readable location
  lat         Float?
  lng         Float?
  severity    String   // low | medium | high | critical
  description String
  isEmergency Boolean  @default(false)
  status      String   @default("submitted")
                       // submitted | in_progress | resolved | closed
  ticketId    String?  // External ticket ID if govt API available
  audioUrl    String?  // Recorded voice (Supabase Storage)
  photoUrls   String[] // Report photos
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  user User @relation(fields: [userId], references: [id])

  @@index([userId])
  @@index([lat, lng])
  @@index([status])
  @@map("civic_reports")
}

// ─── Location & Risk ─────────────────────────────────────────

model LocationSnapshot {
  id        String   @id @default(uuid())
  userId    String
  lat       Float
  lng       Float
  accuracy  Float?
  capturedAt DateTime @default(now())

  user User @relation(fields: [userId], references: [id])

  @@index([userId, capturedAt])
  @@map("location_snapshots")
}

model RiskZone {
  id          String   @id @default(uuid())
  name        String
  nameBn      String
  description String?
  level       String   // low | medium | high | critical
  type        String   // flood | crime | accident | fire | construction
  boundary    Json     // GeoJSON polygon coordinates
  division    String?
  district    String?
  thana       String?
  activeFrom  DateTime?
  activeTo    DateTime?
  isActive    Boolean  @default(true)
  createdAt   DateTime @default(now())

  @@map("risk_zones")
}

// ─── Emergency Events ─────────────────────────────────────────

model EmergencyEvent {
  id          String   @id @default(uuid())
  userId      String
  trigger     String   // shake | volume | voice | manual
  lat         Float
  lng         Float
  audioUrl    String?
  contactsNotified Int @default(0)
  policeAlerted    Boolean @default(false)
  resolvedAt  DateTime?
  createdAt   DateTime @default(now())

  @@map("emergency_events")
}

// ─── BD Static Data ───────────────────────────────────────────

model PoliceStation {
  id         String  @id
  nameBn     String
  nameEn     String
  phone      String
  division   String
  district   String
  thana      String
  lat        Float
  lng        Float
  address    String

  @@map("police_stations")
}

model Hospital {
  id         String  @id
  nameBn     String
  nameEn     String
  phone      String
  type       String  // govt | private | clinic
  division   String
  district   String
  thana      String
  lat        Float
  lng        Float
  address    String
  beds       Int?
  emergency  Boolean @default(false)

  @@map("hospitals")
}

// ─── News ─────────────────────────────────────────────────────

model NewsArticle {
  id          String   @id @default(uuid())
  title       String
  titleBn     String?
  summary     String?
  sourceUrl   String   @unique
  source      String   // prothom_alo | bdnews24 | dhaka_tribune
  category    String?  // crime | politics | weather | disaster
  publishedAt DateTime
  fetchedAt   DateTime @default(now())
  isAlert     Boolean  @default(false)  // breaking/emergency news

  @@index([publishedAt])
  @@index([isAlert])
  @@map("news_articles")
}
```

---

## Supabase Row Level Security (RLS)

```sql
-- Users can only read/edit their own data
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users read own profile"
  ON users FOR SELECT
  USING (auth.uid()::text = id);

CREATE POLICY "Users update own profile"
  ON users FOR UPDATE
  USING (auth.uid()::text = id);

-- Reports: users see only their own
ALTER TABLE civic_reports ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users manage own reports"
  ON civic_reports FOR ALL
  USING (auth.uid()::text = user_id);

-- Risk zones: public read
ALTER TABLE risk_zones ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public risk zones read"
  ON risk_zones FOR SELECT
  TO anon, authenticated
  USING (is_active = true);

-- Police stations: public read
ALTER TABLE police_stations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public police read"
  ON police_stations FOR SELECT TO anon, authenticated
  USING (true);
```\n\n