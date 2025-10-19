#!/usr/bin/env python3
"""
Quick setup script for Disc Golf Designer Pro
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def run_application():
    """Run the Streamlit application"""
    print("Starting Disc Golf Designer...")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Thanks for using Disc Golf Designer!")
    except Exception as e:
        print(f"❌ Error running application: {e}")

def main():
    """Main setup and run function"""
    print("🥏 Disc Golf Designer Pro - Setup & Run")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ app.py not found. Please run this script from the project root directory.")
        return
    
    # Install requirements
    if install_requirements():
        print("\n🚀 Ready to launch!")
        print("Starting the application...")
        run_application()
    else:
        print("❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()