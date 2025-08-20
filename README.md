# 📸 URL Screenshot Processor

A powerful Python tool that automatically captures screenshots and extracts logo URLs from websites listed in spreadsheets. Perfect for web research, competitive analysis, and building visual databases of websites.

## ✨ Features

- 🌐 **Batch Processing**: Process multiple URLs simultaneously with configurable concurrency
- 📸 **Full-Page Screenshots**: Capture complete webpage screenshots in PNG format
- 🎯 **Logo Detection**: Automatically extract company logos and favicons
- 📊 **Multiple Formats**: Support for CSV and Excel files
- 🔄 **Retry Logic**: Automatic retry for failed requests with exponential backoff
- 🌐 **Multi-Browser**: Firefox, WebKit, and Chromium browser support with automatic fallback
- 📈 **Progress Tracking**: Real-time progress reporting and comprehensive statistics
- 🛡️ **Error Handling**: Graceful handling of invalid URLs and network issues
- 🎨 **Detailed Logging**: Comprehensive logging with configurable verbosity levels

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- macOS, Windows, or Linux
- Internet connection for downloading browser dependencies

### Installation

1. **Download the files** to your desired directory:
   ```bash
   # Example for Desktop
   cd ~/Desktop
   ```

2. **Run the automated setup**:
   ```bash
   # Make setup script executable
   chmod +x setup_and_run.sh
   
   # Run setup (installs dependencies and browsers)
   ./setup_and_run.sh
   ```

3. **Activate the virtual environment** (required before each use):
   ```bash
   source venv/bin/activate
   ```

## 📋 Usage

### Option 1: Quick Test with Sample Data

```bash
# Create sample spreadsheet with test URLs
python url_screenshot_processor.py --create-sample

# Process the sample file
python url_screenshot_processor.py sample_urls.xlsx
```

### Option 2: Process Your Own URLs

**Create a spreadsheet with URLs in the first column:**

**CSV Format:**
```csv
URL
https://www.google.com
https://www.github.com
https://www.python.org
```

**Process your file:**
```bash
python url_screenshot_processor.py my_urls.csv
```

## 🎛️ Command Line Options

```bash
python url_screenshot_processor.py [FILE] [OPTIONS]

Options:
  --create-sample          Create sample spreadsheet with test URLs
  --output-dir DIR         Output directory for screenshots (default: screenshots)
  --batch-size N           Number of URLs to process concurrently (default: 3)
  --max-retries N          Maximum retry attempts for failed URLs (default: 2)
  --timeout MS             Timeout in milliseconds for page loads (default: 30000)
  --verbose                Enable verbose logging for debugging
  --help                   Show help message and examples
```

## 📚 Step-by-Step Examples

### Complete Workflow Example
```bash
# 1. Navigate to your project directory
cd ~/Desktop

# 2. Activate virtual environment (REQUIRED)
source venv/bin/activate

# 3. Create sample data for testing
python url_screenshot_processor.py --create-sample

# 4. Process with default settings
python url_screenshot_processor.py sample_urls.xlsx

# 5. Check results
ls screenshots/              # View screenshots
open sample_urls_processed.xlsx  # View results spreadsheet
```

### Custom Processing Examples
```bash
# Fast processing for small datasets
python url_screenshot_processor.py websites.xlsx --batch-size 5

# Conservative settings for slow networks
python url_screenshot_processor.py websites.xlsx --batch-size 1 --timeout 60000

# Verbose debugging
python url_screenshot_processor.py websites.xlsx --verbose

# Custom output location
python url_screenshot_processor.py websites.xlsx --output-dir company_logos
```

## 📁 Output Structure

### Results File
Input: `websites.xlsx` → Output: `websites_processed.xlsx`

**Columns added:**
- `Original_URL`: URL as entered
- `Normalized_URL`: Cleaned URL
- `Logo_URL`: Found logo/favicon URL
- `Screenshot_Path`: Path to screenshot file
- `Status`: success/error/invalid_url
- `Error_Message`: Details if failed
- `Processing_Attempts`: Retry count

### Screenshots Directory
```
screenshots/
├── screenshot_001_1692123456.png
├── screenshot_002_1692123461.png
└── screenshot_003_1692123467.png
```

## 🐛 Troubleshooting

### Common Issues

**1. Browser not found:**
```bash
source venv/bin/activate
playwright install firefox
```

**2. Permission denied:**
```bash
chmod +x setup_and_run.sh
chmod +x url_screenshot_processor.py
```

**3. No URLs found:**
- Check URLs are in first column
- Ensure column named "URL" 
- Verify CSV/Excel format

**4. Script fails:**
```bash
# Debug mode
python url_screenshot_processor.py file.xlsx --verbose

# Conservative settings
python url_screenshot_processor.py file.xlsx --batch-size 1 --timeout 45000
```

