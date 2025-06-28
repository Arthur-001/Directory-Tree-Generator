from PySide6.QtGui import QAction  # QAction is now in QtGui
from PySide6.QtWidgets import QMenuBar, QMenu, QMessageBox
# Creates and returns the main menu bar for the application
# Includes Help, About, and Check for Updates options

def create_menu_bar(parent=None):
    menu_bar = QMenuBar(parent)

    # Help menu
    help_menu = QMenu("Help", menu_bar)
    # About action: shows app info
    about_action = QAction("About", menu_bar)
    about_action.triggered.connect(lambda: QMessageBox.information(parent, "About", "Directory Tree Generator\nVersion 1.0\nCreated by YourName"))
    help_menu.addAction(about_action)
    # Check for Updates action: placeholder for update logic
    check_updates_action = QAction("Check for Updates", menu_bar)
    check_updates_action.triggered.connect(lambda: QMessageBox.information(parent, "Check for Updates", "You are using the latest version."))
    help_menu.addAction(check_updates_action)
    # Help action: shows help info
    help_action = QAction("Help", menu_bar)
    help_action.triggered.connect(lambda: QMessageBox.information(parent, "Help", "For help, visit the documentation or contact support."))
    help_menu.addAction(help_action)

    menu_bar.addMenu(help_menu)
    return menu_bar 