# Implementation Notes

This document provides technical details about the KDE/Kirigami implementation of ComfyUI Prompt Extractor.

## Architecture Overview

### Backend (Python)

The backend is implemented in `main.py` using PyQt6 and follows the Model-View pattern:

- **ComfyUIPromptExtractorBackend**: Main backend class that manages state and business logic
- **PromptExtractor**: Core extraction logic (identical to original)
- **ExtractionThread**: QThread for non-blocking file processing
- **TranslationThread**: QThread for non-blocking translation

### Frontend (QML)

The frontend is implemented in `main.qml` using Kirigami components:

- **ApplicationWindow**: Main window with global drawer menu
- **Page**: Main content page with all UI components
- **Dialogs**: File dialogs and about dialog
- **Bindings**: Property bindings between QML and Python backend

## Key Design Decisions

### 1. Threading Model

**Original (tkinter)**: Used Python threading.Thread
**New (Kirigami)**: Uses QThread for better Qt integration

Benefits:
- Proper signal/slot communication
- Better thread safety
- Automatic cleanup
- Integration with Qt event loop

### 2. Property System

**Original (tkinter)**: Used tk.StringVar and tk.BooleanVar
**New (Kirigami)**: Uses Qt properties with signals

Benefits:
- Automatic UI updates via property bindings
- Type safety
- Better performance
- Cleaner code

### 3. File Dialogs

**Original (tkinter)**: Used tkinter.filedialog
**New (Kirigami)**: Uses Qt FileDialog

Benefits:
- Native platform dialogs
- Better file type filtering
- Multiple file selection
- Folder selection support

### 4. Clipboard Operations

**Original (tkinter)**: Used pyperclip library
**New (Kirigami)**: Still uses pyperclip for consistency

Reason:
- pyperclip provides cross-platform clipboard support
- Works reliably across different desktop environments
- Maintains compatibility with original implementation

## Component Mapping

### Tkinter → Kirigami

| Tkinter Component | Kirigami Component | Notes |
|-------------------|-------------------|-------|
| Tk() | ApplicationWindow | Main window |
| ttk.Frame | ColumnLayout/RowLayout | Layout containers |
| ttk.Label | Label | Text display |
| ttk.Button | Button | Clickable buttons |
| ttk.Combobox | ComboBox | Dropdown selection |
| scrolledtext.ScrolledText | ScrollView + TextArea | Scrollable text |
| ttk.Notebook | TabBar + StackLayout | Tabbed interface |
| ttk.Progressbar | ProgressBar | Progress indication |
| Menu | GlobalDrawer + Actions | Menu system |
| messagebox | PromptDialog | Dialogs |
| filedialog | FileDialog | File selection |

## State Management

### Properties

All state is managed through Qt properties in the backend:

```python
@pyqtProperty(str, notify=statusChanged)
def status(self):
    return self._status

@status.setter
def status(self, value):
    if self._status != value:
        self._status = value
        self.statusChanged.emit(value)
```

### Signals

Signals are used to notify the UI of state changes:

- `statusChanged`: Status bar updates
- `promptTextChanged`: Prompt display updates
- `summaryTextChanged`: Summary display updates
- `processingChanged`: Progress indicator visibility
- `hasResultsChanged`: Button enable/disable
- etc.

### Slots

Slots are used to handle user actions:

- `@pyqtSlot(list)`: For file loading
- `@pyqtSlot()`: For button clicks
- `@pyqtSlot(str)`: For file saving

## Extraction Logic

The extraction logic is **identical** to the original implementation:

### ComfyUI Mode

1. Opens PNG file with PIL
2. Extracts metadata from image.info
3. Parses 'workflow' JSON if present
4. Falls back to 'prompt' JSON if needed
5. Identifies CLIPTextEncode nodes
6. Filters positive vs negative prompts
7. Returns structured results

### Parameters Mode

1. Opens PNG file with PIL
2. Extracts 'parameters' metadata
3. Tries JSON parsing first
4. Falls back to text parsing
5. Looks for "Positive prompt:" field
6. Falls back to PNG properties
7. Returns structured results

## Translation Implementation

### Threading

Translation uses QThread to avoid blocking the UI:

```python
class TranslationThread(QThread):
    finished = pyqtSignal(list, str)
    error = pyqtSignal(str)
    
    def run(self):
        # Translation logic
        self.finished.emit(results, direction)
```

### State Preservation

Original prompts are backed up before translation:

```python
if not self._is_translated:
    self.original_prompts = self.all_prompt_texts.copy()
```

### Display Rebuild

After translation, the display is rebuilt with translated text while maintaining the original structure.

## File Operations

### Drag and Drop

