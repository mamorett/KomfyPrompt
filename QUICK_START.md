# Quick Start Guide

Get up and running with ComfyUI Prompt Extractor in 5 minutes!

## Installation

### Step 1: Install Dependencies

```bash
./install.sh
```

Or manually:

```bash
pip install PyQt6 Pillow pyperclip
# Optional for translation:
pip install translators
```

### Step 2: Run the Application

```bash
./run.sh
```

Or manually:

```bash
python3 main.py
```

## First Use

### Extract Prompts from a Single File

1. **Drag and drop** a PNG file into the drop zone
   - Or click "Browse File(s)..." and select a file
   - Or press **Ctrl+O**

2. **View the results** in the "Extracted Prompts" tab

3. **Copy the prompt** by clicking "Copy All Prompts" or pressing **Ctrl+C**

### Extract from Multiple Files

1. **Drag and drop** multiple PNG files or a folder
   - Or click "Browse Folder..." to select a folder

2. **View all results** - each file's prompts are shown separately

3. **Check the Summary** tab for statistics

### Switch Extraction Mode

- Press **Ctrl+E** to toggle between "ComfyUI" and "Parameters" mode
- The application will re-process the current files automatically

### Translate Prompts (Optional)

1. Extract prompts first
2. Click "Translate to CN" for Chinese or "Translate to EN" for English
3. Click "Restore Original" to revert

### Save Results

1. Click "Save to File" or press **Ctrl+S**
2. Choose a location and filename
3. The file includes all prompts with metadata

## Keyboard Shortcuts

- **Ctrl+O**: Open file(s)
- **Ctrl+E**: Toggle extraction mode
- **Ctrl+C**: Copy all prompts
- **Ctrl+S**: Save to file
- **Ctrl+L**: Clear results
- **Ctrl+Q**: Quit

## Tips

- **Drag and drop** is the fastest way to load files
- **Toggle mode** (Ctrl+E) if no prompts are found
- **Check Summary tab** for detailed statistics
- **Use translation** to convert between languages
- **Save to file** to keep a permanent record

## Troubleshooting

### No prompts found?

- Try switching extraction mode with **Ctrl+E**
- Verify the PNG file contains ComfyUI metadata
- Check the Summary tab for details

### Translation not working?

- Install translators: `pip install translators`
- Check internet connection
- Try a different translator engine

### Application won't start?

- Verify Python 3.8+ is installed
- Install dependencies: `./install.sh`
- Check for error messages

## Next Steps

- Read **README.md** for complete documentation
- Check **TESTING.md** for all features
- See **MIGRATION_GUIDE.md** if coming from tkinter version

## Support

For issues or questions:
1. Check the documentation files
2. Verify all dependencies are installed
3. Ensure you're using Python 3.8+ and Qt 6.6+

---

**Ready to extract prompts? Just drag and drop a PNG file!** 🚀