# ComfyUI Prompt Extractor v3.0 - KDE/Kirigami Edition

A powerful tool to extract positive prompts from ComfyUI-generated PNG files, now with a modern KDE/Kirigami interface.

## Features

- **Command Line Interface**: Separate CLI tool for scripting and terminal usage
- **Extraction Modes**: 
  - ComfyUI mode: Extracts from workflow/prompt metadata
  - Parameters mode: Extracts from parameters metadata and PNG properties
  - JSON Support: Extracts directly from saved workflow JSON files
  - Text Fallback: Automatically attempts to parse text content if strict JSON parsing fails
- **Batch Processing**: Process multiple files or entire folders at once
- **Drag & Drop Interface**: Simply drag PNG or JSON files, or folders into the application
- **Image Thumbnails**: Preview images before extraction
- **Translation Support**: Translate prompts between English and Chinese (requires translators library)
- **Multiple Translator Engines**: Choose from alibaba, bing, google, baidu, youdao, or deepl
- **Export Functionality**: Save extracted prompts to text files
- **Keyboard Shortcuts**: Quick access to common operations

## Installation

### Prerequisites

- Python 3.8 or higher
- PyQt6 (for GUI)
- Works on any desktop environment (KDE, GNOME, XFCE, etc.)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Optional: Translation Support

For translation features, install the translators library:

```bash
pip install translators
```

## Usage

### Graphical Interface (GUI)

Run the main application:

```bash
python main.py
```

### Command Line Interface (CLI)

Use the CLI tool for quick extractions or shell scripting:

```bash
# Extract from a single file
python extract_prompts.py image.png

# Extract from multiple files
python extract_prompts.py workflow.json image.png

# Use wildcards (shell expansion or internal globbing)
python extract_prompts.py *.json
python extract_prompts.py "images/*.png"
```

### Basic Workflow (GUI)

1. **Load Files**: 
   - Drag and drop PNG/JSON files or folders into the drop zone
   - Or use "Browse File(s)..." or "Browse Folder..." buttons
   - Or use Ctrl+O keyboard shortcut

2. **Select Extraction Mode**:
   - Choose between "ComfyUI" or "Parameters" mode
   - Toggle with Ctrl+E
   - *Note: JSON files are automatically detected and processed regardless of mode setting.*

3. **View Results**:
   - Extracted prompts appear in the "Extracted Prompts" tab
   - Summary information in the "Summary" tab

4. **Optional Translation**:
   - Click "Translate to CN" for Chinese translation
   - Click "Translate to EN" for English translation
   - Click "Restore Original" to revert to original prompts

5. **Copy or Save**:
   - "Copy All Prompts" (Ctrl+C): Copy all prompts to clipboard
   - "Copy First Prompt": Copy only the first prompt
   - "Save to File" (Ctrl+S): Export to text file

### Keyboard Shortcuts

- **Ctrl+O**: Open file(s)
- **Ctrl+E**: Toggle extraction mode
- **Ctrl+C**: Copy all prompts
- **Ctrl+S**: Save to file
- **Ctrl+L**: Clear results
- **Ctrl+Q**: Quit application

## Extraction Modes

### ComfyUI Mode

Extracts prompts from ComfyUI workflow and prompt metadata:
- Searches for CLIPTextEncode nodes
- Identifies positive prompts based on node titles and content
- Processes workflow JSON structure

### Parameters Mode

Extracts prompts from parameters metadata:
- Looks for "parameters" metadata field
- Falls back to PNG properties if parameters not found
- Supports both JSON and text format parameters

### Automatic JSON Handling

- Detecting `.json` files automatically triggers JSON extraction.
- If standard workflow parsing fails, the extractor falls back to text-based parameter parsing logic.
- This ensures extraction works even for unstructured JSON or text files masquerading as JSON.

## Translation Features

When the `translators` library is installed, you can:

1. **Translate to Chinese**: Convert English prompts to Chinese
2. **Translate to English**: Convert Chinese prompts to English
3. **Choose Translator Engine**: Select from multiple translation services
4. **Restore Original**: Revert to original prompts after translation

Translation state is preserved when copying or saving prompts.

## File Structure

```
.
├── main.py            # Main GUI application
├── extract_prompts.py # CLI entry point
├── extractor.py       # Core extraction logic (shared)
├── icon.png           # Application icon
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Technical Details

### Architecture

- **Backend**: Python with PyQt6
- **UI Framework**: PyQt6 Widgets
- **Core Logic**: Shared `PromptExtractor` class for consistent behavior across CLI and GUI
- **Image Processing**: Pillow (PIL)
- **Clipboard**: pyperclip
- **Translation**: translators library (optional)

### Threading

The application uses QThread for:
- File extraction operations (prevents UI freezing)
- Translation operations (handles network requests)
- *Note: A fresh Extractor instance is created for every thread run to ensure state isolation.*

### Supported File Formats

- Input: 
    - PNG files with embedded metadata (ComfyUI or generic parameters)
    - JSON workflow files

- Output: Plain text files (.txt)

## Troubleshooting

### Translation Not Working

If translation features are disabled:
1. Install the translators library: `pip install translators`
2. Restart the application
3. Check internet connectivity (required for translation)

### No Prompts Extracted

If no prompts are found:
1. Verify the PNG file contains ComfyUI metadata
2. Try switching extraction modes (Ctrl+E)
3. Check the Summary tab for detailed information

### Drag and Drop Not Working

Ensure you're running on a Qt6-compatible environment with proper drag-and-drop support.

## Differences from Original Tkinter Version

This Qt6/QML version maintains 100% functional parity with the original tkinter version while providing:

- Modern Qt Quick interface
- Cross-platform compatibility (works on any desktop environment)
- Improved accessibility features
- Native Qt file dialogs
- Better high-DPI support
- More responsive UI with proper threading
- Optional KDE integration when running on KDE Plasma

## License

This is a conversion of the original ComfyUI Prompt Extractor to KDE/Kirigami framework.

## Credits

- Original concept and extraction logic
- KDE/Kirigami conversion
- Created with Python, Qt6 & Kirigami