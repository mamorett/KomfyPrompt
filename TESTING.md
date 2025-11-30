# Testing Guide for ComfyUI Prompt Extractor

This document provides a comprehensive testing checklist to verify 100% feature parity with the original tkinter application.

## Testing Checklist

### 1. Basic File Operations

- [ ] **Open Single File (Ctrl+O)**
  - Open file dialog appears
  - Can select PNG file
  - File loads and processes correctly
  - Thumbnail appears for single file

- [ ] **Open Multiple Files**
  - Can select multiple PNG files
  - All files process correctly
  - Results show for all files
  - Thumbnail shows file count

- [ ] **Open Folder**
  - Folder dialog appears
  - All PNG files in folder are found
  - Recursive search works
  - All files process correctly

- [ ] **Drag and Drop**
  - Single file drag and drop works
  - Multiple files drag and drop works
  - Folder drag and drop works
  - Drop zone highlights on drag enter
  - Drop zone resets on drag leave

### 2. Extraction Modes

- [ ] **ComfyUI Mode**
  - Extracts from workflow metadata
  - Extracts from prompt metadata
  - Identifies CLIPTextEncode nodes
  - Filters positive vs negative prompts
  - Handles multiple prompts per file

- [ ] **Parameters Mode**
  - Extracts from parameters metadata
  - Falls back to PNG properties
  - Handles JSON format parameters
  - Handles text format parameters
  - Correctly parses "Positive prompt:" field

- [ ] **Mode Toggle (Ctrl+E)**
  - Switches between modes
  - Re-processes current files
  - Updates display correctly
  - Status message shows mode change

### 3. Display and UI

- [ ] **Extracted Prompts Tab**
  - Shows all extracted prompts
  - Proper formatting with separators
  - File headers for multiple files
  - Prompt titles and numbers
  - Text is selectable

- [ ] **Summary Tab**
  - Shows extraction summary
  - Displays file count
  - Shows prompts count
  - Lists files with prompts
  - Shows extraction method

- [ ] **Thumbnail Preview**
  - Shows for single file
  - Displays image correctly
  - Shows image dimensions
  - Shows filename
  - Hides for multiple files

- [ ] **Status Bar**
  - Shows current status
  - Updates during processing
  - Shows success messages
  - Shows error messages
  - Shows prompt counts

- [ ] **Progress Indicator**
  - Shows during extraction
  - Shows during translation
  - Indeterminate animation
  - Hides when complete

### 4. Translation Features (if translators installed)

- [ ] **Translate to Chinese**
  - Button enabled with results
  - Translation processes correctly
  - Display updates with translations
  - Status shows translation info
  - Direction indicator appears

- [ ] **Translate to English**
  - Button enabled with results
  - Translation processes correctly
  - Display updates with translations
  - Status shows translation info
  - Direction indicator appears

- [ ] **Translator Engine Selection**
  - Dropdown shows all engines
  - Can select different engines
  - Selected engine is used
  - All engines work correctly

- [ ] **Restore Original**
  - Button enabled after translation
  - Restores original prompts
  - Display updates correctly
  - Button disables after restore
  - Status shows restore message

- [ ] **Translation State**
  - State preserved when copying
  - State preserved when saving
  - Direction shown in status
  - Direction shown in file headers

### 5. Copy Operations

- [ ] **Copy All Prompts (Ctrl+C)**
  - Copies all prompts to clipboard
  - Prompts separated correctly
  - Status shows success message
  - Works with translated prompts
  - Translation info in status

- [ ] **Copy First Prompt**
  - Copies only first prompt
  - Status shows success message
  - Works with translated prompts
  - Translation info in status

### 6. Save Operations

- [ ] **Save to File (Ctrl+S)**
  - File dialog appears
  - Default filename generated
  - Can specify custom filename
  - File saves correctly
  - Includes header information
  - Includes extraction info
  - Includes translation info (if translated)
  - Includes all prompts
  - Includes file information
  - Status shows success message

### 7. Clear Operations

- [ ] **Clear Results (Ctrl+L)**
  - Clears prompt text
  - Clears summary text
  - Clears thumbnail
  - Resets status
  - Disables action buttons
  - Resets translation state

