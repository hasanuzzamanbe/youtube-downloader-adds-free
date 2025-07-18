# YouTube Video Downloader

A modern, web-based YouTube video downloader with real-time progress tracking, built with Vue.js 3 and Flask.

## Features

- 🎥 Download YouTube videos in best quality
- 📊 Real-time progress bar with download speed and ETA
- 🎨 Modern, responsive UI built with Vue.js
- ⚡ Fast and efficient downloads
- 🔄 Automatic progress tracking
- 🛡️ Error handling and user feedback
- 🔧 Modern development setup with Vite

## Installation

### Prerequisites
- Python 3.7+
- Node.js 16+

### Setup

1. **Clone or download this repository**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

4. **Build the frontend:**
   ```bash
   npm run build
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Open your browser and go to:**
   ```
   http://localhost:5300
   ```

## Development

For development with hot reload:

1. **Start the Flask backend:**
   ```bash
   python app.py
   ```

2. **Start the Vue.js development server (in another terminal):**
   ```bash
   npm run dev
   ```

3. **Open your browser and go to:**
   ```
   http://localhost:3000
   ```

## Usage

1. Enter a YouTube URL in the input field
2. Click "Download Video"
3. Watch the real-time progress bar
4. The video will be downloaded to your browser's default download location

## Technology Stack

- **Backend**: Python 3.7+, Flask, yt-dlp
- **Frontend**: Vue.js 3 (Options API), Vite
- **Build Tool**: Vite for fast development and optimized builds

## Notes

- Videos are downloaded directly to the browser's default download location
- Progress data is automatically cleaned up after 5 minutes
- The application runs on port 5300 by default

## Troubleshooting

If you encounter issues:

1. Make sure you have the latest version of yt-dlp
2. Check that the YouTube URL is valid
3. Ensure you have sufficient disk space
4. Check your internet connection

## License

This project is for personal use only. Please respect YouTube's terms of service and copyright laws.