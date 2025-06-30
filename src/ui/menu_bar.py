from PySide6.QtGui import QAction, QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QMenuBar, QMenu, QMessageBox, QPushButton
import os
import zipfile
import webbrowser
from logger import get_error_logger, get_user_logger

# Creates and returns the main menu bar for the application
# Includes Help, About, and Check for Updates options

def create_menu_bar(parent=None):
    menu_bar = QMenuBar(parent)

    # Help menu
    help_menu = QMenu("Help", menu_bar)
    # About action: shows app info
    about_action = QAction("About", menu_bar)
    about_action.triggered.connect(lambda: QMessageBox.information(parent, "About", "Directory Tree Generator\nVersion 1.0.0\nCreated by Arthur-001"))
    help_menu.addAction(about_action)
    # Check for Updates action: placeholder for update logic
    check_updates_action = QAction("Check for Updates", menu_bar)
    check_updates_action.triggered.connect(lambda: QMessageBox.information(parent, "Check for Updates", "You are using the latest version."))
    help_menu.addAction(check_updates_action)
    # Help action: shows help info
    help_action = QAction("Help", menu_bar)
    help_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/Arthur-001/Directory-Tree-Generator")))
    help_menu.addAction(help_action)
    # Feedback action: compress logs and open GitHub issues
    feedback_action = QAction("Feedback", menu_bar)
    def send_feedback():
        logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
        os.makedirs(logs_dir, exist_ok=True)  # Ensure logs directory exists
        logs_json = os.path.join(logs_dir, 'Logs.json')
        zip_path = os.path.join(logs_dir, 'logs.zip')
        
        # If no logs exist
        if not os.path.exists(logs_json):
            msg = QMessageBox(parent)
            msg.setWindowTitle("Feedback")
            msg.setText("No logs are available to report, but you can still open an issue.")
            report_btn = msg.addButton("Report an Issue", QMessageBox.ActionRole)
            msg.addButton(QMessageBox.Cancel)
            msg.exec()
            if msg.clickedButton() == report_btn:
                webbrowser.open('https://github.com/Arthur-001/Directory-Tree-Generator/issues/new')
            return

        # If logs exist
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(logs_json, arcname='Logs.json')
        
        msg = QMessageBox(parent)
        msg.setWindowTitle("Feedback")
        msg.setText(f"A logs.zip file has been created.\nPlease upload it to the GitHub issue page.\n\nLocation: {zip_path}")
        report_btn = msg.addButton("Report an Issue", QMessageBox.ActionRole)
        msg.addButton(QMessageBox.Ok)
        msg.exec()
        if msg.clickedButton() == report_btn:
            webbrowser.open('https://github.com/Arthur-001/Directory-Tree-Generator/issues/new')
            
    feedback_action.triggered.connect(send_feedback)
    help_menu.addAction(feedback_action)

    menu_bar.addMenu(help_menu)
    return menu_bar 

user_logger = get_user_logger()
user_logger.info("User clicked Generate Tree") 