from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy
)
from database import SessionLocal
from models import User
import hashlib
from PyQt5.QtCore import Qt



class LoginUI(QWidget):
    def __init__(self,on_login_success, on_register_clicked):
        super().__init__()
        self.setWindowTitle("Login")
        self.on_login_success = on_login_success
        self.on_register_clicked = on_register_clicked
        self.setFixedWidth(300)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        header = QLabel("<h2>Company Login</h2>")
        header.setStyleSheet("text-align: center;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        layout.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)
        login_btn.setStyleSheet("padding: 8px; font-weight: bold;")
        layout.addWidget(login_btn)

        # Spacer
        layout.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        register_layout = QHBoxLayout()
        register_label = QLabel("New Company?")
        register_btn = QPushButton("Register")
        register_btn.setStyleSheet("color: blue; text-decoration: underline; background: none; border: none;")
        register_btn.setFlat(True)
        register_btn.clicked.connect(self.on_register_clicked)

        register_layout.addWidget(register_label)
        register_layout.addWidget(register_btn)
        layout.addLayout(register_layout)

        self.setLayout(layout)

    def login(self):
        session = SessionLocal()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        user = session.query(User).filter_by(email=email, password=hashed_password).first()
        session.close()

        if user:
            QMessageBox.information(self, "Success", f"Logged in as {user.role}")
            self.on_login_success(user)
        else:
            QMessageBox.warning(self, "Failed", "Invalid credentials")
