# YouTube Video Downloader

A modern, web-based YouTube video downloader with real-time progress tracking.

## Features

- 🎥 Download YouTube videos in best quality
- 📊 Real-time progress bar with download speed and ETA
- 🎨 Modern, responsive UI
- ⚡ Fast and efficient downloads
- 🔄 Automatic progress tracking
- 🛡️ Error handling and user feedback

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open your browser and go to:**
   ```
   http://localhost:5300
   ```

## Usage

1. Enter a YouTube URL in the input field
2. Click "Download Video"
3. Watch the real-time progress bar
4. The video will be downloaded to your browser's default download location

## Requirements

- Python 3.7+
- Flask
- yt-dlp

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