Implemented using Qt's DropArea:

```qml
DropArea {
    id: dropArea
    anchors.fill: parent
    
    onDropped: function(drop) {
        if (drop.hasUrls) {
            backend.loadFiles(drop.urls)
        }
    }
}
```

### File Validation

PNG validation is performed in the backend:

```python
if os.path.exists(path) and path.lower().endswith('.png'):
    file_paths.append(path)
```

### Thumbnail Generation

Thumbnails are created using PIL and saved to temp directory:

```python
img.thumbnail((240, 240), Image.Resampling.LANCZOS)
temp_path = os.path.join(temp_dir, "comfyui_thumbnail.png")
img.save(temp_path, "PNG")
self.thumbnailPath = "file://" + temp_path
```

## Error Handling

### Thread-Safe Error Reporting

Errors from threads are emitted as signals:

```python
try:
    # Processing
    self.finished.emit(results)
except Exception as e:
    self.error.emit(str(e))
```

### UI Error Display

Errors are displayed in the status bar:

```python
def on_extraction_error(self, error_message):
    self.processing = False
    self.status = f"✗ Error: {error_message}"
```

## Performance Considerations

### Threading

All long-running operations use threads:
- File extraction
- Translation
- Batch processing

### Memory Management

- Thumbnails are saved to temp files (not kept in memory)
- Large text is stored as strings (not duplicated)
- Results are cleared when not needed

### UI Responsiveness

- Progress indicators during operations
- Non-blocking file operations
- Efficient property updates

## Testing Strategy

### Unit Testing

Test individual components:
- Extraction logic
- File validation
- State management

### Integration Testing

Test component interactions:
- File loading → extraction → display
- Translation → display update
- Copy → clipboard

### Manual Testing

Use TESTING.md checklist to verify:
- All UI interactions
- All keyboard shortcuts
- All error conditions
- All edge cases

## Deployment

### Desktop Entry

The `.desktop` file allows integration with KDE:

```ini
[Desktop Entry]
Name=ComfyUI Prompt Extractor
Exec=python3 /path/to/main.py
Icon=applications-graphics
Type=Application
Categories=Graphics;Utility;Qt;KDE;
```

### Installation

1. Install dependencies: `./install.sh`
2. Run application: `./run.sh`
3. Optional: Install .desktop file to `~/.local/share/applications/`

## Future Enhancements

Possible improvements while maintaining feature parity:

1. **Settings Dialog**: Save user preferences (default mode, translator engine)
2. **Recent Files**: Quick access to recently processed files
3. **Batch Export**: Export all prompts to separate files
4. **Custom Themes**: Additional color schemes
5. **Plugin System**: Extensible extraction methods

## Compatibility

### Python Versions

- Minimum: Python 3.8
- Recommended: Python 3.11+
- Tested: Python 3.11

### Qt Versions

- Minimum: Qt 6.6
- Recommended: Qt 6.7+
- Tested: Qt 6.6

### Desktop Environments

- Primary: KDE Plasma 5.27+
- Compatible: Any Qt6-compatible environment
- Tested: KDE Plasma 5.27

## Known Limitations

1. **Translation Requires Internet**: Translation features need network access
2. **PNG Only**: Only PNG files with metadata are supported
3. **Memory Usage**: Large batches may use significant memory
4. **Thumbnail Size**: Fixed at 240x240 pixels

## Troubleshooting

### Import Errors

If PyQt6 import fails:
```bash
pip install --upgrade PyQt6
```

### Translation Not Available

If translators library is missing:
```bash
pip install translators
```

### Drag and Drop Not Working

Ensure Qt platform plugin is properly installed:
```bash
export QT_QPA_PLATFORM=xcb  # For X11
export QT_QPA_PLATFORM=wayland  # For Wayland
```

### High DPI Issues

Set Qt scaling:
```bash
export QT_AUTO_SCREEN_SCALE_FACTOR=1
```

## Code Style

### Python

- PEP 8 compliant
- Type hints where appropriate
- Docstrings for all classes and methods
- Clear variable names

### QML

- Proper indentation (4 spaces)
- Clear component hierarchy
- Descriptive IDs
- Comments for complex logic

## Version History

### v3.0 (KDE/Kirigami Edition)

- Complete rewrite using PyQt6 and Kirigami
- 100% feature parity with tkinter version
- Modern KDE-native interface
- Improved threading and performance
- Better error handling
- Enhanced accessibility

## Credits

- Original tkinter implementation
- KDE/Kirigami conversion
- Python, Qt6, and Kirigami frameworks
- PIL/Pillow for image processing
- pyperclip for clipboard operations
- translators library for translation features