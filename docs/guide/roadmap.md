# Full Project Roadmap\n\n## Team Task Allocation (4-5 people)

| Person | Role | Responsibilities |
|---|---|---|
| Dev 1 | Flutter Lead | Agent UI, voice pipeline, maps |
| Dev 2 | Flutter | Auth, forms, news, profile |
| Dev 3 | Backend Lead | Node.js API, OpenRouter integration |
| Dev 4 | Backend | Database, risk zones, emergency router |
| Dev 5 | Fullstack / DevOps | CI/CD, Firebase, testing, app store |

---

## Phase 1 - MVP (Weeks 1-8)

```
Week 1-2: Foundation
  ✅ Flutter project setup + navigation
  ✅ Supabase auth (email + phone OTP)
  ✅ User profile + emergency contacts
  ✅ Node.js backend skeleton
  ✅ OpenRouter integration + basic prompt

Week 3-4: Core Agent
  ✅ Voice input (flutter_speech_to_text)
  ✅ Agent state machine
  ✅ Live reasoning widget
  ✅ Form auto-fill with typewriter animation
  ✅ Civic report submission

Week 5-6: Safety Features
  ✅ Basic map with flutter_map
  ✅ Nearby places (Google Places)
  ✅ Panic button (shake + volume + manual)
  ✅ Emergency SMS sending
  ✅ BD helpline directory

Week 7-8: Polish + Launch
  ✅ Offline map tile caching
  ✅ News feed (RSS)
  ✅ Push notifications (FCM)
  ✅ Play Store beta launch
  ✅ Performance optimization
  ✅ Bug fixes from beta testers
```

---

## Phase 2 - Emergency Router (Months 3-4)

```
- Severity detection refinement
- Direct call routing automation
- Dhaka risk zone polygon data
- Background location service
- Night-time risk alerts
- Audio recording on panic
- Upstream to Supabase on panic
```

---

## Phase 3 - Intelligence Layer (Months 5-6)

```
- Bangladesh Law AI (RAG implementation)
- Government form PDF generation
  (GD, RTI, consumer complaint)
- AI news summarization in Bangla
- Smart helpline routing (AI-assisted)
- iOS App Store launch
- Analytics dashboard
```

---

## Phase 4 - Production Hardening (Months 7-9)

```
- Full offline voice (on-device model evaluation)
- Multi-division rollout (beyond Dhaka)
- Government API integrations (if available)
- Adapter middleware for non-API departments
- Multilingual: Chittagong/Sylhet dialect tuning
- Accessibility (screen reader support)
- Enterprise/NGO dashboard
- GDPR-compliant data deletion
```

---

## Git Branching Strategy

```
main        → production releases only
develop     → integration branch
feature/*   → individual features (PR to develop)
hotfix/*    → urgent fixes (PR to main + develop)

Example branches:
  feature/voice-agent-ui
  feature/panic-button
  feature/bd-law-ai
  feature/play-store-assets
```

---

## Definition of Done (DoD)

For every feature before merging:
```
✅ Works on Android 9+ physical device
✅ No red errors in Flutter DevTools
✅ Error states handled (network failure, empty state)
✅ Bangla text renders correctly (no boxes/question marks)
✅ Permissions handled gracefully (denial case)
✅ Works on slow 3G connection
✅ Dark mode compatible (if UI supports)
✅ PR reviewed by at least 1 other team member
```

---

## Key Technical Risks & Mitigations

| Risk | Probability | Mitigation |
|---|---|---|
| Google STT Bangla accuracy poor | Medium | Two-step pipeline + LLM normalization |
| OpenRouter cost overrun | Low | Per-user quota + caching |
| Android background kill | High | Battery optimization request + Workmanager |
| Play Store rejection | Medium | Policy compliance checklist |
| Govt API unavailability | High | Adapter/email fallback built-in |
| iOS background location rejection | Medium | Detailed justification text |\n\n