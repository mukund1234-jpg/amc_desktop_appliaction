from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QMessageBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QWidget
)
from PyQt5.QtCore import Qt
from models import User
from utils.auth import hash_password

class AdminWorkerTab(QWidget):
    def __init__(self, session, company_id):
        super().__init__()
        self.session = session
        self.company_id = company_id

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

        self.worker_full_name = QLineEdit()
        self.worker_full_name.setPlaceholderText("Full Name")
        form.addRow("Full Name:", self.worker_full_name)

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
        self.workers_table = QTableWidget(0, 6)  # Extra column for actions
        self.workers_table.setHorizontalHeaderLabels(["Full Name", "Email", "Phone", "Address", "Role", "Actions"])
        self.workers_table.setAlternatingRowColors(True)
        self.workers_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.workers_table)

        refresh_btn = QPushButton("Refresh Workers List")
        refresh_btn.clicked.connect(self.load_workers)
        layout.addWidget(refresh_btn)

        self.setLayout(layout)

    def add_worker(self):
        full_name = self.worker_full_name.text().strip()
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

        user = User(
            full_name=full_name,
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

        self.worker_full_name.clear()
        self.worker_email.clear()
        self.worker_pwd.clear()
        self.worker_phone.clear()
        self.worker_address.clear()

        self.load_workers()

    def load_workers(self):
        self.workers_table.setRowCount(0)
        workers = (
            self.session.query(User)
            .filter(User.company_id == self.company_id, User.role == 'office_worker')
            .all()
        )

        for w in workers:
            row = self.workers_table.rowCount()
            self.workers_table.insertRow(row)
            self.workers_table.setItem(row, 0, QTableWidgetItem(w.full_name))
            self.workers_table.setItem(row, 1, QTableWidgetItem(w.email))
            self.workers_table.setItem(row, 2, QTableWidgetItem(w.phone or ""))
            self.workers_table.setItem(row, 3, QTableWidgetItem(w.address or ""))
            self.workers_table.setItem(row, 4, QTableWidgetItem(w.role))

            # Action buttons
            action_widget = QWidget()
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(0, 0, 0, 0)

            update_btn = QPushButton("Update")
            delete_btn = QPushButton("Delete")

            update_btn.clicked.connect(lambda _, user_id=w.id: self.update_worker(user_id))
            delete_btn.clicked.connect(lambda _, user_id=w.id: self.delete_worker(user_id))

            btn_layout.addWidget(update_btn)
            btn_layout.addWidget(delete_btn)
            action_widget.setLayout(btn_layout)

            self.workers_table.setCellWidget(row, 5, action_widget)

    def update_worker(self, user_id):
        worker = self.session.query(User).get(user_id)
        if not worker:
            QMessageBox.warning(self, "Error", "Worker not found")
            return

        # Update using form inputs
        full_name = self.worker_full_name.text().strip()
        pwd = self.worker_pwd.text().strip()
        phone = self.worker_phone.text().strip()
        address = self.worker_address.text().strip()

        if full_name:
            worker.full_name = full_name
        if pwd:
            worker.password = hash_password(pwd)
        if phone:
            worker.phone = phone
        if address:
            worker.address = address

        self.session.commit()
        QMessageBox.information(self, "Success", "Worker updated successfully!")
        self.load_workers()

    def delete_worker(self, user_id):
        worker = self.session.query(User).get(user_id)
        if not worker:
            QMessageBox.warning(self, "Error", "Worker not found")
            return

        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete {worker.full_name}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            self.session.delete(worker)
            self.session.commit()
            QMessageBox.information(self, "Deleted", "Worker deleted successfully.")
            self.load_workers()
