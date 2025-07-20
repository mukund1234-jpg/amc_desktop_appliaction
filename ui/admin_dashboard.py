# ui/admin_dashboard.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QTableWidget, QTableWidgetItem
from database import SessionLocal
from models import User
from utils.auth import hash_password

class AdminDashboard(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Admin Dashboard")
        self.setup_ui()

    def setup_ui(self):
        self.session = SessionLocal()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Admin: {self.user.email} (Company: {self.user.company_id})"))

        form = QFormLayout()
        self.worker_email = QLineEdit(); form.addRow("New Worker Email:", self.worker_email)
        self.worker_pwd = QLineEdit(); self.worker_pwd.setEchoMode(QLineEdit.Password); form.addRow("Password:", self.worker_pwd)
        add_btn = QPushButton("Add Worker"); add_btn.clicked.connect(self.add_worker)
        layout.addLayout(form); layout.addWidget(add_btn)

        self.workers_table = QTableWidget(0, 2)
        self.workers_table.setHorizontalHeaderLabels(["Email", "Role"])
        layout.addWidget(self.workers_table)

        load_btn = QPushButton("Refresh Workers List"); load_btn.clicked.connect(self.load_workers)
        layout.addWidget(load_btn)
        layout.addWidget(QLabel("Office Workers"))
        self.load_workers()
        self.setLayout(layout)

    def add_worker(self):
        email = self.worker_email.text().strip()
        pwd = self.worker_pwd.text().strip()
        if not (email and pwd):
            QMessageBox.warning(self, "Error", "Email and password are required")
            return

        if self.session.query(User).filter_by(email=email).first():
            QMessageBox.warning(self, "Error", "User exists")
            return

        user = User(email=email, password=hash_password(pwd), role='office_worker', company_id=self.user.company_id)
        self.session.add(user)
        self.session.commit()
        QMessageBox.information(self, "Success", "Office Worker added!")
        self.load_workers()

    def load_workers(self):
        self.workers_table.setRowCount(0)
        workers = self.session.query(User).filter_by(company_id=self.user.company_id, role='office_worker').all()
        for w in workers:
            row = self.workers_table.rowCount()
            self.workers_table.insertRow(row)
            self.workers_table.setItem(row, 0, QTableWidgetItem(w.email))
            self.workers_table.setItem(row, 1, QTableWidgetItem(w.role))
