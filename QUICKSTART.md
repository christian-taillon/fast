# FAST TUI - Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run FAST TUI

```bash
python fast_tui.py
```

Or use the launcher:

```bash
./fast
```

### 3. Follow the Wizard

The interactive menu will guide you through:
- Selecting a directory to organize
- Previewing changes before execution
- Choosing operation mode
- Executing the organization

## 💡 First Time User?

### Try Preview Mode First

1. Run `python fast_tui.py`
2. Select **👁️ Preview Organization**
3. Choose your Downloads folder
4. See how files will be organized (no changes made)

### Then Try Test Mode

1. Select **🚀 Organize Files**
2. Choose your directory
3. Select **🧪 Test Mode** as operation mode
4. This simulates the organization without actually moving files

### Finally, Organize for Real

1. Select **🚀 Organize Files**
2. Choose your directory
3. Select **⚡ Execute** mode
4. Confirm the preview
5. Files will be organized!

## 📁 What Happens to My Files?

Files are organized into a structure like this:

```
Your Directory/
├── 2024/
│   ├── archive_documents/
│   │   ├── report.pdf
│   │   └── notes.txt
│   ├── archive_pictures/
│   │   └── photo.jpg
│   └── archive_videos/
│       └── video.mp4
└── 2023/
    └── archive_music/
        └── song.mp3
```

- Files are grouped by **year** (based on modification date)
- Within each year, files are grouped by **category** (based on file type)
- Original files in subdirectories are also organized

## ⚙️ Customizing Categories

1. Run FAST TUI
2. Select **📁 Manage Categories**
3. Add, edit, or delete categories as needed

Or edit `categories.conf` directly:

```
# Add your own category
my_category: ext1, ext2, ext3
```

## 🔍 Understanding Modes

| Mode | What It Does | When to Use |
|------|-------------|-------------|
| **Preview** | Shows structure without changes | First time, or to plan |
| **Test** | Simulates with detailed logging | Verify before execution |
| **Execute** | Actually moves files | When you're ready |
| **Dedup Prompt** | Asks about duplicates | When you have duplicates |
| **Dedup Force** | Auto-keeps newest | ⚠️ Use with caution |

## ❓ FAQ

**Q: Will this delete my files?**
A: No! FAST only moves/organizes files. Dedup modes may delete duplicates, but you're prompted first (except in force mode).

**Q: Can I undo the organization?**
A: Not automatically yet. That's why we recommend:
1. Use Preview first
2. Use Test mode
3. Backup important files

**Q: What if a file type isn't recognized?**
A: It won't be moved. Add the extension to `categories.conf` to include it.

**Q: Can I organize the same directory twice?**
A: Yes, but files already organized won't be moved again (they're already in year/category folders).

**Q: Is it safe?**
A: Yes, when used properly:
- Always preview first
- Start with test mode
- Backup critical data
- Check the logs

## 🎯 Pro Tips

1. **Start Small**: Try with a copy of your data first
2. **Check Logs**: After organizing, check the log files for details
3. **Customize**: Tailor categories to your workflow
4. **Regular Use**: Run FAST regularly to keep directories organized
5. **Statistics**: Use the stats feature to analyze directory before organizing

## 🆘 Need Help?

- Press `Ctrl+C` to cancel at any time
- Select **❓ Help** from the main menu for detailed documentation
- Check the logs if something goes wrong
- Review `README.MD` for comprehensive documentation

## 🎨 Navigation Tips

- **Arrow Keys**: Move up/down in menus
- **Enter**: Select an option
- **Ctrl+C**: Cancel/Go back
- **Type and Enter**: Enter custom paths or values

---

**Ready to organize?** Run `python fast_tui.py` and let's get started! 🚀
