import os
import shutil
import logging
import argparse
from datetime import datetime

def setup_logging(log_file=None):
    """Setup logging configuration."""
    handlers = [logging.StreamHandler()]
    
    if log_file:
        log_filename = f"{log_file}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        handlers.append(logging.FileHandler(log_filename))
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

def log(message, level='info'):
    """Log a message with the given level."""
    log_function = getattr(logging, level.lower(), logging.info)
    log_function(message)

def parse_config(config_file):
    """Parse the categories configuration file."""
    categories = {}
    ignore_paths = []
    with open(config_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                if ':' in line:
                    folder, extensions = line.split(':')
                    folder = folder.strip()
                    extensions = [ext.strip() for ext in extensions.split(',')]
                    if folder.lower() == "ignore":
                        ignore_paths.extend(extensions)
                    else:
                        categories[folder] = extensions
    log(f"Parsed categories: {categories}")
    log(f"Parsed ignore paths: {ignore_paths}")
    return categories, ignore_paths

def should_ignore(path, ignore_paths):
    """Check if the file path should be ignored."""
    for ignore in ignore_paths:
        if ignore in path:
            log(f"File {path} ignored due to pattern: {ignore}", level='warning')
            return True
    return False

def get_year_of_last_modified(file_path):
    """Get the year of the last modified date of the file."""
    last_modified_time = os.path.getmtime(file_path)
    year = datetime.fromtimestamp(last_modified_time).year
    log(f"File {file_path} last modified in year: {year}")
    return year

def organize_files(base_dir, categories, ignore_paths, test_mode=False):
    """Organize files into specified categories by year."""
    for root, _, files in os.walk(base_dir):
        for file in files:
            file_ext = file.split('.')[-1].lower()
            file_path = os.path.join(root, file)

            if should_ignore(file_path, ignore_paths):
                continue

            year = get_year_of_last_modified(file_path)

            for folder, extensions in categories.items():
                if file_ext in extensions:
                    dest_dir = os.path.join(base_dir, str(year), folder)
                    if not os.path.exists(dest_dir):
                        log(f"Creating directory: {dest_dir}")
                        if not test_mode:
                            os.makedirs(dest_dir)

                    dest_file_path = os.path.join(dest_dir, file)
                    log(f"Moving {file_path} to {dest_file_path}")
                    if not test_mode:
                        shutil.move(file_path, dest_file_path)
                    break

def main():
    parser = argparse.ArgumentParser(description="Organize files by year and category.")
    parser.add_argument("--path", "-p", required=True, help="Full path to the directory to organize")
    parser.add_argument("--test", "-t", action="store_true", help="Run in test mode without moving files")
    parser.add_argument("--log_file", "-l", help="Log to a file with the given base name (timestamp will be added)")
    args = parser.parse_args()

    BASE_DIR = os.path.expanduser(args.path)
    CONFIG_FILE = "categories.conf"
    LOG_FILE_BASE = args.log_file

    setup_logging(LOG_FILE_BASE)

    log(f"Starting file organization process for directory: {BASE_DIR}")
    test_mode = args.test

    if test_mode:
        log("Running in test mode")

    categories, ignore_paths = parse_config(CONFIG_FILE)
    organize_files(BASE_DIR, categories, ignore_paths, test_mode)

    log("File organization process completed")

if __name__ == "__main__":
    main()
