from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QMessageBox, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt
from models import User
from utils.auth import hash_password

class AdminWorkerTab(QWidget):
    def __init__(self, session, company_id):
        super().__init__()
        self.session = session
        self.company_id = company_id  # ✅ store company_id

        # Input fields
        self.worker_email = None
        self.worker_pwd = None
        self.worker_phone = None
        self.worker_address = None
        self.workers_table = None

        self.setup_ui()
        self.load_workers()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(18)

        # --- Form ---
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        self.worker_email = QLineEdit()
        self.worker_email.setPlaceholderText("Worker Email")
        form.addRow("Worker Email:", self.worker_email)

        self.worker_pwd = QLineEdit()
        self.worker_pwd.setPlaceholderText("Password")
        self.worker_pwd.setEchoMode(QLineEdit.Password)
        form.addRow("Password:", self.worker_pwd)

        self.worker_phone = QLineEdit()
        self.worker_phone.setPlaceholderText("Phone Number")
        form.addRow("Phone:", self.worker_phone)

        self.worker_address = QLineEdit()
        self.worker_address.setPlaceholderText("Full Address")
        form.addRow("Address:", self.worker_address)

        add_btn = QPushButton("Add Worker")
        add_btn.clicked.connect(self.add_worker)

        layout.addLayout(form)
        layout.addWidget(add_btn)

        # --- Workers Table ---
        self.workers_table = QTableWidget(0, 4)
        self.workers_table.setHorizontalHeaderLabels(["Email", "Phone", "Address", "Role"])
        self.workers_table.setAlternatingRowColors(True)
        self.workers_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.workers_table)

        refresh_btn = QPushButton("Refresh Workers List")
        refresh_btn.clicked.connect(self.load_workers)
        layout.addWidget(refresh_btn)

        self.setLayout(layout)

    def add_worker(self):
        email = self.worker_email.text().strip()
        pwd = self.worker_pwd.text().strip()
        phone = self.worker_phone.text().strip()
        address = self.worker_address.text().strip()

        if not (email and pwd):
            QMessageBox.warning(self, "Error", "Email and password are required")
            return

        if self.session.query(User).filter_by(email=email).first():
            QMessageBox.warning(self, "Error", "User already exists")
            return

        # ✅ Create new office worker with phone & address
        user = User(
            email=email,
            password=hash_password(pwd),
            role='office_worker',
            company_id=self.company_id,
            phone=phone,
            address=address
        )

        self.session.add(user)
        self.session.commit()
        QMessageBox.information(self, "Success", "Office Worker added successfully!")

        # Clear form
        self.worker_email.clear()
        self.worker_pwd.clear()
        self.worker_phone.clear()
        self.worker_address.clear()

        # Refresh table
        self.load_workers()

    def load_workers(self):
        self.workers_table.setRowCount(0)
        workers = (
            self.session.query(User)
            .filter(User.company_id == self.company_id, User.role == 'office_worker')  # ✅ fixed
            .all()
        )

        for w in workers:
            row = self.workers_table.rowCount()
            self.workers_table.insertRow(row)
            self.workers_table.setItem(row, 0, QTableWidgetItem(w.email))
            self.workers_table.setItem(row, 1, QTableWidgetItem(w.phone or ""))
            self.workers_table.setItem(row, 2, QTableWidgetItem(w.address or ""))
            self.workers_table.setItem(row, 3, QTableWidgetItem(w.role))
