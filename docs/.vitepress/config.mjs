import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "NagrikAI Docs",
  description: "AI-Driven Voice Civic Agent for Bangladesh",
  base: '/nagrik-docs/',
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Guide', link: '/guide/architecture' }
    ],
    sidebar: [
      {
        text: 'Introduction',
        items: [
          { text: 'Overview', link: '/guide/overview' },
          { text: 'Architecture & Tech Stack', link: '/guide/architecture' }
        ]
      },
      {
        text: 'Frontend (Flutter)',
        items: [
          { text: 'Flutter Implementation', link: '/guide/flutter-frontend' },
          { text: 'Agent Visual UI', link: '/guide/agent-ui' },
          { text: 'Voice Pipeline', link: '/guide/voice' },
          { text: 'Maps & Places', link: '/guide/maps' },
          { text: 'Safety & Panic', link: '/guide/safety-features' },
          { text: 'Offline Mode', link: '/guide/offline' }
        ]
      },
      {
        text: 'Backend (Node.js)',
        items: [
          { text: 'Backend API', link: '/guide/backend-api' },
          { text: 'Database Schema', link: '/guide/database' },
          { text: 'Auth & Profiles', link: '/guide/auth' }
        ]
      },
      {
        text: 'AI & Intelligence',
        items: [
          { text: 'AI Agent Core', link: '/guide/ai-core' },
          { text: 'Bangla NLP', link: '/guide/bangla-nlp' },
          { text: 'BD Law AI', link: '/guide/bd-law' },
          { text: 'Form Auto-fill', link: '/guide/forms' },
          { text: 'News & Alerts', link: '/guide/news' }
        ]
      },
      {
        text: 'Deployment & Publishing',
        items: [
          { text: 'Deployment & DevOps', link: '/guide/deployment' },
          { text: 'Play Store Guide', link: '/guide/playstore' },
          { text: 'App Store Guide', link: '/guide/appstore' },
          { text: 'Cost Estimation', link: '/guide/cost' },
          { text: 'Roadmap', link: '/guide/roadmap' }
        ]
      }
    ],
    socialLinks: [
      { icon: 'github', link: 'https://github.com/nagrik-ai' }
    ]
  }
})
