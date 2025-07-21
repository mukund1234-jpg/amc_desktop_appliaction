from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget, QMessageBox
from database import SessionLocal
from ui.service_form_tab import ServiceFormTab
from ui.pending_tab import PendingRequestsTab
from ui.complet_request import CompletedRequestsTab

class OfficeWorkerDashboard(QWidget):
    def __init__(self, user, logout_callback):
        super().__init__()
        self.setWindowTitle("AMC Service Management - Office Worker")
        self.setGeometry(300, 200, 900, 600)
        self.db = SessionLocal()
        self.user = user
        self.logout_callback = logout_callback

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # --- Top layout with Logout Button on the right ---
        top_layout = QHBoxLayout()
        top_layout.addStretch()  # Pushes the button to the right
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout)
        top_layout.addWidget(logout_btn)
        layout.addLayout(top_layout)

        # --- Tabs ---
        self.tabs = QTabWidget()

        self.completed_tab = CompletedRequestsTab(self.db, self.user)
        self.pending_tab = PendingRequestsTab(self.db, self.user, self.completed_tab.load_completed_requests)
        self.form_tab = ServiceFormTab(self.db, self.user, self.pending_tab.load_pending_requests)

        self.tabs.addTab(self.form_tab, "Service Request Form")
        self.tabs.addTab(self.pending_tab, "Pending Requests")
        self.tabs.addTab(self.completed_tab, "Completed Requests")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def logout(self):
        confirm = QMessageBox.question(self, "Confirm Logout", "Are you sure you want to logout?")
        if confirm == QMessageBox.Yes:
            self.db.close()
            self.logout_callback()
            self.close()
        else:
            QMessageBox.information(self, "Logout Cancelled", "You are still logged in.")