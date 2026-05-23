# Node.js Backend - Full API\n\n## Project Structure

```
nagrik-ai-backend/
├── src/
│   ├── index.ts               # Entry point
│   ├── app.ts                 # Express app setup
│   ├── config/
│   │   ├── env.ts             # Zod env validation
│   │   ├── supabase.ts
│   │   └── redis.ts
│   ├── middleware/
│   │   ├── auth.middleware.ts  # JWT verification
│   │   ├── rate-limit.ts
│   │   └── error-handler.ts
│   ├── routes/
│   │   ├── agent.ts           # AI agent endpoints
│   │   ├── auth.ts            # Auth endpoints
│   │   ├── reports.ts         # Civic reports
│   │   ├── places.ts          # Nearby places
│   │   ├── emergency.ts       # Emergency routing
│   │   ├── news.ts            # News aggregation
│   │   ├── risk-zones.ts      # Risk zone data
│   │   └── law.ts             # BD law AI
│   ├── services/
│   │   ├── openrouter.service.ts
│   │   ├── google-stt.service.ts
│   │   ├── places.service.ts
│   │   └── rss.service.ts
│   └── lib/
│       └── prisma.ts
├── prisma/
│   └── schema.prisma
├── .env.example
├── package.json
└── tsconfig.json
```

---

## Environment Variables (.env)

```bash
# Server
PORT=3000
NODE_ENV=production

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...

# OpenRouter
OPENROUTER_API_KEY=sk-or-...

# Google APIs
GOOGLE_STT_API_KEY=AIza...
GOOGLE_PLACES_API_KEY=AIza...

# Redis (Upstash)
REDIS_URL=redis://...
REDIS_TOKEN=...

# JWT
JWT_SECRET=your-secret-key-here
```

---

## Express App Setup

```typescript
// src/app.ts

import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import { authMiddleware } from './middleware/auth.middleware';

const app = express();

app.use(helmet());
app.use(cors({ origin: '*' })); // restrict in production
app.use(express.json({ limit: '10mb' }));

// Rate limiting
app.use('/api/', rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: 'Too many requests, please try again.',
}));

// Public routes
app.use('/api/auth', authRouter);

// Protected routes (require JWT)
app.use('/api/agent', authMiddleware, agentRouter);
app.use('/api/reports', authMiddleware, reportsRouter);
app.use('/api/places', authMiddleware, placesRouter);
app.use('/api/emergency', authMiddleware, emergencyRouter);
app.use('/api/news', newsRouter);           // Public
app.use('/api/risk-zones', riskZonesRouter); // Public
app.use('/api/law', authMiddleware, lawRouter);

export default app;
```

---

## Auth Middleware

```typescript
// src/middleware/auth.middleware.ts

import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_KEY!
);

export const authMiddleware = async (req, res, next) => {
  const token = req.headers.authorization?.replace('Bearer ', '');

  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  const { data: { user }, error } = await supabase.auth.getUser(token);

  if (error || !user) {
    return res.status(401).json({ error: 'Invalid token' });
  }

  req.user = user;
  next();
};
```

---

## Reports API

```typescript
// src/routes/reports.ts

router.post('/', async (req, res) => {
  const { category, sub_category, location, severity,
          description, lat, lng, is_emergency } = req.body;

  const report = await prisma.civicReport.create({
    data: {
      userId: req.user.id,
      category,
      subCategory: sub_category,
      location,
      severity,
      description,
      lat,
      lng,
      isEmergency: is_emergency,
      status: 'submitted',
    },
  });

  // If critical - trigger emergency flow
  if (is_emergency) {
    await emergencyQueue.add('route', { reportId: report.id });
  }

  res.status(201).json({ report, id: report.id });
});

router.get('/my', async (req, res) => {
  const reports = await prisma.civicReport.findMany({
    where: { userId: req.user.id },
    orderBy: { createdAt: 'desc' },
    take: 20,
  });
  res.json({ reports });
});
```\n\n