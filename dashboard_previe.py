import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QComboBox, QListWidget, QFrame, QCalendarWidget, QSizePolicy, QScrollArea
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

# --- Widget 1: Weekly / Monthly Summary Card ---
class SummaryCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #222; border-radius: 8px; padding: 10px;")
        layout = QVBoxLayout(self)

        title = QLabel("Weekly Summary")
        title.setStyleSheet("font-weight: bold; font-size: 18px; color: orange;")
        layout.addWidget(title)

        reps = QLabel("Total Reps: 350")
        calories = QLabel("Calories Burned: 1200")
        duration = QLabel("Duration: 5h 20m")

        for lbl in (reps, calories, duration):
            lbl.setStyleSheet("font-size: 14px; color: white;")
            layout.addWidget(lbl)

# --- Widget 2: Calendar View ---
class CalendarWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        calendar = QCalendarWidget()
        calendar.setGridVisible(True)
        layout.addWidget(calendar)

# --- Widget 3: Progress Chart ---
class ProgressChart(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.figure, self.ax = plt.subplots(figsize=(4,2))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.plot()

    def plot(self):
        dates = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        reps = [50, 45, 55, 60, 52, 48, 65]
        self.ax.clear()
        self.ax.plot(dates, reps, marker='o', color='orange')
        self.ax.set_title("Reps Over Past Week")
        self.ax.set_ylabel("Reps")
        self.canvas.draw()

# --- Widget 4: Achievements ---
class AchievementCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #222; border-radius: 8px; padding: 10px;")
        layout = QHBoxLayout(self)

        badge = QLabel()
        # Just use a colored square as placeholder for icon
        badge.setStyleSheet("background-color: gold; border-radius: 10px; min-width: 40px; min-height: 40px;")
        layout.addWidget(badge)

        label = QLabel("🔥 100 Reps in a Day!")
        label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        layout.addWidget(label)

# --- Widget 5: Voice Commands Summary ---
class VoiceCommandsSummary(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        # Add some dummy commands
        commands = ["Start workout", "Pause", "I'm tired", "Stop"]
        for cmd in commands:
            self.list_widget.addItem(cmd)

# --- Widget 6: Mood History ---
class MoodHistory(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        moods = ["😊", "😐", "😟", "😊", "😊", "😐"]
        for mood in moods:
            lbl = QLabel(mood)
            lbl.setStyleSheet("font-size: 24px; padding: 5px;")
            layout.addWidget(lbl)

# --- Widget 7: Form Breakdown Chart ---
class FormBreakdownChart(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.figure, self.ax = plt.subplots(figsize=(3,3))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.plot()

    def plot(self):
        labels = ['Good Form', 'Bad Form']
        sizes = [75, 25]
        colors = ['#4CAF50', '#F44336']
        self.ax.clear()
        self.ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        self.ax.set_title("Form Quality Breakdown")
        self.canvas.draw()

# --- Widget 8: User Switcher ---
class UserSwitcher(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.combo = QComboBox()
        self.combo.addItems(["User1", "User2", "Guest"])
        layout.addWidget(QLabel("Switch User:"))
        layout.addWidget(self.combo)


class StreakCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #2E2E2E; border-radius: 8px; padding: 10px;")
        layout = QVBoxLayout(self)

        title = QLabel("🔥 Longest Streak")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: orange;")
        layout.addWidget(title)

        days = QLabel("7 days in a row")
        days.setStyleSheet("font-size: 16px; color: white;")
        layout.addWidget(days)

class MostPerformedWorkout(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        label = QLabel("🏋️ Most Performed Workout")
        label.setStyleSheet("font-size: 18px; font-weight: bold; color: orange;")
        workout = QLabel("Pushups - 450 reps")
        workout.setStyleSheet("font-size: 16px; color: white;")
        layout.addWidget(label)
        layout.addWidget(workout)

class WorkoutHeatmap(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day in days:
            lbl = QLabel(day)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("background-color: #444; color: white; border-radius: 5px; padding: 8px; margin: 2px;")
            layout.addWidget(lbl)
class TodaysGoalsCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #202020; border-radius: 10px; padding: 12px;")
        layout = QVBoxLayout(self)

        title = QLabel("🎯 Today's Goals")
        title.setStyleSheet("color: orange; font-weight: bold; font-size: 16px;")
        layout.addWidget(title)

        goals = ["✅ 50 pushups", "❌ 10 minutes plank", "✅ 100 calories"]
        for g in goals:
            lbl = QLabel(g)
            lbl.setStyleSheet("color: white; font-size: 14px;")
            layout.addWidget(lbl)

class ActiveTimeChart(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.figure, self.ax = plt.subplots(figsize=(3,3))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.plot()

    def plot(self):
        labels = ['Pushups', 'Squats', 'Curls', 'Plank']
        times = [20, 15, 10, 5]  # in minutes
        self.ax.clear()
        self.ax.pie(times, labels=labels, autopct='%1.1f%%', startangle=140)
        self.ax.set_title("Workout Time Split")
        self.canvas.draw()
class LastSessionsRecap(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("🗓️ Last 5 Sessions")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: orange;")
        layout.addWidget(title)

        sessions = [
            "Jul 1: 120 reps, 75 cal",
            "Jul 2: 140 reps, 90 cal",
            "Jul 3: 100 reps, 60 cal",
            "Jul 4: 80 reps, 45 cal",
            "Jul 5: 160 reps, 100 cal"
        ]

        for s in sessions:
            lbl = QLabel(s)
            lbl.setStyleSheet("font-size: 14px; color: white;")
            layout.addWidget(lbl)
class TopVoiceCommands(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.plot()

    def plot(self):
        commands = ['Start', 'Pause', 'Break', 'Stop']
        usage = [10, 7, 5, 3]
        self.ax.clear()
        self.ax.bar(commands, usage, color='orange')
        self.ax.set_title("Top Voice Commands")
        self.canvas.draw()
class MoodTrendChart(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.plot()

    def plot(self):
        moods = [3, 2, 1, 3, 2, 3, 3]  # 3=happy, 2=neutral, 1=sad
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        self.ax.clear()
        self.ax.plot(days, moods, marker='o', color='lime')
        self.ax.set_title("Mood Over the Week")
        self.ax.set_ylim(0, 4)
        self.ax.set_yticks([1,2,3])
        self.ax.set_yticklabels(["😟", "😐", "😊"])
        self.canvas.draw()

# --- Main Window to display all ---
class DashboardDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard Preview")
        self.setStyleSheet("background-color: #121212; color: white;")
        main_layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)
        layout = QVBoxLayout(container)
        layout.setSpacing(20)

        # Add each widget with a label
        def add_section(title, widget):
            lbl = QLabel(f"<b style='color:orange;'>{title}</b>")
            layout.addWidget(lbl)
            layout.addWidget(widget)
        
        add_section("1. Weekly / Monthly Summary Card", SummaryCard())
        add_section("2. Calendar View", CalendarWidget())
        add_section("3. Progress Chart", ProgressChart())
        add_section("4. Achievements Section", AchievementCard())
        add_section("5. Voice Commands Summary", VoiceCommandsSummary())
        add_section("6. Mood History", MoodHistory())
        add_section("7. Form Breakdown Chart", FormBreakdownChart())
        add_section("8. User Switcher", UserSwitcher())
        add_section("9. Longest Streak", StreakCard())
        add_section("10. Most Performed Workout", MostPerformedWorkout())
        add_section("11. Workout Heatmap", WorkoutHeatmap())
        add_section("12. Today's Goals", TodaysGoalsCard())
        add_section("13. Active Time Breakdown", ActiveTimeChart())
        add_section("14. Last 5 Sessions", LastSessionsRecap())
        add_section("15. Top Voice Commands", TopVoiceCommands())
        add_section("16. Mood Trend Line", MoodTrendChart())



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashboardDemo()
    window.resize(600, 900)
    window.show()
    sys.exit(app.exec())
