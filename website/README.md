# Physical AI & Humanoid Robotics Textbook - Website

This directory contains the Docusaurus website for the textbook.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Serve production build locally
npm run serve
```

## Structure

```
website/
├── docusaurus.config.ts   # Main configuration
├── sidebars.ts            # Sidebar navigation
├── package.json           # Dependencies
├── tsconfig.json          # TypeScript config
├── babel.config.js        # Babel config
├── src/
│   ├── css/
│   │   └── custom.css     # Custom styles
│   └── pages/
│       ├── index.tsx      # Homepage
│       └── index.module.css
├── static/
│   └── img/               # Static images
└── build/                 # Production build (generated)
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000/api/v1` |
| `VITE_AUTH_URL` | Auth service URL | `http://localhost:3001` |
| `GITHUB_REPOSITORY_OWNER` | GitHub username for deployment | `your-username` |

### Book Content

The book content is located in `../book/` and organized by modules:

- `book/module-1/` - ROS2 Foundations
- `book/module-2/` - Simulation & Digital Twins
- `book/module-3/` - Isaac & Reinforcement Learning
- `book/module-4/` - Vision-Language-Action

### RAG Chatbot Plugin

The chatbot is embedded via `../docusaurus-plugin/`. Configure it in `docusaurus.config.ts`:

```typescript
plugins: [
  [
    '../docusaurus-plugin',
    {
      apiUrl: 'https://your-api.example.com/api/v1',
      position: 'bottom-right',
      defaultOpen: false,
      excludePages: ['^/blog'],
    },
  ],
],
```

## Deployment

### GitHub Pages

Push to `master` branch to trigger automatic deployment via GitHub Actions.

See `../.github/workflows/deploy-docs.yml` for the workflow configuration.

### Manual Deployment

```bash
# Build the site
npm run build

# Deploy to GitHub Pages
npm run deploy
```

## Development

### Adding a New Chapter

1. Create the markdown file in `../book/module-X/chapters/`
2. Add the chapter to `sidebars.ts`
3. Update any cross-references

### Customizing Styles

Edit `src/css/custom.css` to customize:

- Color scheme (CSS variables)
- Typography
- Code block styling
- Component layouts

### Adding Pages

Create React components in `src/pages/`:

```tsx
// src/pages/my-page.tsx
import Layout from '@theme/Layout';

export default function MyPage() {
  return (
    <Layout title="My Page">
      <main>
        <h1>My Custom Page</h1>
      </main>
    </Layout>
  );
}
```

## Troubleshooting

### Build Errors

```bash
# Clear cache and rebuild
npm run clear
npm run build
```

### Plugin Not Loading

Ensure the plugin is built:

```bash
cd ../docusaurus-plugin
npm install
npm run build
```

### Missing Styles

If chatbot styles are missing, check the CSS import in `custom.css`:

```css
@import '../../../frontend/src/styles/widget.css';
```
