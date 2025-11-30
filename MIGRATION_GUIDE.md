# Migration Guide: From Tkinter to KDE/Kirigami

This guide helps users transition from the original tkinter version to the new KDE/Kirigami version.

## What's Changed?

### User Interface

**Before (Tkinter)**:
- Traditional desktop application look
- Standard tkinter widgets
- Platform-dependent appearance

**After (Kirigami)**:
- Modern KDE-native interface
- Kirigami components
- Consistent KDE Plasma integration

### Installation

**Before (Tkinter)**:
```bash
pip install Pillow pyperclip translators
# Optional: pip install tkinterdnd2
```

**After (Kirigami)**:
```bash
pip install PyQt6 Pillow pyperclip translators
# Or use: ./install.sh
```

### Running the Application

**Before (Tkinter)**:
```bash
python comfyui_extractor.py
```

**After (Kirigami)**:
```bash
python3 main.py
# Or use: ./run.sh
```

## What Stays the Same?

### All Features

✅ **100% feature parity** - Every feature from the tkinter version is available:

- Dual extraction modes (ComfyUI / Parameters)
- Batch processing
- Drag & drop
- Image thumbnails
- Translation support
- Export to file
- All keyboard shortcuts
- All menu items
- All buttons and actions

### Extraction Logic

✅ **Identical extraction** - The core extraction logic is unchanged:

- Same ComfyUI metadata parsing
- Same Parameters metadata parsing
- Same PNG properties fallback
- Same prompt filtering logic
- Same results structure

### File Formats

✅ **Same file support**:

- Input: PNG files with metadata
- Output: Plain text files
- Same file structure
- Same formatting

### Keyboard Shortcuts

✅ **All shortcuts preserved**:

- Ctrl+O: Open file(s)
- Ctrl+E: Toggle mode
- Ctrl+C: Copy all prompts
- Ctrl+S: Save to file
- Ctrl+L: Clear results

## User Experience Improvements

### Better Performance

1. **Non-blocking operations**: UI stays responsive during processing
2. **Efficient threading**: Better use of system resources
3. **Faster rendering**: Qt6 graphics acceleration

### Better Integration

1. **KDE Plasma integration**: Native look and feel
2. **System theme support**: Respects your KDE theme
3. **Better file dialogs**: Native platform dialogs
4. **High DPI support**: Proper scaling on high-resolution displays

### Better Accessibility

1. **Screen reader support**: Better accessibility features
2. **Keyboard navigation**: Full keyboard support
3. **Focus indicators**: Clear visual feedback

## Common Questions

### Q: Will my workflow change?

**A**: No. The workflow is identical:
1. Load PNG files
2. Select extraction mode
3. View results
4. Copy or save prompts

### Q: Are my saved files compatible?

**A**: Yes. The output format is identical. Files saved with the tkinter version can be read by the Kirigami version and vice versa.

### Q: Do I need to learn new shortcuts?

**A**: No. All keyboard shortcuts are the same.

### Q: Will translation still work?

**A**: Yes. Translation works exactly the same way, using the same translators library.

### Q: Can I use both versions?

**A**: Yes. Both versions can coexist on the same system without conflicts.

### Q: Is the Kirigami version slower?

**A**: No. The Kirigami version is actually faster due to better threading and Qt6 optimizations.

### Q: Do I need KDE Plasma?

**A**: No. While optimized for KDE Plasma, the application works on any Qt6-compatible environment.

## Side-by-Side Comparison

### Main Window

| Feature | Tkinter | Kirigami |
|---------|---------|----------|
| Window title | ✓ | ✓ |
| Menu bar | ✓ | ✓ (Global drawer) |
| Control panel | ✓ | ✓ |
| Drop zone | ✓ | ✓ |
| File buttons | ✓ | ✓ |
| Thumbnail | ✓ | ✓ |
| Tabs | ✓ | ✓ |
| Status bar | ✓ | ✓ |
| Action buttons | ✓ | ✓ |
| Progress bar | ✓ | ✓ |

### Functionality

| Feature | Tkinter | Kirigami |
|---------|---------|----------|
| ComfyUI extraction | ✓ | ✓ |
| Parameters extraction | ✓ | ✓ |
| Batch processing | ✓ | ✓ |
| Translation | ✓ | ✓ |
| Copy to clipboard | ✓ | ✓ |
| Save to file | ✓ | ✓ |
| Drag & drop | ✓ | ✓ |
| Keyboard shortcuts | ✓ | ✓ |

## Troubleshooting Migration Issues

### Issue: Application won't start

**Solution**:
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check PyQt6 installation
python3 -c "import PyQt6"

# Reinstall if needed
pip install --upgrade PyQt6
```

### Issue: Translation not working

**Solution**:
```bash
# Install translators library
pip install translators

# Restart application
```

### Issue: Drag and drop not working

**Solution**:
```bash
# Set Qt platform plugin
export QT_QPA_PLATFORM=xcb  # For X11
# Or
export QT_QPA_PLATFORM=wayland  # For Wayland

# Run application
python3 main.py
```

### Issue: High DPI display issues

**Solution**:
```bash
# Enable Qt auto-scaling
export QT_AUTO_SCREEN_SCALE_FACTOR=1

# Run application
python3 main.py
```

## Feedback and Support

If you encounter any issues during migration:

1. Check TESTING.md for comprehensive testing checklist
2. Review IMPLEMENTATION_NOTES.md for technical details
3. Verify all dependencies are installed correctly
4. Ensure you're using Python 3.8+ and Qt 6.6+

## Conclusion

The migration from tkinter to KDE/Kirigami provides:

✅ **100% feature parity**
✅ **Better performance**
✅ **Modern interface**
✅ **Better integration**
✅ **Same workflow**

You can confidently switch to the Kirigami version knowing that all your familiar features and workflows are preserved while gaining the benefits of a modern, KDE-native application.