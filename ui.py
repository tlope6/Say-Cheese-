from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout

class AppUI(QWidget) :
    def __init__(self, on_click) :
        super().__init__()
        self.setWindowTItle("Say Cheese?")

        button = QPushButton("📷 Capture")
        button.clicked.connect(on_click)

        layout = QVBoxLayout()
        layout.addWidget(button)
        self.setLayout(layout)


    