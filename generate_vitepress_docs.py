import os
import re
import json

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def create_config():
    ensure_dir('docs/.vitepress')
    config_content = """import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "NagrikAI Docs",
  description: "AI-Driven Voice Civic Agent for Bangladesh",
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
"""
    with open('docs/.vitepress/config.js', 'w', encoding='utf-8') as f:
        f.write(config_content)

def create_index():
    index_content = """---
layout: home

hero:
  name: "NagrikAI"
  text: "AI-Driven Voice Civic Agent"
  tagline: "Empowering citizens with zero-UI voice input, transparent reasoning & autonomous action."
  actions:
    - theme: brand
      text: Read the Guide
      link: /guide/overview
    - theme: alt
      text: View Project Roadmap
      link: /guide/roadmap

features:
  - title: Voice-First Native App
    details: Users can report civic issues and get assistance through natural Bangla voice commands, with real-time AI reasoning displayed on screen.
  - title: Emergency Routing
    details: Smart detection of critical situations automatically routes users to 999, 333, 109, and alerts emergency contacts with precise GPS locations.
  - title: BD Law Assistant
    details: Advanced Retrieval-Augmented Generation (RAG) system providing clear answers about Bangladesh law, citing specific legal sections.
  - title: Offline-Ready
    details: Core safety features including cached maps, risk zones, and panic button triggers work flawlessly without an internet connection.
---
"""
    with open('docs/index.md', 'w', encoding='utf-8') as f:
        f.write(index_content)

def extract_sections():
    # Read prompt.txt
    with open('../prompt.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to extract the SECTIONS object
    sections_match = re.search(r'const SECTIONS = \{(.*?)\};\n\nexport default function', content, re.DOTALL)
    
    if not sections_match:
        print("Could not find SECTIONS in prompt.txt")
        return {}

    sections_text = sections_match.group(1)
    
    # We will just use regex to parse out each section
    pattern = r'(\w+):\s*\{\s*title:\s*"(.*?)",\s*badge:\s*"(.*?)",\s*content:\s*`(.*?)`,\s*\}'
    matches = re.finditer(pattern, sections_text, re.DOTALL)
    
    sections = {}
    for match in matches:
        key = match.group(1)
        title = match.group(2)
        badge = match.group(3)
        content = match.group(4)
        sections[key] = {
            'title': title,
            'badge': badge,
            'content': content.strip()
        }
    
    # Since the string contains backticks or other nested things, a simpler regex might be needed.
    # Let's try an alternative regex that captures everything until the next key.
    # Wait, the prompt.txt uses format like `content: \`\n## What is NagrikAI?... \`,\n  },`
    
    alt_pattern = r'(\w+|"[^"]+"):\s*\{\s*title:\s*"(.*?)",\s*badge:\s*"(.*?)",\s*content:\s*`([\s\S]*?)`,\n\s*\}'
    matches = re.finditer(alt_pattern, sections_text)
    sections = {}
    for match in matches:
        key = match.group(1).strip('"')
        title = match.group(2)
        badge = match.group(3)
        content = match.group(4).strip()
        sections[key] = {'title': title, 'content': content}
        
    return sections

def main():
    ensure_dir('docs/guide')
    create_config()
    create_index()
    
    sections = extract_sections()
    print(f"Extracted {len(sections)} sections.")
    
    # Map section keys to filenames
    file_map = {
        'overview': 'overview.md',
        'techstack': 'architecture.md',
        'architecture': 'architecture.md', # will merge
        'flutter': 'flutter-frontend.md',
        'agent-ui': 'agent-ui.md',
        'voice': 'voice.md',
        'maps': 'maps.md',
        'panic': 'safety-features.md', # will merge
        'offline': 'offline.md',
        'backend': 'backend-api.md',
        'database': 'database.md',
        'auth': 'auth.md',
        'ai': 'ai-core.md',
        'bangla': 'bangla-nlp.md',
        'law': 'bd-law.md',
        'forms': 'forms.md',
        'news': 'news.md',
        'location': 'safety-features.md', # will merge
        'emergency': 'safety-features.md', # will merge
        'playstore': 'playstore.md',
        'appstore': 'appstore.md',
        'deployment': 'deployment.md',
        'cost': 'cost.md',
        'roadmap': 'roadmap.md'
    }
    
    files_content = {}
    for key, data in sections.items():
        if key in file_map:
            filename = file_map[key]
            if filename not in files_content:
                files_content[filename] = f"# {data['title']}\\n\\n{data['content']}\\n\\n"
            else:
                files_content[filename] += f"## {data['title']}\\n\\n{data['content']}\\n\\n"
        else:
            # Create a file for any unmapped key
            files_content[f"{key}.md"] = f"# {data['title']}\\n\\n{data['content']}\\n\\n"
            
    for filename, content in files_content.items():
        with open(f"docs/guide/{filename}", 'w', encoding='utf-8') as f:
            f.write(content)
            
    print("All markdown files generated successfully in docs/guide/")

if __name__ == '__main__':
    main()
