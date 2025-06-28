from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, 
    QFormLayout, QLineEdit, QSpinBox, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QMessageBox, QInputDialog, QCheckBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QAbstractItemView,
    QFileDialog
)
from PySide6.QtCore import Qt
import os

class RuleEditDialog(QDialog):
    def __init__(self, rule_type, directory="", pattern="", action="", recursive=False, parent=None, root_dir=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Directory Rule")
        self.setMinimumSize(400, 300)
        self.rule_type = rule_type
        self.root_dir = root_dir
        self.setup_ui(directory, pattern, action, recursive)
        
    def setup_ui(self, directory, pattern, action, recursive):
        layout = QVBoxLayout(self)
        
        # Directory input with Browse button
        dir_layout = QHBoxLayout()
        self.dir_edit = QLineEdit(directory)
        dir_layout.addWidget(self.dir_edit)
        browse_btn = QPushButton("Browse...")
        browse_btn.setFixedWidth(90)
        browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(browse_btn)
        form_layout = QFormLayout()
        form_layout.addRow("Directory Name:", dir_layout)
        
        # Rule type selection
        type_layout = QFormLayout()
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Exclude folder",
            "Exclude file",
            "Exclude file and folder"
        ])
        
        # Set current selection based on rule type
        type_index = {
            "exclude_folder": 0,
            "exclude_file": 1,
            "exclude_file_and_folder": 2
        }.get(self.rule_type, 0)
        self.type_combo.setCurrentIndex(type_index)
        type_layout.addRow("Rule Type:", self.type_combo)
        
        # Pattern input
        pattern_layout = QFormLayout()
        self.pattern_edit = QLineEdit(pattern)
        pattern_layout.addRow("Pattern:", self.pattern_edit)
        
        # Action for exclude rules
        action_layout = QFormLayout()
        self.action_combo = QComboBox()
        self.action_combo.addItems(["Exclude all", "Exclude specific patterns"])
        if action == "*":
            self.action_combo.setCurrentIndex(0)
        else:
            self.action_combo.setCurrentIndex(1)
        action_layout.addRow("Action:", self.action_combo)
        
        # Recursive option
        recursive_layout = QFormLayout()
        self.recursive_cb = QCheckBox("Apply this rule to all subdirectories")
        self.recursive_cb.setChecked(recursive)
        recursive_layout.addRow("", self.recursive_cb)
        
        # Add to main layout
        layout.addLayout(form_layout)
        layout.addLayout(type_layout)
        layout.addLayout(pattern_layout)
        layout.addLayout(action_layout)
        layout.addLayout(recursive_layout)  # Add recursive option
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        # Connect action combo and pattern edit for dynamic behavior
        self.action_combo.currentIndexChanged.connect(self.on_action_changed)
        self.pattern_edit.textChanged.connect(self.on_pattern_changed)
        self.on_action_changed(self.action_combo.currentIndex())
        self.on_pattern_changed(self.pattern_edit.text())
    
    def on_action_changed(self, idx):
        if idx == 0:  # Exclude all
            self.pattern_edit.setText("*")
            self.pattern_edit.setEnabled(False)
            self.ok_btn.setEnabled(True)
        else:  # Exclude specific patterns
            self.pattern_edit.setEnabled(True)
            # Only clear if previous value was '*', otherwise keep existing pattern for editing
            if self.pattern_edit.text() == "*":
                self.pattern_edit.setText("")
            self.ok_btn.setEnabled(bool(self.pattern_edit.text().strip()))
    
    def on_pattern_changed(self, text):
        if self.action_combo.currentIndex() == 1:
            self.ok_btn.setEnabled(bool(text.strip()))
    
    def get_rule(self):
        directory = self.dir_edit.text().strip()
        pattern = self.pattern_edit.text().strip()
        rule_type = [
            "exclude_folder",
            "exclude_file",
            "exclude_file_and_folder"
        ][self.type_combo.currentIndex()]
        
        # For exclude rules, handle wildcard action
        if self.action_combo.currentIndex() == 0:  # Exclude all
            pattern = "*"
        
        return {
            "directory": directory,
            "type": rule_type,
            "pattern": pattern,
            "recursive": self.recursive_cb.isChecked()  # Add recursive flag
        }

    def browse_directory(self):
        # Start from root_dir if available, else home
        start_dir = self.root_dir if self.root_dir else os.path.expanduser("~")
        selected_dir = QFileDialog.getExistingDirectory(self, "Select Directory", start_dir)
        if selected_dir:
            # Only set the directory name, not the full path
            self.dir_edit.setText(os.path.basename(selected_dir))