## 📊 Performance Guidelines

**Quick Testing (< 10 URLs):**
```bash
python url_screenshot_processor.py test.csv --batch-size 3
```

**Small Projects (10-50 URLs):**
```bash
python url_screenshot_processor.py project.xlsx --batch-size 5
```

**Large Datasets (100+ URLs):**
```bash
python url_screenshot_processor.py large.xlsx --batch-size 3 --timeout 20000
```

### Expected Times
- Single URL: 3-8 seconds
- 10 URLs: 1-3 minutes  
- 50 URLs: 5-15 minutes
- 100 URLs: 10-30 minutes

## 💡 Pro Tips

1. **Always activate the virtual environment first:**
   ```bash
   source venv/bin/activate
   ```

2. **Start with sample data to test:**
   ```bash
   python url_screenshot_processor.py --create-sample
   ```

3. **Use conservative settings for first runs:**
   ```bash
   python url_screenshot_processor.py file.xlsx --batch-size 2
   ```

4. **Check the log file for detailed errors:**
   ```bash
   tail -f url_processor.log
   ```

5. **For large datasets, process in chunks:**
   - Split files into 100-200 URLs each
   - Process during off-peak hours

## 🔍 Logo Detection

The tool finds logos using multiple strategies:
1. **Logo-specific selectors**: `.logo img`, `#logo img`
2. **Header images**: `header img`, `nav img`
3. **Alt text matching**: Images with "logo" in alt/title
4. **Favicon fallback**: Site favicons as last resort

Quality filtering excludes tracking pixels and ensures reasonable image sizes.

## ⚙️ File Format Requirements

**CSV Format:**
```csv
URL
https://example1.com
https://example2.com
```

**Excel Format:** URLs in first column with "URL" header

**Supported:** `.csv`, `.xlsx`, `.xls` files

---

**Ready to start? Run the setup and create your first sample!** 🚀

```bash
./setup_and_run.sh
source venv/bin/activate  
python url_screenshot_processor.py --create-sample
python url_screenshot_processor.py sample_urls.xlsx
```


## 🖥️ GUI Version

For users who prefer a graphical interface, we now have a simple GUI version:

### Launch the GUI
```bash
# Activate virtual environment first
source venv/bin/activate

# Launch the GUI
python gui_screenshot_processor.py
```

### GUI Features
- 📁 **File Browser**: Easy file selection with drag & drop support
- ⚙️ **Visual Settings**: Adjust all parameters with sliders and checkboxes
- 📊 **Real-time Progress**: Live output log and progress indicator
- 🔄 **Process Control**: Start, stop, and monitor processing
- 📖 **Built-in Help**: Comprehensive help dialog
- 🚀 **Quick Actions**: Create sample files and open results folders

### GUI Workflow
1. **Setup**: Click "Create Sample File" for test data
2. **Select**: Use "Browse" to choose your CSV/Excel file
3. **Configure**: Adjust batch size, timeout, and other settings
4. **Process**: Click "Start Processing" and monitor progress
5. **Results**: Click "Open Results Folder" to view screenshots

The GUI provides the same functionality as the command-line version but with a user-friendly interface perfect for occasional use or users who prefer visual tools.


## 🖥️ GUI Version

For users who prefer a graphical interface, we now have a simple GUI version:

### Launch the GUI
```bash
# Activate virtual environment first
source venv/bin/activate

# Launch the GUI
python gui_screenshot_processor.py
```

### GUI Features
- 📁 **File Browser**: Easy file selection with drag & drop support
- ⚙️ **Visual Settings**: Adjust all parameters with sliders and checkboxes
- 📊 **Real-time Progress**: Live output log and progress indicator
- 🔄 **Process Control**: Start, stop, and monitor processing
- 📖 **Built-in Help**: Comprehensive help dialog
- 🚀 **Quick Actions**: Create sample files and open results folders

### GUI Workflow
1. **Setup**: Click "Create Sample File" for test data
2. **Select**: Use "Browse" to choose your CSV/Excel file
3. **Configure**: Adjust batch size, timeout, and other settings
4. **Process**: Click "Start Processing" and monitor progress
5. **Results**: Click "Open Results Folder" to view screenshots

The GUI provides the same functionality as the command-line version but with a user-friendly interface perfect for occasional use or users who prefer visual tools.

### 🚀 Easy GUI Launch

For the quickest startup, use the launcher script:

```bash
# Simple one-click launch
./launch_gui.sh
```

This script automatically:
- ✅ Checks for virtual environment
- ✅ Activates the environment
- ✅ Verifies all files are present
- ✅ Launches the GUI application

**Perfect for bookmarking or desktop shortcuts!**
