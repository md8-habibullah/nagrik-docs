# Cost Estimation & Budget\n\n## Monthly Cost Breakdown

### Hackathon / Development Phase (0 users)

| Service | Plan | Cost |
|---|---|---|
| Railway (backend) | Hobby | $5/month |
| Supabase | Free | $0 |
| OpenRouter | Pay per use | ~$5-10 |
| Google Places API | Free tier | $0 (< $200 credit) |
| Google STT | Free tier | $0 (< 60 min/month) |
| Firebase | Free Spark | $0 |
| Upstash Redis | Free | $0 |
| **Total** | | **~$10-15/month** |

---

### Growth Phase (1,000 active users)

| Service | Usage | Cost |
|---|---|---|
| Railway (backend) | Pro plan | $20/month |
| Supabase | Pro | $25/month |
| OpenRouter (Gemini 1.5 Pro) | ~50K queries × $0.003 | ~$150/month |
| Google Places API | 10K requests | ~$32/month |
| Google STT API | 500 hours | ~$180/month |
| Firebase (FCM) | Free | $0 |
| **Total** | | **~$407/month** |

---

### Scale Phase (10,000 active users)

| Service | Cost |
|---|---|
| Railway / Render (2x instances) | $80/month |
| Supabase Pro | $25/month |
| OpenRouter | ~$800/month |
| Google APIs | ~$500/month |
| CDN (Cloudflare) | Free |
| **Total** | **~$1,400/month** |

---

## Cost Optimization Strategies

```
1. Cache AI responses (Redis)
   - Identical transcripts → return cached result
   - Saves ~30-40% OpenRouter cost

2. Use Gemini Flash for simple tasks
   - Flash costs 20x less than Pro
   - Use Flash for: news categorization, simple Q&A
   - Use Pro only for: civic extraction, law Q&A

3. Batch STT processing
   - Group audio uploads → process in batch
   - Saves API call overhead

4. Rate limit per user
   - Free: 50 AI queries/month
   - Premium: unlimited
   - Prevents single user from draining budget

5. Cache map tiles
   - OpenStreetMap is FREE
   - Cache on device → zero map tile cost

6. Free STT first
   - Use flutter_speech_to_text (device) by default
   - Only fallback to Google STT if accuracy < threshold
   - Saves ~60% STT cost
```

---

## Revenue Model (Future)

```
Phase 1 (now): Free, grant-funded / competition
Phase 2: Freemium
  - Free: 50 reports/month, basic features
  - Premium: ৳199/month = unlimited + priority support
Phase 3: B2B
  - Government department dashboards
  - NGO/INGO civic monitoring tools
Phase 4: API
  - Sell NagrikAI API to other civic apps
```\n\n