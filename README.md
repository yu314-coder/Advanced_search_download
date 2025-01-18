```markdown
# Advanced File Downloader

A sophisticated file downloading tool with web interface, supporting both manual URL analysis and Bing search integration. This project was developed with assistance from ChatGPT and Claude Sonnet.

## Features

### Core Functionality
- Manual URL analysis for file discovery
- Bing search integration for finding downloadable content
- Intelligent file detection and metadata extraction
- Support for Google Drive links
- Human-like browsing behavior to avoid detection
- Cross-platform compatibility (Windows, Linux, macOS)

### File Support
- Documents: PDF, DOCX, etc.
- Archives: ZIP, RAR
- Media: MP3, MP4, AVI, MKV
- Images: PNG, JPG, JPEG, GIF
- Custom extension support

### Advanced Features
- PDF metadata extraction
- File size detection
- Proxy support
- Optional automatic file deletion after download
- Detailed logging system
- Custom file extension support
- Progress tracking and status updates

## Quick Start with Manager

1. Clone the repository:
```bash
git clone https://github.com/yu314-coder/Advanced_search_download.git
cd Advanced_search_download
```

2. Run the manager:
```bash
python manage.py
```

The manager will automatically:
- Check and install required system dependencies
- Set up a Python virtual environment
- Install all required packages
- Install Playwright browsers
- Provide a menu interface for managing the application

## Manual Installation

If you prefer to install manually:

1. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Unix/MacOS
python3 -m venv venv
source venv/bin/activate
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install
```

## System Requirements

- Python 3.8 or higher
- Git
- Internet connection
- Sufficient disk space for downloads
- System-level dependencies (automatically handled by manager)

## Usage

### Using the Manager Interface

Launch the manager and use the menu options:
1. Update all scripts from GitHub
2. Update installed packages
3. Run Advanced Search Download
4. Clean environment
5. Exit

### Using the Web Interface

1. Start the application:
```bash
python download_script.py
```

2. Open your browser and navigate to:
```
http://127.0.0.1:7860
```

3. Choose your operating mode:
   - Manual URL: Direct webpage analysis
   - Bing Search: Search-based file discovery

4. Configure settings:
   - Add custom file extensions (optional)
   - Set proxy (optional)
   - Choose download directory
   - Enable/disable auto-deletion

5. Select files and download

## Advanced Configuration

### Custom Extensions
Add your own file extensions through the web interface's Advanced Options panel.

### Proxy Setup
Enable and configure proxy support through either:
- Web interface settings
- Command line arguments
- Configuration file

### Download Directory
Default locations:
- Manual mode: ./downloads_manual
- Search mode: ./downloads_search

## Troubleshooting

Common issues and solutions:

1. **Installation Fails**
   - Check Python version
   - Verify internet connection
   - Run manager with administrator privileges

2. **Downloads Fail**
   - Check URL accessibility
   - Verify write permissions
   - Try enabling proxy

3. **Browser Launch Issues**
   - Reinstall Playwright browsers
   - Check system dependencies
   - Verify display server (Linux)

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This project was developed with assistance from:
- OpenAI's ChatGPT
- Anthropic's Claude Sonnet

## Disclaimer

- Use responsibly and in accordance with websites' terms of service
- Respect robots.txt policies
- Developers are not responsible for misuse
- Always verify download sources

## Status Logs

Find detailed logs in:
```
advanced_download_log.txt
```

## Security Notes

- Always scan downloaded files
- Use proxy for anonymity when needed
- Verify file signatures when available
- Keep system and dependencies updated

## Future Plans

- Additional file format support
- Enhanced metadata extraction
- Batch processing capabilities
- Download scheduling
- Custom filtering rules

## Contact

For issues and suggestions:
- Create an issue on GitHub
- Fork and submit a pull request

---

**Note**: This tool is for educational purposes and legitimate file downloads. Always respect copyright and terms of service.
```

This README.md provides:
1. Comprehensive project overview
2. Clear installation instructions
3. Detailed usage guidelines
4. Troubleshooting tips
5. Security considerations
6. Future development plans
7. Contribution guidelines
8. Proper acknowledgments and disclaimers

The format is clean and professional, with proper markdown formatting and clear section organization. You can customize it further by:
1. Adding specific examples
2. Including screenshots
3. Adding more detailed configuration options
4. Expanding the troubleshooting section based on user feedback
