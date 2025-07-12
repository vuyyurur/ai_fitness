from pydoc import doc, text
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from datetime import date, datetime, timedelta

from sympy import false
from ui.main_window import FitnessApp  # adjust this if path is different
from firebase_admin import firestore
from firebase_client import db

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import mplcursors

from PyQt6.QtWidgets import QCalendarWidget

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QCalendarWidget
from datetime import datetime

import matplotlib.pyplot as plt



class Dashboard(QWidget):
    def __init__(self, user_id, display_name):  # ✅ Add user_id
        super().__init__()
        self.user_id = user_id                   # ✅ Store user_id for later
        self.display_name = display_name
        self.current_date = datetime.today().date()

        self.setWindowTitle("Fitness Dashboard")
        self.resize(800, 600)  # optional default starting size

         # Main layout - only one and set once!
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Scroll area setup
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.main_layout.addWidget(scroll_area)

        # Content widget inside scroll area
        content = QWidget()
        content_layout = QVBoxLayout(content)
        scroll_area.setWidget(content)

        # Welcome label
        welcome_label = QLabel(f"Welcome, {self.display_name}!")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        content_layout.addWidget(welcome_label)
        # --- Toggle Buttons for Dashboard Widgets ---
        toggle_layout = QHBoxLayout()

        self.line_toggle = QPushButton("📈 Line Summary")
        self.bar_toggle = QPushButton("📊 Bar Summary")
        self.calendar_toggle = QPushButton("📅 Calendar Stats")
        self.card_toggle = QPushButton("📋 Weekly Card")
        self.form_toggle = QPushButton("🥧 Form Quality")

        self.toggle_buttons = [
            (self.line_toggle, 'line'),
            (self.bar_toggle, 'bar'),
            (self.calendar_toggle, 'calendar'),
            (self.card_toggle, 'card'),
            (self.form_toggle, 'form')
        ]

        for btn, _ in self.toggle_buttons:
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #333;
                    color: #FFA500;
                    border: 2px solid #FFA500;
                    border-radius: 6px;
                    padding: 6px 12px;
                }
                QPushButton:checked {
                    background-color: #FFA500;
                    color: black;
                }
            """)
            toggle_layout.addWidget(btn)

        content_layout.addLayout(toggle_layout)

        # Create widgets first
        self.weekly_line_summary = QWidget()
        self.weekly_bar_summary = QWidget()
        self.calendar_widget = QWidget()

        # Define self.stats_card before using it
        self.stats_card = QFrame()
        self.stats_card.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 8px;
                padding: 10px;
                margin-top: 15px;
            }
        """)
        content_layout.addWidget(self.stats_card)

        # One stats_layout for stats_card
        stats_layout = QVBoxLayout(self.stats_card)

        # Date navigation
        date_nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("⬅️")
        self.next_btn = QPushButton("➡️")
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        date_nav_layout.addWidget(self.prev_btn)
        date_nav_layout.addWidget(self.date_label)
        date_nav_layout.addWidget(self.next_btn)
        stats_layout.addLayout(date_nav_layout)

        # Stats labels
        self.reps_label = QLabel()
        self.pushups_label = QLabel()
        self.squats_label = QLabel()
        self.curls_label = QLabel()
        self.situps_label = QLabel()
        self.plank_label = QLabel()
        self.calories_label = QLabel()
        self.duration_label = QLabel()

        for lbl in (
            self.reps_label, self.pushups_label, self.squats_label, self.curls_label,
            self.situps_label, self.plank_label, self.calories_label, self.duration_label
        ):
            lbl.setStyleSheet("font-size: 16px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stats_layout.addWidget(lbl)  # Add to stats_layout here!

        # Connect buttons
        self.prev_btn.clicked.connect(self.load_previous_day)
        self.next_btn.clicked.connect(self.load_next_day)

        # ======= ADD NEW DASHBOARD WIDGETS HERE =======

        # Weekly Summary Card (aggregate for past 7 days)
        self.weekly_summary_card = QFrame()
        self.weekly_summary_card.setStyleSheet("""
            QFrame {
                background-color: #222;
                border-radius: 8px;
                padding: 10px;
                margin-top: 15px;
            }
        """)
        weekly_layout = QVBoxLayout(self.weekly_summary_card)
        title = QLabel("Weekly Summary")
        title.setStyleSheet("font-weight: bold; font-size: 18px; color: orange;")
        weekly_layout.addWidget(title)

        self.weekly_reps_label = QLabel("Total Reps: Loading...")
        self.weekly_calories_label = QLabel("Calories Burned: Loading...")
        self.weekly_duration_label = QLabel("Duration: Loading...")

        for lbl in (self.weekly_reps_label, self.weekly_calories_label, self.weekly_duration_label):
            lbl.setStyleSheet("font-size: 14px; color: white;")
            weekly_layout.addWidget(lbl)

        content_layout.addWidget(self.weekly_summary_card)

        # Weekly Line Summary Widget
        self.weekly_line_summary.setStyleSheet("background-color: #1E1E1E; border-radius: 8px; padding: 10px; margin-top: 10px;")
        line_layout = QVBoxLayout(self.weekly_line_summary)
        content_layout.addWidget(self.weekly_line_summary)

        self.line_fig, self.line_ax = plt.subplots(figsize=(7, 3))
        self.line_canvas = FigureCanvas(self.line_fig)
        line_layout.addWidget(self.line_canvas)

        # Weekly Bar Summary Widget
        self.weekly_bar_summary.setStyleSheet("background-color: #1E1E1E; border-radius: 8px; padding: 10px; margin-top: 10px;")
        bar_layout = QVBoxLayout(self.weekly_bar_summary)
        content_layout.addWidget(self.weekly_bar_summary)

        self.bar_fig, self.bar_ax = plt.subplots(figsize=(7, 3))
        self.bar_canvas = FigureCanvas(self.bar_fig)
        bar_layout.addWidget(self.bar_canvas)

        # Calendar Widget
        self.calendar_widget.setStyleSheet("background-color: #1E1E1E; border-radius: 8px; padding: 10px; margin-top: 10px;")
        calendar_layout = QVBoxLayout(self.calendar_widget)
        content_layout.addWidget(self.calendar_widget)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        calendar_layout.addWidget(self.calendar)

        self.calendar_info_label = QLabel("Select a date to view stats")
        self.calendar_info_label.setStyleSheet("color: white; font-size: 14px; padding: 8px;")
        calendar_layout.addWidget(self.calendar_info_label)

        # Connect calendar selection to update info
        self.calendar.selectionChanged.connect(self.display_calendar_stats)

        # Then assign them to the dictionary
        self.toggle_sections = {
            'line': self.weekly_line_summary,
            'bar': self.weekly_bar_summary,
            'calendar': self.calendar_widget,
            'card': self.weekly_summary_card
        }

        # Define the toggle handler before using it
        def make_toggle_handler(selected_key):
            def handler():
                for key, widget in self.toggle_sections.items():
                    is_selected = (key == selected_key)
                    self.toggle_sections[key].setVisible(is_selected)
                    btn = next(btn for btn, k in self.toggle_buttons if k == key)
                    btn.setChecked(is_selected)
            return handler

        # Connect toggles
        for btn, key in self.toggle_buttons:
            btn.clicked.connect(make_toggle_handler(key))

        # Hide all except 'line' by default
        self.toggle_sections['line'].setVisible(True)
        for k in ('bar', 'calendar', 'card'):
            self.toggle_sections[k].setVisible(False)

        # Connect toggle visibility to buttons checked state
        self.line_toggle.toggled.connect(self.weekly_line_summary.setVisible)
        self.bar_toggle.toggled.connect(self.weekly_bar_summary.setVisible)
        self.calendar_toggle.toggled.connect(self.calendar_widget.setVisible)
        self.card_toggle.toggled.connect(self.weekly_summary_card.setVisible)

        # ======= END ADDITION OF NEW WIDGETS =======

        # Start workout button
        start_button = QPushButton("🚀 Start Workout")
        start_button.setFixedHeight(50)
        start_button.setStyleSheet("font-size: 18px;")
        content_layout.addWidget(start_button)
        start_button.clicked.connect(self.launch_main_app)

        # === How It Works ===
        how_it_works = QLabel(
            "🧠 How it works:\n\n"
            "- Counts reps via webcam\n"
            "- Detects bad form with AI\n"
            "- Responds to voice commands\n"
            "- Tracks your mood and progress\n\n"
        )
        how_it_works.setAlignment(Qt.AlignmentFlag.AlignCenter)
        how_it_works.setWordWrap(True)
        how_it_works.setStyleSheet("font-size: 14px; padding: 20px;")
        content_layout.addWidget(how_it_works)

        # Finalize scroll area
        scroll_area.setWidget(content)
        self.main_layout.addWidget(scroll_area)

        # Apply dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #FFA500;
                font-family: Arial;
            }
            QLabel {
                font-size: 16px;
            }
            QPushButton {
                background-color: #333333;
                color: #FFA500;
                border: 2px solid #FFA500;
                padding: 10px;
                font-size: 16px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
        """)

        # Load today's stats
        self.update_stats_view()

        # Load weekly data and plot everything
        self.load_and_plot_weekly_summary()
        self.load_and_plot_weekly_line()
        self.load_and_plot_weekly_bar()


    # ==== Stats Logic ====

    def update_stats_view(self):
        date_str = self.current_date.strftime("%B %d, %Y")
        self.date_label.setText(date_str)

        stats = self.get_stats_for_date(self.current_date)

        self.reps_label.setText(f"Reps: {stats.get('reps', 0)}")
        self.pushups_label.setText(f"Pushups: {stats.get('pushups', 0)}")
        self.squats_label.setText(f"Squats: {stats.get('squats', 0)}")
        self.curls_label.setText(f"Curls: {stats.get('curls', 0)}")
        self.situps_label.setText(f"Situps: {stats.get('situps', 0)}")
        self.plank_label.setText(f"Plank Time: {stats.get('plank_time', 0)} sec")
        self.calories_label.setText(f"Calories Burned: {stats.get('calories', 0)}")
        self.duration_label.setText(f"Duration: {stats.get('duration', 0)} min")

    def get_stats_for_date(self, date):
        date_str = date.strftime("%Y-%m-%d")
        doc_id = f"{self.user_id}_{date_str}"
        doc_ref = db.collection('workout_data').document(doc_id)
        doc = doc_ref.get()

        if doc.exists:
            data = doc.to_dict()
            pushups = data.get("pushups", 0)
            situps = data.get("situps", 0)
            squats = data.get("squats", 0)
            curls = data.get("curls", 0)
            reps = pushups + situps + squats + curls
            return {
                "reps": reps,
                "pushups": pushups,
                "situps": situps,
                "squats": squats,
                "curls": curls,
                "plank_time": data.get("plank_time", 0),
                "calories": data.get("calories", 0),
                "duration": data.get("duration", 0)
            }
        else:
            return {
                "reps": 0,
                "pushups": 0,
                "situps": 0,
                "squats": 0,
                "curls": 0,
                "plank_time": 0,
                "calories": 0,
                "duration": 0
            }


    def load_previous_day(self):
        self.current_date -= timedelta(days=1)
        self.update_stats_view()

    def load_next_day(self):
        self.current_date += timedelta(days=1)
        self.update_stats_view()

    def launch_main_app(self):
        self.fitness_app = FitnessApp(user_id=self.user_id)  # ✅ Send user_id
        self.fitness_app.show()
        self.close()

    # ==== New widget helpers ==== #

    def load_and_plot_weekly_summary(self):
        # Aggregate last 7 days of data for weekly summary card
        today = datetime.today().date()
        reps_total = 0
        calories_total = 0
        duration_total = 0

        for i in range(7):
            dt = today - timedelta(days=i)
            date_str = dt.strftime("%Y-%m-%d")
            doc_id = f"{self.user_id}_{date_str}"
            doc_ref = db.collection('workout_data').document(doc_id)
            doc = doc_ref.get()
            if doc.exists:
                d = doc.to_dict()
                reps_total += d.get("reps", 0)
                calories_total += d.get("calories", 0)
                duration_total += d.get("duration", 0)

        self.weekly_reps_label.setText(f"Total Reps: {reps_total}")
        self.weekly_calories_label.setText(f"Calories Burned: {calories_total}")
        self.weekly_duration_label.setText(f"Duration: {duration_total} min")

    def load_and_plot_weekly_line(self):
        data = self.load_weekly_data()  # Your existing method to get last 7 days

        self.line_ax.clear()
        days = [d["day"] for d in data]
        reps = [d["reps"] for d in data]

        # Plot line graph with circle markers
        line, = self.line_ax.plot(days, reps, marker='o', color="orange", linewidth=2)
        self.line_ax.set_title("Weekly Reps Summary (Line Graph)")
        self.line_ax.set_ylabel("Total Reps")
        self.line_ax.grid(True, linestyle="--", alpha=0.3)

        self.line_ax.set_ylim(0, 100)
        self.line_ax.relim()
        self.line_ax.autoscale_view()

        # Add mplcursors hover tooltips on data points
        cursor = mplcursors.cursor([line], hover=True)

        @cursor.connect("add")
        def on_hover(sel):
            try:
                # Index in the line data
                idx = sel.index  # This is always an integer index
                day_data = data[int(idx)]

                text = (
                    f"{day_data['day']}\n"
                    f"Total: {day_data['reps']} reps\n"
                    f"Calories: {day_data['calories']} cal"
                )

                for k, v in day_data["details"].items():
                    text += f"\n{k.capitalize()}: {v}"

                sel.annotation.set_text(text)
                sel.annotation.get_bbox_patch().set(fc="black", alpha=0.8)
                sel.annotation.set_fontsize(10)
                sel.annotation.set_color("white")
                sel.annotation.arrow_patch.set_visible(False)

            except Exception as e:
                print("Hover error:", e)

        self.line_canvas.draw()


    def load_weekly_data(self):
        data = []
        today = datetime.today()

        for i in range(6, -1, -1):  # 6 days ago to today
            day_date = today - timedelta(days=i)
            day_str = day_date.strftime("%a")  # 'Mon', 'Tue', etc.
            stats = self.get_stats_for_date(day_date)

            # Build 'details' from individual workout types
            details = {
                "pushups": stats["pushups"],
                "situps": stats["situps"],
                "squats": stats["squats"],
                "curls": stats["curls"]
            }

            data.append({
                "day": day_str,
                "reps": stats["reps"],
                "calories": stats["calories"],
                "details": details
            })

        return data


    def display_calendar_stats(self):
        selected_date = self.calendar.selectedDate().toPyDate()
        stats = self.get_stats_for_date(selected_date)
        text = (
            f"Stats for {selected_date.strftime('%b %d, %Y')}:\n"
            f"Reps: {stats.get('reps', 0)}\n"
            f"Pushups: {stats.get('pushups', 0)}\n"
            f"Squats: {stats.get('squats', 0)}\n"
            f"Curls: {stats.get('curls', 0)}\n"
            f"Situps: {stats.get('situps', 0)}\n"
            f"Plank Time: {stats.get('plank_time', 0)} sec\n"
            f"Calories: {stats.get('calories', 0)}\n"
            f"Duration: {stats.get('duration', 0)} min"
        )
        self.calendar_info_label.setText(text)

    def load_and_plot_weekly_bar(self):
        data = self.load_weekly_data()
        self.bar_ax.clear()
        days = [d["day"] for d in data]
        reps = [d["reps"] for d in data]

        bars = self.bar_ax.bar(days, reps, color="orange")
        self.bar_ax.set_title("Weekly Reps Summary (Bar Chart)")
        self.bar_ax.set_ylabel("Total Reps")
        self.bar_ax.set_xlabel("Day")

        self.bar_ax.grid(True, linestyle="--", alpha=0.3)
        self.bar_fig.tight_layout()
        self.bar_canvas.draw()

        cursor = mplcursors.cursor(bars, hover=True)

        @cursor.connect("add")
        def on_hover(sel):
            idx = sel.index
            day_data = data[idx]
            details = day_data["details"]
            text = f"{day_data['day']}\nTotal: {day_data['reps']} reps\nCalories: {day_data['calories']} cal"
            for k, v in details.items():
                text += f"\n{k.capitalize()}: {v}"
            sel.annotation.set_text(text)
            sel.annotation.get_bbox_patch().set(fc="black", alpha=0.8)
            sel.annotation.set_fontsize(10)
            sel.annotation.set_color("white")
