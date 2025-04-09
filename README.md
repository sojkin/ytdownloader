# YT Downloader

## Project Description
YT Downloader is a versatile tool for downloading YouTube videos with a simple and intuitive interface.

## System Requirements
- Python 3.7+
- Operating Systems: 
  * Windows 10/11
  * macOS 10.14+
  * Linux (Ubuntu 20.04+, Debian 10+)

## Installation

### Windows
1. Clone the repository:
```bash
git clone https://github.com/sojkin/ytdownloader.git
cd ytdownloader
```

2. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### macOS/Linux
1. Clone the repository:
```bash
git clone https://github.com/sojkin/ytdownloader.git
cd ytdownloader
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Console Mode
```bash
python src/main.py
```

### GUI Mode
```bash
python src/gui.py
```

## Configuration

### Environment Variables
- `DOWNLOAD_PATH`: Download directory (default: `~/Downloads/YTDownloader`)
- `MAX_DOWNLOAD_QUALITY`: Maximum download quality (default: 720p)

## Troubleshooting

### Common Issues
- No internet connection
- Outdated YouTube API
- Insufficient permissions

### Updating
```bash
git pull origin master
pip install -r requirements.txt
```

## Features
- Download YouTube videos
- Select video quality
- Customize download location
- Support for multiple platforms

## Security
- Regularly update the software
- Use official download sources
- Respect copyright laws when downloading content

## License
MIT License

## Authors
- Marcin Sojka (@sojkin)

## Support
Report issues: https://github.com/sojkin/ytdownloader/issues

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request