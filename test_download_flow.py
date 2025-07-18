#!/usr/bin/env python3
"""
Test the complete download flow
"""
import requests
import time
import json

def test_video_download():
    base_url = "http://localhost:5300"
    
    # Test video URL (short video for testing)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - short video
    
    print("🧪 Testing Video Download Flow...")
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
        
        # Step 3: Start download (video format, 720p)
        print("📥 Step 3: Starting video download (720p)...")
        response = requests.post(f"{base_url}/start-download", data={
            "info_id": info_id,
            "format": "video",
            "quality": "720"
        }, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Failed to start download: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        download_data = response.json()
        download_id = download_data.get("download_id")
        print(f"✅ Started download: {download_id}")
        
        # Step 4: Monitor progress
        print("📊 Step 4: Monitoring progress...")
        for i in range(60):  # Wait up to 60 seconds
            try:
                response = requests.get(f"{base_url}/progress/{download_id}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status", "unknown")
                    progress = data.get("progress_text", "0%")
                    
                    print(f"📈 Progress: {progress} - Status: {status}")
                    
                    if status == "finished" and data.get("download_ready"):
                        print(f"✅ Download ready: {data.get('filename')}")
                        print(f"   Download type: {data.get('download_type', 'unknown')}")
                        print(f"   Quality info: {data.get('quality_info', 'unknown')}")
                        return True
                    elif status == "error":
                        print(f"❌ Download error: {data.get('error', 'Unknown error')}")
                        return False
                else:
                    print(f"⚠️ Progress check failed: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Request error: {e}")
            
            time.sleep(2)
        
        print("❌ Timeout waiting for download")
        return False
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting download flow test...")
    print("Make sure your Flask server is running on localhost:5300")
    
    success = test_video_download()
    
    if success:
        print("\n🎉 Test PASSED! Download flow is working correctly.")
    else:
        print("\n❌ Test FAILED! Check the server logs for details.")
