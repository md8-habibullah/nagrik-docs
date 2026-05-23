# Deployment, CI/CD & DevOps\n\n## Infrastructure Overview

```
GitHub (code) 
    │
    ▼ push to main
GitHub Actions CI/CD
    │
    ├──▶ Run tests
    ├──▶ Build Docker image
    ├──▶ Deploy to Railway (backend)
    └──▶ Notify team (Slack/Discord)

Supabase (database)
    └── Managed PostgreSQL, no server to maintain

Flutter app
    ├──▶ firebase app distribution (beta)
    └──▶ Play Store / App Store (production)
```

---

## Backend Deployment - Railway

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Set environment variables
railway variables set OPENROUTER_API_KEY=sk-or-...
railway variables set SUPABASE_URL=https://...
railway variables set SUPABASE_SERVICE_KEY=eyJ...
railway variables set GOOGLE_PLACES_API_KEY=AIza...
railway variables set GOOGLE_STT_API_KEY=AIza...
railway variables set NODE_ENV=production

# 5. Deploy
railway up

# Your backend is now live at:
# https://nagrik-ai-backend.railway.app
```

---

## Dockerfile

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY dist/ ./dist/
COPY prisma/ ./prisma/

RUN npx prisma generate

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

---

## GitHub Actions - Backend CI/CD

```yaml
# .github/workflows/deploy-backend.yml

name: Deploy Backend

on:
  push:
    branches: [main]
    paths: ['backend/**']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
        working-directory: backend
      - run: npm test
        working-directory: backend
      - run: npm run build
        working-directory: backend

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: railway/action@v1
        with:
          service: nagrik-ai-backend
        env:
          RAILWAY_TOKEN: \${{ secrets.RAILWAY_TOKEN }}
```

---

## GitHub Actions - Flutter Beta Build

```yaml
# .github/workflows/flutter-beta.yml

name: Flutter Beta Build

on:
  push:
    branches: [develop]

jobs:
  android-beta:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with: { flutter-version: '3.22.0' }

      - name: Setup Android signing
        run: |
          echo "\${{ secrets.KEYSTORE_BASE64 }}" | base64 -d > android/nagrik-ai.keystore
          echo "storePassword=\${{ secrets.KEY_STORE_PASSWORD }}" > android/key.properties
          echo "keyPassword=\${{ secrets.KEY_PASSWORD }}" >> android/key.properties
          echo "keyAlias=nagrik-ai" >> android/key.properties
          echo "storeFile=../nagrik-ai.keystore" >> android/key.properties

      - run: flutter pub get
      - run: flutter build apk --release

      - name: Distribute to Firebase App Distribution
        uses: wzieba/Firebase-Distribution-Github-Action@v1
        with:
          appId: \${{ secrets.FIREBASE_APP_ID }}
          serviceCredentialsFileContent: \${{ secrets.FIREBASE_SERVICE_ACCOUNT }}
          groups: testers
          file: build/app/outputs/flutter-apk/app-release.apk
          releaseNotes: "Build from commit \${{ github.sha }}"
```

---

## Supabase Database Migration

```bash
# Run migrations
npx prisma migrate deploy

# Seed initial data (police stations, hospitals, risk zones)
npx prisma db seed

# Generate Prisma client
npx prisma generate
```

---

## Monitoring & Alerts

```
Firebase Crashlytics → crash reports → email alert
Firebase Analytics  → user behavior
Sentry (backend)    → backend errors → Slack alert
Railway Metrics     → CPU/memory/response time
Upstash Redis       → cache hit rate
Supabase Dashboard  → DB queries, storage
```\n\n