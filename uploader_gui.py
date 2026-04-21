import os
import glob
import boto3
from botocore.config import Config
from dotenv import load_dotenv
import sys

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QPushButton, QLabel, QFileDialog, QProgressBar, 
    QTextEdit, QFrame
)
from PyQt6.QtCore import QThread, pyqtSignal, QObject, Qt
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette

# Load environment variables
load_dotenv()

class UploadWorker(QObject):
    progress = pyqtSignal(int, int)  # current, total
    log = pyqtSignal(str, bool)     # message, is_error
    finished = pyqtSignal(int)      # final success count

    def __init__(self, folder_path, prefix):
        super().__init__()
        self.folder_path = folder_path
        self.prefix = prefix
        self.is_running = True

    def run(self):
        # Initialize S3 client inside the thread for safety
        account_id = os.getenv("R2_ACCOUNT_ID")
        access_key = os.getenv("R2_ACCESS_KEY_ID")
        secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
        bucket_name = os.getenv("R2_BUCKET_NAME")

        if not all([account_id, access_key, secret_key, bucket_name]):
            self.log.emit("Missing credentials in .env file!", True)
            self.finished.emit(0)
            return

        s3 = boto3.client(
            's3',
            endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4'),
            region_name='auto'
        )

        if not os.path.exists(self.folder_path):
            self.log.emit(f"Folder '{self.folder_path}' not found.", True)
            self.finished.emit(0)
            return

        files = glob.glob(os.path.join(self.folder_path, '**/*'), recursive=True)
        files = [f for f in files if os.path.isfile(f)]

        if not files:
            self.log.emit(f"No files found in '{self.folder_path}'.", False)
            self.finished.emit(0)
            return

        total_files = len(files)
        success_count = 0

        for i, file_path in enumerate(files):
            if not self.is_running:
                break
            
            relative_path = os.path.relpath(file_path, self.folder_path)
            object_name = os.path.join(self.prefix, relative_path).replace('\\', '/')
            
            try:
                s3.upload_file(file_path, bucket_name, object_name)
                self.log.emit(f"✓ {relative_path} → {object_name}", False)
                success_count += 1
            except Exception as e:
                self.log.emit(f"✗ {relative_path}: {str(e)}", True)
            
            self.progress.emit(i + 1, total_files)

        self.finished.emit(success_count)

    def stop(self):
        self.is_running = False

class ModernUploaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("R2 Cloud Uploader")
        self.setMinimumSize(600, 500)
        
        self.setup_ui()
        self.apply_styles()
        
        self.thread = None
        self.worker = None

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)

        # Header
        header_label = QLabel("Cloudflare R2 Uploader")
        header_label.setObjectName("header")
        main_layout.addWidget(header_label)

        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setObjectName("separator")
        main_layout.addWidget(line)

        # Source Section
        main_layout.addWidget(QLabel("Local Source Folder:"))
        source_layout = QHBoxLayout()
        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("Select folder to upload...")
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_folder)
        source_layout.addWidget(self.source_input)
        source_layout.addWidget(self.browse_btn)
        main_layout.addLayout(source_layout)

        # Target Section
        main_layout.addWidget(QLabel("R2 Target Prefix:"))
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("e.g. data/uploads/2026/")
        main_layout.addWidget(self.target_input)

        # Upload Button
        self.upload_btn = QPushButton("Start Upload")
        self.upload_btn.setObjectName("upload_btn")
        self.upload_btn.setMinimumHeight(40)
        self.upload_btn.clicked.connect(self.start_upload)
        main_layout.addWidget(self.upload_btn)

        # Progress Section
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%v/%m files")
        main_layout.addWidget(self.progress_bar)

        # Log Section
        main_layout.addWidget(QLabel("Upload Logs:"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Activity will be shown here...")
        main_layout.addWidget(self.log_output)

        # Footer status
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("status_footer")
        main_layout.addWidget(self.status_label)

    def apply_styles(self):
        # Premium Dark Theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 13px;
                font-weight: 500;
            }
            #header {
                font-size: 24px;
                font-weight: bold;
                color: #ffffff;
                margin-bottom: 5px;
            }
            #separator {
                background-color: #333333;
                height: 1px;
                border: none;
            }
            QLineEdit {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 10px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d4;
            }
            QPushButton {
                background-color: #333333;
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
                color: #ffffff;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
            #upload_btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0078d4, stop:1 #00bcff);
                color: white;
                font-size: 14px;
            }
            #upload_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1086e0, stop:1 #10c6ff);
            }
            #upload_btn:disabled {
                background: #555555;
                color: #888888;
            }
            QProgressBar {
                border: 1px solid #333333;
                border-radius: 6px;
                background-color: #1e1e1e;
                text-align: center;
                color: white;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 5px;
            }
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 10px;
                color: #d4d4d4;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
            #status_footer {
                color: #888888;
                font-size: 11px;
            }
        """)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Upload")
        if folder:
            self.source_input.setText(folder)

    def start_upload(self):
        source = self.source_input.text()
        target = self.target_input.text()

        if not source:
            self.log_message("Error: Please select a source folder.", True)
            return

        self.toggle_ui(False)
        self.log_output.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText("Uploading...")

        # Setup Threading
        self.thread = QThread()
        self.worker = UploadWorker(source, target)
        self.worker.moveToThread(self.thread)

        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.update_progress)
        self.worker.log.connect(self.log_message)
        self.worker.finished.connect(self.on_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def toggle_ui(self, enabled):
        self.upload_btn.setEnabled(enabled)
        self.browse_btn.setEnabled(enabled)
        self.source_input.setEnabled(enabled)
        self.target_input.setEnabled(enabled)

    def update_progress(self, current, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

    def log_message(self, message, is_error=False):
        color = "red" if is_error else "#00ff00" if "✓" in message else "#d4d4d4"
        self.log_output.append(f'<span style="color: {color}">{message}</span>')

    def on_finished(self, count):
        self.toggle_ui(True)
        self.status_label.setText(f"Finished! {count} files uploaded.")
        self.log_message(f"\n--- Upload Complete: {count} files successful ---")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernUploaderApp()
    window.show()
    sys.exit(app.exec())
