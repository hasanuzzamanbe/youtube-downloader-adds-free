#!/usr/bin/env python3
"""
Debug script to test frontend progress updates
"""
import requests
import time
import json

def test_progress_updates():
    base_url = "http://localhost:5300"
    
    # Test video URL
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    print("🧪 Testing Frontend Progress Updates...")
    print(f"URL: {test_url}")
    
    try:
        # Step 1: Get video info
        print("\n📋 Step 1: Getting video info...")
        response = requests.post(f"{base_url}/get-video-info", data={"url": test_url}, timeout=30)
        if response.status_code != 200:
            print(f"❌ Failed to get video info: {response.status_code}")
            return False
        
        info_data = response.json()
        info_id = info_data.get("info_id")
        print(f"✅ Got info_id: {info_id}")
        
        # Step 2: Wait for video info
        print("⏳ Step 2: Waiting for video info...")
        for i in range(30):
            response = requests.get(f"{base_url}/video-info/{info_id}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ready":
                    print(f"✅ Video info ready: {data.get('title', 'Unknown')}")
                    break
            time.sleep(1)
        else:
            print("❌ Timeout waiting for video info")
            return False
        
        # Step 3: Start download
        print("📥 Step 3: Starting video download...")
        response = requests.post(f"{base_url}/start-download", data={
            "info_id": info_id,
            "format": "video",
            "quality": "720"
        }, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Failed to start download: {response.status_code}")
            return False
        
        download_data = response.json()
        download_id = download_data.get("download_id")
        print(f"✅ Started download: {download_id}")
        
        # Step 4: Monitor progress with detailed logging
        print("📊 Step 4: Monitoring progress (detailed)...")
        
        # Check debug endpoint first
        try:
            response = requests.get(f"{base_url}/debug/progress", timeout=5)
            if response.status_code == 200:
                debug_data = response.json()
                print(f"🔍 Active downloads: {debug_data.get('active_downloads', 0)}")
                print(f"🔍 Progress data keys: {list(debug_data.get('progress_data', {}).keys())}")
        except:
            print("⚠️ Debug endpoint not available")
        
        # Monitor progress with 500ms intervals (same as frontend)
        for i in range(120):  # 60 seconds total
            try:
                response = requests.get(f"{base_url}/progress/{download_id}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status", "unknown")
                    progress = data.get("progress_text", "0%")
                    progress_num = data.get("progress", "0%")
                    
                    print(f"📈 [{i:3d}] Progress: {progress} ({progress_num}) - Status: {status}")
                    
                    # Show additional details if available
                    if data.get("downloaded"):
                        print(f"     Downloaded: {data.get('downloaded')} / {data.get('total', 'Unknown')}")
                    if data.get("speed"):
                        print(f"     Speed: {data.get('speed')}, ETA: {data.get('eta', 'Unknown')}")
                    
                    if status == "finished" and data.get("download_ready"):
                        print(f"✅ Download ready: {data.get('filename')}")
                        print(f"   URL available: {'Yes' if data.get('url') else 'No'}")
                        return True
                    elif status == "error":
                        print(f"❌ Download error: {data.get('error', 'Unknown error')}")
                        return False
                    elif status == "processing":
                        print(f"🔄 Still processing... (attempt {i+1}/120)")
                else:
                    print(f"⚠️ Progress check failed: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Request error: {e}")
            
            time.sleep(0.5)  # Same interval as frontend
        
        print("❌ Timeout waiting for download completion")
        
        # Final debug check
        try:
            response = requests.get(f"{base_url}/debug/progress", timeout=5)
            if response.status_code == 200:
                debug_data = response.json()
                print(f"🔍 Final state - Active downloads: {debug_data.get('active_downloads', 0)}")
                if download_id in debug_data.get('progress_data', {}):
                    final_state = debug_data['progress_data'][download_id]
                    print(f"🔍 Final download state: {final_state}")
        except:
            pass
        
        return False
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting frontend debug test...")
    print("This will simulate the exact same polling behavior as the frontend")
    print("Make sure your Flask server is running on localhost:5300")
    print()
    
    success = test_progress_updates()
    
    if success:
        print("\n🎉 Test PASSED! Progress updates are working correctly.")
    else:
        print("\n❌ Test FAILED! This shows the same issue the frontend is experiencing.")
