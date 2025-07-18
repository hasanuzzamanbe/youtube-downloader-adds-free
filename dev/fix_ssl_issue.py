#!/usr/bin/env python3
"""
Fix urllib3 SSL compatibility issue
"""
import subprocess
import sys

def fix_urllib3_issue():
    print("🔧 Fixing urllib3 SSL compatibility issue...")
    
    try:
        # Downgrade urllib3 to compatible version
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "urllib3<2.0", "--upgrade"
        ])
        print("✅ urllib3 downgraded to compatible version")
        
        # Also ensure requests is compatible
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "requests>=2.28.0", "--upgrade"
        ])
        print("✅ requests updated to compatible version")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to fix urllib3 issue: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if fix_urllib3_issue():
        print("🎉 SSL issue fixed! Restart your Python server.")
    else:
        print("❌ Failed to fix SSL issue. Try manual installation:")
        print("   pip install 'urllib3<2.0' --upgrade")
