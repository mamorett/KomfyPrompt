#!/usr/bin/env python3
"""
ComfyUI Prompt Extractor v3.0 - KDE Native Edition
A tool to extract positive prompts from ComfyUI-generated PNG files.
"""

import sys
import os
import json
import glob
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QComboBox, QTabWidget,
    QFileDialog, QMessageBox, QStatusBar, QMenuBar, QMenu,
    QGroupBox, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMimeData, QUrl
from PyQt6.QtGui import QAction, QPixmap, QDragEnterEvent, QDropEvent

from PIL import Image
import pyperclip

# Try to import translators library
try:
    import translators as ts
    HAS_TRANSLATOR = True
except ImportError:
    HAS_TRANSLATOR = False
    print("Warning: 'translators' library not found. Translation features will be disabled.")
    print("Install with: pip install translators")


class ExtractionThread(QThread):
    """Thread for extracting prompts from files"""
    finished = pyqtSignal(list, list)
    error = pyqtSignal(str)
    
    def __init__(self, file_paths, mode, extractor):
        super().__init__()
        self.file_paths = file_paths
        self.mode = mode
        self.extractor = extractor
    
    def run(self):
        try:
            results = []
            for file_path in self.file_paths:
                if self.mode == "ComfyUI":
                    result = self.extractor.extract_positive_prompts_comfyui(file_path)
                else:
                    result = self.extractor.extract_positive_prompts_parameters(file_path)
                results.append(result)
            
            self.finished.emit(results, self.file_paths)
        except Exception as e:
            self.error.emit(str(e))


class TranslationThread(QThread):
    """Thread for translating prompts"""
    finished = pyqtSignal(list, str)
    error = pyqtSignal(str)
    
    def __init__(self, prompts, from_lang, to_lang, direction, engine):
        super().__init__()
        self.prompts = prompts
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.direction = direction
        self.engine = engine
    
    def run(self):
        try:
            translated_prompts = []
            
            for prompt_text in self.prompts:
                try:
                    translated = ts.translate_text(
                        query_text=prompt_text,
                        translator=self.engine,
                        from_language=self.from_lang,
                        to_language=self.to_lang,
                        timeout=10.0,
                        if_ignore_empty_query=True,
                        if_print_warning=False
                    )
                    translated_prompts.append(translated)
                except Exception as e:
                    print(f"Translation error for prompt using {self.engine}: {e}")
                    translated_prompts.append(f"[Translation failed] {prompt_text}")
            
            self.finished.emit(translated_prompts, self.direction)
        except Exception as e:
            self.error.emit(str(e))


