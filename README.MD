# FAST - File Arrangement and Sorting Tool

This project is developed as a personal solution to help keep the Downloads folder organized. It categorizes files and directories in the Downloads folder based on their file types and last modified dates into a structured, year-based format. Ignored files and paths are not moved and may be archived as per configuration.

## ✨ Two Ways to Use FAST

### 🎨 **NEW: Interactive TUI (Recommended)**
A beautiful, wizard-style terminal interface that guides you through file organization with:
- Interactive menus and navigation
- Live preview of changes before execution
- Visual tree structure display
- Statistics and analytics
- Configuration management UI
- No command-line arguments needed!

### 📟 **Classic CLI**
Traditional command-line interface for automation and scripting

## Features

### Core Features
- ✅ Categorizes files based on configuration rules
- ✅ Organizes files by year (based on modification date)
- ✅ Ignores files and directories based on patterns
- ✅ Archives directories as needed
- ✅ Supports intelligent deduplication of files
- ✅ Preview mode to see changes before execution
- ✅ Detailed logging and statistics

### TUI-Specific Features
- 🎯 **Interactive Wizard**: Step-by-step guidance through organization process
- 👁️ **Live Preview**: Visual tree structure of proposed changes
- 📊 **Statistics Dashboard**: File distribution by type, year, and size
- ⚙️ **Configuration Manager**: Edit categories and rules through UI
- 🎨 **Beautiful Interface**: Color-coded, easy-to-read terminal UI
- ⌨️ **Keyboard Navigation**: Full keyboard support with arrow keys
- 🔍 **Directory Browser**: Interactive directory selection
- 📁 **Category Manager**: Add, edit, or delete categories visually

## Requirements

- Python 3.6 or higher
- Dependencies (see requirements.txt)

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 🎨 Interactive TUI Mode (Recommended for Beginners)

Simply run the TUI wizard:

```bash
python fast_tui.py
```

Or make it executable and run directly:

```bash
chmod +x fast_tui.py
./fast_tui.py
```

**Features:**
- Navigate with arrow keys
- Select options with Enter
- Cancel with Ctrl+C
- Follow the wizard for step-by-step guidance

**Main Menu Options:**
1. **🚀 Organize Files** - Interactive wizard for file organization
2. **👁️ Preview Organization** - See changes without executing
3. **⚙️ View/Edit Configuration** - Manage your settings
4. **📁 Manage Categories** - Add/edit/delete file categories
5. **📊 View Statistics** - Analyze directory contents
6. **❓ Help** - Detailed help and documentation

### 📟 Classic CLI Mode

For automation, scripting, or advanced users:

```bash
python fast.py --path /path/to/downloads
```

#### CLI Options

- **Test mode**: Use `-t` or `--test` to run in test mode without actually moving files:

  ```bash
  python fast.py --path /path/to/downloads --test
  ```

- **Simulate mode**: Use `-s` or `--simulate` to simulate and visualize the changes:

  ```bash
  python fast.py --path /path/to/downloads --simulate
  ```

- **Simulate to file**: Specify a base name for the simulation output file (timestamp will be added):

  ```bash
  python fast.py --path /path/to/downloads --simulate --simulate_file simulate_output
  ```

- **Logging**: Log the process to a file with the given base name (timestamp will be added):

  ```bash
  python fast.py --path /path/to/downloads --log_file log_output
  ```

- **Deduplication (prompt)**: Prompt before handling duplicate files:

  ```bash
  python fast.py --path /path/to/downloads --dedup
  ```

- **Deduplication (force)**: Automatically keep the most recent file (dangerous option):

  ```bash
  python fast.py --path /path/to/downloads --dedup-force
  ```

#### CLI Example

To organize files in the Downloads folder in test mode with logging:

```bash
python fast.py --path ~/Downloads --test --log_file organize_downloads_log
```

## Configuration

The `categories.conf` file specifies categories and ignore/archival rules:

```
# Category format: FolderName: extension1, extension2, ...
archive_documents: pdf, docx, txt, odf, xls, xlsx, ppt, pptx
archive_pictures: png, jpeg, jpg, gif, bmp, svg, webp
archive_videos: mp4, avi, mkv, mov, flv, wmv, webm
archive_music: mp3, wav, flac, aac, ogg, m4a

# Ignore file types (won't be organized)
ignore: tmp, log, cache

# Ignore specific paths (won't be organized)
ignore_path: path1, path2

# Archive specific directories as a whole
archive_dir: OldDownloads
```

**Configuration Tips:**
- Categories are organized as `Year/CategoryName/files`
- Use the TUI's Category Manager for easy editing
- You can have multiple configuration files and switch between them

## How It Works

1. **Scan**: FAST scans the target directory for files and directories
2. **Categorize**: Files are categorized based on their extension
3. **Year Assignment**: Each file is assigned to a year based on modification date
4. **Preview** (optional): See the proposed structure before changes
5. **Execute**: Files are moved to `Year/Category/filename` structure

**Example Structure:**
```
Downloads/
├── 2024/
│   ├── archive_documents/
│   │   ├── report.pdf
│   │   └── presentation.pptx
│   ├── archive_pictures/
│   │   ├── photo1.jpg
│   │   └── photo2.png
│   └── archive_videos/
│       └── video.mp4
└── 2023/
    ├── archive_documents/
    │   └── old_doc.pdf
    └── archive_music/
        └── song.mp3
```

## Screenshots & Examples

### TUI Main Menu
```
╔═══════════════════════════════════════════════════════════════╗
║   ███████╗ █████╗ ███████╗████████╗    ████████╗██╗   ██╗██╗ ║
║   ██╔════╝██╔══██╗██╔════╝╚══██╔══╝    ╚══██╔══╝██║   ██║██║ ║
║   █████╗  ███████║███████╗   ██║          ██║   ██║   ██║██║ ║
║   ██╔══╝  ██╔══██║╚════██║   ██║          ██║   ██║   ██║██║ ║
║   ██║     ██║  ██║███████║   ██║          ██║   ╚██████╔╝██║ ║
║   ╚═╝     ╚═╝  ╚═╝╚══════╝   ╚═╝          ╚═╝    ╚═════╝ ╚═╝ ║
╚═══════════════════════════════════════════════════════════════╝
```

## Tips & Best Practices

1. **Always Preview First**: Use preview mode or test mode before actual execution
2. **Backup Important Data**: Make backups before organizing critical files
3. **Start Small**: Test on a small directory first
4. **Check Logs**: Review log files after organization
5. **Customize Categories**: Tailor categories to your workflow
6. **Use Test Mode**: Run with `--test` flag to verify behavior

## Troubleshooting

**Issue**: Files not being categorized
- **Solution**: Check if file extension is in `categories.conf`

**Issue**: Files being ignored unexpectedly
- **Solution**: Review `ignore` and `ignore_path` patterns in config

**Issue**: Dependencies not found
- **Solution**: Run `pip install -r requirements.txt`

**Issue**: Permission errors
- **Solution**: Ensure you have write permissions on target directory

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## Roadmap

- [ ] Watch mode for automatic organization
- [ ] Multiple configuration profiles
- [ ] Cloud storage integration
- [ ] Advanced filtering rules
- [ ] Undo functionality
- [ ] GUI version

## License

This project is licensed under the terms of the MIT license.