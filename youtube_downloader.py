import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QFileDialog,
    QProgressBar,
    QTextEdit,
    QGroupBox,
    QCheckBox,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtSvg import QSvgWidget
import yt_dlp
import webbrowser
import shutil
import uuid
import re


class DownloaderThread(QThread):
    progress_signal = pyqtSignal(int)
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)

    def __init__(self, url, save_path, filename, quality, format_type, force_download):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.filename = filename
        self.quality = quality
        self.format_type = format_type
        self.force_download = force_download
        self.ydl_opts = {}
        self.temp_id = str(uuid.uuid4())[:8]  # Generate a unique ID for temp file

    def progress_hook(self, d):
        if d["status"] == "downloading":
            # Calculate download progress
            if "total_bytes" in d and d["total_bytes"] > 0:
                percent = int(d["downloaded_bytes"] / d["total_bytes"] * 100)
                self.progress_signal.emit(percent)
            elif "total_bytes_estimate" in d and d["total_bytes_estimate"] > 0:
                percent = int(d["downloaded_bytes"] / d["total_bytes_estimate"] * 100)
                self.progress_signal.emit(percent)

            # Log download speed and ETA
            if "_percent_str" in d and "_speed_str" in d and "_eta_str" in d:
                self.log_signal.emit(
                    f"Progress: {d['_percent_str']} | Speed: {d['_speed_str']} | ETA: {d['_eta_str']}"
                )

        elif d["status"] == "finished":
            self.log_signal.emit("Download completed, now processing...")

    def run(self):
        try:
            # Get quality suffix - only for video format
            quality_suffix = ""
            if self.format_type == "video":
                if self.quality == "Low":
                    quality_suffix = "-low"
                elif self.quality == "Medium":
                    quality_suffix = "-medium"
                elif self.quality == "High":
                    quality_suffix = "-high"

            # First get video information without downloading
            with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
                info_dict = ydl.extract_info(self.url, download=False)
                video_title = info_dict.get("title", "Unknown")

                # Clean up the video title for use as a filename
                safe_title = "".join(
                    c for c in video_title if c.isalnum() or c in " _-()[]{}.,"
                ).strip()
                safe_title = re.sub(
                    r"\s+", " ", safe_title
                )  # Replace multiple spaces with a single space

                # Determine the file extension
                if self.format_type == "audio":
                    ext = "mp3"
                else:
                    ext = "mp4"

                # Determine the final filename
                if self.filename:
                    base_filename = self.filename
                else:
                    base_filename = safe_title

                final_filename = f"{base_filename}{quality_suffix}.{ext}"
                final_path = os.path.join(self.save_path, final_filename)

                # Check if the file with this quality already exists
                if os.path.exists(final_path) and not self.force_download:
                    self.log_signal.emit(f"File already exists: {final_filename}")
                    self.log_signal.emit(
                        "Use 'Force download' option to redownload it."
                    )
                    self.finished_signal.emit("Download skipped - file exists")
                    return

                # File doesn't exist or force download is enabled, proceed with download
                self.log_signal.emit(f"Starting download: {self.url}")
                self.log_signal.emit(f"Video title: {video_title}")

                # Use a temporary filename for initial download to avoid conflicts
                temp_template = os.path.join(
                    self.save_path, f"temp_{self.temp_id}.%(ext)s"
                )

                # Setup yt-dlp options based on quality and format
                self.ydl_opts = {
                    "progress_hooks": [self.progress_hook],
                    "outtmpl": temp_template,
                    "no_warnings": False,
                    "quiet": False,
                    "verbose": False,
                }

                # Force download even if file exists
                if self.force_download:
                    self.ydl_opts["overwrites"] = True

                if self.format_type == "video":
                    if self.quality == "Low":
                        self.ydl_opts.update(
                            {
                                "format": "worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst[ext=mp4]",
                            }
                        )
                    elif self.quality == "Medium":
                        self.ydl_opts.update(
                            {
                                "format": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]",
                            }
                        )
                    elif self.quality == "High":
                        self.ydl_opts.update(
                            {
                                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
                            }
                        )

                elif self.format_type == "audio":
                    self.ydl_opts.update(
                        {
                            "format": "bestaudio/best",
                            "postprocessors": [
                                {
                                    "key": "FFmpegExtractAudio",
                                    "preferredcodec": "mp3",
                                    "preferredquality": "192",
                                }
                            ],
                        }
                    )

                # Log options for debugging
                self.log_signal.emit(
                    f"Download options: format={self.format_type}, quality={self.quality}"
                )

                # Download the video
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    ydl.extract_info(self.url, download=True)

                    # Find the temporary file
                    temp_file = os.path.join(
                        self.save_path, f"temp_{self.temp_id}.{ext}"
                    )

                    # If the final file already exists, remove it (in case of force download)
                    if os.path.exists(final_path):
                        os.remove(final_path)

                    # Move the temp file to the final location
                    if os.path.exists(temp_file):
                        shutil.move(temp_file, final_path)
                        self.log_signal.emit(f"Saved as: {final_filename}")
                    else:
                        # If the temp file doesn't exist, try to find it with other naming conventions
                        self.log_signal.emit(
                            f"Looking for downloaded file (temp file not found at: {temp_file})"
                        )

                        # Try other potential filenames
                        temp_audio_file = os.path.join(
                            self.save_path, f"temp_{self.temp_id}.{ext}"
                        )
                        if os.path.exists(temp_audio_file):
                            shutil.move(temp_audio_file, final_path)
                            self.log_signal.emit(f"Saved as: {final_filename}")
                            return

                        # Last resort: check for any recently created files
                        for file in os.listdir(self.save_path):
                            if file.startswith("temp_") and (
                                file.endswith(f".{ext}") or file.endswith(".webm")
                            ):
                                source_path = os.path.join(self.save_path, file)
                                shutil.move(source_path, final_path)
                                self.log_signal.emit(f"Saved as: {final_filename}")
                                return

                        self.log_signal.emit(
                            f"Warning: Could not find the downloaded file. It may be saved with a different name."
                        )
                        self.log_signal.emit(
                            f"Check the {self.save_path} directory for new files."
                        )

                self.finished_signal.emit("Download completed successfully!")

        except yt_dlp.utils.DownloadError as e:
            self.log_signal.emit(f"Error: {str(e)}")
            self.finished_signal.emit("Download failed")
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")
            self.finished_signal.emit("Download failed")


class YouTubeDownloaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("YouTube Downloader")
        self.setGeometry(100, 100, 600, 500)

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        # URL section
        url_group = QGroupBox("Video URL")
        url_layout = QHBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube video link here")
        url_layout.addWidget(self.url_input)

        url_group.setLayout(url_layout)
        main_layout.addWidget(url_group)

        # Options section
        options_group = QGroupBox("Download Options")
        options_layout = QVBoxLayout()

        # Format selection
        format_layout = QHBoxLayout()
        format_label = QLabel("Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["video", "audio"])
        self.format_combo.setFixedWidth(200)
        self.format_combo.currentTextChanged.connect(self.format_changed)
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        options_layout.addLayout(format_layout)

        # Quality selection
        quality_layout = QHBoxLayout()
        quality_label = QLabel("Quality:")
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Low", "Medium", "High"])
        self.quality_combo.setFixedWidth(200)
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_combo)
        quality_layout.addStretch()
        options_layout.addLayout(quality_layout)

        # Force download checkbox
        force_layout = QHBoxLayout()
        self.force_checkbox = QCheckBox(
            "Force download (redownload even if file exists)"
        )
        self.force_checkbox.setChecked(False)  # Default to unchecked
        force_layout.addWidget(self.force_checkbox)
        options_layout.addLayout(force_layout)

        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)

        # Save options section
        save_group = QGroupBox("Save Options")
        save_layout = QVBoxLayout()

        # Directory selection
        dir_layout = QHBoxLayout()
        dir_label = QLabel("Directory:")
        self.dir_input = QLineEdit()
        self.dir_input.setReadOnly(True)
        self.dir_input.setText(os.path.expanduser("~/Downloads"))
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(browse_btn)
        save_layout.addLayout(dir_layout)

        # Filename input
        filename_layout = QHBoxLayout()
        filename_label = QLabel("Filename:")
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText(
            "File name (empty = original YouTube title)"
        )
        filename_layout.addWidget(filename_label)
        filename_layout.addWidget(self.filename_input)
        save_layout.addLayout(filename_layout)

        save_group.setLayout(save_layout)
        main_layout.addWidget(save_group)

        # Progress bar
        progress_group = QGroupBox("Download Progress")
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)

        # Action buttons
        buttons_layout = QHBoxLayout()

        # Check if SVG file exists
        svg_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "bmc-button.svg"
        )
        self.button_width = 170  # Default width
        self.button_height = 40  # Default height

        if os.path.exists(svg_path):
            # Use SVG for Buy me a coffee button
            coffee_widget = QWidget()
            coffee_layout = QHBoxLayout(coffee_widget)
            coffee_layout.setContentsMargins(0, 0, 0, 0)

            self.svg_widget = QSvgWidget(svg_path)
            self.svg_widget.setFixedSize(QSize(self.button_width, self.button_height))
            coffee_layout.addWidget(self.svg_widget)

            coffee_widget.setCursor(Qt.PointingHandCursor)
            coffee_widget.mouseReleaseEvent = self.open_coffee_link

            buttons_layout.addWidget(coffee_widget)
        else:
            # Fallback to regular button if SVG is not found
            self.coffee_btn = QPushButton("Buy me a coffee")
            self.coffee_btn.setFixedSize(QSize(self.button_width, self.button_height))
            self.coffee_btn.clicked.connect(self.open_coffee_link)
            buttons_layout.addWidget(self.coffee_btn)
            self.log("SVG button image not found, using text button instead")

        buttons_layout.addStretch()

        # Download button - make same size as coffee button
        self.download_btn = QPushButton("Download")
        self.download_btn.setFixedSize(QSize(self.button_width, self.button_height))
        self.download_btn.clicked.connect(self.start_download)
        buttons_layout.addWidget(self.download_btn)

        main_layout.addLayout(buttons_layout)

        # Log window
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(100)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)

        # Set main layout
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Initialize log
        self.log("Application ready")

    def format_changed(self, format_type):
        """Handle format selection change to enable/disable quality options"""
        if format_type == "audio":
            # For audio format, quality doesn't apply the same way
            self.quality_combo.setEnabled(False)
            self.log(
                "Note: For audio format, quality selection is not applicable (always best quality)"
            )
        else:
            self.quality_combo.setEnabled(True)

    def log(self, message):
        self.log_text.append(message)
        # Auto-scroll to bottom
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        if directory:
            self.dir_input.setText(directory)
            self.log(f"Selected directory: {directory}")

    def open_coffee_link(self, event=None):
        self.log("Opening Buy me a coffee link...")
        webbrowser.open("https://buymeacoffee.com/4dpbvzmph0")

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            self.log("Error: Please enter a video URL")
            return

        save_path = self.dir_input.text()
        filename = self.filename_input.text()
        quality = self.quality_combo.currentText()
        format_type = self.format_combo.currentText()
        force_download = self.force_checkbox.isChecked()

        # Reset progress bar
        self.progress_bar.setValue(0)

        # Disable download button during download
        self.download_btn.setEnabled(False)

        # Start download thread
        self.download_thread = DownloaderThread(
            url, save_path, filename, quality, format_type, force_download
        )
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.log_signal.connect(self.log)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def download_finished(self, message):
        self.log(message)
        self.download_btn.setEnabled(True)


