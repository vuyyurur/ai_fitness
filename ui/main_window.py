# ui/main_window.py
""" from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QComboBox
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPixmap, QImage
import sys
import cv2
from core.rep_counter import start_workout
from core.free_for_all import main as free_for_all_main

class FitnessApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fitness AI App 💪")
        self.setFixedSize(800, 600)

        self.video_label = QLabel("Webcam feed will show here.")
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setFixedSize(640, 480)

        self.workout_selector = QComboBox()
        self.workout_selector.addItems(["Select Workout", "Curls", "Pushups", "Situps", "Squats", "Plank", "Let AI Detect"])

        self.start_button = QPushButton("Start Workout")
        self.start_button.clicked.connect(self.start_selected_workout)

        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.workout_selector)
        layout.addWidget(self.start_button)

        self.setLayout(layout)

        # Webcam setup
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(image))

    def start_selected_workout(self):
        choice = self.workout_selector.currentText().lower()
        self.cap.release()  # close webcam for main logic to take over
        self.timer.stop()
        self.hide()

        if "let ai detect" in choice:
            free_for_all_main()
        else:
            start_workout(workout_type=choice)

        self.close()

def launch_app():
    app = QApplication(sys.argv)
    window = FitnessApp()
    window.show()
    sys.exit(app.exec()) """

# ui/main_window.py

from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QComboBox
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPixmap, QImage
import cv2
from core.rep_counter import start_workout
from core.free_for_all import main as free_for_all_main


class FitnessApp(QWidget):
    def __init__(self, user_id=None, display_name="User"):  # ✅ Accept user_id
        super().__init__()
        self.showFullScreen()
        self.user_id = user_id         # ✅ Store user_id
        self.display_name = display_name
        self.setWindowTitle("Fitness AI App 💪")
        self.setFixedSize(800, 600)

        self.video_label = QLabel("Webcam feed will show here.")
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setFixedSize(640, 480)

        self.workout_selector = QComboBox()
        self.workout_selector.addItems([
            "Select Workout", "Curls", "Pushups", "Situps", "Squats", "Plank", "Let AI Detect"
        ])

        self.start_button = QPushButton("Start Workout")
        self.start_button.clicked.connect(self.start_selected_workout)

        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.workout_selector)
        layout.addWidget(self.start_button)

        self.setLayout(layout)

        # Webcam setup
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.setStyleSheet("""
            QWidget {
                background-color: #343434;
                color: #FFA500;
                font-family: Arial;
            }
            QLabel {
                font-size: 14px;
            }
            QComboBox {
                background-color: #343434;
                color: #FFA500;
                border: 1px solid #FFA500;
                padding: 5px;
            }
            QPushButton {
                background-color: #343434;
                color: #FFA500;
                border: 2px solid #FFA500;
                padding: 10px;
                font-size: 16px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #343434;
            }
            QPushButton:pressed {
                background-color: #343434;
            }
        """)
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()


    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(image))

    def start_selected_workout(self):
        choice = self.workout_selector.currentText().lower()
        self.cap.release()  # Close webcam
        self.timer.stop()
        self.hide()
        result = None  # initialize result


        if "let ai detect" in choice:
            result = free_for_all_main(user_id=self.user_id)
        if result == "done":
            from ui.dashboard import Dashboard
            self.dashboard = Dashboard(user_id=self.user_id, display_name=self.display_name)
            self.dashboard.show()
        else:
            start_workout(workout_type=choice)



        self.close()


# Only used when run directly
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    win = FitnessApp(user_id="test_user")  # ✅ Pass dummy ID for standalone testing
    win.show()
    win.showFullScreen()()
    sys.exit(app.exec())
