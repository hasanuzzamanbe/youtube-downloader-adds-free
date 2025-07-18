from flask import Flask, render_template, request, jsonify, send_file, Response, stream_template, send_from_directory
import yt_dlp
import os
import threading
import uuid
import time
import glob
import tempfile
import requests
import re
import subprocess
import shutil
from urllib.parse import urlparse, quote

# Configure Flask to serve Vue.js build files
app = Flask(__name__,
            static_folder='dist/assets',
            template_folder='dist')
DOWNLOAD_DIR = "downloads"
progress_data = {}
video_info_data = {}

# Create download directory but clean it on startup
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def check_ffmpeg():
    """Check if FFmpeg is available"""
    return shutil.which('ffmpeg') is not None

def cleanup_download_directory():
    """Clean up any existing files in download directory"""
    try:
        for filename in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
                print(f"Cleaned up: {filename}")
    except Exception as e:
        print(f"Error cleaning download directory: {e}")

# Check FFmpeg availability on startup
FFMPEG_AVAILABLE = check_ffmpeg()
if not FFMPEG_AVAILABLE:
    print("INFO: FFmpeg not found. Audio extraction disabled (direct streaming mode).")

# Clean up any existing downloads on startup
cleanup_download_directory()
print("🚀 Server running in direct streaming mode - no files stored on server!")

def sanitize_filename(filename):
    """Sanitize filename to be safe for HTTP headers and file systems"""
    # Remove or replace problematic characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)  # Remove invalid file chars
    filename = re.sub(r'[^\x00-\x7F]+', '_', filename)  # Remove non-ASCII chars
    filename = re.sub(r'\s+', '_', filename)  # Replace spaces with underscores
    filename = re.sub(r'_+', '_', filename)  # Replace multiple underscores with single
    filename = filename.strip('_.')  # Remove leading/trailing underscores and dots
    
    # Ensure filename is not too long
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200-len(ext)] + ext
    
    # Ensure filename is not empty
    if not filename:
        filename = "video"
    
    return filename

def clean_youtube_url(url):
    """Clean YouTube URL by removing playlist and other parameters"""
    if 'youtube.com' in url or 'youtu.be' in url:
        # Extract video ID
        if 'v=' in url:
            video_id = url.split('v=')[1].split('&')[0]
        else:
            video_id = url.split('/')[-1].split('?')[0]
        # Return clean URL
        return f'https://www.youtube.com/watch?v={video_id}'
    return url

def get_video_info(url, info_id):
    """Get video information without downloading - Optimized for speed"""
    # Clean the URL first
    url = clean_youtube_url(url)
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'extract_flat': False,  # Get full video info
            'no_color': True,
            'prefer_ffmpeg': False,
            'skip_download': True,
            'noplaylist': True,
            'format': 'best',  # Get best available format
            'format_sort': ['res', 'fps', 'codec', 'ext'],
            'max_downloads': 1,
            'playlist_items': '1'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video info with minimal processing
            info = ydl.extract_info(url, download=False)
            if not info:
                video_info_data[info_id] = {'error': 'Failed to extract video info', 'status': 'error'}
                return
                
            # Extract only essential info for speed
            title = info.get('title', 'Unknown Title')
            duration = info.get('duration', 0)
            uploader = info.get('uploader', 'Unknown')
            view_count = info.get('view_count', 0)
            thumbnail = info.get('thumbnail', '')
            description = info.get('description', '')[:200] + '...' if info.get('description', '') else 'No description available'
            ext = info.get('ext', 'mp4')
            
            # Fast duration formatting
            if duration:
                minutes = duration // 60
                seconds = duration % 60
                duration_str = f"{minutes}:{seconds:02d}"
            else:
                duration_str = "Unknown"
            
            # Fast view count formatting
            if view_count:
                if view_count >= 1000000:
                    view_str = f"{view_count//1000000}M views"
                elif view_count >= 1000:
                    view_str = f"{view_count//1000}K views"
                else:
                    view_str = f"{view_count} views"
            else:
                view_str = "Unknown views"
            
            # Fast filename sanitization
            original_filename = f"{title}.{ext}"
            safe_filename = sanitize_filename(original_filename)
            
            # Optimized format selection - get first good format quickly
            formats = info.get('formats', [])
            best_video_format = None
            
            # Quick format selection - prioritize mp4 with both video and audio
            for f in formats:
                if (f and f.get('vcodec') != 'none' and
                    f.get('acodec') != 'none' and
                    f.get('ext') == 'mp4' and
                    f.get('height', 0) > 0):
                    best_video_format = f
                    break
            
            # Fallback to any format with video
            if not best_video_format:
                for f in formats:
                    if f and f.get('vcodec') != 'none' and f.get('height', 0) > 0:
                        best_video_format = f
                        break
            
            # Last resort - any format
            if not best_video_format and formats:
                best_video_format = formats[0]  # Take first instead of last
            
            if best_video_format:
                direct_url = best_video_format.get('url', '')
                format_info = best_video_format.get('format_note', '')
                height = best_video_format.get('height', 0)
                
                # Store video info immediately
                video_info_data[info_id] = {
                    'title': title,
                    'duration': duration_str,
                    'uploader': uploader,
                    'view_count': view_str,
                    'thumbnail': thumbnail,
                    'description': description,
                    'filename': safe_filename,
                    'original_filename': original_filename,
                    'url': direct_url,
                    'original_youtube_url': url,
                    'status': 'ready',
                    'ext': ext,
                    'format_info': format_info,
                    'height': height
                }
            else:
                video_info_data[info_id] = {'error': 'No suitable video format found', 'status': 'error'}
                
    except Exception as e:
        video_info_data[info_id] = {'error': str(e), 'status': 'error'}
    
    # Clean up video info data after 30 minutes
    def cleanup_video_info():
        time.sleep(1800)  # 30 minutes
        if info_id in video_info_data:
            del video_info_data[info_id]
    
    threading.Thread(target=cleanup_video_info, daemon=True).start()

