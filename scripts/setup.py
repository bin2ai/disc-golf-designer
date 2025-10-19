#!/usr/bin/env python3
"""
Setup script for Disc Golf Designer Pro
Automatically configures the Python environment and installs dependencies
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command with error handling"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}:")
        print(f"Command: {command}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🥏 Disc Golf Designer Pro - Setup Script")
    print("=" * 50)
    
    # Check if Python is available
    try:
        python_version = sys.version_info
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} detected")
    except:
        print("❌ Python not found. Please install Python 3.8 or higher.")
        return False
    
    # Check if we're in the right directory
    if not Path("disc_designer.py").exists():
        print("❌ disc_designer.py not found. Please run this script from the project directory.")
        return False
    
    # Create virtual environment if it doesn't exist
    if not Path(".venv").exists():
        if not run_command("python -m venv .venv", "Creating virtual environment"):
            return False
    else:
        print("✅ Virtual environment already exists")
    
    # Activate virtual environment and install packages
    if os.name == 'nt':  # Windows
        pip_path = ".venv\\Scripts\\pip.exe"
        python_path = ".venv\\Scripts\\python.exe"
        activate_script = ".venv\\Scripts\\activate.bat"
    else:  # Unix/Linux/Mac
        pip_path = ".venv/bin/pip"
        python_path = ".venv/bin/python"
        activate_script = ".venv/bin/activate"
    
    # Install requirements
    if not run_command(f"{pip_path} install -r requirements.txt", "Installing Python packages"):
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nTo start the application:")
    print("1. On Windows: Run start.bat")
    print("2. On Unix/Linux/Mac:")
    print(f"   source {activate_script}")
    print("   streamlit run disc_designer.py")
    print("\nThe application will be available at: http://localhost:8501")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)