from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
from database import SessionLocal
from models import Company, User
import hashlib

class RegistrationUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register Company")
        layout = QVBoxLayout()

        self.company_name_input = QLineEdit()
        self.company_name_input.setPlaceholderText("Company Name")
        layout.addWidget(self.company_name_input)

        self.admin_email_input = QLineEdit()
        self.admin_email_input.setPlaceholderText("Admin Email")
        layout.addWidget(self.admin_email_input)

        self.admin_password_input = QLineEdit()
        self.admin_password_input.setPlaceholderText("Admin Password")
        self.admin_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.admin_password_input)

        register_btn = QPushButton("Register Company + Admin")
        register_btn.clicked.connect(self.register_company)
        layout.addWidget(register_btn)

        self.setLayout(layout)

    def register_company(self):
        session = SessionLocal()
        company_name = self.company_name_input.text()
        email = self.admin_email_input.text()
        password = self.admin_password_input.text()

        if not all([company_name, email, password]):
            QMessageBox.warning(self, "Input Error", "All fields are required")
            return

        existing_company = session.query(Company).filter_by(name=company_name).first()
        if existing_company:
            QMessageBox.warning(self, "Error", "Company already exists")
            return

        company = Company(name=company_name)
        session.add(company)
        session.commit()

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        admin = User(email=email, password=hashed_password, role='admin', company_id=company.id)
        session.add(admin)
        session.commit()

        QMessageBox.information(self, "Success", "Company and Admin created!")
        session.close()
