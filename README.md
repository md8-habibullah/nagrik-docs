# NagrikAI — Comprehensive Documentation

<div align="center">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" alt="Status Active" />
  <img src="https://img.shields.io/badge/Platform-Android%20%7C%20iOS-blue" alt="Platform" />
  <img src="https://img.shields.io/badge/Backend-Node.js%20%7C%20Supabase-orange" alt="Backend" />
</div>

Welcome to the official repository for **NagrikAI**! This repository holds the comprehensive documentation, architecture, and step-by-step implementation plans for building the NagrikAI platform. 

This guide is specifically designed for a **4-5 person development team** to successfully build the MVP phase in 1-2 months.

---

## Live Documentation Website

The most important part of this repository is our beautifully formatted Documentation Website. Instead of reading raw text files, you can view the entire project plan mapped out cleanly.

**View the Live Documentation here:** 
[https://md8-habibullah.github.io/nagrik-docs/](https://md8-habibullah.github.io/nagrik-docs/)

*Note: This site automatically updates every time code is pushed to the `main` branch.*

---

## What's Included in the Guide?

The VitePress documentation covers every single "bit-by-bit" technical requirement of the app:

1. **Architecture & Tech Stack:** Flutter, Node.js, Express, Supabase.
2. **AI & OpenRouter:** How we route requests to Gemini 1.5 Pro and Claude 3.5 Sonnet.
3. **Agent Sandbox UI:** The exact state machine (Listening -> Transcribing -> Reasoning -> Extracting).
4. **Safety & Emergency:** The background panic button, shaking detection, and offline caching strategies.
5. **BD Law RAG:** How the AI understands and references Bangladesh legal code.
6. **Deployment Checklists:** Exact guidelines for publishing to the Google Play Store and Apple App Store.

---

## Local Setup & Contribution Guidelines

If you want to edit or add new pages to the documentation, follow these steps:

### 1. Clone the Repository
```bash
git clone https://github.com/md8-habibullah/nagrik-docs.git
cd nagrik-docs
```

### 2. Install Dependencies
Make sure you have [Node.js](https://nodejs.org/) installed, then run:
```bash
npm install
```

### 3. Start the Development Server
```bash
npm run docs:dev
```
*Open your browser and navigate to `http://localhost:5173` to view the live-reloading site.*

### 4. Adding Content
- All documentation files are located in the `docs/guide/` directory.
- Simply edit the `.md` files or create new ones.
- If you create a new file, make sure to add it to the sidebar navigation inside `docs/.vitepress/config.mjs`.

### 5. Publishing
You don't need to do anything complex to publish! Simply commit and push your changes to GitHub:
```bash
git add .
git commit -m "Updated documentation"
git push
```
GitHub Actions will automatically catch your push, build the VitePress site, and update the live URL for free.

---

## The Development Team

When building the core NagrikAI app, follow the division of labor outlined in the **Roadmap** section of the docs:
- **Dev 1 (Flutter Lead):** Agent UI, Voice Pipeline, Maps
- **Dev 2 (Flutter):** Auth, Forms, News, Profile
- **Dev 3 (Backend Lead):** Node.js API, OpenRouter integration
- **Dev 4 (Backend):** Database, Risk zones, Emergency Router
- **Dev 5 (DevOps):** CI/CD, App Store Deployment