# If running this script directly, create the sample SVG file if it doesn't exist
if __name__ == "__main__":
    # Create a sample Buy Me a Coffee SVG if it doesn't exist
    svg_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "bmc-button.svg"
    )
    if not os.path.exists(svg_path):
        with open(svg_path, "w") as f:
            f.write(
                """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="170" height="40" viewBox="0 0 170 40" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- Yellow background -->
  <rect width="170" height="40" rx="8" fill="#FFDD00"/>
  
  <!-- Coffee cup icon -->
  <g transform="translate(15, 8)">
    <path d="M10 3C13.5 3 15 5 15 8C15 11 13.5 21 13.5 21H6.5C6.5 21 5 11 5 8C5 5 6.5 3 10 3Z" stroke="black" stroke-width="2" fill="white"/>
    <path d="M5 10H3C2 10 1 9 1 8C1 7 2 6 3 6H5" stroke="black" stroke-width="2"/>
    <path d="M15 7H17C18 7 19 8 19 9C19 10 18 11 17 11H15" stroke="black" stroke-width="2"/>
    <path d="M7 23H13" stroke="black" stroke-width="2"/>
  </g>
  
  <!-- Buy me a coffee text -->
  <text x="45" y="24" font-family="Arial" font-size="14" font-weight="bold" fill="black">Buy me a coffee</text>
</svg>"""
            )

    app = QApplication(sys.argv)
    window = YouTubeDownloaderApp()
    window.show()
    sys.exit(app.exec_())
