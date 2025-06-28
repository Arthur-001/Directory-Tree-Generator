import os
import json
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QPushButton, QSpinBox, QCheckBox, QTextEdit, QLabel, 
    QFileDialog, QStatusBar
)
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QIcon, QFont, QTextCursor
from ui.settings_dialog import SettingsDialog
from backend.generate_tree import generate_directory_tree
from PySide6.QtWidgets import QApplication
# Import the custom menu bar
from ui.menu_bar import create_menu_bar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Directory Tree Generator")
        self.setGeometry(100, 100, 1000, 700)
        # Set up the menu bar
        self.menuBar = create_menu_bar(self)
        self.setMenuBar(self.menuBar)
        self.setup_ui()
        self.load_settings()
        self.advanced_settings = self.load_advanced_settings()
        
    def setup_ui(self):
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Directory selection
        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Select directory...")
        browse_btn = QPushButton("Browse...")
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(QLabel("Root Directory:"))
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(browse_btn)
        
        # Options layout
        options_layout = QHBoxLayout()
        
        # Depth setting
        depth_layout = QVBoxLayout()
        depth_layout.addWidget(QLabel("Depth"))
        self.depth_spin = QSpinBox()
        self.depth_spin.setRange(0, 10)
        self.depth_spin.setValue(2)
        depth_layout.addWidget(self.depth_spin)
        
        # Checkboxes
        self.show_files_cb = QCheckBox("Show Files")
        self.show_files_cb.setChecked(True)
        self.subdir_files_cb = QCheckBox("Show Subdirectory Files")
        self.subdir_files_cb.setChecked(True)
        self.sort_cb = QCheckBox("Sort Alphabetically")
        self.sort_cb.setChecked(True)
        
        options_layout.addLayout(depth_layout)
        options_layout.addWidget(self.show_files_cb)
        options_layout.addWidget(self.subdir_files_cb)
        options_layout.addWidget(self.sort_cb)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.generate_btn = QPushButton("Generate Tree")
        self.generate_btn.setFixedHeight(40)
        self.generate_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.generate_btn.clicked.connect(self.generate_tree)
        
        settings_btn = QPushButton("Settings")
        settings_btn.setFixedHeight(40)
        settings_btn.clicked.connect(self.open_settings)
        
        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(settings_btn)
        
        # Output area
        output_layout = QVBoxLayout()
        output_layout.addWidget(QLabel("Directory Tree Output:"))
        
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setFont(QFont("Consolas", 10))
        
        # Save and Copy buttons
        btns_layout = QHBoxLayout()
        save_btn = QPushButton("Save to File")
        save_btn.setFixedHeight(35)
        save_btn.clicked.connect(self.save_tree)
        copy_btn = QPushButton("Copy")
        copy_btn.setFixedHeight(35)
        copy_btn.clicked.connect(self.copy_tree)
        btns_layout.addWidget(save_btn)
        btns_layout.addWidget(copy_btn)
        
        # Assemble main layout
        main_layout.addLayout(dir_layout)
        main_layout.addLayout(options_layout)
        main_layout.addLayout(btn_layout)
        main_layout.addLayout(output_layout)
        main_layout.addWidget(self.output_area)
        main_layout.addLayout(btns_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def browse_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            self.dir_input.setText(dir_path)
            self.status_bar.showMessage(f"Selected: {dir_path}")
    
    def load_settings(self):
        settings = QSettings("YourCompany", "DirectoryTreeGenerator")
        self.dir_input.setText(settings.value("last_directory", ""))
        self.depth_spin.setValue(int(settings.value("tree_depth", 2)))
        self.show_files_cb.setChecked(settings.value("show_files", "true") == "true")
        self.subdir_files_cb.setChecked(settings.value("show_subdir_files", "true") == "true")
        self.sort_cb.setChecked(settings.value("sort_alphabetically", "true") == "true")
    
    def save_settings(self):
        settings = QSettings("YourCompany", "DirectoryTreeGenerator")
        settings.setValue("last_directory", self.dir_input.text())
        settings.setValue("tree_depth", self.depth_spin.value())
        settings.setValue("show_files", self.show_files_cb.isChecked())
        settings.setValue("show_subdir_files", self.subdir_files_cb.isChecked())
        settings.setValue("sort_alphabetically", self.sort_cb.isChecked())
    
    def load_advanced_settings(self):
        settings = QSettings("YourCompany", "DirectoryTreeGenerator")
        return {
            "root_emoji": settings.value("root_emoji", "🌐"),
            "subdir_emoji": settings.value("subdir_emoji", "📁"),
            "extra_indent": int(settings.value("extra_indent", 0)),
            "exclude_folders": json.loads(settings.value("exclude_folders", '["node_modules", ".git", "venv"]')),
            "exclude_patterns": json.loads(settings.value("exclude_patterns", '["#", "~"]')),
            "min_file_size": int(settings.value("min_file_size", 0)),
            "max_file_size": settings.value("max_file_size", "inf"),
            "exclude_folders_in_dirs": self.parse_dict_setting(settings, "exclude_folders_in_dirs", {}),
            "exclude_files_in_dirs": self.parse_dict_setting(settings, "exclude_files_in_dirs", {}),
            "only_show_files_with_specific_char_indir": self.parse_dict_setting(settings, "only_show_files_with_specific_char_indir", {}),
            "only_show_folders_with_specific_char_indir": self.parse_dict_setting(settings, "only_show_folders_with_specific_char_indir", {}),
            "exclude_folders_in_dirs_recursive": self.parse_dict_setting(settings, "exclude_folders_in_dirs_recursive", {}),
            "exclude_files_in_dirs_recursive": self.parse_dict_setting(settings, "exclude_files_in_dirs_recursive", {}),
            "only_show_files_with_specific_char_indir_recursive": self.parse_dict_setting(settings, "only_show_files_with_specific_char_indir_recursive", {}),
            "only_show_folders_with_specific_char_indir_recursive": self.parse_dict_setting(settings, "only_show_folders_with_specific_char_indir_recursive", {}),
            "directory_rules": self.parse_dict_setting(settings, "directory_rules", [])
        }
    
    def parse_dict_setting(self, settings, key, default):
        """Parse dictionary settings stored as JSON strings"""
        value = settings.value(key)
        if value is None:
            return default
        try:
            return json.loads(value)
        except:
            return default
    
    def save_advanced_settings(self, settings):
        qsettings = QSettings("YourCompany", "DirectoryTreeGenerator")
        for key, value in settings.items():
            if isinstance(value, dict):
                # Store dictionaries as JSON strings
                qsettings.setValue(key, json.dumps(value))
            elif isinstance(value, list):
                qsettings.setValue(key, json.dumps(value))
            else:
                qsettings.setValue(key, value)
    
    def open_settings(self):
        dialog = SettingsDialog(self.advanced_settings, self)
        if dialog.exec():
            self.advanced_settings = dialog.get_settings()
            self.save_advanced_settings(self.advanced_settings)
            self.status_bar.showMessage("Settings updated")
    
    def generate_tree(self):
        dir_path = self.dir_input.text()
        if not dir_path or not os.path.isdir(dir_path):
            self.status_bar.showMessage("Please select a valid directory")
            return
        from backend import generate_tree
        generate_tree.tree_depth = self.depth_spin.value()
        generate_tree.show_subdirectory_files = self.subdir_files_cb.isChecked()
        generate_tree.sort_alphabetically = self.sort_cb.isChecked()
        generate_tree.show_files = self.show_files_cb.isChecked()
        # Convert directory_rules to backend dicts
        exclude_folders_in_dirs = {}
        exclude_files_in_dirs = {}
        for rule in self.advanced_settings.get("directory_rules", []):
            d = rule["directory"]
            pat = rule["pattern"]
            rec = rule.get("recursive", False)
            if rule["type"] == "exclude_folder":
                if d not in exclude_folders_in_dirs:
                    exclude_folders_in_dirs[d] = []
                exclude_folders_in_dirs[d].append(pat)
            elif rule["type"] == "exclude_file":
                if d not in exclude_files_in_dirs:
                    exclude_files_in_dirs[d] = []
                exclude_files_in_dirs[d].append(pat)
            elif rule["type"] == "exclude_file_and_folder":
                if d not in exclude_folders_in_dirs:
                    exclude_folders_in_dirs[d] = []
                if d not in exclude_files_in_dirs:
                    exclude_files_in_dirs[d] = []
                exclude_folders_in_dirs[d].append(pat)
                exclude_files_in_dirs[d].append(pat)
        generate_tree.exclude_folders_in_dirs = exclude_folders_in_dirs
        generate_tree.exclude_files_in_dirs = exclude_files_in_dirs
        # Apply other advanced settings
        for key, value in self.advanced_settings.items():
            if key in ("exclude_folders_in_dirs", "exclude_files_in_dirs"):
                continue
            if hasattr(generate_tree, key):
                setattr(generate_tree, key, value)
        try:
            tree_output = generate_directory_tree(dir_path, output_file=None)
            self.output_area.clear()
            self.output_area.setPlainText(tree_output)
            self.output_area.moveCursor(QTextCursor.Start)
            self.status_bar.showMessage(f"Tree generated for: {dir_path}")
        except Exception as e:
            self.status_bar.showMessage(f"Error: {str(e)}")
    
    def save_tree(self):
        if not self.output_area.toPlainText():
            self.status_bar.showMessage("No tree to save")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Directory Tree", 
            "", 
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.output_area.toPlainText())
                self.status_bar.showMessage(f"Tree saved to: {file_path}")
            except Exception as e:
                self.status_bar.showMessage(f"Save error: {str(e)}")
    
    def copy_tree(self):
        text = self.output_area.toPlainText()
        if not text:
            self.status_bar.showMessage("No tree to copy")
            return
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.status_bar.showMessage("Tree copied to clipboard")
    
    def closeEvent(self, event):
        self.save_settings()
        event.accept()