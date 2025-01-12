import os
import shutil
import logging
import argparse
from datetime import datetime
from collections import defaultdict
import fnmatch

def setup_logging(log_file=None):
    """Setup logging configuration."""
    handlers = [logging.StreamHandler()]
    
    if log_file:
        log_filename = f"{log_file}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        handlers.append(logging.FileHandler(log_filename))
    
    logging.basicConfig(
        level=logging.DEBUG,  # Set to DEBUG for detailed logging
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

def log(message, level='info'):
    """Log a message with the given level."""
    log_function = getattr(logging, level.lower(), logging.info)
    log_function(message)

def parse_config(config_file, base_dir):
    """Parse the categories configuration file."""
    categories = {}
    ignore_patterns = []
    ignore_paths = []
    archive_dirs = []
    with open(config_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                if ':' in line:
                    folder, extensions = line.split(':')
                    folder = folder.strip()
                    extensions = [ext.strip() for ext in extensions.split(',')]
                    if folder.lower() == "ignore":
                        ignore_patterns.extend(extensions)
                    elif folder.lower() == "ignore_path":
                        ignore_paths.extend([os.path.abspath(os.path.join(base_dir, ignore_path.strip())) for ignore_path in extensions])
                    elif folder.lower() == "archive_dir":
                        archive_dirs.extend(extensions)
                    else:
                        categories[folder] = extensions
    log(f"Parsed categories: {categories}", level='debug')
    log(f"Parsed ignore patterns: {ignore_patterns}", level='debug')
    log(f"Parsed ignore paths: {ignore_paths}", level='debug')
    log(f"Parsed archive directories: {archive_dirs}", level='debug')
    return categories, ignore_patterns, ignore_paths, archive_dirs

def should_ignore(path, ignore_patterns):
    """Check if the file or directory path should be ignored."""
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(os.path.basename(path), pattern):
            log(f"File or directory {path} ignored due to pattern: {pattern}", level='warning')
            return True
    return False

def is_in_ignore_path(path, ignore_paths):
    """Check if the file or directory path is within an ignore path."""
    for ignore_path in ignore_paths:
        if os.path.commonpath([os.path.abspath(path), ignore_path]) == ignore_path or fnmatch.fnmatch(path, f"*{ignore_path}*"):
            log(f"File or directory {path} ignored due to being in ignore path: {ignore_path}", level='warning')
            return True
    return False

def get_year_of_last_modified(file_path):
    """Get the year of the last modified date of the file."""
    last_modified_time = os.path.getmtime(file_path)
    year = int(datetime.fromtimestamp(last_modified_time).year)
    log(f"File {file_path} last modified in year: {year}", level='debug')
    return year

def get_last_modified_time(file_path):
    """Get the last modified time of the file."""
    return os.path.getmtime(file_path)

def should_archive_directory(path, archive_dirs):
    """Check if the directory should be archived as a whole."""
    return any(fnmatch.fnmatch(path, f"*{dir_name}*") for dir_name in archive_dirs)

def list_files_and_dirs(base_dir):
    """List files and directories at the given path without recursion."""
    files = []
    dirs = []
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path):
            dirs.append(item_path)
        else:
            files.append(item_path)
    log(f"Listed files: {files}", level='debug')
    log(f"Listed directories: {dirs}", level='debug')
    return files, dirs

def handle_ignore_paths(base_dir, ignore_patterns, ignore_paths):
    """Handle files and directories recursively in ignore paths."""
    handled_paths = []
    for root, dirs, files in os.walk(base_dir):
        if should_ignore(root, ignore_patterns) or is_in_ignore_path(root, ignore_paths):
            for file in files:
                handled_paths.append(os.path.join(root, file))
            for directory in dirs:
                handled_paths.append(os.path.join(root, directory))
    log(f"Handled ignore paths: {handled_paths}", level='debug')
    return handled_paths

def simulate_file_structure(base_dir, categories, ignore_patterns, ignore_paths, archive_dirs, dedup_mode=None):
    """Simulate the file structure changes."""
    simulated_structure = defaultdict(lambda: defaultdict(list))
    files, dirs = list_files_and_dirs(base_dir)

    for file_path in files:
        if should_ignore(file_path, ignore_patterns) or is_in_ignore_path(file_path, ignore_paths):
            continue

        file_ext = os.path.splitext(file_path)[1].lower().lstrip('.')
        year = get_year_of_last_modified(file_path)

        for folder, extensions in categories.items():
            if file_ext in extensions:
                dest_dir = os.path.join(base_dir, str(year), folder)
                if dedup_mode:
                    simulate_deduplication(file_path, dest_dir, simulated_structure, dedup_mode)
                else:
                    simulated_structure[year][folder].append(file_path)
                break

    for dir_path in dirs:
        if should_ignore(dir_path, ignore_patterns) or is_in_ignore_path(dir_path, ignore_paths):
            continue

        if should_archive_directory(dir_path, archive_dirs):
            year = get_year_of_last_modified(dir_path)
            relative_dir_path = os.path.relpath(dir_path, base_dir)
            dest_dir = os.path.join(base_dir, str(year), "archive_dir", relative_dir_path)
            simulated_structure[year]["archive_dir"].append(dest_dir)

    handled_ignore_paths = handle_ignore_paths(base_dir, ignore_patterns, ignore_paths)
    for path in handled_ignore_paths:
        year = get_year_of_last_modified(path)
        if os.path.isdir(path):
            simulated_structure[year]["archive_dir"].append(path)
        else:
            file_ext = os.path.splitext(path)[1].lower().lstrip('.')
            for folder, extensions in categories.items():
                if file_ext in extensions:
                    dest_dir = os.path.join(base_dir, str(year), folder)
                    if dedup_mode:
                        simulate_deduplication(path, dest_dir, simulated_structure, dedup_mode)
                    else:
                        simulated_structure[year][folder].append(path)
                    break

    return simulated_structure

def simulate_deduplication(file_path, dest_dir, simulated_structure, dedup_mode):
    """Simulate deduplication of files."""
    file_name = os.path.basename(file_path)
    year = os.path.basename(os.path.dirname(dest_dir))
    folder = os.path.basename(dest_dir)
    
    if dedup_mode == "force":
        for existing_file in simulated_structure[int(year)][folder]:
            if os.path.basename(existing_file) == file_name:
                log(f"[SIMULATE] --dedup-force: Keeping most recent {file_name} in {dest_dir}", level='info')
                return
        simulated_structure[int(year)][folder].append(file_path)

    elif dedup_mode == "prompt":
        for existing_file in simulated_structure[int(year)][folder]:
            if os.path.basename(existing_file) == file_name:
                while True:
                    choice = input(f"[SIMULATE] File {file_name} in {dest_dir} already exists. Full path: {existing_file}. Do you want to (y) keep the most recent, (k) keep both, or (d) delete duplicates? ")
                    log(f"Duplicate handling choice for {file_path}: {choice}", level='debug')
                    if choice.lower() in ["y", "yes"]:
                        log(f"[SIMULATE] Keeping most recent {file_name} in {dest_dir}", level='info')
                        return
                    elif choice.lower() in ["k", "keep"]:
                        new_file_name = f"{os.path.splitext(file_name)[0]}_dup{os.path.splitext(file_name)[1]}"
                        log(f"[SIMULATE] Keeping both files: {file_name} and {new_file_name}", level='info')
                        simulated_structure[int(year)][folder].append(os.path.join(dest_dir, new_file_name))
                        return
                    elif choice.lower() in ["d", "delete"]:
                        log(f"[SIMULATE] Deleting duplicate {file_path}", level='info')
                        os.remove(file_path)
                        return
                    else:
                        print("Invalid choice, please type 'y' to keep the most recent, 'k' to keep both, or 'd' to delete duplicates.")
        simulated_structure[int(year)][folder].append(file_path)

def print_simulated_structure(base_dir, simulated_structure, simulate_file=None):
    """Print the simulated directory structure."""
    if simulate_file:
        with open(simulate_file, 'w') as f:
            f.write(f"{base_dir}\n")
            for year, folders in sorted(simulated_structure.items(), reverse=True):
                f.write(f"|-- {year}\n")
                for folder, paths in folders.items():
                    f.write(f"|   |-- {folder}\n")
                    for path in sorted(paths):
                        if folder == "archive_dir":
                            f.write(f"|   |   |-- {os.path.relpath(path, os.path.join(base_dir, str(year), 'archive_dir'))}\n")
                        else:
                            f.write(f"|   |   |-- {os.path.basename(path)}\n")
    else:
        print(base_dir)
        for year, folders in sorted(simulated_structure.items(), reverse=True):
            print(f"|-- {year}")
            for folder, paths in folders.items():
                print(f"|   |-- {folder}")
                for path in sorted(paths):
                    if folder == "archive_dir":
                        print(f"|   |   |-- {os.path.relpath(path, os.path.join(base_dir, str(year), 'archive_dir'))}")
                    else:
                        print(f"|   |   |-- {os.path.basename(path)}")

def deduplicate_files(file_path, dest_file_path, dedup_mode, test_mode=False):
    """Handle deduplication of files."""
    if dedup_mode == "force":
        if os.path.exists(dest_file_path):
            existing_file_mtime = get_last_modified_time(dest_file_path)
            new_file_mtime = get_last_modified_time(file_path)
            if new_file_mtime > existing_file_mtime:
                log(f"Replacing {dest_file_path} with newer file {file_path}", level='info')
                if not test_mode:
                    os.remove(dest_file_path)
                    shutil.move(file_path, dest_file_path)
            else:
                log(f"Keeping existing file {dest_file_path}, newer file found", level='info')
                if not test_mode:
                    os.remove(file_path)
        else:
            if not test_mode:
                shutil.move(file_path, dest_file_path)

    elif dedup_mode == "prompt":
        if os.path.exists(dest_file_path):
            while True:
                choice = input(f"File {dest_file_path} already exists. Do you want to (y) keep the most recent, (k) keep both, or (d) delete duplicates? ")
                log(f"Duplicate handling choice for {file_path}: {choice}", level='debug')
                if choice.lower() in ["y", "yes"]:
                    existing_file_mtime = get_last_modified_time(dest_file_path)
                    new_file_mtime = get_last_modified_time(file_path)
                    if new_file_mtime > existing_file_mtime:
                        log(f"Replacing {dest_file_path} with newer file {file_path}", level='info')
                        if not test_mode:
                            os.remove(dest_file_path)
                            shutil.move(file_path, dest_file_path)
                    else:
                        log(f"Keeping existing file {dest_file_path}, newer file found", level='info')
                        if not test_mode:
                            os.remove(file_path)
                    break
                elif choice.lower() in ["k", "keep"]:
                    new_file_name = f"{os.path.splitext(dest_file_path)[0]}_dup{os.path.splitext(dest_file_path)[1]}"
                    log(f"Keeping both files. Moving {file_path} to {new_file_name}", level='info')
                    if not test_mode:
                        shutil.move(file_path, new_file_name)
                    break
                elif choice.lower() in ["d", "delete"]:
                    log(f"Deleting duplicate {file_path}", level='info')
                    if not test_mode:
                        os.remove(file_path)
                    break
                else:
                    print("Invalid choice, please type 'y' to keep the most recent, 'k' to keep both, or 'd' to delete duplicates.")

    else:
        if not test_mode:
            shutil.move(file_path, dest_file_path)

def organize_files(base_dir, categories, ignore_patterns, ignore_paths, archive_dirs, test_mode=False, dedup_mode=None):
    """Organize files into specified categories by year."""
    files, dirs = list_files_and_dirs(base_dir)

    for file_path in files:
        if should_ignore(file_path, ignore_patterns) or is_in_ignore_path(file_path, ignore_paths):
            continue

        file_ext = os.path.splitext(file_path)[1].lower().lstrip('.')
        year = get_year_of_last_modified(file_path)

        for folder, extensions in categories.items():
            if file_ext in extensions:
                dest_dir = os.path.join(base_dir, str(year), folder)
                if not os.path.exists(dest_dir):
                    log(f"Creating directory: {dest_dir}", level='info')
                    if not test_mode:
                        os.makedirs(dest_dir)

                dest_file_path = os.path.join(dest_dir, os.path.basename(file_path))
                if dedup_mode:
                    deduplicate_files(file_path, dest_file_path, dedup_mode, test_mode)
                else:
                    log(f"Moving {file_path} to {dest_file_path}", level='info')
                    if not test_mode:
                        shutil.move(file_path, dest_file_path)
                break

    for dir_path in dirs:
        if should_ignore(dir_path, ignore_patterns) or is_in_ignore_path(dir_path, ignore_paths):
            continue

        if should_archive_directory(dir_path, archive_dirs):
            year = get_year_of_last_modified(dir_path)
            relative_dir_path = os.path.relpath(dir_path, base_dir)
            dest_dir = os.path.join(base_dir, str(year), "archive_dir", relative_dir_path)
            log(f"Moving directory {dir_path} to {dest_dir}", level='info')
            if not test_mode:
                shutil.move(dir_path, dest_dir)

    handled_ignore_paths = handle_ignore_paths(base_dir, ignore_patterns, ignore_paths)
    for path in handled_ignore_paths:
        year = get_year_of_last_modified(path)
        if os.path.isdir(path):
            relative_dir_path = os.path.relpath(path, base_dir)
            dest_dir = os.path.join(base_dir, str(year), "archive_dir", relative_dir_path)
            log(f"Moving ignored directory {path} to {dest_dir}", level='info')
            if not test_mode:
                shutil.move(path, dest_dir)
        else:
            file_ext = os.path.splitext(path)[1].lower().lstrip('.')
            for folder, extensions in categories.items():
                if file_ext in extensions:
                    dest_dir = os.path.join(base_dir, str(year), folder)
                    if not os.path.exists(dest_dir):
                        log(f"Creating directory: {dest_dir}", level='info')
                        if not test_mode:
                            os.makedirs(dest_dir)

                    dest_file_path = os.path.join(dest_dir, os.path.basename(path))
                    if dedup_mode:
                        deduplicate_files(path, dest_file_path, dedup_mode, test_mode)
                    else:
                        log(f"Moving {path} to {dest_file_path}", level='info')
                        if not test_mode:
                            shutil.move(path, dest_file_path)
                    break

def main():
    parser = argparse.ArgumentParser(description="Organize files by year and category.")
    parser.add_argument("--path", "-p", required=True, help="Full path to the directory to organize")
    parser.add_argument("--test", "-t", action="store_true", help="Run in test mode without moving files")
    parser.add_argument("--simulate", "-s", action="store_true", help="Simulate and visualize the changes")
    parser.add_argument("--simulate_file", help="Output the simulation to a file with the given base name (timestamp will be added)")
    parser.add_argument("--log_file", "-l", help="Log to a file with the given base name (timestamp will be added)")
    parser.add_argument("--dedup", action="store_true", help="Prompt before handling duplicate files")
    parser.add_argument("--dedup-force", action="store_true", help="Automatically keep the most recent file, dangerous option")
    args = parser.parse_args()

    BASE_DIR = os.path.expanduser(args.path)
    CONFIG_FILE = "categories.conf"
    LOG_FILE_BASE = args.log_file
    SIMULATE_FILE_BASE = args.simulate_file

    setup_logging(LOG_FILE_BASE)

    log(f"Starting file organization process for directory: {BASE_DIR}")
    test_mode = args.test
    simulate_mode = args.simulate

    dedup_mode = None
    if args.dedup_force:
        log("WARNING: --dedup-force is enabled. This will automatically keep the most recent file.", level='warning')
        confirmation = input("Are you sure you want to continue? Type 'YES' to proceed: ")
        if confirmation != 'YES':
            log("Operation cancelled by user.", level='info')
            return
        dedup_mode = "force"
    elif args.dedup:
        dedup_mode = "prompt"

    if test_mode:
        log("Running in test mode", level='info')

    categories, ignore_patterns, ignore_paths, archive_dirs = parse_config(CONFIG_FILE, BASE_DIR)

    if simulate_mode:
        log("Simulating file organization", level='info')
        simulated_structure = simulate_file_structure(BASE_DIR, categories, ignore_patterns, ignore_paths, archive_dirs, dedup_mode)
        if SIMULATE_FILE_BASE:
            simulate_file_path = f"{SIMULATE_FILE_BASE}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            print_simulated_structure(BASE_DIR, simulated_structure, simulate_file_path)
            log(f"Simulation output saved to {simulate_file_path}", level='info')
        else:
            print_simulated_structure(BASE_DIR, simulated_structure)
    else:
        organize_files(BASE_DIR, categories, ignore_patterns, ignore_paths, archive_dirs, test_mode, dedup_mode)

    log("File organization process completed", level='info')

if __name__ == "__main__":
    main()
