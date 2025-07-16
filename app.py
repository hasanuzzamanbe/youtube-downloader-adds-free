from flask import Flask, render_template, request, jsonify, send_file, Response, stream_template
import yt_dlp
import os
import threading
import uuid
import time
import glob
import tempfile
import requests
import re
from urllib.parse import urlparse, quote

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"
progress_data = {}
video_info_data = {}

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

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

def get_video_info(url, info_id):
    """Get video information without downloading"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video info
            info = ydl.extract_info(url, download=False)
            if not info:
                video_info_data[info_id] = {'error': 'Failed to extract video info', 'status': 'error'}
                return
                
            title = info.get('title', 'Unknown Title')
            duration = info.get('duration', 0)
            uploader = info.get('uploader', 'Unknown')
            view_count = info.get('view_count', 0)
            thumbnail = info.get('thumbnail', '')
            description = info.get('description', '')[:200] + '...' if info.get('description', '') else 'No description available'
            ext = info.get('ext', 'mp4')
            
            # Format duration
            if duration:
                minutes = duration // 60
                seconds = duration % 60
                duration_str = f"{minutes}:{seconds:02d}"
            else:
                duration_str = "Unknown"
            
            # Format view count
            if view_count:
                if view_count >= 1000000:
                    view_str = f"{view_count/1000000:.1f}M views"
                elif view_count >= 1000:
                    view_str = f"{view_count/1000:.1f}K views"
                else:
                    view_str = f"{view_count} views"
            else:
                view_str = "Unknown views"
            
            # Sanitize the filename
            original_filename = f"{title}.{ext}"
            safe_filename = sanitize_filename(original_filename)
            
            # Get the best format URL - look for video formats specifically
            formats = info.get('formats', []) if info else []
            best_video_format = None
            
            # First, try to find the best video format
            for f in formats:
                if f and f.get('vcodec') != 'none' and f.get('acodec') != 'none':  # Has both video and audio
                    if f.get('height', 0) > 0:  # Has video resolution
                        best_video_format = f
                        break
            
            # If no video+audio format found, look for best video only
            if not best_video_format:
                for f in formats:
                    if f and f.get('vcodec') != 'none' and f.get('height', 0) > 0:
                        best_video_format = f
                        break
            
            # If still no video format, take the last format
            if not best_video_format and formats:
                best_video_format = formats[-1]
            
            if best_video_format:
                direct_url = best_video_format.get('url', '')
                format_info = best_video_format.get('format_note', '')
                height = best_video_format.get('height', 0)
                
                # Debug: Print format information
                print(f"Selected format: {format_info}, Height: {height}, URL: {direct_url[:100]}...")
                
                # Update progress data with video info
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
                    'original_youtube_url': url,  # Store original URL as fallback
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

def download_video(download_id, direct_url, filename, original_filename, original_youtube_url):
    """Stream video directly to browser while downloading"""
    def progress_hook(d):
        if d['status'] == 'downloading':
            # Extract percentage as a number for the progress bar
            percent_str = d.get('_percent_str', '0.0%')
            try:
                # Remove % and convert to float, then back to percentage for CSS
                percent_num = float(percent_str.replace('%', ''))
                progress_data[download_id] = {
                    'progress': f"{percent_num}%",  # For CSS width
                    'progress_text': percent_str,   # For display text
                    'eta': d.get('_eta_str', '...'),
                    'speed': d.get('_speed_str', '...'),
                    'filename': filename,
                    'status': 'downloading',
                    'url': direct_url
                }
            except ValueError:
                progress_data[download_id] = {
                    'progress': '0%',
                    'progress_text': '0.0%',
                    'eta': '...',
                    'speed': '...',
                    'filename': filename,
                    'status': 'downloading',
                    'url': direct_url
                }
        elif d['status'] == 'finished':
            progress_data[download_id] = {
                'progress': '100%',
                'progress_text': '100%',
                'eta': 'Done',
                'speed': 'Done',
                'filename': filename,
                'download_ready': True,
                'status': 'finished',
                'url': direct_url
            }

    # Instead of downloading to server, we'll stream directly
    # Just mark as ready for streaming
    progress_data[download_id] = {
        'progress': '0%',
        'progress_text': '0.0%',
        'eta': '...',
        'speed': '...',
        'filename': filename,
        'status': 'starting',
        'url': direct_url
    }
    
    # Simulate a brief preparation time
    time.sleep(1)
    
    progress_data[download_id] = {
        'progress': '100%',
        'progress_text': '100%',
        'eta': 'Done',
        'speed': 'Done',
        'filename': filename,
        'download_ready': True,
        'status': 'finished',
        'url': direct_url
    }
    
    # Clean up progress data after 10 minutes
    def cleanup_progress():
        time.sleep(600)  # 10 minutes
        if download_id in progress_data:
            del progress_data[download_id]
    
    threading.Thread(target=cleanup_progress, daemon=True).start()

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

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
        'status': 'starting'
    }

    # Start download in a thread
    threading.Thread(target=download_video, args=(
        download_id, 
        video_info.get('url', ''), 
        video_info.get('filename', ''),
        video_info.get('original_filename', ''),
        video_info.get('original_youtube_url', '')
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
    direct_url = progress_info.get('url', '')
    
    if not direct_url:
        return jsonify({"error": "No download URL available"}), 404
    
    try:
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
                    
                    # Get content type and size
                    content_type = r.headers.get('content-type', 'video/mp4')
                    total_size = int(r.headers.get('content-length', 0))
                    downloaded = 0
                    
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            downloaded += len(chunk)
                            # Update progress
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                progress_data[download_id] = {
                                    **progress_data.get(download_id, {}),
                                    'progress': f"{percent:.1f}%",
                                    'progress_text': f"{percent:.1f}%",
                                    'status': 'streaming'
                                }
                            yield chunk
                            
            except requests.exceptions.RequestException as e:
                print(f"Request error: {e}")
                raise e
        
        # Create safe headers with proper encoding
        safe_filename = quote(filename)  # URL encode the filename
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
        
    except Exception as e:
        print(f"Streaming error: {e}")
        return jsonify({"error": f"Error streaming video: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5300)