def download_video(download_id, youtube_url, filename, original_filename, format_type, quality):
    """Get direct download URL for streaming to browser without server storage"""
    # Clean the URL first to remove playlist parameters
    youtube_url = clean_youtube_url(youtube_url)
    try:
        # Initialize progress
        progress_data[download_id] = {
            'progress': '0%',
            'progress_text': 'Getting download URL...',
            'eta': '...',
            'speed': '...',
            'filename': filename,
            'status': 'starting'
        }

        # Configure yt-dlp options based on format and quality
        if format_type == 'audio':
            # Audio: Download to server with automatic cleanup
            if not FFMPEG_AVAILABLE:
                progress_data[download_id] = {
                    'progress': '0%',
                    'progress_text': 'Error',
                    'eta': '...',
                    'speed': '...',
                    'filename': filename,
                    'status': 'error',
                    'error': 'FFmpeg not found. Please install FFmpeg to download audio files.'
                }
                return

            # Audio download with progress tracking
            def progress_hook(d):
                if d['status'] == 'downloading':
                    percent_str = d.get('_percent_str', '0.0%')
                    try:
                        percent_num = float(percent_str.replace('%', '').strip()) if percent_str else 0
                        progress_data[download_id] = {
                            'progress': f"{percent_num}%",
                            'progress_text': percent_str,
                            'eta': d.get('_eta_str', '...'),
                            'speed': d.get('_speed_str', '...'),
                            'filename': os.path.basename(d.get('filename', filename)),
                            'status': 'downloading'
                        }
                    except:
                        pass
                elif d['status'] == 'finished':
                    final_filename = d.get('filename', filename)
                    progress_data[download_id] = {
                        'progress': '100%',
                        'progress_text': '100%',
                        'eta': 'Done',
                        'speed': 'Done',
                        'filename': os.path.basename(final_filename),
                        'download_ready': True,
                        'status': 'finished',
                        'filepath': final_filename,
                        'download_type': 'audio'
                    }

            # Audio download options
            audio_quality_map = {
                'high': '320',
                'medium': '192',
                'low': '128'
            }

            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': audio_quality_map.get(quality, '192'),
                }],
                'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
                'progress_hooks': [progress_hook],
                'quiet': False,
                'no_warnings': False
            }

            # Update filename for audio
            base_name = os.path.splitext(filename)[0]
            filename = f"{base_name}.mp3"

            # Download audio file to server
            print(f"Starting audio download with quality: {quality}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            return

        else:
            # Video download options with flexible format selection
            if quality == 'best':
                format_selector = 'bestvideo[height<=?1080]+bestaudio/best'
            elif quality == '1080':
                format_selector = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
            elif quality == '720':
                format_selector = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
            elif quality == '480':
                format_selector = 'bestvideo[height<=480]+bestaudio/best[height<=480]'
            elif quality == '360':
                format_selector = 'bestvideo[height<=360]+bestaudio/best[height<=360]'
            elif quality == '240':
                format_selector = 'bestvideo[height<=240]+bestaudio/best[height<=240]'
            else:
                format_selector = 'bestvideo+bestaudio/best'

            ydl_opts = {
                'format': format_selector,
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
                'extract_flat': False,
                'max_downloads': 1,
                'playlist_items': '1',
                'skip_download': False,
                'format_sort': ['res', 'fps', 'codec', 'ext'],
                'merge_output_format': None  # Let yt-dlp choose the best format
            }

        # Get direct URL without downloading
        print(f"Getting direct URL for format: {format_type}, quality: {quality}")

        progress_data[download_id] = {
            'progress': '50%',
            'progress_text': 'Extracting download URL...',
            'eta': '...',
            'speed': '...',
            'filename': filename,
            'status': 'processing'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # Extract info with format selection
                info = ydl.extract_info(youtube_url, download=False)
                
                # Get available formats
                formats = info.get('formats', [])
                if not formats:
                    raise Exception("No formats available for this video")
                
                # Try to find a suitable format
                for fmt in reversed(formats):  # Start from highest quality
                    if fmt.get('url'):
                        direct_url = fmt['url']
                        break
                else:
                    raise Exception("No playable format found")
                
                if not direct_url:
                    raise Exception("Could not extract video URL")
            except Exception as e:
                print(f"Format selection error: {str(e)}")
                # Fallback to simpler format selection
                ydl.params['format'] = 'best'
                info = ydl.extract_info(youtube_url, download=False)
                direct_url = info.get('url', '')

            # Update progress with success
            progress_data[download_id] = {
                'progress': '100%',
                'progress_text': 'Ready for download',
                'eta': 'Ready',
                'speed': 'Ready',
                'filename': filename,
                'download_ready': True,
                'status': 'finished',
                'url': direct_url,
                'quality_info': f"{info.get('height', 'Unknown')}p" if info.get('height') else 'Unknown',
                'filesize': info.get('filesize') or info.get('filesize_approx', 0)
            }

    except Exception as e:
        error_message = str(e)
        print(f"Download error for {youtube_url}: {error_message}")
        
        if "No suitable format found" in error_message:
            error_message = "No suitable video format found. Please try a different quality setting or check if the video is available."
        elif "No playable format found" in error_message:
            error_message = "Could not find a playable video format. Please try a different quality setting."
        elif "No formats available" in error_message:
            error_message = "No video formats available. The video might be restricted or unavailable."
        
        progress_data[download_id] = {
            'progress': '0%',
            'progress_text': 'Error',
            'eta': '...',
            'speed': '...',
            'filename': filename,
            'status': 'error',
            'error': error_message
        }

    # Clean up progress data after 10 minutes
    def cleanup_progress():
        time.sleep(600)  # 10 minutes
        if download_id in progress_data:
            del progress_data[download_id]
        # Also clean any files that might have been created
        cleanup_download_directory()

    threading.Thread(target=cleanup_progress, daemon=True).start()

@app.route("/", methods=["GET", "POST"])
def index():
    return send_from_directory('dist', 'index.html')

@app.route("/watch")
def watch_route():
    return send_from_directory('dist', 'index.html')

@app.route("/shorts/<path:video_id>")
def shorts_route(video_id):
    return send_from_directory('dist', 'index.html')

# Serve Vue.js static assets
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('dist/assets', filename)

@app.route("/get-video-info", methods=["POST"])
def get_video_info_route():
    url = request.form["url"]
    # Use UUID for unique info IDs
    info_id = str(uuid.uuid4())
    
    # Initialize video info data
    video_info_data[info_id] = {
        'status': 'starting'
    }

    # Start video info extraction in a thread
    threading.Thread(target=get_video_info, args=(url, info_id)).start()

    return jsonify({"info_id": info_id})

@app.route("/video-info/<info_id>")
def check_video_info(info_id):
    return jsonify(video_info_data.get(info_id, {
        "status": "unknown"
    }))

@app.route("/start-download", methods=["POST"])
def start_download():
    info_id = request.form["info_id"]
    format_type = request.form.get("format", "video")
    quality = request.form.get("quality", "best")
    audio_quality = request.form.get("audio_quality", "high")

    video_info = video_info_data.get(info_id, {})

    if not video_info or video_info.get('status') != 'ready':
        return jsonify({"error": "Video info not ready"}), 400

    # Use UUID for unique download IDs
    download_id = str(uuid.uuid4())

    # Initialize progress data
    progress_data[download_id] = {
        'progress': '0%',
        'progress_text': '0.0%',
        'eta': '...',
        'speed': '...',
        'filename': video_info.get('filename', ''),
        'download_ready': False,
        'status': 'starting',
        'format': format_type,
        'quality': quality if format_type == 'video' else audio_quality
    }

    # Start download in a thread
    threading.Thread(target=download_video, args=(
        download_id,
        video_info.get('original_youtube_url', ''),
        video_info.get('filename', ''),
        video_info.get('original_filename', ''),
        format_type,
        quality if format_type == 'video' else audio_quality
    )).start()

    return jsonify({"download_id": download_id})

@app.route("/progress/<download_id>")
def check_progress(download_id):
    return jsonify(progress_data.get(download_id, {
        "progress": "0%",
        "progress_text": "0.0%",
        "eta": "...",
        "speed": "...",
        "filename": "",
        "download_ready": False,
        "status": "unknown"
    }))

@app.route("/system-info")
def system_info():
    """Get system information including FFmpeg availability"""
    return jsonify({
        "ffmpeg_available": FFMPEG_AVAILABLE,
        "supported_formats": {
            "video": ["best", "1080", "720", "480", "360", "240"],
            "audio": ["high", "medium", "low"] if FFMPEG_AVAILABLE else []
        }
    })

@app.route("/stream-download/<download_id>")
def stream_download(download_id):
    """Stream video directly to browser's download section"""
    progress_info = progress_data.get(download_id, {})
    
    if progress_info.get('status') == 'starting':
        return jsonify({"error": "Download not started yet"}), 400
    
    if progress_info.get('status') == 'downloading':
        return jsonify({"error": "Download in progress, please wait"}), 400
    
    if progress_info.get('status') == 'error':
        return jsonify({"error": "Download failed"}), 400
    
    if not progress_info.get('download_ready'):
        return jsonify({"error": "Download not ready yet"}), 400
    
    filename = progress_info.get('filename', 'video.mp4')
    download_type = progress_info.get('download_type', 'video')

    try:
        if download_type == 'video':
            # Video: Stream directly from YouTube
            direct_url = progress_info.get('url', '')

            if not direct_url:
                return jsonify({"error": "No download URL available"}), 404

            # Stream the video directly from YouTube to browser
            def generate():
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'identity',
                    'Range': 'bytes=0-',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.youtube.com/',
                }

                try:
                    with requests.get(direct_url, stream=True, headers=headers, timeout=60) as r:
                        r.raise_for_status()

                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                yield chunk

                except requests.exceptions.RequestException as e:
                    print(f"Request error: {e}")
                    raise e

            # Create safe headers with proper encoding
            safe_filename = quote(filename)
            content_disposition = f'attachment; filename="{filename}"; filename*=UTF-8\'\'{safe_filename}'

            response = Response(
                generate(),
                mimetype='video/mp4',
                headers={
                    'Content-Disposition': content_disposition,
                    'Cache-Control': 'no-cache',
                    'Accept-Ranges': 'bytes',
                    'Connection': 'keep-alive'
                }
            )

            return response

        else:
            # Audio: Serve file from server then delete it
            filepath = progress_info.get('filepath', '')

            if not filepath or not os.path.exists(filepath):
                return jsonify({"error": "Downloaded file not found"}), 404

            # Determine MIME type
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext == '.mp3':
                mimetype = 'audio/mpeg'
            else:
                mimetype = 'application/octet-stream'

            # Create a custom response that deletes the file after serving
            def generate_and_cleanup():
                try:
                    with open(filepath, 'rb') as f:
                        while True:
                            chunk = f.read(8192)
                            if not chunk:
                                break
                            yield chunk
                finally:
                    # Delete the file after serving
                    try:
                        if os.path.exists(filepath):
                            os.unlink(filepath)
                            print(f"🗑️ Cleaned up audio file: {os.path.basename(filepath)}")
                    except Exception as e:
                        print(f"Error cleaning up file {filepath}: {e}")

            # Create safe headers with proper encoding
            safe_filename = quote(filename)
            content_disposition = f'attachment; filename="{filename}"; filename*=UTF-8\'\'{safe_filename}'

            response = Response(
                generate_and_cleanup(),
                mimetype=mimetype,
                headers={
                    'Content-Disposition': content_disposition,
                    'Cache-Control': 'no-cache'
                }
            )

            return response

    except Exception as e:
        print(f"File serving error: {e}")
        return jsonify({"error": f"Error serving file: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5300)
