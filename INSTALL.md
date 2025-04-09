# YouTube Downloader - Installation Guide

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

## Installation on Windows

### Method 1: Installation via CMD
1. Open Command Prompt (cmd)
2. Navigate to the project directory
```cmd
cd path\to\project
```
3. Create a virtual environment (optional, but recommended)
```cmd
python -m venv venv
venv\Scripts\activate
```
4. Install requirements
```cmd
pip install -r requirements.txt
```

### Method 2: Installation via PowerShell
1. Open PowerShell
2. Navigate to the project directory
```powershell
cd path\to\project
```
3. Create a virtual environment
```powershell
python -m venv venv
.\venv\Scripts\Activate
```
4. Install requirements
```powershell
pip install -r requirements.txt
```

## Installation on Linux (Ubuntu/Debian)

### Preparation
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### Installation
```bash
# Navigate to project directory
cd ~/path/to/project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

## Installation on macOS

### Method 1: Using Homebrew
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python

# Navigate to project directory
cd ~/path/to/project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Method 2: Using macOS System Python
```bash
# Navigate to project directory
cd ~/path/to/project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

## Troubleshooting

### Installation Errors
- Ensure you have the latest version of pip:
```bash
pip install --upgrade pip
```

### Dependency Issues
- For Windows, Microsoft Visual C++ Build Tools might be required
- For Linux, ensure basic build tools are installed:
```bash
sudo apt-get install build-essential python3-dev
```

### Additional System Libraries
- Linux (Ubuntu/Debian):
```bash
sudo apt-get install python3-pyqt5
```
- macOS (Homebrew):
```bash
brew install pyqt5
```

## Running the Application
```bash
# Activate virtual environment
# (Windows)
venv\Scripts\activate

# (Linux/macOS)
source venv/bin/activate

# Run the program
python youtube_downloader.py
```

## Notes
- Always use a virtual environment
- Regularly update libraries: `pip install --upgrade -r requirements.txt`

## Common Issues and Solutions

### PyQt5 Installation Problems
- If you encounter issues with PyQt5 installation, try:
```bash
pip install --upgrade pip wheel
pip install PyQt5
```

### FFmpeg Requirement for yt-dlp
- Some systems might require FFmpeg for full functionality
- Windows: Download from official FFmpeg website
- Linux: 
```bash
sudo apt-get install ffmpeg
```
- macOS:
```bash
brew install ffmpeg
```

### Permission Issues
- On Linux/macOS, use `sudo` if you encounter permission problems
- Preferably, use virtual environments to avoid system-wide installations

## Recommended Development Environment
- Visual Studio Code
- PyCharm
- Anaconda Navigator