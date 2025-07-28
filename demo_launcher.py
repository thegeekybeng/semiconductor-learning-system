"""
Quick Launcher for Semiconductor Learning System Streamlit Demo
Run this directly: python3 demo_launcher.py
"""

import subprocess
import sys
import os
from pathlib import Path

def install_streamlit():
    """Install streamlit if not available"""
    try:
        import streamlit
        return True
    except ImportError:
        print("📦 Installing Streamlit...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit", "plotly", "psutil"])
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Streamlit. Please install manually:")
            print("   pip install streamlit plotly psutil")
            return False

def main():
    print("🔬 Semiconductor Learning System - Demo Launcher")
    print("=" * 50)
    
    # Ensure we're in the right directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Check and install Streamlit
    if not install_streamlit():
        return
    
    print("🚀 Launching Streamlit demo...")
    print("📱 Demo will open at: http://localhost:8501")
    print("💡 Press Ctrl+C to stop the demo")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_demo.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Demo stopped. Thank you!")
    except Exception as e:
        print(f"❌ Error running demo: {e}")

if __name__ == "__main__":
    main()
