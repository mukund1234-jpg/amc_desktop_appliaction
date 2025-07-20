from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from database import SessionLocal
from ui.service_form_tab import ServiceFormTab
from ui.pending_tab import PendingRequestsTab
from ui.complet_request import CompletedRequestsTab

class OfficeWorkerDashboard(QWidget):
    def __init__(self,user):
        super().__init__()
        self.setWindowTitle("AMC Service Management")
        self.setGeometry(300, 200, 900, 600)
        self.db = SessionLocal()
        self.user = user

        self.tabs = QTabWidget()

        self.completed_tab = CompletedRequestsTab(self.db,self.user)
        self.pending_tab = PendingRequestsTab(self.db,self.user, self.completed_tab.load_completed_requests)
        self.form_tab = ServiceFormTab(self.db, self.user, self.pending_tab.load_pending_requests)

        self.tabs.addTab(self.form_tab, "Service Request Form")
        self.tabs.addTab(self.pending_tab, "Pending Requests")
        self.tabs.addTab(self.completed_tab, "Completed Requests")

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)
