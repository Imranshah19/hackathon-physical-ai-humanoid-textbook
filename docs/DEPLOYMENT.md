# Deployment Guide

This guide covers deploying the Physical AI & Humanoid Robotics Textbook platform:

1. **Docusaurus Book** → GitHub Pages (static site)
2. **FastAPI Backend** → Cloud provider (Railway, Render, or Fly.io)
3. **Auth Service** → Cloud provider (co-located with backend)
4. **Chatbot Widget** → Embedded in Docusaurus

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        GitHub Pages                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Docusaurus Static Site                      │    │
│  │  • Book content (MDX)                                    │    │
│  │  • Embedded chatbot widget                               │    │
│  │  • Auth wrapper components                               │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS API calls
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Cloud Platform                                │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │   Auth Service   │    │  FastAPI Backend │                   │
│  │   (Hono/Node.js) │    │  (Python 3.11+)  │                   │
│  │   Port 3001      │    │  Port 8000       │                   │
│  └────────┬─────────┘    └────────┬─────────┘                   │
│           │                       │                              │
│           ▼                       ▼                              │
│  ┌──────────────────────────────────────────┐                   │
│  │            Neon Postgres                  │                   │
│  │  • User sessions (better-auth)           │                   │
│  │  • User profiles                          │                   │
│  │  • Conversations                          │                   │
│  └──────────────────────────────────────────┘                   │
│                       │                                          │
│                       ▼                                          │
│  ┌──────────────────────────────────────────┐                   │
│  │            Qdrant Cloud                   │                   │
│  │  • Document embeddings                    │                   │
│  │  • Vector similarity search               │                   │
│  └──────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Part 1: Docusaurus → GitHub Pages

### 1.1 Create Docusaurus Site

First, create a Docusaurus site for the book content:

```bash
# From project root
npx create-docusaurus@latest website classic --typescript

cd website
```

### 1.2 Configure Docusaurus

Update `website/docusaurus.config.ts`:

```typescript
import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'A Comprehensive Textbook for Building Intelligent Robots',
  favicon: 'img/favicon.ico',

  // GitHub Pages URL
  url: 'https://YOUR_GITHUB_USERNAME.github.io',
  baseUrl: '/hackathon-physical-ai-humanoid-textbook/',

  // GitHub Pages deployment config
  organizationName: 'YOUR_GITHUB_USERNAME',
  projectName: 'hackathon-physical-ai-humanoid-textbook',
  trailingSlash: false,
  deploymentBranch: 'gh-pages',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  // Add the RAG chatbot plugin
  plugins: [
    [
      '../docusaurus-plugin',  // Local plugin path
      {
        apiUrl: process.env.VITE_API_URL || 'https://your-api.railway.app/api/v1',
        position: 'bottom-right',
        defaultOpen: false,
        excludePages: ['^/blog'],
      },
    ],
  ],

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          path: '../book',  // Point to book content
          routeBasePath: '/',  // Serve docs at root
          editUrl: 'https://github.com/YOUR_USERNAME/hackathon-physical-ai-humanoid-textbook/tree/master/',
        },
        blog: false,  // Disable blog
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'Physical AI & Humanoid Robotics',
      logo: {
        alt: 'Textbook Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Modules',
        },
        {
          href: 'https://github.com/YOUR_USERNAME/hackathon-physical-ai-humanoid-textbook',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI Textbook. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'cpp', 'bash', 'yaml'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
```

### 1.3 GitHub Actions Workflow

Create `.github/workflows/deploy-docs.yml`:

