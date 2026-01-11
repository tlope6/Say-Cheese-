from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QWidget, QVBoxLayout
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
import numpy as np

from vision.camera import Camera

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Say Cheese?")
        self.setGeometry(100, 100, 900, 600)

        # DARK THEME
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0e0e0e;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
        """)

        self.camera = Camera()

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout()
        central_widget.setLayout(self.main_layout)

        # Status Label
        self.status_label = QLabel("🔍 Scanning for presence...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.status_label)

        # Camera Display
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setStyleSheet("""
            QLabel {
                border: 2px solid #1f1f1f;
                background-color: #000000;
            }
        """)
        self.main_layout.addWidget(self.camera_label)

        # Timer for live feed
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # ~30 FPS

    def update_frame(self):
        frame, face_detected = self.camera.get_frame()
        if frame is None:
            return

        # frame, face_detected = result

        if face_detected:
            self.status_label.setText("👁 Face detected — analyzing...")
            self.status_label.setStyleSheet("color: #00ff99;")
        else:
            self.status_label.setText("🔍 Scanning for presence...")
            self.status_label.setStyleSheet("color: #ffffff;")

        height, width, channels = frame.shape
        bytes_per_line = channels * width

        qt_image = QImage(
            frame.data,
            width,
            height,
            bytes_per_line,
            QImage.Format_RGB888
        )

        pixmap = QPixmap.fromImage(qt_image)
        self.camera_label.setPixmap(
            pixmap.scaled(
                self.camera_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )


    def closeEvent(self, event):
        self.camera.release()
        event.accept()
