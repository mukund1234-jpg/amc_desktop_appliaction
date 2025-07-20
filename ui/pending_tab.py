from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox
from models import Customer, ServiceRequest, ServiceItem, Visit
from utils.pdf_generator import generate_pdf
from utils.visit_utils import regenerate_visits_for_request
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
from ui.scroll import ServiceDetailsDialog
import os


class PendingRequestsTab(QWidget):
    def __init__(self, db, user, reload_completed_callback):
        super().__init__()
        self.db = db
        self.user = user
        self.reload_completed = reload_completed_callback
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.pending_table = QTableWidget(0, 11)
        self.pending_table.setHorizontalHeaderLabels([
            'Request ID', 'Customer Name', 'Email', 'Phone', 'Address',
            'Created Date', 'AMC Years', 'Total Visits',
            'Total Price', 'Service Details', 'Actions'
        ])
        layout.addWidget(self.pending_table)

        self.setLayout(layout)
        self.load_pending_requests()

    def load_pending_requests(self):
        self.pending_table.setRowCount(0)
        requests = (
            self.db.query(ServiceRequest)
            .join(Customer)
            .filter(ServiceRequest.status == 'Pending', Customer.company_id == self.user.company_id)
            .options(joinedload(ServiceRequest.items), joinedload(ServiceRequest.visits))
            .all()
        )

        for req in requests:
            self.add_request_row(req)

    def add_request_row(self, req):
        customer = req.customer
        items = req.items

        if not req.start_time:
            req.start_time = datetime.now().date()
            req.end_time = req.start_time + timedelta(days=365 * self.get_max_amc_years(items))
            self.db.commit()

        if not req.visits:
            regenerate_visits_for_request(self.db, req.id)

        total_price = self.calculate_total_price(items)
        amc_years = self.get_max_amc_years(items)
        total_visits = self.calculate_total_visits(items)

        row = self.pending_table.rowCount()
        self.pending_table.insertRow(row)

        self.pending_table.setItem(row, 0, QTableWidgetItem(str(req.id)))
        self.pending_table.setItem(row, 1, QTableWidgetItem(customer.name))
        self.pending_table.setItem(row, 2, QTableWidgetItem(customer.email))
        self.pending_table.setItem(row, 3, QTableWidgetItem(customer.phone))
        self.pending_table.setItem(row, 4, QTableWidgetItem(customer.address))
        self.pending_table.setItem(row, 5, QTableWidgetItem(req.start_time.strftime('%Y-%m-%d')))
        self.pending_table.setItem(row, 6, QTableWidgetItem(str(amc_years)))
        self.pending_table.setItem(row, 7, QTableWidgetItem(str(total_visits)))
        self.pending_table.setItem(row, 8, QTableWidgetItem(f"Rs. {total_price}"))

        view_btn = QPushButton("View")
        view_btn.clicked.connect(lambda _, r=req: self.show_service_details(r))
        self.pending_table.setCellWidget(row, 9, view_btn)

        complete_btn = QPushButton("Complete & Bill")
        complete_btn.clicked.connect(lambda _, rid=req.id: self.complete_request(rid))
        self.pending_table.setCellWidget(row, 10, complete_btn)

    def calculate_total_price(self, items):
        return sum(item.total_price for item in items)

    def get_max_amc_years(self, items):
        return max((item.amc_years for item in items), default=0)

    def calculate_total_visits(self, items):
        return sum(3 if item.amc_years == 1 else 9 for item in items)

    def show_service_details(self, request):
        details = ""
        for item in request.items:
            details += f"<b>{item.category}</b>: {item.brand} - {item.type} | Qty: {item.quantity} | AMC: {item.amc_years} Years | Comp: {item.comprehensive} | Price: Rs. {item.total_price}<br>"

            visits = [v for v in request.visits if v.service_item_id == item.id]
            for visit in visits:
                status = 'Completed' if visit.completed else 'Pending'
                date = visit.scheduled_date.strftime('%d-%m-%Y') if visit.scheduled_date else 'N/A'
                details += f"&emsp;➡ Visit {visit.visit_number}: {date} | Status: {status}<br>"

            details += "<hr>"

        dialog = ServiceDetailsDialog(details, parent=self)
        dialog.exec_()

    def complete_request(self, request_id):
        request = (
            self.db.query(ServiceRequest)
            .options(joinedload(ServiceRequest.items))
            .get(request_id)
        )

        customer = request.customer
        bill_folder = 'bills'
        os.makedirs(bill_folder, exist_ok=True)
        bill_filename = os.path.join(bill_folder, f'bill_{request.id}.pdf')

        customer_info = {
            'name': customer.name,
            'address': customer.address,
            'phone': customer.phone,
            'email': customer.email
        }

        generate_pdf(
            customer_info,
            request.items,
            filename=bill_filename,
            start=request.start_time,
            end=request.end_time
        )

        request.status = 'Completed'
        request.bill_file = bill_filename
        self.db.commit()

        QMessageBox.information(self, "Completed", f"Request Completed. Bill generated: {bill_filename}")
        self.load_pending_requests()
        self.reload_completed()