### 8. Menu System

- [ ] **File Menu**
  - Open File(s) works
  - Open Folder works
  - Save to File works
  - Exit works

- [ ] **Edit Menu**
  - Copy All Prompts works
  - Copy First Prompt works
  - Clear Results works

- [ ] **Help Menu**
  - About dialog opens
  - Shows version info
  - Shows features list
  - Shows keyboard shortcuts

### 9. Keyboard Shortcuts

- [ ] **Ctrl+O** - Open file(s)
- [ ] **Ctrl+E** - Toggle mode
- [ ] **Ctrl+C** - Copy all prompts
- [ ] **Ctrl+S** - Save to file
- [ ] **Ctrl+L** - Clear results
- [ ] **Ctrl+Q** - Quit application

### 10. Button States

- [ ] **Buttons Disabled During Processing**
  - All action buttons disabled
  - Browse buttons disabled
  - Translation buttons disabled

- [ ] **Buttons Enabled After Processing**
  - Action buttons enabled with results
  - Browse buttons enabled
  - Translation buttons enabled (if translator available)

- [ ] **Conditional Button States**
  - Copy buttons only enabled with results
  - Save button only enabled with results
  - Translation buttons only enabled with results
  - Restore button only enabled after translation

### 11. Error Handling

- [ ] **Invalid File Type**
  - Shows error message
  - Status shows error
  - Application remains stable

- [ ] **No Prompts Found**
  - Shows appropriate message
  - Summary explains issue
  - Suggests mode switch

- [ ] **Translation Errors**
  - Shows error message
  - Status shows error
  - Original prompts preserved

- [ ] **File Save Errors**
  - Shows error message
  - Status shows error
  - Application remains stable

### 12. Batch Processing

- [ ] **Multiple Files**
  - All files process correctly
  - Results separated by file
  - File headers show correctly
  - Summary shows all files

- [ ] **Large Batches**
  - UI remains responsive
  - Progress indicator shows
  - All files complete
  - Memory usage reasonable

### 13. Edge Cases

- [ ] **Empty PNG Files**
  - Handles gracefully
  - Shows no prompts message

- [ ] **Corrupted Metadata**
  - Handles gracefully
  - Shows appropriate error

- [ ] **Very Long Prompts**
  - Displays correctly
  - Copies correctly
  - Saves correctly

- [ ] **Special Characters**
  - Displays correctly
  - Copies correctly
  - Saves correctly

- [ ] **Unicode Characters**
  - Displays correctly
  - Copies correctly
  - Saves correctly

### 14. Translation Edge Cases (if available)

- [ ] **Translation Failures**
  - Shows failure message
  - Keeps original text
  - Application remains stable

- [ ] **Network Issues**
  - Handles timeout gracefully
  - Shows appropriate error

- [ ] **Mixed Language Content**
  - Translates correctly
  - Preserves formatting

### 15. UI/UX Features

- [ ] **Window Resizing**
  - Layout adapts correctly
  - All elements remain accessible
  - Text areas resize properly

- [ ] **Text Selection**
  - Can select text in prompts
  - Can select text in summary
  - Copy from selection works

- [ ] **Scrolling**
  - Scroll bars appear when needed
  - Scrolling works smoothly
  - Content fully accessible

- [ ] **Theme Integration**
  - Respects KDE theme
  - Colors appropriate
  - Icons display correctly

## Test Data Requirements

To fully test the application, you need:

1. **ComfyUI PNG files** with workflow metadata
2. **PNG files** with parameters metadata
3. **PNG files** with PNG properties metadata
4. **Multiple PNG files** for batch testing
5. **Folder** containing PNG files
6. **PNG files** with various prompt lengths
7. **PNG files** with special characters
8. **PNG files** with unicode characters

## Automated Testing

While this is primarily a manual testing checklist, consider:

1. Creating a test suite with sample PNG files
2. Automating file loading tests
3. Automating extraction tests
4. Verifying output format consistency

## Reporting Issues

When reporting issues, include:

1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. Sample PNG file (if possible)
5. Error messages
6. System information (OS, Python version, Qt version)