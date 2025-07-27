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

            self.dashboard = Dashboard(user_id=user_id, display_name=display_name)
            self.dashboard.show()
            self.close()
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid credentials.")
        if result:
            user_id = result['localId']
            user_data = get_user_data(user_id)
            display_name = user_data.get("display_name", email)

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
