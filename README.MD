# FAST - File Arrangement and Sorting Tool

This project is developed as a personal solution to help keep the Downloads folder organized. It categorizes files and directories in the Downloads folder based on their file types and last modified dates into a structured, year-based format. Ignored files and paths are not moved and may be archived as per configuration.

## Features

- Categorizes files based on configuration rules.
- Ignores files and directories based on patterns.
- Archives directories as needed.
- Supports deduplication of files.

## Requirements

- Python 3.6 or higher

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install dependencies (if any):

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Configuration

The repository includes a sample `categories.conf` file. The file specifies categories and ignore/archival rules:

```
# Category format: FolderName: extension1, extension2, ...
Documents: pdf, docx, txt
Images: jpg, jpeg, png

# Ignore file types
ignore: tmp, log

# Ignore specific paths
ignore_path: /path/to/ignore

# Archive specific directories
archive_dir: OldDownloads
```

Feel free to modify the `categories.conf` file to suit your needs.

### Running the Script

```bash
python organize_downloads.py --path /path/to/downloads
```

### Additional Options

- **Test mode**: Use `-t` or `--test` to run in test mode without actually moving files:

  ```bash
  python organize_downloads.py --path /path/to/downloads --test
  ```

- **Simulate mode**: Use `-s` or `--simulate` to simulate and visualize the changes:

  ```bash
  python organize_downloads.py --path /path/to/downloads --simulate
  ```

- **Simulate to file**: Specify a base name for the simulation output file (timestamp will be added):

  ```bash
  python organize_downloads.py --path /path/to/downloads --simulate --simulate_file simulate_output
  ```

- **Logging**: Log the process to a file with the given base name (timestamp will be added):

  ```bash
  python organize_downloads.py --path /path/to/downloads --log_file log_output
  ```

- **Deduplication (prompt)**: Prompt before handling duplicate files:

  ```bash
  python organize_downloads.py --path /path/to/downloads --dedup
  ```

- **Deduplication (force)**: Automatically keep the most recent file (dangerous option):

  ```bash
  python organize_downloads.py --path /path/to/downloads --dedup-force
  ```

## Example

To organize files in the Downloads folder in test mode with logging:

```bash
python organize_downloads.py --path ~/Downloads --test --log_file organize_downloads_log
```

## License

This project is licensed under the terms of the MIT license.