# YouTube Downloader - Vue.js Frontend

This project has been converted from vanilla JavaScript to Vue.js 3 with the Options API, using Vite as the build tool.

## Project Structure

```
├── src/
│   ├── App.vue          # Main Vue component
│   ├── main.js          # Vue app entry point
│   └── style.css        # Global styles
├── dist/                # Built files (served by Flask)
├── package.json         # Node.js dependencies
├── vite.config.js       # Vite configuration
├── index.html           # HTML template for development
└── app.py              # Flask backend (updated to serve Vue build)
```

## Development Setup

### Prerequisites
- Node.js (v16 or higher)
- Python 3.7+
- Flask and other Python dependencies (see requirements.txt)

### Frontend Development

1. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```
   This starts the Vite dev server on http://localhost:3000 with hot reload.

3. **Start Flask backend (in another terminal):**
   ```bash
   python app.py
   ```
   This starts the Flask API server on http://localhost:5300.

The Vite dev server is configured to proxy API calls to the Flask backend.

### Production Build

1. **Build the Vue application:**
   ```bash
   npm run build
   ```

2. **Start Flask server:**
   ```bash
   python app.py
   ```
   Flask will serve the built Vue files from the `dist/` directory.

## Available Scripts

- `npm run dev` - Start Vite development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run build:prod` - Build and show instructions

## Vue.js Features Used

- **Options API**: Traditional Vue.js component structure
- **Reactive Data**: All state is reactive and updates the UI automatically
- **Computed Properties**: For derived state like URL validation
- **Watchers**: For automatic video info fetching on URL changes
- **Lifecycle Hooks**: For initialization and cleanup
- **Event Handling**: For form submission and user interactions
- **Conditional Rendering**: Using v-if, v-else-if, v-show
- **Two-way Data Binding**: Using v-model for form inputs

## Key Improvements

1. **Better State Management**: All state is centralized in Vue data
2. **Reactive UI**: No manual DOM manipulation needed
3. **Component Structure**: Clean separation of template, script, and styles
4. **Modern Build Process**: Vite provides fast builds and hot reload
5. **Type Safety**: Better development experience with Vue DevTools
6. **Maintainability**: Easier to extend and modify

## API Integration

The Vue app communicates with the Flask backend through the same API endpoints:
- `/get-video-info` - Get video information
- `/video-info/<id>` - Poll for video info status
- `/start-download` - Start video download
- `/progress/<id>` - Poll for download progress
- `/stream-download/<id>` - Download the video file
