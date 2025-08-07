from pydoc import doc, text
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QScrollArea, QFrame, QCalendarWidget
)
from PyQt6.QtCore import Qt
from datetime import date, datetime, timedelta
from firebase_admin import firestore
from firebase_client import db
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import mplcursors

from ui.main_window import FitnessApp

class Dashboard(QWidget):
    def __init__(self, user_id, display_name):
        super().__init__()
        self.user_id = user_id
        self.display_name = display_name
        self.current_date = datetime.today().date()

        self.setWindowTitle("Fitness Dashboard")
        self.resize(900, 700)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Scroll area setup
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")
        self.main_layout.addWidget(scroll_area)

        # Content widget
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)
        scroll_area.setWidget(content)

        # Welcome label
        welcome_label = QLabel(f"Welcome, {self.display_name}!")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #FFCA28;
            padding: 15px;
            font-family: 'Segoe UI', Arial, sans-serif;
        """)
        content_layout.addWidget(welcome_label)

        # Toggle buttons
        toggle_layout = QHBoxLayout()
        toggle_layout.setSpacing(10)
        self.line_toggle = QPushButton("📈 Line")
        self.bar_toggle = QPushButton("📊 Bar")
        self.calendar_toggle = QPushButton("📅 Calendar")
        self.card_toggle = QPushButton("📋 Weekly")
        self.form_toggle = QPushButton("🥧 Form")

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
                    background-color: #2A2A2A;
                    color: #FFCA28;
                    border: 1px solid #FFCA28;
                    border-radius: 8px;
                    padding: 10px 15px;
                    font-size: 14px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    transition: all 0.2s ease;
                }
                QPushButton:checked {
                    background-color: #FFCA28;
                    color: #121212;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3A3A3A;
                    border-color: #FFD700;
                }
            """)
            toggle_layout.addWidget(btn)
        content_layout.addLayout(toggle_layout)

        # Stats card
        self.stats_card = QFrame()
        self.stats_card.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 12px;
                padding: 15px;
                margin-top: 15px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
        """)
        content_layout.addWidget(self.stats_card)

        stats_layout = QVBoxLayout(self.stats_card)
        stats_layout.setSpacing(10)

        # Date navigation
        date_nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("⬅️")
        self.next_btn = QPushButton("➡️")
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setStyleSheet('font-size: 18px; color: #FFCA28; font-family: "Segoe UI";')
        
        for btn in (self.prev_btn, self.next_btn):
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2A2A2A;
                    color: #FFCA28;
                    border: 1px solid #FFCA28;
                    border-radius: 8px;
                    padding: 8px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #3A3A3A;
                }
            """)
            date_nav_layout.addWidget(btn)
        date_nav_layout.addWidget(self.date_label)
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
            lbl.setStyleSheet("font-size: 16px; color: #FFFFFF; font-family: 'Segoe UI'; padding: 5px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stats_layout.addWidget(lbl)

        # Connect buttons
        self.prev_btn.clicked.connect(self.load_previous_day)
        self.next_btn.clicked.connect(self.load_next_day)

        # Weekly Summary Card
        self.weekly_summary_card = QFrame()
        self.weekly_summary_card.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 12px;
                padding: 15px;
                margin-top: 15px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
        """)
        weekly_layout = QVBoxLayout(self.weekly_summary_card)
        title = QLabel("Weekly Summary")
        title.setStyleSheet("font-weight: bold; font-size: 18px; color: #FFCA28; font-family: 'Segoe UI';")
        weekly_layout.addWidget(title)

        self.weekly_reps_label = QLabel("Total Reps: Loading...")
        self.weekly_calories_label = QLabel("Calories Burned: Loading...")
        self.weekly_duration_label = QLabel("Duration: Loading...")

        for lbl in (self.weekly_reps_label, self.weekly_calories_label, self.weekly_duration_label):
            lbl.setStyleSheet("font-size: 14px; color: #FFFFFF; font-family: 'Segoe UI'; padding: 5px;")
            weekly_layout.addWidget(lbl)

        content_layout.addWidget(self.weekly_summary_card)

        # Weekly Line Summary Widget
        self.weekly_line_summary = QWidget()
        self.weekly_line_summary.setStyleSheet("""
            background-color: #1E1E1E;
            border-radius: 12px;
            padding: 15px;
            margin-top: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        """)
        line_layout = QVBoxLayout(self.weekly_line_summary)
        content_layout.addWidget(self.weekly_line_summary)

        self.line_fig, self.line_ax = plt.subplots(figsize=(7, 3))
        self.line_fig.patch.set_facecolor('#1E1E1E')
        self.line_ax.set_facecolor('#2A2A2A')
        self.line_canvas = FigureCanvas(self.line_fig)
        line_layout.addWidget(self.line_canvas)

        # Weekly Bar Summary Widget
        self.weekly_bar_summary = QWidget()
        self.weekly_bar_summary.setStyleSheet("""
            background-color: #1E1E1E;
            border-radius: 12px;
            padding: 15px;
            margin-top: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        """)
        bar_layout = QVBoxLayout(self.weekly_bar_summary)
        content_layout.addWidget(self.weekly_bar_summary)

        self.bar_fig, self.bar_ax = plt.subplots(figsize=(7, 3))
        self.bar_fig.patch.set_facecolor('#1E1E1E')
        self.bar_ax.set_facecolor('#2A2A2A')
        self.bar_canvas = FigureCanvas(self.bar_fig)
        bar_layout.addWidget(self.bar_canvas)

        # Calendar Widget
        self.calendar_widget = QWidget()
        self.calendar_widget.setStyleSheet("""
            background-color: #1E1E1E;
            border-radius: 12px;
            padding: 15px;
            margin-top: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        """)
        calendar_layout = QVBoxLayout(self.calendar_widget)
        content_layout.addWidget(self.calendar_widget)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: #2A2A2A;
                color: #FFFFFF;
                font-family: 'Segoe UI';
            }
            QCalendarWidget QToolButton {
                color: #FFCA28;
                background-color: #2A2A2A;
                border: none;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #3A3A3A;
            }
        """)
        calendar_layout.addWidget(self.calendar)

        self.calendar_info_label = QLabel("Select a date to view stats")
        self.calendar_info_label.setStyleSheet("color: #FFFFFF; font-size: 14px; padding: 10px; font-family: 'Segoe UI';")
        calendar_layout.addWidget(self.calendar_info_label)

        self.calendar.selectionChanged.connect(self.display_calendar_stats)

        # Form Quality Pie Chart Widget
        self.form_pie_widget = QWidget()
        self.form_pie_widget.setStyleSheet("""
            background-color: #1E1E1E;
            border-radius: 12px;
            padding: 15px;
            margin-top: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        """)
        form_layout = QVBoxLayout(self.form_pie_widget)

        self.form_time_selector = QHBoxLayout()
        self.day_btn = QPushButton("Day")
        self.week_btn = QPushButton("Week")
        self.month_btn = QPushButton("Month")

        for btn in [self.day_btn, self.week_btn, self.month_btn]:
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2A2A2A;
                    color: #FFCA28;
                    border: 1px solid #FFCA28;
                    border-radius: 8px;
                    padding: 8px;
                    font-family: 'Segoe UI';
                }
                QPushButton:checked {
                    background-color: #FFCA28;
                    color: #121212;
                }
                QPushButton:hover {
                    background-color: #3A3A3A;
                }
            """)
            self.form_time_selector.addWidget(btn)

        form_layout.addLayout(self.form_time_selector)

        self.form_fig, self.form_ax = plt.subplots(figsize=(4, 4))
        self.form_fig.patch.set_facecolor('#1E1E1E')
        self.form_ax.set_facecolor('#2A2A2A')
        self.form_canvas = FigureCanvas(self.form_fig)
        form_layout.addWidget(self.form_canvas)

        content_layout.addWidget(self.form_pie_widget)

        # Toggle sections
        self.toggle_sections = {
            'line': self.weekly_line_summary,
            'bar': self.weekly_bar_summary,
            'calendar': self.calendar_widget,
            'card': self.weekly_summary_card,
            'form': self.form_pie_widget
        }

        self.day_btn.clicked.connect(lambda: self.draw_form_pie_chart("day"))
        self.week_btn.clicked.connect(lambda: self.draw_form_pie_chart("week"))
        self.month_btn.clicked.connect(lambda: self.draw_form_pie_chart("month"))

        def make_toggle_handler(selected_key):
            def handler():
                for key, widget in self.toggle_sections.items():
                    is_selected = (key == selected_key)
                    self.toggle_sections[key].setVisible(is_selected)
                    btn = next(btn for btn, k in self.toggle_buttons if k == key)
                    btn.setChecked(is_selected)
            return handler

        for btn, key in self.toggle_buttons:
            btn.clicked.connect(make_toggle_handler(key))

        self.toggle_sections['line'].setVisible(True)
        for k in ('bar', 'calendar', 'card', 'form'):
            self.toggle_sections[k].setVisible(False)

        self.line_toggle.toggled.connect(self.weekly_line_summary.setVisible)
        self.bar_toggle.toggled.connect(self.weekly_bar_summary.setVisible)
        self.calendar_toggle.toggled.connect(self.calendar_widget.setVisible)
        self.card_toggle.toggled.connect(self.weekly_summary_card.setVisible)
        self.form_toggle.toggled.connect(self.form_pie_widget.setVisible)

        # Start workout button
        start_button = QPushButton("🚀 Start Workout")
        start_button.setFixedHeight(60)
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #FFCA28;
                color: #121212;
                border: none;
                padding: 15px;
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
                font-family: 'Segoe UI';
                transition: all 0.2s ease;
            }
            QPushButton:hover {
                background-color: #FFD700;
            }
            QPushButton:pressed {
                background-color: #FFB300;
            }
        """)
        content_layout.addWidget(start_button)
        start_button.clicked.connect(self.launch_main_app)

        # How it works
        how_it_works = QLabel(
            "🧠 How it works:\n\n"
            "- Counts reps via webcam\n"
            "- Detects bad form with AI\n"
            "- Responds to voice commands\n"
            "- Tracks your mood and progress\n\n"
        )
        how_it_works.setAlignment(Qt.AlignmentFlag.AlignCenter)
        how_it_works.setWordWrap(True)
        how_it_works.setStyleSheet("""
            font-size: 14px;
            color: #B0B0B0;
            padding: 20px;
            background-color: #1E1E1E;
            border-radius: 12px;
            font-family: 'Segoe UI';
            margin-top: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        """)
        content_layout.addWidget(how_it_works)

        # Apply global stylesheet
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #FFFFFF;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

        # Load initial data
        self.update_stats_view()
        self.load_and_plot_weekly_summary()
        self.load_and_plot_weekly_line()
        self.load_and_plot_weekly_bar()
        self.draw_form_pie_chart("day")

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

    def get_form_quality_data(self, range_type):
        db = firestore.client()
        today = datetime.today().date()

        if range_type == "day":
            date_list = [today]
        elif range_type == "week":
            date_list = [today - timedelta(days=i) for i in range(7)]
        elif range_type == "month":
            date_list = [today - timedelta(days=i) for i in range(30)]
        else:
            return {}

        form_summary = {
            "pushups": {"good": 0, "bad": 0},
            "squats": {"good": 0, "bad": 0},
            "situps": {"good": 0, "bad": 0},
            "curls": {"good": 0, "bad": 0}
        }

        for dt in date_list:
            date_str = dt.strftime("%Y-%m-%d")
            doc_id = f"{self.user_id}_{date_str}"
            doc = db.collection("workout_data").document(doc_id).get()
            if doc.exists:
                data = doc.to_dict()
                for workout in form_summary.keys():
                    form_summary[workout]["good"] += data.get(f"{workout}_good", 0)
                    form_summary[workout]["bad"] += data.get(f"{workout}_bad", 0)

        return form_summary

    def load_previous_day(self):
        self.current_date -= timedelta(days=1)
        self.update_stats_view()

    def load_next_day(self):
        self.current_date += timedelta(days=1)
        self.update_stats_view()

    def launch_main_app(self):
        self.fitness_app = FitnessApp(user_id=self.user_id)
        self.fitness_app.show()
        self.close()

    def load_and_plot_weekly_summary(self):
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
        data = self.load_weekly_data()
        self.line_ax.clear()
        days = [d["day"] for d in data]
        reps = [d["reps"] for d in data]

        line, = self.line_ax.plot(days, reps, marker='o', color="#FFCA28", linewidth=2)
        self.line_ax.set_title("Weekly Reps Summary", color="#FFFFFF", fontsize=14, pad=10)
        self.line_ax.set_ylabel("Total Reps", color="#FFFFFF")
        self.line_ax.set_xlabel("Day", color="#FFFFFF")
        self.line_ax.grid(True, linestyle="--", alpha=0.3, color="#FFFFFF")
        self.line_ax.tick_params(colors="#FFFFFF")
        self.line_ax.spines['top'].set_color('#FFFFFF')
        self.line_ax.spines['right'].set_color('#FFFFFF')
        self.line_ax.spines['left'].set_color('#FFFFFF')
        self.line_ax.spines['bottom'].set_color('#FFFFFF')
        self.line_ax.set_ylim(0, max(reps) * 1.2 if reps else 100)

        cursor = mplcursors.cursor([line], hover=True)
        @cursor.connect("add")
        def on_hover(sel):
            try:
                idx = sel.index
                day_data = data[int(idx)]
                text = (
                    f"{day_data['day']}\n"
                    f"Total: {day_data['reps']} reps\n"
                    f"Calories: {day_data['calories']} cal"
                )
                for k, v in day_data["details"].items():
                    text += f"\n{k.capitalize()}: {v}"
                sel.annotation.set_text(text)
                sel.annotation.get_bbox_patch().set(fc="#2A2A2A", alpha=0.9)
                sel.annotation.set_fontsize(10)
                sel.annotation.set_color("#FFFFFF")
                sel.annotation.arrow_patch.set_visible(False)
            except Exception as e:
                print("Hover error:", e)

        self.line_canvas.draw()

    def load_weekly_data(self):
        data = []
        today = datetime.today()
        for i in range(6, -1, -1):
            day_date = today - timedelta(days=i)
            day_str = day_date.strftime("%a")
            stats = self.get_stats_for_date(day_date)
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

        bars = self.bar_ax.bar(days, reps, color="#FFCA28")
        self.bar_ax.set_title("Weekly Reps Summary", color="#FFFFFF", fontsize=14, pad=10)
        self.bar_ax.set_ylabel("Total Reps", color="#FFFFFF")
        self.bar_ax.set_xlabel("Day", color="#FFFFFF")
        self.bar_ax.grid(True, linestyle="--", alpha=0.3, color="#FFFFFF")
        self.bar_ax.tick_params(colors="#FFFFFF")
        self.bar_ax.spines['top'].set_color('#FFFFFF')
        self.bar_ax.spines['right'].set_color('#FFFFFF')
        self.bar_ax.spines['left'].set_color('#FFFFFF')
        self.bar_ax.spines['bottom'].set_color('#FFFFFF')
        self.bar_ax.set_ylim(0, max(reps) * 1.2 if reps else 100)

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
            sel.annotation.get_bbox_patch().set(fc="#2A2A2A", alpha=0.9)
            sel.annotation.set_fontsize(10)
            sel.annotation.set_color("#FFFFFF")

        self.bar_fig.tight_layout()
        self.bar_canvas.draw()

    def draw_form_pie_chart(self, range_type):
        from_date = datetime.today().date()
        if range_type == "day":
            dates = [from_date]
        elif range_type == "week":
            dates = [from_date - timedelta(days=i) for i in range(7)]
        elif range_type == "month":
            dates = [from_date - timedelta(days=i) for i in range(30)]

        good = {"pushups": 0, "curls": 0, "situps": 0, "squats": 0}
        bad = {"pushups": 0, "curls": 0, "situps": 0, "squats": 0}

        for d in dates:
            doc_id = f"{self.user_id}_{d.strftime('%Y-%m-%d')}"
            doc = db.collection("workout_data").document(doc_id).get()
            if doc.exists:
                data = doc.to_dict()
                for k in good:
                    good[k] += data.get(f"{k}_good", 0)
                    bad[k] += data.get(f"{k}_bad", 0)

        self.form_ax.clear()
        total_good = sum(good.values())
        total_bad = sum(bad.values())

        if total_good == 0 and total_bad == 0:
            wedges, texts, autotexts = self.form_ax.pie(
                [1],
                labels=["Good Form"],
                colors=["#4CAF50"],
                autopct=lambda pct: "100%",
                startangle=140,
                textprops={'color': '#FFFFFF', 'fontsize': 12}
            )
            self.form_ax.set_title(f"{range_type.capitalize()} Form Quality (No Data)", color="#FFFFFF", fontsize=14)
            self.form_ax.axis("equal")
            self.form_canvas.draw()
            return

        wedges, texts, autotexts = self.form_ax.pie(
            [total_good, total_bad],
            labels=["Good Form", "Bad Form"],
            colors=["#4CAF50", "#FF5252"],
            autopct='%1.1f%%',
            startangle=140,
            textprops={'color': '#FFFFFF', 'fontsize': 12}
        )
        self.form_ax.set_title(f"{range_type.capitalize()} Form Quality", color="#FFFFFF", fontsize=14)
        self.form_ax.axis("equal")

        for text in autotexts:
            text.set_color('#121212')

        for w in wedges:
            w.set_picker(True)

        cursor = mplcursors.cursor(wedges, hover=True)
        @cursor.connect("add")
        def on_hover(sel):
            try:
                if sel.index == 0:
                    breakdown = "\n".join([f"{k.capitalize()}: {v}" for k, v in good.items()])
                    text = f"Good Form Breakdown:\n{breakdown}"
                else:
                    breakdown = "\n".join([f"{k.capitalize()}: {v}" for k, v in bad.items()])
                    text = f"Bad Form Breakdown:\n{breakdown}"
                sel.annotation.set_text(text)
                sel.annotation.get_bbox_patch().set(fc="#2A2A2A", alpha=0.9)
                sel.annotation.set_fontsize(10)
                sel.annotation.set_color("#FFFFFF")
                sel.annotation.arrow_patch.set_visible(False)
            except Exception as e:
                print("Hover error (pie chart):", e)

        self.form_canvas.draw()