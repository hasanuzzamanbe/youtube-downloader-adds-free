#!/usr/bin/env python3
"""
Install FFmpeg on macOS
"""
import subprocess
import sys
import shutil
import os

def check_homebrew():
    """Check if Homebrew is installed"""
    return shutil.which('brew') is not None

def install_homebrew():
    """Install Homebrew"""
    print("📦 Installing Homebrew...")
    try:
        subprocess.check_call([
            '/bin/bash', '-c', 
            '$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)'
        ])
        return True
    except subprocess.CalledProcessError:
        return False

def install_ffmpeg_with_brew():
    """Install FFmpeg using Homebrew"""
    print("🎬 Installing FFmpeg with Homebrew...")
    try:
        subprocess.check_call(['brew', 'install', 'ffmpeg'])
        return True
    except subprocess.CalledProcessError:
        return False

def check_ffmpeg():
    """Check if FFmpeg is installed and working"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg installed: {version_line}")
            return True
    except FileNotFoundError:
        pass
    return False

def main():
    print("🔍 Checking FFmpeg installation...")
    
    if check_ffmpeg():
        print("✅ FFmpeg is already installed and working!")
        return True
    
    print("❌ FFmpeg not found. Installing...")
    
    # Check if Homebrew is installed
    if not check_homebrew():
        print("📦 Homebrew not found. Installing Homebrew first...")
        if not install_homebrew():
            print("❌ Failed to install Homebrew")
            print("🔧 Manual installation required:")
            print("   1. Install Homebrew: https://brew.sh/")
            print("   2. Run: brew install ffmpeg")
            return False
        
        # Add Homebrew to PATH for this session
        homebrew_paths = [
            '/opt/homebrew/bin',  # Apple Silicon
            '/usr/local/bin'      # Intel
        ]
        for path in homebrew_paths:
            if os.path.exists(path) and path not in os.environ['PATH']:
                os.environ['PATH'] = f"{path}:{os.environ['PATH']}"
    
    # Install FFmpeg
    if install_ffmpeg_with_brew():
        print("✅ FFmpeg installation completed!")
        
        # Verify installation
        if check_ffmpeg():
            print("🎉 FFmpeg is working correctly!")
            return True
        else:
            print("⚠️ FFmpeg installed but not in PATH")
            print("🔧 Try restarting your terminal or run:")
            print("   export PATH=\"/opt/homebrew/bin:/usr/local/bin:$PATH\"")
    else:
        print("❌ Failed to install FFmpeg")
        print("🔧 Manual installation:")
        print("   brew install ffmpeg")
    
    return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 Ready to use audio downloads!")
        print("   Restart your Python server to enable audio functionality.")
    else:
        print("\n❌ FFmpeg installation failed.")
        print("   Audio downloads will not work until FFmpeg is installed.")
