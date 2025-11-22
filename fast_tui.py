#!/usr/bin/env python3
"""
FAST TUI - File Arrangement and Sorting Tool (Terminal User Interface)
Interactive wizard for organizing files by category and year
"""

import os
import sys
import shutil
from datetime import datetime
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Confirm, Prompt
from rich.layout import Layout
from rich.live import Live
from rich import box
from rich.text import Text
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

# Import core functions from original fast.py
from fast import (
    parse_config, should_ignore, is_in_ignore_path,
    get_year_of_last_modified, should_archive_directory,
    list_files_and_dirs, organize_files, simulate_file_structure,
    setup_logging, log, get_last_modified_time
)

console = Console()


class FASTWizard:
    """Interactive TUI wizard for FAST file organization"""

    def __init__(self):
        self.config_file = "categories.conf"
        self.base_dir = None
        self.categories = {}
        self.ignore_patterns = []
        self.ignore_paths = []
        self.archive_dirs = []

    def show_banner(self):
        """Display welcome banner"""
        banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ███████╗ █████╗ ███████╗████████╗    ████████╗██╗   ██╗██╗ ║
║   ██╔════╝██╔══██╗██╔════╝╚══██╔══╝    ╚══██╔══╝██║   ██║██║ ║
║   █████╗  ███████║███████╗   ██║          ██║   ██║   ██║██║ ║
║   ██╔══╝  ██╔══██║╚════██║   ██║          ██║   ██║   ██║██║ ║
║   ██║     ██║  ██║███████║   ██║          ██║   ╚██████╔╝██║ ║
║   ╚═╝     ╚═╝  ╚═╝╚══════╝   ╚═╝          ╚═╝    ╚═════╝ ╚═╝ ║
║                                                               ║
║        File Arrangement and Sorting Tool - Interactive        ║
║                    Organize Files by Year & Type              ║
╚═══════════════════════════════════════════════════════════════╝
        """
        console.print(banner, style="bold cyan")
        console.print("Welcome to FAST TUI - Your intelligent file organization wizard\n",
                     style="bold white", justify="center")

    def main_menu(self):
        """Display and handle main menu"""
        while True:
            console.clear()
            self.show_banner()

            choices = [
                Choice(value="organize", name="🚀 Organize Files (Wizard Mode)"),
                Choice(value="preview", name="👁️  Preview Organization"),
                Choice(value="config", name="⚙️  View/Edit Configuration"),
                Choice(value="categories", name="📁 Manage Categories"),
                Choice(value="stats", name="📊 View Directory Statistics"),
                Separator(),
                Choice(value="help", name="❓ Help & Documentation"),
                Choice(value="exit", name="🚪 Exit")
            ]

            action = inquirer.select(
                message="What would you like to do?",
                choices=choices,
                default="organize",
                pointer="→",
                style={
                    'pointer': 'cyan bold',
                    'highlighted': 'cyan bold',
                }
            ).execute()

            if action == "organize":
                self.organize_wizard()
            elif action == "preview":
                self.preview_organization()
            elif action == "config":
                self.view_edit_config()
            elif action == "categories":
                self.manage_categories()
            elif action == "stats":
                self.show_statistics()
            elif action == "help":
                self.show_help()
            elif action == "exit":
                if Confirm.ask("\n[yellow]Are you sure you want to exit?[/yellow]", default=False):
                    console.print("\n[cyan]Thanks for using FAST TUI! Goodbye! 👋[/cyan]\n")
                    sys.exit(0)

    def organize_wizard(self):
        """Interactive wizard for organizing files"""
        console.clear()
        console.print(Panel.fit(
            "[bold cyan]File Organization Wizard[/bold cyan]\n\n"
            "This wizard will guide you through organizing your files.\n"
            "Files will be sorted by year and category.",
            border_style="cyan"
        ))

        # Step 1: Select directory
        self.base_dir = self.select_directory()
        if not self.base_dir:
            return

        # Step 2: Load configuration
        if not self.load_configuration():
            return

        # Step 3: Choose operation mode
        mode = self.select_operation_mode()
        if not mode:
            return

        # Step 4: Preview changes
        if not self.show_preview_confirmation():
            return

        # Step 5: Execute organization
        self.execute_organization(mode)

    def select_directory(self) -> Optional[str]:
        """Interactive directory selection"""
        console.print("\n[bold]Step 1: Select Directory[/bold]", style="cyan")
        console.print("Choose the directory you want to organize\n")

        # Provide common options
        home = str(Path.home())
        downloads = os.path.join(home, "Downloads")
        documents = os.path.join(home, "Documents")

        choices = []
        if os.path.exists(downloads):
            choices.append(Choice(value=downloads, name=f"📥 Downloads ({downloads})"))
        if os.path.exists(documents):
            choices.append(Choice(value=documents, name=f"📄 Documents ({documents})"))

        choices.extend([
            Choice(value=home, name=f"🏠 Home ({home})"),
            Choice(value="current", name=f"📂 Current Directory ({os.getcwd()})"),
            Choice(value="custom", name="✏️  Enter Custom Path"),
            Separator(),
            Choice(value="cancel", name="❌ Cancel")
        ])

        selection = inquirer.select(
            message="Select target directory:",
            choices=choices,
            pointer="→",
        ).execute()

        if selection == "cancel":
            return None
        elif selection == "custom":
            path = inquirer.filepath(
                message="Enter directory path:",
                default=home,
                validate=lambda x: os.path.isdir(x) if x else False,
                invalid_message="Please enter a valid directory path",
            ).execute()
            return path
        elif selection == "current":
            return os.getcwd()
        else:
            return selection

    def load_configuration(self) -> bool:
        """Load configuration file"""
        console.print(f"\n[bold]Step 2: Load Configuration[/bold]", style="cyan")

        if not os.path.exists(self.config_file):
            console.print(f"[yellow]Configuration file '{self.config_file}' not found.[/yellow]")
            if Confirm.ask("Would you like to create a default configuration?", default=True):
                self.create_default_config()
            else:
                return False

        try:
            self.categories, self.ignore_patterns, self.ignore_paths, self.archive_dirs = \
                parse_config(self.config_file, self.base_dir)

            console.print(f"[green]✓[/green] Configuration loaded successfully")
            console.print(f"  • Categories: {len(self.categories)}")
            console.print(f"  • Ignore patterns: {len(self.ignore_patterns)}")
            console.print(f"  • Archive directories: {len(self.archive_dirs)}\n")

            return True
        except Exception as e:
            console.print(f"[red]Error loading configuration: {e}[/red]")
            return False

    def select_operation_mode(self) -> Optional[str]:
        """Select operation mode"""
        console.print("\n[bold]Step 3: Operation Mode[/bold]", style="cyan")

        choices = [
            Choice(value="execute", name="⚡ Execute - Organize files immediately"),
            Choice(value="test", name="🧪 Test Mode - Simulate without moving files"),
            Choice(value="dedup", name="🔍 Dedup Prompt - Handle duplicates interactively"),
            Choice(value="dedup_force", name="⚠️  Dedup Force - Auto-keep most recent (dangerous)"),
            Separator(),
            Choice(value="cancel", name="❌ Cancel")
        ]

        mode = inquirer.select(
            message="Select operation mode:",
            choices=choices,
            pointer="→",
        ).execute()

        if mode == "cancel":
            return None

        if mode == "dedup_force":
            console.print("\n[bold red]⚠️  WARNING: Dedup Force Mode[/bold red]")
            console.print("This will automatically keep the most recent file and delete older duplicates.")
            if not Confirm.ask("[yellow]Are you ABSOLUTELY sure?[/yellow]", default=False):
                return None

        return mode

    def show_preview_confirmation(self) -> bool:
        """Show preview and get confirmation"""
        console.print("\n[bold]Step 4: Preview Changes[/bold]", style="cyan")
        console.print("Analyzing directory structure...\n")

        # Generate preview
        with console.status("[bold green]Analyzing files..."):
            simulated_structure = simulate_file_structure(
                self.base_dir,
                self.categories,
                self.ignore_patterns,
                self.ignore_paths,
                self.archive_dirs
            )

        # Display preview tree
        self.display_tree_preview(simulated_structure)

        # Show statistics
        self.display_preview_stats(simulated_structure)

        return Confirm.ask("\n[bold]Proceed with organization?[/bold]", default=True)

    def display_tree_preview(self, simulated_structure: Dict):
        """Display tree preview of changes"""
        tree = Tree(f"[bold cyan]📁 {self.base_dir}[/bold cyan]", guide_style="cyan")

        for year in sorted(simulated_structure.keys(), reverse=True):
            year_node = tree.add(f"[yellow]📅 {year}[/yellow]")

            for folder, files in sorted(simulated_structure[year].items()):
                folder_node = year_node.add(f"[blue]📂 {folder}[/blue] ({len(files)} files)")

                # Show first 5 files as sample
                for file_path in sorted(files)[:5]:
                    file_name = os.path.basename(file_path)
                    folder_node.add(f"[dim]📄 {file_name}[/dim]")

                if len(files) > 5:
                    folder_node.add(f"[dim]... and {len(files) - 5} more files[/dim]")

        console.print(Panel(tree, title="[bold]Preview: Proposed Structure[/bold]", border_style="cyan"))

    def display_preview_stats(self, simulated_structure: Dict):
        """Display statistics about the preview"""
        table = Table(title="Statistics", box=box.ROUNDED, border_style="cyan")
        table.add_column("Category", style="cyan", no_wrap=True)
        table.add_column("Files", justify="right", style="green")
        table.add_column("Years", justify="right", style="yellow")

        category_stats = defaultdict(lambda: {"count": 0, "years": set()})

        for year, folders in simulated_structure.items():
            for folder, files in folders.items():
                category_stats[folder]["count"] += len(files)
                category_stats[folder]["years"].add(year)

        total_files = 0
        for category, stats in sorted(category_stats.items()):
            table.add_row(
                category,
                str(stats["count"]),
                str(len(stats["years"]))
            )
            total_files += stats["count"]

        table.add_section()
        table.add_row("[bold]TOTAL[/bold]", f"[bold]{total_files}[/bold]", "-")

        console.print(table)

    def execute_organization(self, mode: str):
        """Execute the file organization"""
        console.print("\n[bold]Step 5: Executing Organization[/bold]", style="cyan")

        test_mode = mode == "test"
        dedup_mode = None

        if mode == "dedup":
            dedup_mode = "prompt"
        elif mode == "dedup_force":
            dedup_mode = "force"

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:

                task = progress.add_task("[cyan]Organizing files...", total=100)

                # Setup logging
                log_file = f"fast_organization_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                setup_logging(log_file)

                progress.update(task, advance=20, description="[cyan]Loading configuration...")

                # Execute organization
                progress.update(task, advance=30, description="[cyan]Analyzing files...")

                organize_files(
                    self.base_dir,
                    self.categories,
                    self.ignore_patterns,
                    self.ignore_paths,
                    self.archive_dirs,
                    test_mode=test_mode,
                    dedup_mode=dedup_mode
                )

                progress.update(task, advance=50, description="[green]Completed!")

            if test_mode:
                console.print("\n[green]✓ Test completed successfully![/green]")
                console.print("[dim]No files were actually moved.[/dim]")
            else:
                console.print("\n[green]✓ Files organized successfully![/green]")

            console.print(f"[dim]Log saved to: {log_file}_*.log[/dim]")

        except Exception as e:
            console.print(f"\n[red]✗ Error during organization: {e}[/red]")

        input("\nPress Enter to continue...")

    def preview_organization(self):
        """Preview organization without executing"""
        console.clear()
        console.print(Panel.fit("[bold cyan]Preview Organization[/bold cyan]", border_style="cyan"))

        # Select directory
        self.base_dir = self.select_directory()
        if not self.base_dir:
            return

        # Load configuration
        if not self.load_configuration():
            return

        # Generate and show preview
        console.print("\n[bold green]Generating preview...[/bold green]\n")

        with console.status("[bold green]Analyzing files..."):
            simulated_structure = simulate_file_structure(
                self.base_dir,
                self.categories,
                self.ignore_patterns,
                self.ignore_paths,
                self.archive_dirs
            )

        self.display_tree_preview(simulated_structure)
        self.display_preview_stats(simulated_structure)

        # Option to save preview
        if Confirm.ask("\nWould you like to save this preview to a file?", default=False):
            filename = Prompt.ask("Enter filename", default="preview_output")
            filepath = f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

            from fast import print_simulated_structure
            print_simulated_structure(self.base_dir, simulated_structure, filepath)
            console.print(f"[green]✓ Preview saved to {filepath}[/green]")

        input("\nPress Enter to continue...")

    def view_edit_config(self):
        """View and edit configuration"""
        console.clear()
        console.print(Panel.fit("[bold cyan]Configuration Viewer[/bold cyan]", border_style="cyan"))

        if not os.path.exists(self.config_file):
            console.print(f"\n[yellow]Configuration file '{self.config_file}' not found.[/yellow]")
            if Confirm.ask("Create default configuration?", default=True):
                self.create_default_config()
            return

        # Read and display config
        with open(self.config_file, 'r') as f:
            config_content = f.read()

        console.print(Panel(config_content, title=f"[bold]{self.config_file}[/bold]", border_style="blue"))

        choices = [
            Choice(value="edit", name="✏️  Edit Configuration"),
            Choice(value="reload", name="🔄 Reload Configuration"),
            Choice(value="back", name="← Back to Main Menu")
        ]

        action = inquirer.select(
            message="What would you like to do?",
            choices=choices,
        ).execute()

        if action == "edit":
            editor = os.environ.get('EDITOR', 'nano')
            os.system(f"{editor} {self.config_file}")
            console.print("[green]✓ Configuration file updated[/green]")
        elif action == "reload":
            console.print("[green]✓ Configuration will be reloaded on next operation[/green]")

        if action != "back":
            input("\nPress Enter to continue...")

    def manage_categories(self):
        """Manage file categories"""
        console.clear()
        console.print(Panel.fit("[bold cyan]Category Manager[/bold cyan]", border_style="cyan"))

        if not os.path.exists(self.config_file):
            console.print("\n[yellow]Please create a configuration file first.[/yellow]")
            input("\nPress Enter to continue...")
            return

        # Load current categories
        categories, _, _, _ = parse_config(self.config_file, os.getcwd())

        # Display categories table
        table = Table(title="Current Categories", box=box.ROUNDED, border_style="cyan")
        table.add_column("Category", style="cyan", no_wrap=True)
        table.add_column("Extensions", style="green")
        table.add_column("Count", justify="right", style="yellow")

        for category, extensions in sorted(categories.items()):
            table.add_row(
                category,
                ", ".join(extensions[:5]) + ("..." if len(extensions) > 5 else ""),
                str(len(extensions))
            )

        console.print(table)

        choices = [
            Choice(value="add", name="➕ Add New Category"),
            Choice(value="edit", name="✏️  Edit Category"),
            Choice(value="delete", name="🗑️  Delete Category"),
            Choice(value="back", name="← Back to Main Menu")
        ]

        action = inquirer.select(
            message="What would you like to do?",
            choices=choices,
        ).execute()

        if action == "add":
            self.add_category()
        elif action == "edit":
            self.edit_category(categories)
        elif action == "delete":
            self.delete_category(categories)

        if action != "back":
            input("\nPress Enter to continue...")

    def add_category(self):
        """Add a new category"""
        console.print("\n[bold]Add New Category[/bold]", style="cyan")

        name = Prompt.ask("Category name")
        extensions = Prompt.ask("File extensions (comma-separated)")

        # Append to config file
        with open(self.config_file, 'a') as f:
            f.write(f"\n{name}: {extensions}")

        console.print(f"[green]✓ Category '{name}' added successfully[/green]")

    def edit_category(self, categories):
        """Edit existing category"""
        if not categories:
            console.print("[yellow]No categories to edit[/yellow]")
            return

        choices = [Choice(value=cat, name=f"{cat} ({len(exts)} extensions)")
                  for cat, exts in sorted(categories.items())]
        choices.append(Choice(value="cancel", name="❌ Cancel"))

        category = inquirer.select(
            message="Select category to edit:",
            choices=choices,
        ).execute()

        if category == "cancel":
            return

        current_exts = ", ".join(categories[category])
        console.print(f"\nCurrent extensions: [cyan]{current_exts}[/cyan]")

        new_extensions = Prompt.ask("New extensions (comma-separated)", default=current_exts)

        # Update config file
        self.update_config_category(category, new_extensions)
        console.print(f"[green]✓ Category '{category}' updated[/green]")

    def delete_category(self, categories):
        """Delete a category"""
        if not categories:
            console.print("[yellow]No categories to delete[/yellow]")
            return

        choices = [Choice(value=cat, name=cat) for cat in sorted(categories.keys())]
        choices.append(Choice(value="cancel", name="❌ Cancel"))

        category = inquirer.select(
            message="Select category to delete:",
            choices=choices,
        ).execute()

        if category == "cancel":
            return

        if Confirm.ask(f"[yellow]Delete category '{category}'?[/yellow]", default=False):
            self.remove_config_category(category)
            console.print(f"[green]✓ Category '{category}' deleted[/green]")

    def update_config_category(self, category: str, extensions: str):
        """Update a category in config file"""
        with open(self.config_file, 'r') as f:
            lines = f.readlines()

        with open(self.config_file, 'w') as f:
            for line in lines:
                if line.strip().startswith(f"{category}:"):
                    f.write(f"{category}: {extensions}\n")
                else:
                    f.write(line)

    def remove_config_category(self, category: str):
        """Remove a category from config file"""
        with open(self.config_file, 'r') as f:
            lines = f.readlines()

        with open(self.config_file, 'w') as f:
            for line in lines:
                if not line.strip().startswith(f"{category}:"):
                    f.write(line)

    def show_statistics(self):
        """Show directory statistics"""
        console.clear()
        console.print(Panel.fit("[bold cyan]Directory Statistics[/bold cyan]", border_style="cyan"))

        # Select directory
        self.base_dir = self.select_directory()
        if not self.base_dir:
            return

        console.print(f"\n[bold]Analyzing: [cyan]{self.base_dir}[/cyan][/bold]\n")

        with console.status("[bold green]Scanning directory..."):
            stats = self.calculate_directory_stats()

        # Display statistics
        self.display_statistics(stats)

        input("\nPress Enter to continue...")

    def calculate_directory_stats(self) -> Dict:
        """Calculate directory statistics"""
        stats = {
            'total_files': 0,
            'total_dirs': 0,
            'total_size': 0,
            'by_extension': defaultdict(int),
            'by_year': defaultdict(int),
            'largest_files': []
        }

        all_files = []

        for root, dirs, files in os.walk(self.base_dir):
            stats['total_dirs'] += len(dirs)

            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                    stats['total_files'] += 1
                    stats['total_size'] += file_size

                    # Track by extension
                    ext = os.path.splitext(file)[1].lower().lstrip('.')
                    if ext:
                        stats['by_extension'][ext] += 1

                    # Track by year
                    year = get_year_of_last_modified(file_path)
                    stats['by_year'][year] += 1

                    # Track for largest files
                    all_files.append((file_path, file_size))

                except (OSError, IOError):
                    continue

        # Get top 10 largest files
        all_files.sort(key=lambda x: x[1], reverse=True)
        stats['largest_files'] = all_files[:10]

        return stats

    def display_statistics(self, stats: Dict):
        """Display directory statistics"""
        # Summary table
        summary = Table(title="Summary", box=box.ROUNDED, border_style="cyan")
        summary.add_column("Metric", style="cyan")
        summary.add_column("Value", style="green", justify="right")

        summary.add_row("Total Files", str(stats['total_files']))
        summary.add_row("Total Directories", str(stats['total_dirs']))
        summary.add_row("Total Size", self.format_size(stats['total_size']))

        console.print(summary)

        # Top extensions
        if stats['by_extension']:
            ext_table = Table(title="\nTop 10 File Types", box=box.ROUNDED, border_style="cyan")
            ext_table.add_column("Extension", style="cyan")
            ext_table.add_column("Count", style="green", justify="right")

            sorted_exts = sorted(stats['by_extension'].items(), key=lambda x: x[1], reverse=True)
            for ext, count in sorted_exts[:10]:
                ext_table.add_row(ext or "(no extension)", str(count))

            console.print(ext_table)

        # Files by year
        if stats['by_year']:
            year_table = Table(title="\nFiles by Year", box=box.ROUNDED, border_style="cyan")
            year_table.add_column("Year", style="yellow")
            year_table.add_column("Count", style="green", justify="right")

            for year, count in sorted(stats['by_year'].items(), reverse=True):
                year_table.add_row(str(year), str(count))

            console.print(year_table)

        # Largest files
        if stats['largest_files']:
            large_table = Table(title="\nTop 10 Largest Files", box=box.ROUNDED, border_style="cyan")
            large_table.add_column("File", style="cyan")
            large_table.add_column("Size", style="green", justify="right")

            for file_path, size in stats['largest_files']:
                file_name = os.path.basename(file_path)
                large_table.add_row(file_name, self.format_size(size))

            console.print(large_table)

    def format_size(self, size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"

    def create_default_config(self):
        """Create default configuration file"""
        default_config = """# FAST Configuration File
