import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import mplcursors

class WeeklyLineSummary(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Dummy weekly data
        self.data = [
            {"day": "Mon", "reps": 120, "calories": 80, "details": {"pushups": 30, "squats": 40, "curls": 20, "situps": 30}},
            {"day": "Tue", "reps": 90,  "calories": 60, "details": {"pushups": 20, "squats": 25, "curls": 15, "situps": 30}},
            {"day": "Wed", "reps": 150, "calories": 100, "details": {"pushups": 40, "squats": 50, "curls": 30, "situps": 30}},
            {"day": "Thu", "reps": 70,  "calories": 50, "details": {"pushups": 15, "squats": 25, "curls": 10, "situps": 20}},
            {"day": "Fri", "reps": 180, "calories": 120, "details": {"pushups": 50, "squats": 60, "curls": 40, "situps": 30}},
            {"day": "Sat", "reps": 140, "calories": 95, "details": {"pushups": 35, "squats": 45, "curls": 30, "situps": 30}},
            {"day": "Sun", "reps": 100, "calories": 70, "details": {"pushups": 25, "squats": 35, "curls": 20, "situps": 20}},
        ]

        # Matplotlib plot
        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.plot()

    def plot(self):
        self.ax.clear()
        days = [d["day"] for d in self.data]
        reps = [d["reps"] for d in self.data]

        # Plotting line chart with points
        line, = self.ax.plot(days, reps, marker='o', color="orange", linewidth=2)

        self.ax.set_title("Weekly Reps Summary (Line Graph)")
        self.ax.set_ylabel("Total Reps")
        self.ax.grid(True, linestyle="--", alpha=0.3)

        # Enable hover tooltips on the points
        cursor = mplcursors.cursor([line], hover=True)

        @cursor.connect("add")
        def on_hover(sel):
            idx = sel.index
            day_data = self.data[idx]
            details = day_data["details"]
            text = f"{day_data['day']}\nTotal: {day_data['reps']} reps\nCalories: {day_data['calories']} cal"
            for k, v in details.items():
                text += f"\n{k.capitalize()}: {v}"
            sel.annotation.set_text(text)
            sel.annotation.get_bbox_patch().set(fc="black", alpha=0.8)
            sel.annotation.set_fontsize(10)
            sel.annotation.set_color("white")

        self.canvas.draw()

# Run it standalone
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WeeklyLineSummary()
    window.setWindowTitle("Weekly Line Chart")
    window.resize(640, 480)
    window.show()
    sys.exit(app.exec())
