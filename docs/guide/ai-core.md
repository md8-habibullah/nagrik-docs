# AI Agent Core - OpenRouter Integration\n\n## OpenRouter Model Strategy

| Task | Model | Why | Cost/1M tokens |
|---|---|---|---|
| Voice report extraction | gemini-1.5-pro | Best Bangla, fast | $3.50/$10.50 |
| BD Law Q&A | claude-3.5-sonnet | Deep reasoning | $3/$15 |
| News summarization | gemini-flash-1.5 | Cheap, fast | $0.075/$0.30 |
| Emergency detection | gemini-flash-1.5 | Real-time speed | $0.075/$0.30 |
| Form field mapping | gemini-1.5-pro | Structured output | $3.50/$10.50 |

---

## OpenRouter Service

```typescript
// src/services/openrouter.service.ts

import OpenAI from 'openai';

const client = new OpenAI({
  baseURL: 'https://openrouter.ai/api/v1',
  apiKey: process.env.OPENROUTER_API_KEY!,
  defaultHeaders: {
    'HTTP-Referer': 'https://nagrik.ai',
    'X-Title': 'NagrikAI',
  },
});

export type ModelChoice =
  | 'google/gemini-1.5-pro'
  | 'google/gemini-flash-1.5'
  | 'anthropic/claude-3.5-sonnet';

export class OpenRouterService {

  async extractCivicReport(
    transcript: string,
    userContext: { lat?: number; lng?: number; userId: string }
  ): Promise<CivicReportData> {

    const completion = await client.chat.completions.create({
      model: 'google/gemini-1.5-pro',
      messages: [
        { role: 'system', content: CIVIC_EXTRACTION_PROMPT },
        { role: 'user', content: buildUserMessage(transcript, userContext) },
      ],
      temperature: 0.1,
      max_tokens: 600,
      response_format: { type: 'json_object' },
    });

    return JSON.parse(completion.choices[0].message.content!);
  }

  async answerLawQuestion(
    question: string,
    conversationHistory: Message[]
  ): Promise<string> {

    const completion = await client.chat.completions.create({
      model: 'anthropic/claude-3.5-sonnet',
      messages: [
        { role: 'system', content: BD_LAW_SYSTEM_PROMPT },
        ...conversationHistory,
        { role: 'user', content: question },
      ],
      temperature: 0.3,
      max_tokens: 1000,
      stream: true,  // Stream for UI responsiveness
    });

    // Handle streaming
    let fullResponse = '';
    for await (const chunk of completion) {
      const delta = chunk.choices[0]?.delta?.content ?? '';
      fullResponse += delta;
    }
    return fullResponse;
  }

  async summarizeNews(articles: RawArticle[]): Promise<SummarizedArticle[]> {
    const summaryPrompt = articles
      .map((a, i) => \`Article \${i+1}: \${a.title}\\n\${a.content}\`)
      .join('\\n---\\n');

    const completion = await client.chat.completions.create({
      model: 'google/gemini-flash-1.5',
      messages: [
        { role: 'system', content: NEWS_SUMMARY_PROMPT },
        { role: 'user', content: summaryPrompt },
      ],
      max_tokens: 2000,
      response_format: { type: 'json_object' },
    });

    return JSON.parse(completion.choices[0].message.content!).articles;
  }
}
```

---

## Core Prompts

```typescript
// src/prompts/civic_extraction.ts

export const CIVIC_EXTRACTION_PROMPT = \`
You are NagrikAI, a civic assistant AI for Bangladesh.
Your job: extract structured data from Bangla voice transcripts.

## Dialect normalization
পানি = হানী = water/পানি সমস্যা
ড্রেন = নালা = drainage
রাস্তা = পথ = road
ডাক্তারখানা = হাসপাতাল = hospital
থানা = পুলিশ স্টেশন = police station

## Category taxonomy
- road_damage: pothole, broken road, speed bump, bridge damage
- drainage: clogged drain, waterlogging, sewage overflow
- electricity: power outage, dangerous wire, transformer issue
- water: supply problem, dirty water, pipeline break
- crime: theft, harassment, fight, vandalism
- fire: fire emergency, gas leak
- medical: injury, illness, ambulance needed
- flood: flooding, river overflow
- noise: construction, vehicle noise
- waste: garbage pile, waste burning
- other: anything else

## Emergency rules (STRICT)
- Fire/gas leak → is_emergency: true, suggested_helpline: "999"
- Crime in progress → is_emergency: true, suggested_helpline: "999"
- Medical crisis → is_emergency: true, suggested_helpline: "999"
- Flood/disaster → is_emergency: true, suggested_helpline: "333"
- General civic issue → is_emergency: false

## Output (JSON ONLY, no markdown)
{
  "category": "string",
  "sub_category": "string",
  "location": "extracted location or 'GPS location'",
  "severity": "low|medium|high|critical",
  "description": "brief Bangla description max 100 chars",
  "is_emergency": boolean,
  "suggested_helpline": "999|333|109|16000|null",
  "lat": number or null,
  "lng": number or null,
  "confidence": 0.0-1.0
}
\`;
```

---

## Cost Control Strategy

```typescript
// Cache identical or very similar transcripts
// Use Redis with 1-hour TTL

async function processWithCache(transcript: string, context: any) {
  const cacheKey = \`agent:\${hashTranscript(transcript)}\`;
  const cached = await redis.get(cacheKey);

  if (cached) return JSON.parse(cached);

  const result = await openRouterService.extractCivicReport(transcript, context);
  await redis.setex(cacheKey, 3600, JSON.stringify(result));
  return result;
}

// Token budgeting: track per-user monthly usage
// Free tier: 100 AI queries/month
// Premium: unlimited
```\n\n
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
