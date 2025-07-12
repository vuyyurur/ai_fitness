from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class MainAppWindow(QWidget):
    def __init__(self, display_name):
        super().__init__()
        self.setWindowTitle("Fitness Tracker")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()
        welcome_label = QLabel(f"Welcome to your Fitness Dashboard, {display_name}!")
        welcome_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(welcome_label)

        # You can add workout buttons or stats here

        self.setLayout(layout)
