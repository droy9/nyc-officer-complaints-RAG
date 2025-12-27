# Decarceration Lab — Frontend

A minimalist document study and reference tool powered by LLM/RAG.

## Features

- **Document Upload**: Drag-and-drop support for PDF, TXT, DOCX files
- **Chat Interface**: Clean query input with real-time responses
- **Chat History**: Track and revisit previous conversations
- **Document Management**: View uploaded documents and their processing status
- **Visual States**: Idle, loading (with spinning logo), complete, and error states
- **Responsive Design**: Works on desktop and mobile devices

## Design

- **Typography**: Newsreader (serif) for headings, DM Mono for UI elements
- **Color Palette**: Deep charcoal background with warm terracotta accents
- **Aesthetic**: Legal/academic inspired, clean and institutional

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Opens at [http://localhost:3000](http://localhost:3000)

### Production Build

```bash
npm run build
npm run preview
```

## API Integration

The frontend expects a backend API at `/api/query`. Configure the proxy in `vite.config.js`:

```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true
  }
}
```

### Expected API Endpoints

#### POST /api/query

Request:
```json
{
  "query": "What are the main findings?",
  "documents": ["doc-id-1", "doc-id-2"]
}
```

Response:
```json
{
  "response": "Based on the documents..."
}
```

#### POST /api/upload

Upload documents for processing.

## Project Structure

```
frontend/
├── public/
│   └── logo.svg
├── src/
│   ├── components/
│   │   ├── ChatInterface.jsx
│   │   ├── DocumentUpload.jsx
│   │   ├── Logo.jsx
│   │   └── Sidebar.jsx
│   ├── App.jsx
│   ├── index.css
│   └── main.jsx
├── index.html
├── package.json
└── vite.config.js
```

## Customization

### Colors

Edit CSS variables in `src/index.css`:

```css
:root {
  --accent: #c96442;        /* Primary accent */
  --background: #0d0f0e;    /* Page background */
  --surface: #161a18;       /* Card/sidebar background */
}
```

### Typography

Fonts are loaded from Google Fonts in `index.html`. Modify the link tags and CSS variables to use different fonts.