```yaml
name: Deploy Docusaurus to GitHub Pages

on:
  push:
    branches:
      - master
    paths:
      - 'book/**'
      - 'website/**'
      - 'frontend/**'
      - 'docusaurus-plugin/**'
      - '.github/workflows/deploy-docs.yml'
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: |
            website/package-lock.json
            frontend/package-lock.json
            docusaurus-plugin/package-lock.json

      - name: Install frontend dependencies
        working-directory: frontend
        run: npm ci

      - name: Build frontend widget
        working-directory: frontend
        run: npm run build
        env:
          VITE_API_URL: ${{ vars.API_URL }}
          VITE_AUTH_URL: ${{ vars.AUTH_URL }}

      - name: Install plugin dependencies
        working-directory: docusaurus-plugin
        run: npm ci

      - name: Build plugin
        working-directory: docusaurus-plugin
        run: npm run build

      - name: Install website dependencies
        working-directory: website
        run: npm ci

      - name: Build Docusaurus
        working-directory: website
        run: npm run build
        env:
          VITE_API_URL: ${{ vars.API_URL }}
          VITE_AUTH_URL: ${{ vars.AUTH_URL }}

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: website/build

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### 1.4 Enable GitHub Pages

1. Go to repository **Settings** → **Pages**
2. Under "Build and deployment":
   - Source: **GitHub Actions**
3. Add repository variables (**Settings** → **Secrets and variables** → **Actions** → **Variables**):
   - `API_URL`: `https://your-backend.railway.app/api/v1`
   - `AUTH_URL`: `https://your-auth.railway.app`

### 1.5 Local Development

```bash
# Install all dependencies
cd frontend && npm install && cd ..
cd docusaurus-plugin && npm install && npm run build && cd ..
cd website && npm install

# Start development server
cd website
npm run start
```

---

## Part 2: FastAPI Backend → Cloud

### Option A: Railway (Recommended)

Railway offers simple deployment with PostgreSQL add-on support.

