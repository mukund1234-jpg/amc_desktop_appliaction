from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy
)
from database import SessionLocal
from models import User
import hashlib
from PyQt5.QtCore import Qt

class LoginUI(QWidget):
    def __init__(self, on_login_success, on_register_clicked):
        super().__init__()
        self.setWindowTitle("Login")
        self.on_login_success = on_login_success
        self.on_register_clicked = on_register_clicked
        self.setFixedWidth(350)
        self.setStyleSheet("""
            QWidget {
                background: #f5f6fa;
            }
            #LoginCard {
                background: #fff;
                border-radius: 16px;
                padding: 32px 24px 24px 24px;
               
            }
            QLabel#Header {
                font-size: 22px;
                font-weight: bold;
                color: #273c75;
                margin-bottom: 16px;
            }
            QLineEdit {
                border: 1.5px solid #dcdde1;
                border-radius: 8px;
                padding: 10px;
                font-size: 15px;
                margin-bottom: 12px;
                background: #f8f9fa;
            }
            QLineEdit:focus {
                border: 1.5px solid #4078c0;
                background: #fff;
            }
            QPushButton#LoginBtn {
                background: #4078c0;
                color: #fff;
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 8px;
            }
            QPushButton#LoginBtn:hover {
                background: #274472;
            }
            QPushButton#RegisterBtn {
                color: #4078c0;
                background: none;
                border: none;
                text-decoration: underline;
                font-weight: bold;
            }
            QPushButton#RegisterBtn:hover {
                color: #274472;
            }
        """)

        # Center the card
        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignCenter)
        outer_layout.setContentsMargins(0, 60, 0, 60)

        card = QWidget()
        card.setObjectName("LoginCard")
        layout = QVBoxLayout(card)
        layout.setSpacing(10)

        header = QLabel("Login")
        header.setObjectName("Header")
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
        login_btn.setObjectName("LoginBtn")
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)

        # Spacer
        layout.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        register_layout = QHBoxLayout()
        register_label = QLabel("New Company?")
        register_btn = QPushButton("Register")
        register_btn.setObjectName("RegisterBtn")
        register_btn.setFlat(True)
        register_btn.clicked.connect(self.on_register_clicked)

        register_layout.addWidget(register_label)
        register_layout.addWidget(register_btn)
        register_layout.addStretch()
        layout.addLayout(register_layout)

        outer_layout.addWidget(card, alignment=Qt.AlignCenter)

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