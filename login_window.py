""" import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox
)
from auth_manager import signup_user, login_user

class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fitness App - Login/Signup")
        self.setGeometry(100, 100, 300, 200)

        self.mode = "login"  # can be 'login' or 'signup'
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout()

        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email")

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password")

        self.submit_button = QPushButton("Log In")
        self.switch_mode_button = QPushButton("Don't have an account? Sign Up")

        self.submit_button.clicked.connect(self.handle_submit)
        self.switch_mode_button.clicked.connect(self.toggle_mode)

        self.layout.addWidget(self.email_label)
        self.layout.addWidget(self.email_input)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.submit_button)
        self.layout.addWidget(self.switch_mode_button)

        self.setLayout(self.layout)

    def toggle_mode(self):
        if self.mode == "login":
            self.mode = "signup"
            self.submit_button.setText("Sign Up")
            self.switch_mode_button.setText("Already have an account? Log In")
        else:
            self.mode = "login"
            self.submit_button.setText("Log In")
            self.switch_mode_button.setText("Don't have an account? Sign Up")

    def handle_submit(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return

        try:
            if self.mode == "signup":
                user_id = signup_user(email, password)
                QMessageBox.information(self, "Success", f"Account created!\nUID: {user_id}")
            else:
                id_token = login_user(email, password)
                QMessageBox.information(self, "Success", f"Logged in successfully!")
                # Proceed to main workout app window here (not implemented yet)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AuthWindow()
    window.show()
    sys.exit(app.exec())
 """

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
import sys
from system.auth_manager import signup_user, login_user, get_user_data
import subprocess
import sys
from ui.dashboard import Dashboard


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fitness App - Login")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_btn = QPushButton("Login")
        self.signup_btn = QPushButton("Sign Up")

        layout.addWidget(QLabel("Welcome to the Fitness App"))
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.signup_btn)

        self.setLayout(layout)

        # Connect buttons
        self.login_btn.clicked.connect(self.handle_login)
        self.signup_btn.clicked.connect(self.handle_signup)

    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        if not email or not password:
            QMessageBox.warning(self, "Input Error", "Please fill in both fields.")
            return

        result = login_user(email, password)
        if result:
            user_id = result['localId']
            user_data = get_user_data(user_id)
            display_name = user_data.get("display_name", email)
            QMessageBox.information(self, "Login Success", f"Welcome, {display_name}!")

            # 🧠 NEW: Launch the main app
            self.dashboard = Dashboard(user_id=user_id, display_name=display_name)
            self.dashboard.show()
            self.close()
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid credentials.")
        if result:
            user_id = result['localId']
            user_data = get_user_data(user_id)
            display_name = user_data.get("display_name", email)

            # 👇 Launch Dashboard and pass UID
            self.dashboard = Dashboard(user_id=user_id, display_name=display_name)
            self.dashboard.show()
            self.close()


    def handle_signup(self):
        email = self.email_input.text()
        password = self.password_input.text()
        if not email or not password:
            QMessageBox.warning(self, "Input Error", "Please fill in both fields.")
            return

        user_id = signup_user(email, password)
        if user_id:
            QMessageBox.information(self, "Signup Success", "Account created! You can now log in.")
        else:
            QMessageBox.critical(self, "Signup Failed", "Something went wrong.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