class PromptExtractor:
    """Core extraction logic"""
    
    def extract_positive_prompts_comfyui(self, file_path: str) -> Dict[str, Any]:
        """Extract positive prompts using ComfyUI metadata (workflow/prompt)"""
        try:
            with Image.open(file_path) as img:
                if img.format != 'PNG':
                    raise ValueError(f"File is not a PNG: {img.format}")

                metadata = img.info
                result = {
                    'file_info': {
                        'filename': os.path.basename(file_path),
                        'size': img.size,
                        'mode': img.mode
                    },
                    'positive_prompts': [],
                    'extraction_method': 'comfyui'
                }

                processed_nodes = set()

                # Try workflow first
                if 'workflow' in metadata:
                    try:
                        workflow_data = json.loads(metadata['workflow'])
                        prompts = self.extract_positive_from_workflow(workflow_data, processed_nodes)
                        result['positive_prompts'].extend(prompts)
                    except json.JSONDecodeError as e:
                        print(f"Warning: Could not parse workflow JSON: {e}")

                # Then prompt data if none found
                if not result['positive_prompts'] and 'prompt' in metadata:
                    try:
                        prompt_data = json.loads(metadata['prompt'])
                        prompts = self.extract_positive_from_prompt_data(prompt_data, processed_nodes)
                        result['positive_prompts'].extend(prompts)
                    except json.JSONDecodeError as e:
                        print(f"Warning: Could not parse prompt JSON: {e}")

                return result

        except Exception as e:
            raise Exception(f"Error reading PNG file: {e}")

    def extract_positive_prompts_parameters(self, file_path: str) -> Dict[str, Any]:
        """Extract positive prompt using Parameters metadata and direct PNG properties"""
        try:
            with Image.open(file_path) as img:
                if img.format != 'PNG':
                    raise ValueError(f"File is not a PNG: {img.format}")

                metadata = img.info
                result = {
                    'file_info': {
                        'filename': os.path.basename(file_path),
                        'size': img.size,
                        'mode': img.mode
                    },
                    'positive_prompts': [],
                    'extraction_method': 'parameters'
                }

                # First, try the parameters extraction
                prompt_text = self.extract_positive_from_parameters_strict(metadata)
                if prompt_text:
                    result['positive_prompts'].append({
                        'text': prompt_text,
                        'node_id': 'parameters',
                        'node_type': 'parameters',
                        'title': 'Parameters',
                        'source': 'parameters'
                    })
                else:
                    # If original method fails, try PNG properties as fallback
                    prompt_text = self.extract_positive_from_png_properties(metadata)
                    if prompt_text:
                        result['positive_prompts'].append({
                            'text': prompt_text,
                            'node_id': 'png_properties',
                            'node_type': 'png_properties',
                            'title': 'PNG Properties',
                            'source': 'png_properties'
                        })

                return result

        except Exception as e:
            raise Exception(f"Error reading PNG file: {e}")

    def extract_positive_from_workflow(self, workflow_data: Dict, processed_nodes: set) -> List[Dict]:
        """Extract positive prompts from workflow nodes"""
        positive_prompts = []
        nodes = workflow_data.get('nodes', [])

        for node in nodes:
            node_id = node.get('id')
            node_type = node.get('type', '')
            title = node.get('title', '').lower()

            if node_id in processed_nodes:
                continue

            if (node_type == 'CLIPTextEncode' or
                'cliptext' in node_type.lower() or
                node.get('properties', {}).get('Node name for S&R') == 'CLIPTextEncode'):

                widgets_values = node.get('widgets_values', [])

                if widgets_values and len(widgets_values) > 0:
                    prompt_text = widgets_values[0]

                    is_positive = (
                        'positive' in title or
                        'pos' in title or
                        (title == '' and isinstance(prompt_text, str) and prompt_text.strip() != '' and 'negative' not in prompt_text.lower()[:50]) or
                        (title == 'untitled' and isinstance(prompt_text, str) and prompt_text.strip() != '' and 'negative' not in prompt_text.lower()[:50])
                    )

                    is_negative = (
                        'negative' in title or
                        'neg' in title or
                        (isinstance(prompt_text, str) and (prompt_text.strip() == '' or prompt_text.lower().strip().startswith('negative')))
                    )

                    if isinstance(prompt_text, list):
                        prompt_text = '\n'.join(str(x) for x in prompt_text)

                    if is_positive and not is_negative and isinstance(prompt_text, (str, int, float)):
                        prompt_info = {
                            'text': str(prompt_text),
                            'node_id': node_id,
                            'node_type': node_type,
                            'title': node.get('title', 'Untitled'),
                            'source': 'workflow'
                        }

                        positive_prompts.append(prompt_info)
                        processed_nodes.add(node_id)

        return positive_prompts

    def extract_positive_from_prompt_data(self, prompt_data: Dict, processed_nodes: set) -> List[Dict]:
        """Extract positive prompts from prompt data structure"""
        positive_prompts = []

        for key, value in prompt_data.items():
            if isinstance(value, dict):
                class_type = value.get('class_type', '')

                if key in processed_nodes:
                    continue

                if class_type == 'CLIPTextEncode':
                    inputs = value.get('inputs', {})

                    text_content = None
                    if 'text' in inputs:
                        text_content = inputs['text']
                    elif 'prompt' in inputs:
                        text_content = inputs['prompt']

                    if text_content is None:
                        continue
                    if isinstance(text_content, list):
                        text_content = '\n'.join(str(i) for i in text_content)
                    elif not isinstance(text_content, str):
                        text_content = str(text_content)

                    if text_content.strip():
                        is_negative = (
                            'negative' in text_content.lower()[:50]
                        )

                        if not is_negative:
                            prompt_info = {
                                'text': text_content,
                                'node_id': key,
                                'class_type': class_type,
                                'title': f"Node {key}",
                                'source': 'prompt_data'
                            }

                            positive_prompts.append(prompt_info)
                            processed_nodes.add(key)

        return positive_prompts

    def extract_positive_from_png_properties(self, metadata: Dict) -> Optional[str]:
        """Extract positive prompt directly from PNG properties"""
        try:
            possible_keys = [
                'Positive prompt',
                'positive prompt', 
                'Positive Prompt',
                'positive_prompt'
            ]
            
            for key in possible_keys:
                if key in metadata:
                    value = metadata[key]
                    
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8', errors='ignore')
                        except Exception:
                            value = str(value)
                    elif not isinstance(value, str):
                        value = str(value)
                    
                    if value and value.strip():
                        result = value.strip()
                        if ((result.startswith('"') and result.endswith('"')) or 
                            (result.startswith("'") and result.endswith("'"))):
                            result = result[1:-1]
                        return result
            
            return None
            
        except Exception as e:
            print(f"PNG properties extractor error: {e}")
            return None

    def extract_positive_from_parameters_strict(self, metadata: Dict) -> Optional[str]:
        """Extract from parameters metadata with robust type handling"""
        try:
            if 'parameters' not in metadata:
                return None

            parameters_data = metadata['parameters']

            if isinstance(parameters_data, bytes):
                try:
                    parameters_data = parameters_data.decode('utf-8', errors='ignore')
                except Exception:
                    parameters_data = str(parameters_data)
            elif isinstance(parameters_data, (list, dict)):
                parameters_data = json.dumps(parameters_data, ensure_ascii=False)
            elif not isinstance(parameters_data, str):
                parameters_data = str(parameters_data)

            # Try JSON first
            try:
                parsed_params = json.loads(parameters_data)
                if isinstance(parsed_params, dict):
                    possible_keys = [
                        'Positive prompt',
                        'positive prompt',
                        'Positive Prompt',
                        'positive_prompt',
                        'prompt',
                        'Prompt'
                    ]
                    for key in possible_keys:
                        if key in parsed_params:
                            value = parsed_params[key]
                            if isinstance(value, list):
                                return '\n'.join(str(v) for v in value)
                            return str(value) if value is not None else None
            except json.JSONDecodeError:
                pass

            # Parse text format
            lines = parameters_data.split('\n')
            for i, line in enumerate(lines):
                line_stripped_lower = line.strip().lower()
                if line_stripped_lower.startswith('positive prompt:'):
                    prompt_text = line.split(':', 1)[1].strip() if ':' in line else ''
                    j = i + 1
                    prompt_lines = [prompt_text] if prompt_text else []
                    while j < len(lines):
                        next_line = lines[j]
                        nl = next_line.strip().lower()
                        if ':' in nl and any(param in nl for param in
                                             ['negative prompt', 'steps', 'sampler', 'cfg scale', 'seed', 'size', 'model', 'clip skip']):
                            break
                        prompt_lines.append(next_line.rstrip())
                        j += 1

                    full_prompt = '\n'.join(prompt_lines).rstrip()
                    out_lines = full_prompt.splitlines()
                    k = 0
                    while k < len(out_lines) and out_lines[k].strip() == '':
                        k += 1
                    return '\n'.join(out_lines[k:]) if k < len(out_lines) else None

            return None

        except Exception as e:
            print(f"Parameters extractor error: {e}")
            return None


