#!/usr/bin/env python3
"""
Quick test script to verify download functionality
"""
import requests
import time
import json

def test_download_flow():
    base_url = "http://localhost:5300"
    
    # Test video URL (short video for testing)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - short video
    
    print("🧪 Testing YouTube Downloader...")
    
    # Step 1: Get video info
    print("📋 Step 1: Getting video info...")
    response = requests.post(f"{base_url}/get-video-info", data={"url": test_url})
    if response.status_code != 200:
        print(f"❌ Failed to get video info: {response.status_code}")
        return
    
    info_data = response.json()
    info_id = info_data.get("info_id")
    print(f"✅ Got info_id: {info_id}")
    
    # Step 2: Poll for video info
    print("⏳ Step 2: Waiting for video info...")
    for i in range(30):
        response = requests.get(f"{base_url}/video-info/{info_id}")
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ready":
                print(f"✅ Video info ready: {data.get('title', 'Unknown')}")
                break
        time.sleep(1)
    else:
        print("❌ Timeout waiting for video info")
        return
    
    # Step 3: Start download (video format, 720p)
    print("📥 Step 3: Starting download (720p video)...")
    response = requests.post(f"{base_url}/start-download", data={
        "info_id": info_id,
        "format": "video",
        "quality": "720"
    })
    if response.status_code != 200:
        print(f"❌ Failed to start download: {response.status_code}")
        return
    
    download_data = response.json()
    download_id = download_data.get("download_id")
    print(f"✅ Started download: {download_id}")
    
    # Step 4: Monitor progress
    print("📊 Step 4: Monitoring progress...")
    for i in range(60):
        response = requests.get(f"{base_url}/progress/{download_id}")
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            progress = data.get("progress_text", "0%")
            
            print(f"📈 Progress: {progress} - Status: {status}")
            
            if status == "finished" and data.get("download_ready"):
                print(f"✅ Download complete: {data.get('filename')}")
                
                # Test file download
                print("📁 Step 5: Testing file download...")
                response = requests.get(f"{base_url}/stream-download/{download_id}")
                if response.status_code == 200:
                    print(f"✅ File download successful ({len(response.content)} bytes)")
                else:
                    print(f"❌ File download failed: {response.status_code}")
                break
            elif status == "error":
                print(f"❌ Download error: {data.get('error', 'Unknown error')}")
                break
        
        time.sleep(2)
    else:
        print("❌ Timeout waiting for download")
    
    print("🏁 Test completed!")

if __name__ == "__main__":
    try:
        test_download_flow()
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
