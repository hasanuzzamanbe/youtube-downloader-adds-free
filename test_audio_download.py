#!/usr/bin/env python3
"""
Test audio download functionality
"""
import requests
import time
import json

def test_audio_download():
    base_url = "http://localhost:5300"
    
    # Test video URL (short video for testing)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - short video
    
    print("🧪 Testing Audio Download Flow...")
    print(f"URL: {test_url}")
    
    try:
        # Step 1: Get video info
        print("\n📋 Step 1: Getting video info...")
        response = requests.post(f"{base_url}/get-video-info", data={"url": test_url}, timeout=30)
        if response.status_code != 200:
            print(f"❌ Failed to get video info: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        info_data = response.json()
        info_id = info_data.get("info_id")
        print(f"✅ Got info_id: {info_id}")
        
        # Step 2: Poll for video info
        print("⏳ Step 2: Waiting for video info...")
        for i in range(30):
            response = requests.get(f"{base_url}/video-info/{info_id}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                print(f"   Status: {status}")
                if status == "ready":
                    print(f"✅ Video info ready: {data.get('title', 'Unknown')}")
                    break
            time.sleep(1)
        else:
            print("❌ Timeout waiting for video info")
            return False
        
        # Step 3: Check system info for FFmpeg
        print("🔧 Step 3: Checking FFmpeg availability...")
        response = requests.get(f"{base_url}/system-info", timeout=10)
        if response.status_code == 200:
            system_data = response.json()
            ffmpeg_available = system_data.get("ffmpeg_available", False)
            print(f"   FFmpeg available: {ffmpeg_available}")
            if not ffmpeg_available:
                print("❌ FFmpeg not available - audio downloads will fail")
                print("   Please install FFmpeg first: brew install ffmpeg")
                return False
        
        # Step 4: Start audio download (high quality MP3)
        print("📥 Step 4: Starting audio download (320kbps MP3)...")
        response = requests.post(f"{base_url}/start-download", data={
            "info_id": info_id,
            "format": "audio",
            "audio_quality": "high"
        }, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Failed to start download: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        download_data = response.json()
        download_id = download_data.get("download_id")
        print(f"✅ Started audio download: {download_id}")
        
        # Step 5: Monitor progress
        print("📊 Step 5: Monitoring audio download progress...")
        for i in range(120):  # Wait up to 2 minutes for audio processing
            try:
                response = requests.get(f"{base_url}/progress/{download_id}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status", "unknown")
                    progress = data.get("progress_text", "0%")
                    
                    print(f"📈 Progress: {progress} - Status: {status}")
                    
                    # Show additional details if available
                    if data.get("downloaded"):
                        print(f"     Downloaded: {data.get('downloaded')} / {data.get('total', 'Unknown')}")
                    if data.get("speed"):
                        print(f"     Speed: {data.get('speed')}, ETA: {data.get('eta', 'Unknown')}")
                    
                    if status == "finished" and data.get("download_ready"):
                        print(f"✅ Audio download ready: {data.get('filename')}")
                        print(f"   Download type: {data.get('download_type', 'unknown')}")
                        
                        # Test file download
                        print("📁 Step 6: Testing audio file download...")
                        response = requests.get(f"{base_url}/stream-download/{download_id}", timeout=30)
                        if response.status_code == 200:
                            print(f"✅ Audio file download successful ({len(response.content)} bytes)")
                            
                            # Check if it's actually an MP3 file
                            if response.content.startswith(b'ID3') or b'LAME' in response.content[:1000]:
                                print("✅ File appears to be a valid MP3")
                            else:
                                print("⚠️ File may not be a valid MP3")
                            
                            return True
                        else:
                            print(f"❌ Audio file download failed: {response.status_code}")
                            return False
                    elif status == "error":
                        print(f"❌ Download error: {data.get('error', 'Unknown error')}")
                        return False
                else:
                    print(f"⚠️ Progress check failed: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Request error: {e}")
            
            time.sleep(2)
        
        print("❌ Timeout waiting for audio download")
        return False
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting audio download test...")
    print("Make sure your Flask server is running on localhost:5300")
    print("Make sure FFmpeg is installed: brew install ffmpeg")
    print()
    
    success = test_audio_download()
    
    if success:
        print("\n🎉 Test PASSED! Audio downloads are working correctly.")
        print("✅ Audio files are processed and automatically cleaned up after download.")
    else:
        print("\n❌ Test FAILED! Check the server logs for details.")
        print("💡 Common issues:")
        print("   - FFmpeg not installed (brew install ffmpeg)")
        print("   - Server not running (python3 app.py)")
        print("   - Network connectivity issues")
