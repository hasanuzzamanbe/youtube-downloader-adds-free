#!/usr/bin/env python3
"""
Debug script to test video URL extraction
"""
import yt_dlp
import time

def test_video_extraction():
    # Test with a short, reliable video
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - reliable test video
    
    print("🧪 Testing video URL extraction...")
    print(f"URL: {test_url}")
    
    # Test different quality settings
    qualities = ['best', '720', '480', '360']
    
    for quality in qualities:
        print(f"\n📊 Testing quality: {quality}")
        
        try:
            # Configure format selector
            if quality == 'best':
                format_selector = 'best'
            else:
                format_selector = f'best[height<={quality}]'
            
            ydl_opts = {
                'format': format_selector,
                'quiet': True,
                'no_warnings': True,
                'socket_timeout': 30,
                'retries': 3
            }
            
            print(f"Format selector: {format_selector}")
            
            start_time = time.time()
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print("Extracting info...")
                info = ydl.extract_info(test_url, download=False)
                
                extraction_time = time.time() - start_time
                print(f"✅ Extraction completed in {extraction_time:.2f} seconds")
                
                # Check what we got
                if 'url' in info:
                    print(f"✅ Direct URL found: {info['url'][:100]}...")
                elif 'formats' in info and info['formats']:
                    selected_format = info['formats'][-1]
                    direct_url = selected_format.get('url', '')
                    print(f"✅ Format URL found: {direct_url[:100] if direct_url else 'None'}...")
                    print(f"   Format info: {selected_format.get('format_id', 'Unknown')} - {selected_format.get('height', 'Unknown')}p")
                else:
                    print("❌ No URL found")
                
                print(f"   Title: {info.get('title', 'Unknown')}")
                print(f"   Duration: {info.get('duration', 'Unknown')} seconds")
                print(f"   Available formats: {len(info.get('formats', []))}")
                
        except Exception as e:
            print(f"❌ Error with quality {quality}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n🏁 Test completed!")

if __name__ == "__main__":
    test_video_extraction()