# Category format: FolderName: extension1, extension2, ...

# Archives
archive_documents: pdf, doc, docx, txt, odf, xls, xlsx, ppt, pptx, md
archive_pictures: png, jpeg, jpg, gif, bmp, svg, webp, psd, tiff
archive_videos: mp4, avi, mkv, mov, flv, wmv, webm, mpeg, mpg
archive_music: mp3, wav, flac, aac, ogg, m4a, wma
archive_compressed: zip, rar, 7z, tar, gz, bz2, xz, iso
archive_scripts: py, js, ts, php, java, cpp, c, h, cs, rb

# Installers
installer_windows: exe, msi
installer_linux: deb, rpm

# Data
archive_data: json, xml, csv, sql, db

# Other
archive_books: epub, mobi, pdf, chm
archive_fonts: ttf, otf, woff, woff2

# Ignore patterns (files/directories to skip)
ignore: tmp, log, cache

# Paths to ignore (won't be organized)
# ignore_path: path1, path2

# Directories to archive as a whole
# archive_dir: OldDownloads
"""
        with open(self.config_file, 'w') as f:
            f.write(default_config)

        console.print(f"[green]✓ Default configuration created: {self.config_file}[/green]")

    def show_help(self):
        """Display help information"""
        console.clear()

        help_text = """
