import sys
import random
import os
import threading
import speech_recognition as sr
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton,
    QTextEdit, QComboBox, QHBoxLayout, QCheckBox, QSpacerItem, QSizePolicy, QMessageBox
)
from PyQt5.QtGui import QPainter, QColor, QBrush, QFont
from PyQt5.QtCore import Qt, QTimer, QPoint

USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("College Feedback - Login")
        self.setGeometry(100, 100, 300, 200)
        self.users = load_users()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)

        signup_btn = QPushButton("Sign Up")
        signup_btn.clicked.connect(self.signup)
        layout.addWidget(signup_btn)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if username in self.users and self.users[username] == password:
            self.close()
            self.app = CollegeFeedbackApp()
            self.app.show()
        else:
            QMessageBox.warning(self, "Login Failed", "Incorrect username or password.")

    def signup(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if username in self.users:
            QMessageBox.warning(self, "Signup Failed", "Username already exists.")
        else:
            self.users[username] = password
            save_users(self.users)
            QMessageBox.information(self, "Signup Success", "Account created! You can log in now.")

class Particle:
    def __init__(self, x, y):
        self.pos = QPoint(x, y)
        self.radius = random.randint(2, 4)
        self.velocity = QPoint(random.randint(-2, 2), random.randint(-2, 2))
        self.color = QColor(random.randint(150, 255), random.randint(100, 255), random.randint(200, 255), 200)

class FireworkParticle:
    def __init__(self, x, y):
        self.pos = QPoint(x, y)
        self.radius = random.randint(3, 6)
        self.velocity = QPoint(random.randint(-10, 10), random.randint(-10, 10))
        self.life = 30
        self.color = QColor(random.randint(150, 255), random.randint(0, 255), random.randint(100, 255))

class CollegeFeedbackApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎓 College Life Feedback Generator")
        self.setGeometry(100, 100, 700, 750)
        self.trends = {"fun": {}, "challenges": {}, "moods": {}}  # Grouped by department
        self.mood = "😊"
        self.fireworks = []
        self.particles = []
        self.night_mode = False

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.applyStyleSheet()

        self.layout.addWidget(QLabel("🧑 Your Name"))
        self.name_input = QLineEdit()
        self.layout.addWidget(self.name_input)

        self.layout.addWidget(QLabel("🏫 College Name"))
        self.college_name_input = QLineEdit()
        self.layout.addWidget(self.college_name_input)

        self.layout.addWidget(QLabel("📇 SAP ID"))
        self.sap_input = QLineEdit()
        self.layout.addWidget(self.sap_input)

        self.layout.addWidget(QLabel("🏫 College ID"))
        self.college_id_input = QLineEdit()
        self.layout.addWidget(self.college_id_input)

        self.layout.addWidget(QLabel("🎓 Your Year"))
        self.year_combo = QComboBox()
        self.year_combo.addItems(["1st Year", "2nd Year", "3rd Year", "4th Year"])
        self.layout.addWidget(self.year_combo)

        self.layout.addWidget(QLabel("🏛 Department"))
        self.department_input = QLineEdit()
        self.layout.addWidget(self.department_input)

        self.layout.addWidget(QLabel("🎉 College Events Attended"))
        self.events_attended_input = QLineEdit()
        self.layout.addWidget(self.events_attended_input)

        self.layout.addWidget(QLabel("🎉 Most Fun Part of College"))
        self.enjoyment_input = QLineEdit()
        self.layout.addWidget(self.enjoyment_input)

        self.layout.addWidget(QLabel("🧠 Most Challenging Part"))
        self.challenges_input = QLineEdit()
        self.layout.addWidget(self.challenges_input)

        voice_btn = QPushButton("🎤 Speak Challenge")
        voice_btn.clicked.connect(self.captureVoice)
        self.layout.addWidget(voice_btn)

        mood_label = QLabel("🎭 Pick Your Mood")
        self.layout.addWidget(mood_label)
        self.mood_buttons = QHBoxLayout()
        for emoji in ["😊", "😐", "😞", "😎", "🥲"]:
            btn = QPushButton(emoji)
            btn.clicked.connect(lambda _, e=emoji: self.setMood(e))
            self.mood_buttons.addWidget(btn)
        self.layout.addLayout(self.mood_buttons)

        self.generate_btn = QPushButton("✨ Generate Feedback")
        self.generate_btn.clicked.connect(self.generateFeedback)
        self.layout.addWidget(self.generate_btn)

        self.feedback_area = QTextEdit()
        self.feedback_area.setReadOnly(True)
        self.layout.addWidget(self.feedback_area)

        self.trend_area = QTextEdit()
        self.trend_area.setReadOnly(True)
        self.layout.addWidget(QLabel("📈 Feedback Trends"))
        self.layout.addWidget(self.trend_area)

        self.night_toggle = QCheckBox("🌙 Night Mode")
        self.night_toggle.stateChanged.connect(self.toggleNightMode)
        self.layout.addWidget(self.night_toggle)

        self.layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def applyStyleSheet(self):
        if self.night_mode:
            self.setStyleSheet("""
                QWidget {
                    background-color: #121212;
                    color: #f0f0f0;
                    font-family: 'Segoe UI';
                    font-size: 14px;
                }
                QLineEdit, QTextEdit, QComboBox {
                    background-color: #1e1e1e;
                    border: 2px solid #ff9800;
                    border-radius: 8px;
                    padding: 6px;
                    color: #f0f0f0;
                }
                QPushButton {
                    background-color: #ff7043;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #f4511e;
                }
                QCheckBox {
                    font-weight: bold;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #ffe0b2;
                    color: #222;
                    font-family: 'Segoe UI';
                    font-size: 14px;
                }
                QLineEdit, QTextEdit, QComboBox {
                    background-color: #fff3e0;
                    border: 2px solid #ff9800;
                    border-radius: 8px;
                    padding: 6px;
                }
                QPushButton {
                    background-color: #ff7043;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #f4511e;
                }
                QCheckBox {
                    font-weight: bold;
                }
            """)

    def toggleNightMode(self):
        self.night_mode = not self.night_mode
        self.applyStyleSheet()

    def setMood(self, mood):
        self.mood = mood

    def captureVoice(self):
        def _recognize():
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                try:
                    self.feedback_area.setText("🎤 Listening...")
                    audio = recognizer.listen(source)
                    text = recognizer.recognize_google(audio)
                    self.challenges_input.setText(text)
                except Exception as e:
                    self.feedback_area.setText("❌ Could not understand audio.")
        threading.Thread(target=_recognize).start()

    def generateFeedback(self):
        name = self.name_input.text()
        college = self.college_name_input.text()
        sap = self.sap_input.text()
        college_id = self.college_id_input.text()
        year = self.year_combo.currentText()
        dept = self.department_input.text()
        events = self.events_attended_input.text()
        fun = self.enjoyment_input.text()
        challenge = self.challenges_input.text()

        if not all([name, college, sap, college_id, year, dept]):
            self.feedback_area.setText("❗ Please fill in all required fields.")
            return

        self.trends["fun"].setdefault(dept, []).append(fun)
        self.trends["challenges"].setdefault(dept, []).append(challenge)
        self.trends["moods"].setdefault(dept, []).append(self.mood)

        feedback = f"""
👤 Name: {name}
🏫 College: {college} ({college_id})
📇 SAP ID: {sap}
🎓 Year: {year}
🏛 Department: {dept}

🎉 Events Attended: {events}
🥳 Fun Part: {fun}
🧠 Challenge: {challenge}
🎭 Mood: {self.mood}

📝 Thanks for sharing your feedback!
        """.strip()
        self.feedback_area.setText(feedback)
        self.updateTrendSummary()

    def updateTrendSummary(self):
        summary = ""
        for dept, moods in self.trends["moods"].items():
            mood_count = {m: moods.count(m) for m in set(moods)}
            summary += f"📊 {dept} - Mood Summary: {mood_count}\n"
        self.trend_area.setText(summary)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())