class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings.copy()
        self.setWindowTitle("Advanced Settings")
        self.setMinimumSize(800, 600)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create formatting tab
        self.create_formatting_tab()
        # Create exclusion tab
        self.create_exclusion_tab()
        # Create directory rules tab
        self.create_directory_rules_tab()
        
        # Buttons
        btn_layout = QHBoxLayout()
        reset_btn = QPushButton("Reset Defaults")
        reset_btn.clicked.connect(self.reset_defaults)
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def create_formatting_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.root_emoji_edit = QLineEdit(self.settings.get("root_emoji", "🌐"))
        self.subdir_emoji_edit = QLineEdit(self.settings.get("subdir_emoji", "📁"))
        self.extra_indent_spin = QSpinBox()
        self.extra_indent_spin.setRange(0, 10)
        self.extra_indent_spin.setValue(self.settings.get("extra_indent", 0))
        
        layout.addRow("Root Emoji:", self.root_emoji_edit)
        layout.addRow("Subdirectory Emoji:", self.subdir_emoji_edit)
        layout.addRow("Extra Indentation:", self.extra_indent_spin)
        
        self.tabs.addTab(tab, "Formatting")
    
    def create_exclusion_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Folder exclusions
        folder_layout = QVBoxLayout()
        folder_layout.addWidget(QLabel("Excluded Folders:"))
        
        self.folder_list = QListWidget()
        for folder in self.settings.get("exclude_folders", []):
            self.folder_list.addItem(folder)
        
        btn_layout = QHBoxLayout()
        add_folder_btn = QPushButton("Add")
        add_folder_btn.clicked.connect(self.add_excluded_folder)
        remove_folder_btn = QPushButton("Remove")
        remove_folder_btn.clicked.connect(self.remove_excluded_folder)
        
        btn_layout.addWidget(add_folder_btn)
        btn_layout.addWidget(remove_folder_btn)
        
        folder_layout.addWidget(self.folder_list)
        folder_layout.addLayout(btn_layout)
        
        # Pattern exclusions
        pattern_layout = QVBoxLayout()
        pattern_layout.addWidget(QLabel("Excluded Patterns:"))
        
        self.pattern_list = QListWidget()
        for pattern in self.settings.get("exclude_patterns", []):
            self.pattern_list.addItem(pattern)
        
        pattern_btn_layout = QHBoxLayout()
        add_pattern_btn = QPushButton("Add")
        add_pattern_btn.clicked.connect(self.add_excluded_pattern)
        remove_pattern_btn = QPushButton("Remove")
        remove_pattern_btn.clicked.connect(self.remove_excluded_pattern)
        
        pattern_btn_layout.addWidget(add_pattern_btn)
        pattern_btn_layout.addWidget(remove_pattern_btn)
        
        pattern_layout.addWidget(self.pattern_list)
        pattern_layout.addLayout(pattern_btn_layout)
        
        # File size limits
        size_layout = QFormLayout()
        self.min_size_spin = QSpinBox()
        self.min_size_spin.setRange(0, 1000000000)
        self.min_size_spin.setValue(self.settings.get("min_file_size", 0))
        self.max_size_spin = QSpinBox()
        self.max_size_spin.setRange(0, 1000000000)
        self.max_size_spin.setValue(
            1000000000 if self.settings.get("max_file_size", "inf") == "inf" 
            else int(self.settings["max_file_size"])
        )
        self.max_size_inf_cb = QCheckBox("No limit")
        self.max_size_inf_cb.setChecked(self.settings.get("max_file_size", "inf") == "inf")
        self.max_size_inf_cb.stateChanged.connect(
            lambda: self.max_size_spin.setEnabled(not self.max_size_inf_cb.isChecked())
        )
        self.max_size_spin.setEnabled(not self.max_size_inf_cb.isChecked())
        
        size_layout.addRow("Min File Size (bytes):", self.min_size_spin)
        size_layout.addRow("Max File Size (bytes):", self.max_size_spin)
        size_layout.addRow("", self.max_size_inf_cb)
        
        # Assemble tab
        layout.addLayout(folder_layout)
        layout.addLayout(pattern_layout)
        layout.addLayout(size_layout)
        layout.addStretch()
        
        self.tabs.addTab(tab, "Exclusions")
    
    def create_directory_rules_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Table for directory-specific rules
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(5)
        self.rules_table.setHorizontalHeaderLabels(["Directory", "Rule Type", "Pattern", "Action", "Recursive"])
        self.rules_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.rules_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.rules_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.rules_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.rules_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.rules_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.rules_table.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # Load existing rules
        self.load_directory_rules()
        
        # Buttons for rule management
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Rule")
        add_btn.clicked.connect(self.add_directory_rule)
        self.edit_btn = QPushButton("Edit Rule")
        self.edit_btn.clicked.connect(self.edit_directory_rule)
        self.remove_btn = QPushButton("Remove Rule")
        self.remove_btn.clicked.connect(self.remove_directory_rule)
        self.edit_btn.setEnabled(False)
        self.remove_btn.setEnabled(False)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.remove_btn)
        
        layout.addWidget(QLabel("Directory-Specific Rules:"))
        layout.addWidget(self.rules_table)
        layout.addLayout(btn_layout)
        
        self.tabs.addTab(tab, "Directory Rules")
        # Connect selection change to update button states
        self.rules_table.selectionModel().selectionChanged.connect(self.update_rule_buttons)
    
    def add_excluded_folder(self):
        folder, ok = QInputDialog.getText(self, "Add Folder", "Folder name to exclude:")
        if ok and folder:
            self.folder_list.addItem(folder)
    
    def remove_excluded_folder(self):
        if self.folder_list.currentRow() >= 0:
            self.folder_list.takeItem(self.folder_list.currentRow())
    
    def add_excluded_pattern(self):
        pattern, ok = QInputDialog.getText(self, "Add Pattern", "Pattern to exclude (e.g., *.tmp):")
        if ok and pattern:
            self.pattern_list.addItem(pattern)
    
    def remove_excluded_pattern(self):
        if self.pattern_list.currentRow() >= 0:
            self.pattern_list.takeItem(self.pattern_list.currentRow())
            
    def load_directory_rules(self):
        # Clear existing rows
        self.rules_table.setRowCount(0)
        
        # Load rules from settings
        rules = self.settings.get("directory_rules", [])
        for rule in rules:
            self.add_rule_to_table(
                rule["directory"],
                rule["type"],
                rule["pattern"],
                "Exclude all" if rule["pattern"] == "*" else "Pattern",
                rule.get("recursive", False)
            )
    
    def add_rule_to_table(self, directory, rule_type, pattern, action, recursive):
        row = self.rules_table.rowCount()
        self.rules_table.insertRow(row)
        
        # Map rule type to display name
        type_display = {
            "exclude_folder": "Exclude Folder",
            "exclude_file": "Exclude File",
            "exclude_file_and_folder": "Exclude File and Folder"
        }.get(rule_type, rule_type)
        
        # Create items
        dir_item = QTableWidgetItem(directory)
        type_item = QTableWidgetItem(type_display)
        pattern_item = QTableWidgetItem(pattern)
        action_item = QTableWidgetItem(action)
        recursive_item = QTableWidgetItem("Yes" if recursive else "No")
        
        # Store raw rule type in data
        dir_item.setData(Qt.UserRole, rule_type)
        
        # Add to table
        self.rules_table.setItem(row, 0, dir_item)
        self.rules_table.setItem(row, 1, type_item)
        self.rules_table.setItem(row, 2, pattern_item)
        self.rules_table.setItem(row, 3, action_item)
        self.rules_table.setItem(row, 4, recursive_item)
    
    def add_directory_rule(self):
        # Get root directory from parent MainWindow if available
        root_dir = None
        if self.parent() and hasattr(self.parent(), 'dir_input'):
            root_dir = self.parent().dir_input.text()
        dialog = RuleEditDialog("", "", "", "", False, parent=self, root_dir=root_dir)
        if dialog.exec():
            rule = dialog.get_rule()
            self.add_rule_to_table(
                rule["directory"],
                rule["type"],
                rule["pattern"],
                "Exclude all" if rule["pattern"] == "*" else "Pattern",
                rule["recursive"]
            )
    
    def edit_directory_rule(self):
        selected_row = self.rules_table.currentRow()
        if selected_row < 0:
            return
        directory_item = self.rules_table.item(selected_row, 0)
        directory = directory_item.text()
        rule_type = directory_item.data(Qt.UserRole)
        pattern = self.rules_table.item(selected_row, 2).text()
        recursive = self.rules_table.item(selected_row, 4).text() == "Yes"
        action = "Exclude all" if pattern == "*" else ""
        # Get root directory from parent MainWindow if available
        root_dir = None
        if self.parent() and hasattr(self.parent(), 'dir_input'):
            root_dir = self.parent().dir_input.text()
        dialog = RuleEditDialog(rule_type, directory, pattern, action, recursive, parent=self, root_dir=root_dir)
        if dialog.exec():
            new_rule = dialog.get_rule()
            self.rules_table.item(selected_row, 0).setText(new_rule["directory"])
            self.rules_table.item(selected_row, 0).setData(Qt.UserRole, new_rule["type"])
            self.rules_table.item(selected_row, 1).setText({
                "exclude_folder": "Exclude Folder",
                "exclude_file": "Exclude File",
                "exclude_file_and_folder": "Exclude File and Folder"
            }.get(new_rule["type"]))
            self.rules_table.item(selected_row, 2).setText(new_rule["pattern"])
            self.rules_table.item(selected_row, 3).setText(
                "Exclude all" if new_rule["pattern"] == "*" else "Pattern"
            )
            self.rules_table.item(selected_row, 4).setText("Yes" if new_rule["recursive"] else "No")
    
    def remove_directory_rule(self):
        selected_row = self.rules_table.currentRow()
        if selected_row >= 0:
            self.rules_table.removeRow(selected_row)
    
    def reset_defaults(self):
        reply = QMessageBox.question(
            self, 
            "Reset Defaults", 
            "Are you sure you want to reset to default settings?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.settings = {
                "root_emoji": "🌐",
                "subdir_emoji": "📁",
                "extra_indent": 0,
                "exclude_folders": ["node_modules", ".git", "venv"],
                "exclude_patterns": ["#", "~"],
                "min_file_size": 0,
                "max_file_size": "inf",
                "directory_rules": [],
                "exclude_folders_in_dirs": {},
                "exclude_files_in_dirs": {},
                "only_show_files_with_specific_char_indir": {},
                "only_show_folders_with_specific_char_indir": {},
                "exclude_folders_in_dirs_recursive": {},
                "exclude_files_in_dirs_recursive": {},
                "only_show_files_with_specific_char_indir_recursive": {},
                "only_show_folders_with_specific_char_indir_recursive": {}
            }
            self.root_emoji_edit.setText("🌐")
            self.subdir_emoji_edit.setText("📁")
            self.extra_indent_spin.setValue(0)
            
            self.folder_list.clear()
            for folder in self.settings["exclude_folders"]:
                self.folder_list.addItem(folder)
                
            self.pattern_list.clear()
            for pattern in self.settings["exclude_patterns"]:
                self.pattern_list.addItem(pattern)
                
            self.min_size_spin.setValue(0)
            self.max_size_spin.setValue(1000000000)
            self.max_size_inf_cb.setChecked(True)
            self.max_size_spin.setEnabled(False)
            
            self.load_directory_rules()
    
    def get_settings(self):
        # Save all rules as a list of dicts
        directory_rules = []
        for row in range(self.rules_table.rowCount()):
            directory = self.rules_table.item(row, 0).text()
            rule_type = self.rules_table.item(row, 0).data(Qt.UserRole)
            pattern = self.rules_table.item(row, 2).text()
            recursive = self.rules_table.item(row, 4).text() == "Yes"
            directory_rules.append({
                "directory": directory,
                "type": rule_type,
                "pattern": pattern,
                "recursive": recursive
            })
        return {
            "root_emoji": self.root_emoji_edit.text(),
            "subdir_emoji": self.subdir_emoji_edit.text(),
            "extra_indent": self.extra_indent_spin.value(),
            "exclude_folders": [self.folder_list.item(i).text() 
                               for i in range(self.folder_list.count())],
            "exclude_patterns": [self.pattern_list.item(i).text() 
                                for i in range(self.pattern_list.count())],
            "min_file_size": self.min_size_spin.value(),
            "max_file_size": "inf" if self.max_size_inf_cb.isChecked() 
                            else str(self.max_size_spin.value()),
            "directory_rules": directory_rules,
            "exclude_folders_in_dirs": {},
            "exclude_files_in_dirs": {},
            "only_show_files_with_specific_char_indir": {},
            "only_show_folders_with_specific_char_indir": {},
            "exclude_folders_in_dirs_recursive": {},
            "exclude_files_in_dirs_recursive": {},
            "only_show_files_with_specific_char_indir_recursive": {},
            "only_show_folders_with_specific_char_indir_recursive": {}
        }

    def accept(self):
        # Save advanced settings to QSettings
        from PySide6.QtCore import QSettings
        import json
        qsettings = QSettings("YourCompany", "DirectoryTreeGenerator")
        new_settings = self.get_settings()
        for key, value in new_settings.items():
            if isinstance(value, dict):
                qsettings.setValue(key, json.dumps(value))
            elif isinstance(value, list):
                qsettings.setValue(key, json.dumps(value))
            else:
                qsettings.setValue(key, value)
        super().accept()

    def update_rule_buttons(self):
        selected = self.rules_table.currentRow() >= 0
        self.edit_btn.setEnabled(selected)
        self.remove_btn.setEnabled(selected)