[bold cyan]FAST TUI - Help & Documentation[/bold cyan]

[bold yellow]What is FAST?[/bold yellow]
FAST (File Arrangement and Sorting Tool) helps you organize files automatically by:
• Categorizing files by type (documents, images, videos, etc.)
• Organizing files by year (based on modification date)
• Handling duplicates intelligently
• Providing preview before making changes

[bold yellow]How to Use:[/bold yellow]

1. [cyan]Organize Files[/cyan]
   • Select directory to organize
   • Choose operation mode (execute/test/dedup)
   • Preview changes before execution
   • Files will be organized into Year/Category structure

2. [cyan]Preview Organization[/cyan]
   • See how files will be organized without making changes
   • View statistics and file distribution
   • Save preview to file

3. [cyan]Manage Configuration[/cyan]
   • View current categories and rules
   • Add/edit/delete categories
   • Customize file type mappings

4. [cyan]Directory Statistics[/cyan]
   • Analyze any directory
   • View file distribution by type and year
   • Find largest files

[bold yellow]Configuration File:[/bold yellow]
The categories.conf file defines:
• Categories and their file extensions
• Ignore patterns (files to skip)
• Archive directories (folders to archive as whole)

Format: CategoryName: ext1, ext2, ext3

[bold yellow]Operation Modes:[/bold yellow]
• [green]Execute[/green]: Organize files immediately
• [yellow]Test[/yellow]: Simulate without moving files
• [cyan]Dedup Prompt[/cyan]: Ask before handling duplicates
• [red]Dedup Force[/red]: Auto-keep newest (dangerous!)

[bold yellow]Keyboard Shortcuts:[/bold yellow]
• Arrow keys: Navigate menus
• Enter: Select option
• Ctrl+C: Cancel/Exit

[bold yellow]Tips:[/bold yellow]
• Always preview before executing
• Use test mode to verify behavior
• Backup important files first
• Check logs after organization
"""

        console.print(Panel(help_text, border_style="cyan", padding=(1, 2)))
        input("\nPress Enter to continue...")


def main():
    """Main entry point"""
    try:
        wizard = FASTWizard()
        wizard.main_menu()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Fatal error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
