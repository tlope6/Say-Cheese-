import sys
from PyQt5.QtWidgets import QApplication
from ui.ui import AppUI
from vision.camera import capture_frame
from data.database import log_action


def handle_click() :
    success = capture_frame()
    if success :
        log_action("Camera capture")
        print("Captured and logged!")



app = QApplication(sys.argv)
window = AppUI(handle_click)
window.show()
sys.exit(app.exec_())