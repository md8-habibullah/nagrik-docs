# Bangladesh News & Alerts

## News Sources & Strategy

```
Free RSS feeds (no API cost):
├── Prothom Alo    → https://www.prothomalo.com/feed/
├── BD News 24     → https://bdnews24.com/feed
├── Dhaka Tribune  → https://www.dhakatribune.com/feed
└── Daily Star     → https://www.thedailystar.net/rss.xml

Fetch frequency: Every 15 minutes via Node.js cron job
Store in Supabase news_articles table
AI summarize in Bangla → serve to app
```

---

## News Aggregation Service

```typescript
// src/services/rss.service.ts

import Parser from 'rss-parser';
import cron from 'node-cron';

const parser = new Parser();

const RSS_FEEDS = [
  { name: 'prothom_alo', url: 'https://www.prothomalo.com/feed/', lang: 'bn' },
  { name: 'bdnews24', url: 'https://bdnews24.com/feed', lang: 'bn' },
  { name: 'daily_star', url: 'https://www.thedailystar.net/rss.xml', lang: 'en' },
];

// Emergency keywords - trigger push notifications
const EMERGENCY_KEYWORDS = [
  'আগুন', 'বন্যা', 'ভূমিকম্প', 'দুর্ঘটনা', 'বিস্ফোরণ',
  'সন্ত্রাস', 'সাইক্লোন', 'ঘূর্ণিঝড়', 'flood', 'fire',
  'earthquake', 'explosion', 'accident',
];

export class RssService {

  async fetchAllFeeds() {
    for (const feed of RSS_FEEDS) {
      try {
        const parsed = await parser.parseURL(feed.url);

        for (const item of parsed.items.slice(0, 20)) {
          const isAlert = EMERGENCY_KEYWORDS.some(kw =>
            item.title?.toLowerCase().includes(kw.toLowerCase())
          );

          // Upsert to avoid duplicates
          await prisma.newsArticle.upsert({
            where: { sourceUrl: item.link! },
            update: {},
            create: {
              title: item.title ?? '',
              sourceUrl: item.link!,
              source: feed.name,
              publishedAt: new Date(item.pubDate ?? Date.now()),
              isAlert,
            },
          });

          // Push notification for emergency news
          if (isAlert) {
            await sendBreakingNewsPush(item.title!);
          }
        }
      } catch (error) {
        console.error(\`RSS fetch failed for \${feed.name}:\`, error);
      }
    }
  }

  startCronJob() {
    // Every 15 minutes
    cron.schedule('*/15 * * * *', () => this.fetchAllFeeds());
  }
}

// News API endpoint
router.get('/', async (req, res) => {
  const { category, page = 1, limit = 20 } = req.query;

  const news = await prisma.newsArticle.findMany({
    where: category ? { category: category as string } : {},
    orderBy: { publishedAt: 'desc' },
    skip: (Number(page) - 1) * Number(limit),
    take: Number(limit),
  });

  res.json({ news, page: Number(page) });
});
```

---

## News Category Auto-tagging

```typescript
// AI auto-categorize each article when fetched

async function categorizeArticle(title: string): Promise<string> {
  // Use cheap Gemini Flash for this bulk operation
  const result = await openRouterService.categorize(title);
  return result; // crime | weather | politics | disaster | sports | economy | other
}
```

---

## Flutter News Feed

````dart
// lib/features/news/presentation/news_screen.dart

class NewsScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final news = ref.watch(newsProvider);

    return Column(
      children: [
        // Alert banner for breaking news
        ref.watch(breakingNewsProvider).when(
          data: (alert) => alert != null
            ? BreakingNewsBanner(article: alert)
            : const SizedBox.shrink(),
          loading: () => const SizedBox.shrink(),
          error: (_, __) => const SizedBox.shrink(),
        ),

        // Category filter
        NewsCategoryFilter(),

        // News list
        Expanded(
          child: news.when(
            data: (articles) => ListView.builder(
              itemCount: articles.length,
              itemBuilder: (ctx, i) => NewsCard(article: articles[i]),
            ),
            loading: () => const CircularProgressIndicator(),
            error: (e, _) => Text('Error: \$e'),
          ),
        ),
      ],
    );
  }
}
```\n\n
````
