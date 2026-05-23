# NagrikAI Documentation

Welcome to the official documentation repository for **NagrikAI** — the AI-Driven Voice Civic Agent for Bangladesh.

This repository contains the complete, bit-by-bit technical implementation plans, architecture diagrams, and guidelines for the 4-5 person development team.

## 🌐 View the Live Documentation

The documentation is built using [VitePress](https://vitepress.dev/) and is automatically deployed via GitHub Actions.

You can view the live site here (once GitHub Pages finishes its first build):
**[https://md8-habibullah.github.io/nagrik-docs/](https://md8-habibullah.github.io/nagrik-docs/)**

*(Note: Ensure that GitHub Pages is enabled in your repository Settings -> Pages, with the source set to "GitHub Actions".)*

## 🛠 Local Development

To run this documentation website on your local machine:

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Start the Development Server**
   ```bash
   npm run docs:dev
   ```

3. Open your browser and navigate to `http://localhost:5173`.

## 📂 Project Structure

- `docs/` - Contains all the Markdown files for the documentation.
  - `docs/.vitepress/config.mjs` - The sidebar and navigation configuration.
  - `docs/guide/` - The bit-by-bit implementation plans (Architecture, Flutter, Backend, AI, etc.)
- `.github/workflows/deploy.yml` - The CI/CD script that publishes this documentation to GitHub Pages for free.
- `prompt.txt` & `NagrikAI.pdf` - The original reference documents.
