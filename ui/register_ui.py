from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QLabel, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from database import SessionLocal
from models import Company, User
import hashlib

class RegistrationUI(QWidget):
    def __init__(self, switch_to_login_callback):
        super().__init__()
        self.switch_to_login = switch_to_login_callback
        self.setWindowTitle("Register Company")
        self.setFixedWidth(380)
        self.setStyleSheet("""
            QWidget {
                background: #f5f6fa;
            }
            #RegCard {
                background: #fff;
                border-radius: 16px;
                padding: 32px 28px 24px 28px;
                
            }
            QLabel#Header {
                font-size: 22px;
                font-weight: bold;
                color: #273c75;
                margin-bottom: 18px;
            }
            QLineEdit {
                border: 1.5px solid #dcdde1;
                border-radius: 8px;
                padding: 10px;
                font-size: 15px;
                margin-bottom: 14px;
                background: #f8f9fa;
            }
            QLineEdit:focus {
                border: 1.5px solid #4078c0;
                background: #fff;
            }
            QPushButton#RegisterBtn {
                background: #4078c0;
                color: #fff;
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 8px;
            }
            QPushButton#RegisterBtn:hover {
                background: #274472;
            }
            QLabel#LoginLink {
                color: #4078c0;
                font-size: 14px;
                margin-top: 18px;
                qproperty-alignment: AlignCenter;
            }
            QLabel#LoginLink:hover {
                color: #274472;
                text-decoration: underline;
            }
        """)

        # Center the card
        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignCenter)
        outer_layout.setContentsMargins(0, 60, 0, 60)

        card = QWidget()
        card.setObjectName("RegCard")
        layout = QVBoxLayout(card)
        layout.setSpacing(10)

        header = QLabel("Register Company")
        header.setObjectName("Header")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        self.company_input = QLineEdit()
        self.company_input.setPlaceholderText("Enter Company Name")
        layout.addWidget(self.company_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter Admin Email")
        layout.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter Admin Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        register_btn = QPushButton("Register")
        register_btn.setObjectName("RegisterBtn")
        register_btn.clicked.connect(self.register_company)
        layout.addWidget(register_btn)

        # Spacer for better vertical alignment
        layout.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        login_label = QLabel("<a href='#'>Already Registered? Login Here</a>")
        login_label.setObjectName("LoginLink")
        login_label.setTextFormat(Qt.RichText)
        login_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        login_label.setOpenExternalLinks(False)
        login_label.linkActivated.connect(self.switch_to_login)
        layout.addWidget(login_label, alignment=Qt.AlignCenter)

        outer_layout.addWidget(card, alignment=Qt.AlignCenter)

    def register_company(self):
        company_name = self.company_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not all([company_name, email, password]):
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        session = SessionLocal()
        try:
            existing_company = session.query(Company).filter_by(company_name=company_name).first()
            if existing_company:
                QMessageBox.warning(self, "Exists", "Company already exists. Please login.")
                return

            company = Company(company_name=company_name)
            session.add(company)
            session.commit()

            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            admin = User(email=email, password=hashed_password, role='admin', company_id=company.id)
            session.add(admin)
            session.commit()

            QMessageBox.information(self, "Success", "Company and Admin registered successfully!")
            self.clear_inputs()
            self.switch_to_login()

        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error: {e}")
        finally:
            session.close()

    def clear_inputs(self):
        self.company_input.clear()
        self.email_input.clear()
        self.password_input.clear()