class DropFrame(QFrame):
    """Frame that accepts drag and drop"""
    filesDropped = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        self.setLineWidth(2)
        
        layout = QVBoxLayout()
        self.label = QLabel("Drag & Drop PNG file(s) or folder here")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: gray; font-size: 11pt;")
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        self.setMinimumHeight(100)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("background-color: #d0f0d0;")
            self.label.setText("Drop PNG file(s) or folder here!")
            self.label.setStyleSheet("color: #006600; font-size: 11pt; font-weight: bold;")
    
    def dragLeaveEvent(self, event):
        self.setStyleSheet("")
        self.label.setText("Drag & Drop PNG file(s) or folder here")
        self.label.setStyleSheet("color: gray; font-size: 11pt;")
    
    def dropEvent(self, event: QDropEvent):
        files = []
        for url in event.mimeData().urls():
            files.append(url.toLocalFile())
        
        self.filesDropped.emit(files)
        
        self.setStyleSheet("")
        self.label.setText("Drag & Drop PNG file(s) or folder here")
        self.label.setStyleSheet("color: gray; font-size: 11pt;")


class ComfyUIPromptExtractorUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("ComfyUI Prompt Extractor v3.0")
        self.setGeometry(100, 100, 1000, 800)
        
        # Data storage
        self.current_files = []
        self.current_results = []
        self.all_prompt_texts = []
        self.original_prompts = []
        self.is_translated = False
        self.current_translation_direction = None
        
        # Extractor
        self.extractor = PromptExtractor()
        
        # Threads
        self.extraction_thread = None
        self.translation_thread = None
        
        # Thumbnail
        self.thumbnail_image = None
        
        # Setup UI
        self.setup_ui()
        
        # Keyboard shortcuts
        self.setup_shortcuts()
    
    def setup_ui(self):
        # Menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        open_file_action = QAction("Open File(s)...", self)
        open_file_action.setShortcut("Ctrl+O")
        open_file_action.triggered.connect(self.browse_file)
        file_menu.addAction(open_file_action)
        
        open_folder_action = QAction("Open Folder...", self)
        open_folder_action.triggered.connect(self.browse_folder)
        file_menu.addAction(open_folder_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("Save to File...", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_to_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        copy_all_action = QAction("Copy All Prompts", self)
        copy_all_action.setShortcut("Ctrl+C")
        copy_all_action.triggered.connect(self.copy_to_clipboard)
        edit_menu.addAction(copy_all_action)
        
        copy_first_action = QAction("Copy First Prompt", self)
        copy_first_action.triggered.connect(self.copy_first_prompt)
        edit_menu.addAction(copy_first_action)
        
        clear_action = QAction("Clear Results", self)
        clear_action.setShortcut("Ctrl+L")
        clear_action.triggered.connect(self.clear_results)
        edit_menu.addAction(clear_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Control frame
        control_group = QGroupBox("Settings")
        control_layout = QHBoxLayout()
        
        control_layout.addWidget(QLabel("Mode:"))
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["ComfyUI", "Parameters"])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        control_layout.addWidget(self.mode_combo)
        
        control_layout.addWidget(QLabel("(Ctrl+E to toggle)"))
        
        control_layout.addSpacing(20)
        
        if HAS_TRANSLATOR:
            control_layout.addWidget(QLabel("Translator:"))
            
            self.translator_combo = QComboBox()
            self.translator_combo.addItems(["alibaba", "bing", "google", "baidu", "youdao", "deepl"])
            control_layout.addWidget(self.translator_combo)
        
        control_layout.addStretch()
        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)
        
        # Drop zone and file selection
        file_layout = QHBoxLayout()
        
        # Drop zone
        self.drop_frame = DropFrame()
        self.drop_frame.filesDropped.connect(self.load_files)
        file_layout.addWidget(self.drop_frame, 2)
        
        # File buttons and thumbnail
        button_layout = QVBoxLayout()
        
        self.browse_file_btn = QPushButton("Browse File(s)...")
        self.browse_file_btn.clicked.connect(self.browse_file)
        button_layout.addWidget(self.browse_file_btn)
        
        self.browse_folder_btn = QPushButton("Browse Folder...")
        self.browse_folder_btn.clicked.connect(self.browse_folder)
        button_layout.addWidget(self.browse_folder_btn)
        
        # Thumbnail
        self.thumbnail_group = QGroupBox("Preview")
        thumbnail_layout = QVBoxLayout()
        
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setMinimumSize(240, 240)
        thumbnail_layout.addWidget(self.thumbnail_label)
        
        self.thumbnail_info_label = QLabel()
        self.thumbnail_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumbnail_layout.addWidget(self.thumbnail_info_label)
        
        self.thumbnail_group.setLayout(thumbnail_layout)
        self.thumbnail_group.hide()
        button_layout.addWidget(self.thumbnail_group)
        
        button_layout.addStretch()
        
        file_layout.addLayout(button_layout, 1)
        main_layout.addLayout(file_layout)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Prompts tab
        self.prompt_text = QTextEdit()
        self.prompt_text.setReadOnly(True)
        self.tabs.addTab(self.prompt_text, "Extracted Prompts")
        
        # Summary tab
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.tabs.addTab(self.summary_text, "Summary")
        
        main_layout.addWidget(self.tabs)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate
        self.progress.hide()
        main_layout.addWidget(self.progress)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        if HAS_TRANSLATOR:
            self.translate_cn_btn = QPushButton("Translate to CN")
            self.translate_cn_btn.clicked.connect(self.translate_to_chinese)
            self.translate_cn_btn.setEnabled(False)
            button_layout.addWidget(self.translate_cn_btn)
            
            self.translate_en_btn = QPushButton("Translate to EN")
            self.translate_en_btn.clicked.connect(self.translate_to_english)
            self.translate_en_btn.setEnabled(False)
            button_layout.addWidget(self.translate_en_btn)
            
            self.restore_btn = QPushButton("Restore Original")
            self.restore_btn.clicked.connect(self.restore_original)
            self.restore_btn.setEnabled(False)
            button_layout.addWidget(self.restore_btn)
        
        button_layout.addStretch()
        
        self.copy_all_btn = QPushButton("Copy All Prompts")
        self.copy_all_btn.clicked.connect(self.copy_to_clipboard)
        self.copy_all_btn.setEnabled(False)
        button_layout.addWidget(self.copy_all_btn)
        
        self.copy_first_btn = QPushButton("Copy First Prompt")
        self.copy_first_btn.clicked.connect(self.copy_first_prompt)
        self.copy_first_btn.setEnabled(False)
        button_layout.addWidget(self.copy_first_btn)
        
        self.save_btn = QPushButton("Save to File")
        self.save_btn.clicked.connect(self.save_to_file)
        self.save_btn.setEnabled(False)
        button_layout.addWidget(self.save_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_results)
        button_layout.addWidget(self.clear_btn)
        
        main_layout.addLayout(button_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def setup_shortcuts(self):
        # Ctrl+E to toggle mode
        from PyQt6.QtGui import QShortcut, QKeySequence
        toggle_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        toggle_shortcut.activated.connect(self.toggle_mode_and_rerun)
    
    def on_mode_changed(self, mode):
        if self.current_files:
            self.process_files(self.current_files)
    
    def toggle_mode_and_rerun(self):
        current_index = self.mode_combo.currentIndex()
        new_index = 1 if current_index == 0 else 0
        self.mode_combo.setCurrentIndex(new_index)
    
    def browse_file(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select ComfyUI PNG File(s)",
            "",
            "PNG files (*.png);;All files (*.*)"
        )
        if file_paths:
            self.load_files(file_paths)
    
    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder with ComfyUI PNG Files"
        )
        if folder_path:
            png_files = glob.glob(os.path.join(folder_path, "**", "*.png"), recursive=True)
            if png_files:
                self.load_files(png_files)
            else:
                QMessageBox.information(self, "No Files", "No PNG files found in the selected folder.")
    
    def load_files(self, file_paths):
        # Filter for PNG files
        valid_files = []
        for file_path in file_paths:
            if os.path.isdir(file_path):
                png_files = glob.glob(os.path.join(file_path, "**", "*.png"), recursive=True)
                valid_files.extend(png_files)
            elif os.path.exists(file_path) and file_path.lower().endswith('.png'):
                valid_files.append(file_path)
        
        if not valid_files:
            QMessageBox.warning(self, "Warning", "No valid PNG files found")
            return
        
        self.process_files(valid_files)
    
    def process_files(self, file_paths):
        self.current_files = file_paths
        
        # Update thumbnail
        if len(file_paths) == 1:
            self.update_thumbnail(file_paths[0])
        else:
            self.thumbnail_group.hide()
            self.thumbnail_info_label.setText(f"{len(file_paths)} PNG files selected")
        
        # Reset translation state
        self.is_translated = False
        self.original_prompts = []
        self.current_translation_direction = None
        
        # Start extraction
        self.status_bar.showMessage("Processing...")
        self.progress.show()
        self.disable_buttons()
        
        mode = self.mode_combo.currentText()
        self.extraction_thread = ExtractionThread(file_paths, mode, self.extractor)
        self.extraction_thread.finished.connect(self.on_extraction_finished)
        self.extraction_thread.error.connect(self.on_extraction_error)
        self.extraction_thread.start()
    
    def update_thumbnail(self, image_path):
        try:
            from PyQt6.QtGui import QImage
            
            with Image.open(image_path) as img:
                original_size = img.size
                info_text = f"{original_size[0]}×{original_size[1]}\n{os.path.basename(image_path)}"
                
                # Create thumbnail
                img.thumbnail((240, 240), Image.Resampling.LANCZOS)
                
                # Convert PIL Image to QPixmap directly
                img_rgb = img.convert('RGBA')
                data = img_rgb.tobytes('raw', 'RGBA')
                
                qimage = QImage(data, img.width, img.height, QImage.Format.Format_RGBA8888)
                pixmap = QPixmap.fromImage(qimage)
                
                self.thumbnail_label.setPixmap(pixmap)
                self.thumbnail_info_label.setText(info_text)
                self.thumbnail_group.show()
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            self.thumbnail_group.hide()
    
    def on_extraction_finished(self, results, file_paths):
        self.progress.hide()
        self.enable_buttons()
        
        self.current_results = results
        self.current_files = file_paths
        
        # Build display text
        prompt_text = ""
        summary_text = ""
        
        total_prompts = 0
        files_with_prompts = 0
        all_prompt_texts = []
        
        for i, result in enumerate(results):
            file_info = result.get('file_info', {})
            positive_prompts = result.get('positive_prompts', [])
            method = result.get('extraction_method', 'unknown')
            
            if positive_prompts:
                files_with_prompts += 1
                total_prompts += len(positive_prompts)
                
                if len(results) > 1:
                    prompt_text += f"=== {file_info.get('filename', 'Unknown')} [{method}] ===\n"
                
                for j, prompt_info in enumerate(positive_prompts, 1):
                    if len(positive_prompts) > 1:
                        prompt_text += f"\nPrompt {j} - {prompt_info.get('title', 'Untitled')}:\n"
                        prompt_text += "-" * 40 + "\n"
                    
                    prompt_content = prompt_info['text']
                    prompt_text += f"{prompt_content}\n"
                    all_prompt_texts.append(prompt_content)
                    
                    if j < len(positive_prompts):
                        prompt_text += "\n"
                
                if i < len(results) - 1:
                    prompt_text += "\n" + "=" * 60 + "\n\n"
        
        # Build summary
        summary_text += "EXTRACTION SUMMARY\n"
        summary_text += "=" * 50 + "\n\n"
        summary_text += f"Extractor mode: {self.mode_combo.currentText()}\n"
        summary_text += f"Files processed: {len(results)}\n"
        summary_text += f"Files with prompts: {files_with_prompts}\n"
        summary_text += f"Total positive prompts found: {total_prompts}\n\n"
        
        if files_with_prompts == 0:
            msg = "No positive prompts found in any files.\n"
            if self.mode_combo.currentText() == "ComfyUI":
                msg += "Make sure the PNG files contain ComfyUI workflow/prompt metadata, or switch to 'Parameters' mode (Ctrl+E)."
            else:
                msg += "Make sure the PNG files contain 'parameters' metadata or switch to 'ComfyUI' mode (Ctrl+E)."
            summary_text += msg
        else:
            summary_text += "FILES WITH PROMPTS:\n"
            summary_text += "-" * 30 + "\n"
            
            for result in results:
                positive_prompts = result.get('positive_prompts', [])
                method = result.get('extraction_method', 'unknown')
                if positive_prompts:
                    filename = result.get('file_info', {}).get('filename', 'Unknown')
                    summary_text += f"• {filename} ({len(positive_prompts)} prompts) [{method}]\n"
        
        # Update UI
        self.prompt_text.setPlainText(prompt_text)
        self.summary_text.setPlainText(summary_text)
        self.all_prompt_texts = all_prompt_texts
        
        if total_prompts > 0:
            self.status_bar.showMessage(f"✓ Extracted {total_prompts} positive prompts from {files_with_prompts} files")
            self.copy_all_btn.setEnabled(True)
            self.copy_first_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            
            if HAS_TRANSLATOR:
                self.translate_cn_btn.setEnabled(True)
                self.translate_en_btn.setEnabled(True)
        else:
            self.status_bar.showMessage("✗ No positive prompts found")
    
    def on_extraction_error(self, error_message):
        self.progress.hide()
        self.enable_buttons()
        
        self.status_bar.showMessage(f"✗ Error: {error_message}")
        QMessageBox.critical(self, "Error", f"Failed to process file(s):\n{error_message}")
    
    def translate_to_chinese(self):
        if not HAS_TRANSLATOR or not self.all_prompt_texts:
            return
        
        if not self.is_translated:
            self.original_prompts = self.all_prompt_texts.copy()
        
        self.status_bar.showMessage("Translating to Chinese...")
        self.progress.show()
        self.disable_buttons()
        
        engine = self.translator_combo.currentText()
        self.translation_thread = TranslationThread(
            self.all_prompt_texts, "en", "zh", "EN→CN", engine
        )
        self.translation_thread.finished.connect(self.on_translation_finished)
        self.translation_thread.error.connect(self.on_translation_error)
        self.translation_thread.start()
    
    def translate_to_english(self):
        if not HAS_TRANSLATOR or not self.all_prompt_texts:
            return
        
        if not self.is_translated:
            self.original_prompts = self.all_prompt_texts.copy()
        
        self.status_bar.showMessage("Translating to English...")
        self.progress.show()
        self.disable_buttons()
        
        engine = self.translator_combo.currentText()
        self.translation_thread = TranslationThread(
            self.all_prompt_texts, "zh", "en", "CN→EN", engine
        )
        self.translation_thread.finished.connect(self.on_translation_finished)
        self.translation_thread.error.connect(self.on_translation_error)
        self.translation_thread.start()
    
    def on_translation_finished(self, translated_prompts, direction):
        self.progress.hide()
        self.enable_buttons()
        
        self.all_prompt_texts = translated_prompts
        self.is_translated = True
        self.current_translation_direction = direction
        
        # Rebuild display
        prompt_text = ""
        prompt_index = 0
        
        for i, result in enumerate(self.current_results):
            file_info = result.get('file_info', {})
            positive_prompts = result.get('positive_prompts', [])
            method = result.get('extraction_method', 'unknown')
            
            if positive_prompts:
                if len(self.current_results) > 1:
                    prompt_text += f"=== {file_info.get('filename', 'Unknown')} [{method}] [{direction}] ===\n"
                
                for j, prompt_info in enumerate(positive_prompts, 1):
                    if len(positive_prompts) > 1:
                        prompt_text += f"\nPrompt {j} - {prompt_info.get('title', 'Untitled')}:\n"
                        prompt_text += "-" * 40 + "\n"
                    
                    if prompt_index < len(translated_prompts):
                        prompt_text += f"{translated_prompts[prompt_index]}\n"
                        prompt_index += 1
                    
                    if j < len(positive_prompts):
                        prompt_text += "\n"
                
                if i < len(self.current_results) - 1:
                    prompt_text += "\n" + "=" * 60 + "\n\n"
        
        self.prompt_text.setPlainText(prompt_text)
        self.status_bar.showMessage(f"✓ Translated {len(translated_prompts)} prompts ({direction})")
        
        if HAS_TRANSLATOR:
            self.restore_btn.setEnabled(True)
    
    def on_translation_error(self, error_message):
        self.progress.hide()
        self.enable_buttons()
        
        self.status_bar.showMessage(f"✗ Translation error: {error_message}")
        QMessageBox.critical(self, "Translation Error", f"Failed to translate prompts:\n{error_message}")
    
    def restore_original(self):
        if not self.original_prompts:
            return
        
        self.all_prompt_texts = self.original_prompts.copy()
        self.is_translated = False
        self.current_translation_direction = None
        
        # Rebuild display
        prompt_text = ""
        prompt_index = 0
        
        for i, result in enumerate(self.current_results):
            file_info = result.get('file_info', {})
            positive_prompts = result.get('positive_prompts', [])
            method = result.get('extraction_method', 'unknown')
            
            if positive_prompts:
                if len(self.current_results) > 1:
                    prompt_text += f"=== {file_info.get('filename', 'Unknown')} [{method}] ===\n"
                
                for j, prompt_info in enumerate(positive_prompts, 1):
                    if len(positive_prompts) > 1:
                        prompt_text += f"\nPrompt {j} - {prompt_info.get('title', 'Untitled')}:\n"
                        prompt_text += "-" * 40 + "\n"
                    
                    if prompt_index < len(self.original_prompts):
                        prompt_text += f"{self.original_prompts[prompt_index]}\n"
                        prompt_index += 1
                    
                    if j < len(positive_prompts):
                        prompt_text += "\n"
                
                if i < len(self.current_results) - 1:
                    prompt_text += "\n" + "=" * 60 + "\n\n"
        
        self.prompt_text.setPlainText(prompt_text)
        self.status_bar.showMessage("✓ Original prompts restored")
        
        if HAS_TRANSLATOR:
            self.restore_btn.setEnabled(False)
    
    def copy_to_clipboard(self):
        if self.all_prompt_texts:
            try:
                all_text = '\n\n'.join(self.all_prompt_texts)
                pyperclip.copy(all_text)
                
                status_msg = f"✓ All {len(self.all_prompt_texts)} prompts copied to clipboard!"
                if self.is_translated and self.current_translation_direction:
                    status_msg += f" [{self.current_translation_direction}]"
                
                self.status_bar.showMessage(status_msg)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to copy to clipboard:\n{e}")
    
    def copy_first_prompt(self):
        if self.all_prompt_texts:
            try:
                pyperclip.copy(self.all_prompt_texts[0])
                
                status_msg = "✓ First prompt copied to clipboard!"
                if self.is_translated and self.current_translation_direction:
                    status_msg += f" [{self.current_translation_direction}]"
                
                self.status_bar.showMessage(status_msg)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to copy to clipboard:\n{e}")
    
    def save_to_file(self):
        if not self.all_prompt_texts:
            return
        
        # Determine default filename
        if len(self.current_files) == 1:
            base_name = os.path.splitext(os.path.basename(self.current_files[0]))[0]
            default_name = f"{base_name}_prompts.txt"
        else:
            default_name = "extracted_prompts.txt"
        
        if self.is_translated and self.current_translation_direction:
            name_parts = os.path.splitext(default_name)
            default_name = f"{name_parts[0]}_{self.current_translation_direction.replace('→', '_to_')}{name_parts[1]}"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Prompts to File",
            default_name,
            "Text files (*.txt);;All files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write("COMFYUI POSITIVE PROMPTS EXTRACTION\n")
                    f.write("=" * 60 + "\n\n")
                    
                    f.write(f"Extractor mode: {self.mode_combo.currentText()}\n")
                    f.write(f"Files processed: {len(self.current_files)}\n")
                    f.write(f"Total prompts: {len(self.all_prompt_texts)}\n")
                    
                    if self.is_translated and self.current_translation_direction:
                        f.write(f"Translation: {self.current_translation_direction}\n")
                    
                    f.write(f"Extraction date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("\n" + "=" * 60 + "\n\n")
                    
                    prompt_index = 0
                    for i, result in enumerate(self.current_results):
                        file_info = result.get('file_info', {})
                        positive_prompts = result.get('positive_prompts', [])
                        method = result.get('extraction_method', 'unknown')
                        
                        if positive_prompts:
                            if len(self.current_results) > 1:
                                f.write(f"FILE: {file_info.get('filename', 'Unknown')}\n")
                                f.write(f"Method: {method}\n")
                                f.write(f"Size: {file_info.get('size', 'Unknown')}\n")
                                f.write("-" * 60 + "\n\n")
                            
                            for j, prompt_info in enumerate(positive_prompts, 1):
                                if len(positive_prompts) > 1:
                                    f.write(f"Prompt {j} - {prompt_info.get('title', 'Untitled')}:\n")
                                    f.write("-" * 40 + "\n")
                                
                                if prompt_index < len(self.all_prompt_texts):
                                    f.write(f"{self.all_prompt_texts[prompt_index]}\n")
                                    prompt_index += 1
                                
                                if j < len(positive_prompts):
                                    f.write("\n")
                            
                            if i < len(self.current_results) - 1:
                                f.write("\n" + "=" * 60 + "\n\n")
                
                status_msg = f"✓ Saved to {os.path.basename(file_path)}"
                if self.is_translated and self.current_translation_direction:
                    status_msg += f" [{self.current_translation_direction}]"
                
                self.status_bar.showMessage(status_msg)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")
    
    def clear_results(self):
        self.prompt_text.clear()
        self.summary_text.clear()
        self.status_bar.showMessage("Ready")
        self.current_files = []
        self.current_results = []
        self.all_prompt_texts = []
        self.is_translated = False
        self.original_prompts = []
        self.current_translation_direction = None
        self.thumbnail_group.hide()
        
        self.copy_all_btn.setEnabled(False)
        self.copy_first_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        
        if HAS_TRANSLATOR:
            self.translate_cn_btn.setEnabled(False)
            self.translate_en_btn.setEnabled(False)
            self.restore_btn.setEnabled(False)
    
    def disable_buttons(self):
        self.browse_file_btn.setEnabled(False)
        self.browse_folder_btn.setEnabled(False)
        self.copy_all_btn.setEnabled(False)
        self.copy_first_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        
        if HAS_TRANSLATOR:
            self.translate_cn_btn.setEnabled(False)
            self.translate_en_btn.setEnabled(False)
            self.restore_btn.setEnabled(False)
    
    def enable_buttons(self):
        self.browse_file_btn.setEnabled(True)
        self.browse_folder_btn.setEnabled(True)
    
    def show_about(self):
        about_text = """ComfyUI Prompt Extractor
Version 3.0

A tool to extract positive prompts from ComfyUI-generated PNG files.

Features:
• Dual extraction modes (ComfyUI / Parameters)
• Batch processing support
• Drag & drop interface
• Image thumbnails
• Translation support (EN ↔ CN)
• Export to text file

Keyboard Shortcuts:
• Ctrl+O: Open file(s)
• Ctrl+E: Toggle extraction mode
• Ctrl+C: Copy all prompts
• Ctrl+S: Save to file
• Ctrl+L: Clear results

Created with Python & PyQt6
"""
        QMessageBox.about(self, "About", about_text)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("ComfyUI Prompt Extractor")
    app.setOrganizationName("NinjaTech")
    app.setOrganizationDomain("ninjatech.ai")
    
    window = ComfyUIPromptExtractorUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()