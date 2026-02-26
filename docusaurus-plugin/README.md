# Docusaurus RAG Chatbot Plugin

A Docusaurus plugin that embeds an AI-powered documentation chatbot into your documentation site.

## Features

- **Context-aware Q&A**: Users can select text and ask questions about it
- **Citation support**: Responses include citations to relevant documentation
- **Streaming responses**: Real-time response streaming using SSE
- **Theme-aware**: Adapts to light/dark mode automatically
- **Configurable**: Control position, behavior, and excluded pages

## Installation

```bash
npm install docusaurus-plugin-rag-chatbot
```

Or with yarn:

```bash
yarn add docusaurus-plugin-rag-chatbot
```

## Configuration

Add the plugin to your `docusaurus.config.js`:

```javascript
module.exports = {
  // ... other config
  plugins: [
    [
      'docusaurus-plugin-rag-chatbot',
      {
        // Required: Your chatbot API URL
        apiUrl: 'https://your-api.example.com/api/v1',

        // Optional: Widget position (default: 'bottom-right')
        position: 'bottom-right', // or 'bottom-left'

        // Optional: Open widget by default (default: false)
        defaultOpen: false,

        // Optional: Exclude certain pages (regex patterns)
        excludePages: [
          '^/blog', // Exclude blog pages
          '^/community', // Exclude community pages
        ],
      },
    ],
  ],
};
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `apiUrl` | `string` | `'http://localhost:8000/api/v1'` | URL of the chatbot backend API |
| `position` | `'bottom-right' \| 'bottom-left'` | `'bottom-right'` | Position of the floating widget button |
| `defaultOpen` | `boolean` | `false` | Whether to open the chat panel by default |
| `excludePages` | `string[]` | `[]` | Array of regex patterns for pages to exclude |

## Usage

Once installed and configured, the chat widget will automatically appear on your documentation pages.

### User Workflow

1. **Select text**: Highlight any text on the documentation page
2. **Open chat**: Click the floating chat button in the corner
3. **Ask question**: Type your question about the selected text
4. **Get answer**: Receive an AI-generated response with citations

### Keyboard Shortcuts

- **Enter**: Send message
- **Shift + Enter**: New line in input
- **Escape**: Close chat panel

## Styling

The widget uses CSS custom properties for theming. You can override these in your custom CSS:

```css
:root {
  --rag-primary: #2563eb;
  --rag-bg: #ffffff;
  --rag-text: #1e293b;
  /* ... more variables */
}
```

## Backend Setup

This plugin requires a compatible backend API. See the main project documentation for setting up the FastAPI backend with:

- Neon Postgres for conversation storage
- Qdrant Cloud for vector similarity search
- OpenAI for embeddings and chat completions

## API Requirements

The backend must expose these endpoints:

- `POST /chat` - Send message, receive complete response
- `POST /chat/stream` - Send message, receive streaming response (SSE)
- `POST /messages/{id}/feedback` - Submit feedback for a message
- `GET /health` - Health check endpoint

## Troubleshooting

### Widget not appearing

1. Check browser console for errors
2. Verify the API URL is correct and accessible
3. Ensure the page isn't in the `excludePages` list

### CORS errors

Make sure your backend allows requests from your documentation domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-docs.example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Styling issues

If styles conflict with your theme, increase specificity or use Shadow DOM isolation (enabled by default).

## License

MIT