#### 2A.1 Create `railway.json`

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "backend/Dockerfile"
  },
  "deploy": {
    "numReplicas": 1,
    "sleepApplication": false,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 2A.2 Create `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/src ./src
COPY backend/alembic ./alembic
COPY backend/alembic.ini .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"

# Run with Uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2A.3 Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway init

# Link to existing project (if already created in dashboard)
railway link

# Add environment variables
railway variables set DATABASE_URL="postgresql+asyncpg://..."
railway variables set QDRANT_URL="https://your-cluster.qdrant.io"
railway variables set QDRANT_API_KEY="your-key"
railway variables set OPENAI_API_KEY="sk-..."
railway variables set ENVIRONMENT="production"
railway variables set CORS_ORIGINS='["https://YOUR_USERNAME.github.io"]'

# Deploy
railway up
```

#### 2A.4 Run Migrations

```bash
# Connect to Railway shell
railway run alembic upgrade head
```

### Option B: Render

#### 2B.1 Create `render.yaml`

```yaml
services:
  - type: web
    name: textbook-api
    runtime: docker
    dockerfilePath: ./backend/Dockerfile
    dockerContext: .
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: QDRANT_URL
        sync: false
      - key: QDRANT_API_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: ENVIRONMENT
        value: production
      - key: CORS_ORIGINS
        value: '["https://YOUR_USERNAME.github.io"]'
    healthCheckPath: /api/v1/health
    autoDeploy: true

  - type: web
    name: textbook-auth
    runtime: docker
    dockerfilePath: ./auth-service/Dockerfile
    dockerContext: .
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: BETTER_AUTH_SECRET
        generateValue: true
      - key: GOOGLE_CLIENT_ID
        sync: false
      - key: GOOGLE_CLIENT_SECRET
        sync: false
      - key: GITHUB_CLIENT_ID
        sync: false
      - key: GITHUB_CLIENT_SECRET
        sync: false
```

#### 2B.2 Deploy via Dashboard

1. Go to [render.com](https://render.com)
2. Connect GitHub repository
3. Select "Blueprint" deployment
4. Configure environment variables
5. Deploy

### Option C: Fly.io

#### 2C.1 Create `fly.toml`

```toml
app = "textbook-api"
primary_region = "sjc"

[build]
  dockerfile = "backend/Dockerfile"

[env]
  ENVIRONMENT = "production"
  API_PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1
  processes = ["app"]

[[http_service.checks]]
  grace_period = "10s"
  interval = "30s"
  method = "GET"
  timeout = "5s"
  path = "/api/v1/health"

[[vm]]
  memory = "512mb"
  cpu_kind = "shared"
  cpus = 1
```

#### 2C.2 Deploy to Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Create app
fly apps create textbook-api

# Set secrets
fly secrets set DATABASE_URL="postgresql+asyncpg://..."
fly secrets set QDRANT_URL="https://your-cluster.qdrant.io"
fly secrets set QDRANT_API_KEY="your-key"
fly secrets set OPENAI_API_KEY="sk-..."
fly secrets set CORS_ORIGINS='["https://YOUR_USERNAME.github.io"]'

# Deploy
fly deploy
```

---

## Part 3: Auth Service Deployment

### 3.1 Create `auth-service/Dockerfile`

```dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY auth-service/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY auth-service/src ./src
COPY auth-service/tsconfig.json ./

# Build TypeScript
RUN npm run build

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 -G nodejs && \
    chown -R nodejs:nodejs /app

USER nodejs

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3001/api/auth/health || exit 1

# Start server
CMD ["node", "dist/index.js"]
```

### 3.2 Environment Variables for Auth Service

```bash
# Required for auth service
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
BETTER_AUTH_SECRET=your-secure-random-secret-min-32-chars
BETTER_AUTH_URL=https://your-auth.railway.app

# OAuth providers (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# CORS
CORS_ORIGINS=https://YOUR_USERNAME.github.io,https://your-api.railway.app
```

### 3.3 Deploy Auth Service

Deploy alongside the backend using the same cloud provider. Both services can share the same Neon Postgres database.

---

## Part 4: Chatbot Embedding in Book

### 4.1 Plugin Integration

The chatbot is embedded via `docusaurus-plugin-rag-chatbot`. The plugin:

1. Injects the chat widget into every page
2. Captures text selections for context
3. Communicates with the FastAPI backend

### 4.2 Configure API URL

In `website/docusaurus.config.ts`:

```typescript
plugins: [
  [
    '../docusaurus-plugin',
    {
      // Production API URL
      apiUrl: 'https://your-backend.railway.app/api/v1',
      position: 'bottom-right',
      defaultOpen: false,
      excludePages: ['^/blog', '^/404'],
    },
  ],
],
```

### 4.3 Theme Integration

The widget wrapper in `docusaurus-plugin/src/theme/ChatWidgetWrapper.tsx` automatically:

- Adapts to Docusaurus light/dark theme
- Positions the floating button
- Handles page exclusions

### 4.4 Auth Wrapper (Optional)

For personalized content, wrap pages with auth:

```typescript
// In a custom Docusaurus theme component
import { AuthWrapper } from '../packages/docusaurus-plugin-rag-chatbot/src/theme/AuthWrapper';

export default function Root({ children }) {
  return (
    <AuthWrapper loginUrl="/login">
      {children}
    </AuthWrapper>
  );
}
```

---

## Part 5: Database Setup

### 5.1 Neon Postgres

1. Create account at [neon.tech](https://neon.tech)
2. Create new project
3. Copy connection string:
   ```
   postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. For async Python, use `asyncpg`:
   ```
   postgresql+asyncpg://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

### 5.2 Qdrant Cloud

1. Create account at [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create new cluster
3. Copy cluster URL and API key
4. Create collection:
   ```bash
   curl -X PUT "https://your-cluster.qdrant.io/collections/documentation" \
     -H "api-key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{
       "vectors": {
         "size": 1536,
         "distance": "Cosine"
       }
     }'
   ```

### 5.3 Run Migrations

```bash
# Backend database migrations
cd backend
alembic upgrade head

# Auth service migrations (better-auth)
cd auth-service
npx @better-auth/cli migrate
```

---

## Part 6: Environment Configuration

### 6.1 Production Environment Variables

Create a checklist of required variables:

| Service | Variable | Description |
|---------|----------|-------------|
| Backend | `DATABASE_URL` | Neon Postgres async connection |
| Backend | `QDRANT_URL` | Qdrant Cloud cluster URL |
| Backend | `QDRANT_API_KEY` | Qdrant Cloud API key |
| Backend | `OPENAI_API_KEY` | OpenAI API key |
| Backend | `CORS_ORIGINS` | JSON array of allowed origins |
| Backend | `ENVIRONMENT` | `production` |
| Auth | `DATABASE_URL` | Neon Postgres connection |
| Auth | `BETTER_AUTH_SECRET` | Random 32+ char secret |
| Auth | `BETTER_AUTH_URL` | Public URL of auth service |
| Auth | `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| Auth | `GOOGLE_CLIENT_SECRET` | Google OAuth secret |
| Auth | `GITHUB_CLIENT_ID` | GitHub OAuth client ID |
| Auth | `GITHUB_CLIENT_SECRET` | GitHub OAuth secret |
| Frontend | `VITE_API_URL` | Backend API URL |
| Frontend | `VITE_AUTH_URL` | Auth service URL |

### 6.2 GitHub Repository Variables

In **Settings** → **Secrets and variables** → **Actions** → **Variables**:

```
API_URL = https://your-backend.railway.app/api/v1
AUTH_URL = https://your-auth.railway.app
```

---

## Part 7: Post-Deployment Checklist

### 7.1 Verify Deployments

```bash
# Check backend health
curl https://your-backend.railway.app/api/v1/health

# Check auth service
curl https://your-auth.railway.app/api/auth/health

# Check GitHub Pages
curl https://YOUR_USERNAME.github.io/hackathon-physical-ai-humanoid-textbook/
```

### 7.2 Test Chatbot

1. Open the deployed Docusaurus site
2. Click the chat widget button
3. Select some text on a documentation page
4. Ask a question about the selected text
5. Verify response includes citations

### 7.3 Test Authentication

1. Click "Sign Up" or navigate to `/register`
2. Complete registration with email
3. Complete profile wizard
4. Verify personalized content appears

### 7.4 Monitor Logs

```bash
# Railway logs
railway logs

# Fly.io logs
fly logs

# Render logs (via dashboard)
```

---

## Troubleshooting

### CORS Errors

Ensure `CORS_ORIGINS` includes your GitHub Pages URL:

```python
# backend/src/api/middleware/cors.py
CORS_ORIGINS = ["https://YOUR_USERNAME.github.io"]
```

### Widget Not Appearing

1. Check browser console for JavaScript errors
2. Verify `apiUrl` in Docusaurus plugin config
3. Ensure backend is accessible from browser

### Database Connection Issues

1. Verify connection string format (asyncpg for Python async)
2. Check SSL mode is enabled (`?sslmode=require`)
3. Verify IP allowlist in Neon dashboard

### OAuth Redirect Errors

1. Update OAuth provider redirect URIs:
   - Google: `https://your-auth.railway.app/api/auth/callback/google`
   - GitHub: `https://your-auth.railway.app/api/auth/callback/github`
2. Verify `BETTER_AUTH_URL` matches public URL

---

## Cost Estimates

| Service | Free Tier | Paid Tier |
|---------|-----------|-----------|
| GitHub Pages | Unlimited | N/A |
| Railway | $5/month credit | ~$10-20/month |
| Render | 750 hours free | ~$7/month per service |
| Fly.io | 3 shared VMs | ~$5-15/month |
| Neon Postgres | 0.5GB free | $19/month (10GB) |
| Qdrant Cloud | 1GB free | $25/month (4GB) |
| OpenAI | Pay per use | ~$10-50/month |

**Estimated total**: $0-50/month depending on usage

---

## Security Checklist

- [ ] All secrets stored in environment variables (never in code)
- [ ] HTTPS enforced on all services
- [ ] CORS restricted to known origins
- [ ] Rate limiting enabled on API endpoints
- [ ] CSP headers configured
- [ ] OAuth secrets rotated periodically
- [ ] Database connections use SSL
- [ ] No sensitive data in client-side code
