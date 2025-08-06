from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QLabel, QFormLayout, QLineEdit, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from database import SessionLocal
from models import User, Customer, ServiceRequest
from utils.auth import hash_password
from .admin_service_tab import ServiceTab
from .create_profile_tab import ProfileTab
from .add_officeworker_tab import AdminWorkerTab
# After login, get company_id of admin's company


class AdminDashboard(QWidget):
    def __init__(self, user, logout_callback):
        super().__init__()
        self.user = user
        self.logout_callback = logout_callback
        self.session = SessionLocal()
        self.setWindowTitle("Admin Dashboard")
        self.showMaximized()  # Full screen

        self.setStyleSheet("""
            QWidget {
                background: #f5f6fa;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
            }
            QLabel#Header {
                font-size: 28px;
                font-weight: bold;
                color: #273c75;
                padding: 24px 0 12px 0;
                letter-spacing: 1px;
            }
            QTabWidget::pane {
                border: 2px solid #4078c0;
                border-radius: 20px;
                background: #fff;
                margin: 32px 0 0 0; /* More top margin for separation */
                padding: 24px 24px 24px 24px; /* Padding inside the tab pane */
                
            }
            QTabBar::tab {
                background: #d6e4f0;
                color: #273c75;
                border-radius: 16px 16px 0 0;
                min-width: 200px;
                min-height: 48px;
                font-size: 20px;
                font-weight: bold;
                margin-right: 16px; /* More space between tabs */
                margin-top: 12px;   /* Space above tabs */
                margin-bottom: -2px; /* Overlap with pane border */
                padding: 16px 36px 14px 36px; /* More padding for a "pill" look */
                
            }
            QTabBar::tab:selected {
                background: #4078c0;
                color: #fff;
                border-bottom: 4px solid #fff;
                margin-bottom: -4px; /* Overlap selected tab with pane */
            }
            QTabBar::tab:hover {
                background: #b1c9e8;
                color: #273c75;
            }
            QTabBar {
                qproperty-drawBase: 0;
                margin-left: 24px;
                margin-right: 24px;
            }
            QTableWidget {
                background: #f8f9fa;
                border-radius: 10px;
                font-size: 15px;
                alternate-background-color: #eaf0fb;
            }
            QHeaderView::section {
                background: #4078c0;
                color: #fff;
                font-weight: bold;
                font-size: 16px;
                border: none;
                border-radius: 8px;
                padding: 8px;
            }
            QTableWidget::item:selected {
                background: #b1c9e8;
                color: #273c75;
            }
            QLineEdit {
                border: 1.5px solid #dcdde1;
                border-radius: 8px;
                padding: 10px;
                font-size: 15px;
                background: #f8f9fa;
                margin-bottom: 10px;
            }
            QLineEdit:focus {
                border: 1.5px solid #4078c0;
                background: #fff;
            }
            QPushButton {
                background: #4078c0;
                color: #fff;
                border-radius: 8px;
                padding: 12px 28px;
                font-size: 16px;
                font-weight: bold;
                margin: 12px 0;
            }
            QPushButton:hover {
                background: #274472;
            }
        """)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(16)

        # Header
        header = QLabel(f"Admin: {self.user.email} (Company: {self.user.company.company_name})")
        header.setObjectName("Header")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(False)
        self.tabs.setDocumentMode(True)

        self.tabs.addTab(AdminWorkerTab(self.session, self.user.company_id), "Office Workers")
        self.tabs.addTab(self.create_customer_tab(), "Customers")
        # admin pending tab
        self.tabs.addTab(self.create_pending_tab(), "Pending Requests")
        # admin completed tab
        self.tabs.addTab(self.create_completed_tab(), "Completed Requests")

        self.service_tab = ServiceTab(session=self.session, company_id=self.user.company_id)
        self.tabs.addTab(self.service_tab, "Services")
        layout.addWidget(self.tabs)

        # --- New Profile Tab ---
        self.tabs.addTab(ProfileTab(self.session, self.user), "Profile & Company Info")

        # Logout button aligned right
        logout_layout = QHBoxLayout()
        logout_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        logout_btn = QPushButton("Logout")
        logout_btn.setFixedWidth(140)
        logout_btn.clicked.connect(self.logout)
        logout_layout.addWidget(logout_btn)
        layout.addLayout(logout_layout)

        self.setLayout(layout)


        '''
    # ---------- Workers Tab ----------
    def create_worker_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(18)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        self.worker_email = QLineEdit()
        self.worker_email.setPlaceholderText("Worker Email")
        form.addRow("Worker Email:", self.worker_email)

        self.worker_pwd = QLineEdit()
        self.worker_pwd.setPlaceholderText("Password")
        self.worker_pwd.setEchoMode(QLineEdit.Password)
        form.addRow("Password:", self.worker_pwd)

        add_btn = QPushButton("Add Worker")
        add_btn.clicked.connect(self.add_worker)
        layout.addLayout(form)
        layout.addWidget(add_btn)

        self.workers_table = QTableWidget(0, 2)
        self.workers_table.setHorizontalHeaderLabels(["Email", "Role"])
        self.workers_table.setAlternatingRowColors(True)
        self.workers_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.workers_table)

        load_btn = QPushButton("Refresh Workers List")
        load_btn.clicked.connect(self.load_workers)
        layout.addWidget(load_btn)

        self.load_workers()
        widget.setLayout(layout)
        return widget

    def add_worker(self):
        email = self.worker_email.text().strip()
        pwd = self.worker_pwd.text().strip()
        if not (email and pwd):
            QMessageBox.warning(self, "Error", "Email and password are required")
            return

        if self.session.query(User).filter_by(email=email).first():
            QMessageBox.warning(self, "Error", "User already exists")
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
'''
    # ---------- Customers Tab ----------
    def create_customer_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(18)

        self.customer_table = QTableWidget(0, 4)
        self.customer_table.setHorizontalHeaderLabels(["Name", "Email", "Phone", "Address"])
        self.customer_table.setAlternatingRowColors(True)
        self.customer_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.customer_table)

        refresh_btn = QPushButton("Refresh Customer List")
        refresh_btn.clicked.connect(self.load_customers)
        layout.addWidget(refresh_btn)

        self.load_customers()
        widget.setLayout(layout)
        return widget

    def load_customers(self):
        self.customer_table.setRowCount(0)
        customers = self.session.query(Customer).filter_by(company_id=self.user.company_id).all()
        for c in customers:
            row = self.customer_table.rowCount()
            self.customer_table.insertRow(row)
            self.customer_table.setItem(row, 0, QTableWidgetItem(c.name))
            self.customer_table.setItem(row, 1, QTableWidgetItem(c.email))
            self.customer_table.setItem(row, 2, QTableWidgetItem(c.phone))
            self.customer_table.setItem(row, 3, QTableWidgetItem(c.address))

    # ---------- Pending Requests Tab ----------
    def create_pending_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(18)

        self.pending_table = QTableWidget(0, 3)
        self.pending_table.setHorizontalHeaderLabels(["Request ID", "Customer", "Status"])
        self.pending_table.setAlternatingRowColors(True)
        self.pending_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.pending_table)

        refresh_btn = QPushButton("Load Pending Requests")
        refresh_btn.clicked.connect(self.load_pending_requests)
        layout.addWidget(refresh_btn)

        self.load_pending_requests()
        widget.setLayout(layout)
        return widget

    def load_pending_requests(self):
        self.pending_table.setRowCount(0)
        pending = self.session.query(ServiceRequest).filter_by(company_id=self.user.company_id, status='Pending').all()
        for req in pending:
            row = self.pending_table.rowCount()
            self.pending_table.insertRow(row)
            self.pending_table.setItem(row, 0, QTableWidgetItem(str(req.id)))
            self.pending_table.setItem(row, 1, QTableWidgetItem(req.customer.name))
            self.pending_table.setItem(row, 2, QTableWidgetItem(req.status))

    # ---------- Completed Requests Tab ----------
    def create_completed_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(18)

        self.completed_table = QTableWidget(0, 3)
        self.completed_table.setHorizontalHeaderLabels(["Request ID", "Customer", "Bill File"])
        self.completed_table.setAlternatingRowColors(True)
        self.completed_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.completed_table)

        refresh_btn = QPushButton("Load Completed Requests")
        refresh_btn.clicked.connect(self.load_completed_requests)
        layout.addWidget(refresh_btn)

        self.load_completed_requests()
        widget.setLayout(layout)
        return widget

    def load_completed_requests(self):
        self.completed_table.setRowCount(0)
        completed = self.session.query(ServiceRequest).filter_by(company_id=self.user.company_id, status='Completed').all()
        for req in completed:
            row = self.completed_table.rowCount()
            self.completed_table.insertRow(row)
            self.completed_table.setItem(row, 0, QTableWidgetItem(str(req.id)))
            self.completed_table.setItem(row, 1, QTableWidgetItem(req.customer.name))
            self.completed_table.setItem(row, 2, QTableWidgetItem(req.bill_file or "N/A"))

    # ---------- Logout ----------
    def logout(self):
        confirm = QMessageBox.question(self, "Confirm Logout", "Are you sure you want to logout?")
        if confirm == QMessageBox.Yes:
            self.session.close()
            self.logout_callback()
            self.close()