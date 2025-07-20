from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QGridLayout, QApplication, QFrame
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt, QSize
from core.rep_counter import start_workout
from core.free_for_all import main as free_for_all_main
import sys


class FitnessApp(QWidget):
    def __init__(self, user_id=None, display_name="User"):
        super().__init__()
        self.user_id = user_id
        self.display_name = display_name
        self.setWindowTitle("Fitness AI App 💪")
        self.showFullScreen()

        # Load custom font
        font_db = QFont("Segoe UI", 18, QFont.Weight.Bold)
        QApplication.instance().setFont(font_db)

        # Header Frame
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border: 1px solid #FFCA28;
                border-radius: 12px;
                padding: 15px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
        """)

        # Title and Welcome
        self.title_label = QLabel(f"Welcome, {self.display_name}! Choose Your Workout:")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #FFCA28;
            padding: 15px;
            font-family: 'Segoe UI', Arial, sans-serif;
        """)

        # Back Button
        self.back_button = QPushButton("← Back to Dashboard")
        self.back_button.setFixedSize(180, 50)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #2A2A2A;
                color: #FFCA28;
                border: 1px solid #FFCA28;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                transition: all 0.2s ease;
            }
            QPushButton:hover {
                background-color: #3A3A3A;
                border-color: #FFD700;
            }
            QPushButton:pressed {
                background-color: #1E1E1E;
            }
            QPushButton:checked {
                background-color: #FFCA28;
                color: #121212;
                font-weight: bold;
            }
        """)
        self.back_button.clicked.connect(self.go_back_to_dashboard)

        # Header Layout
        header_layout = QVBoxLayout()
        header_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)
        header_layout.addWidget(self.title_label)
        header_frame.setLayout(header_layout)

        # Workout icons
        icon_paths = {
            "Curl": "assets/icons/curl.png",
            "Pushup": "assets/icons/pushup.png",
            "Situp": "assets/icons/situp.png",
            "Squat": "assets/icons/squat.png",
            "Plank": "assets/icons/plank.png",
            "Let AI Detect": "assets/icons/ai.png"
        }

        # Workout Buttons
        self.workout_buttons = {}
        button_container = QFrame()
        button_container.setStyleSheet("""
            background-color: #1E1E1E;
            border-radius: 12px;
            padding: 15px;
            margin-top: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        """)
        
        self.buttons_grid = QGridLayout()
        self.buttons_grid.setHorizontalSpacing(20)
        self.buttons_grid.setVerticalSpacing(60)
        workout_names = list(icon_paths.keys())
        
        for index, name in enumerate(workout_names):
            btn = QPushButton(f"  {name}")
            btn.setFixedSize(250, 100)
            btn.setIcon(QIcon(icon_paths[name]))
            btn.setIconSize(QSize(32, 32))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2A2A2A;
                    color: #FFFFFF;
                    border: 1px solid #FFCA28;
                    border-radius: 8px;
                    padding: 15px;
                    font-size: 18px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    text-align: left;
                    font-weight: bold;
                    transition: all 0.2s ease;
                }
                QPushButton:hover {
                    background-color: #3A3A3A;
                    border-color: #FFD700;
                }
                QPushButton:pressed {
                    background-color: #1E1E1E;
                }
                QPushButton:checked {
                    background-color: #FFCA28;
                    color: #121212;
                    font-weight: bold;
                }
            """)
            btn.clicked.connect(self.start_selected_workout)
            self.workout_buttons[name] = btn
            
            row = index // 3
            col = index % 3
            self.buttons_grid.addWidget(btn, row, col, alignment=Qt.AlignmentFlag.AlignCenter)
        
        button_container.setLayout(self.buttons_grid)

        # Main Layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(header_frame)
        layout.addWidget(button_container, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        self.setLayout(layout)

        # Window Style
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #121212, stop:1 #1E1E1E);
                color: #FFFFFF;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                font-size: 16px;
            }
        """)

    def start_selected_workout(self):
        clicked_button = self.sender()
        choice = clicked_button.text().strip().lower() if clicked_button else None
        self.hide()

        result = None
        if choice:
            if "let ai detect" in choice:
                result = free_for_all_main(user_id=self.user_id)
            else:
                start_workout(workout_type=choice, user_id=self.user_id)

        if result == "done":
            from ui.dashboard import Dashboard
            self.dashboard = Dashboard(user_id=self.user_id, display_name=self.display_name)
            self.dashboard.show()

        self.close()

    def go_back_to_dashboard(self):
        from ui.dashboard import Dashboard
        self.dashboard = Dashboard(user_id=self.user_id, display_name=self.display_name)
        self.dashboard.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = FitnessApp(user_id="test_user")
    win.show()
    sys.exit(app.exec())