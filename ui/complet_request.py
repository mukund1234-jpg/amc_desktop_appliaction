from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox
from models import ServiceRequest, Customer
from sqlalchemy.orm import joinedload
import os
import webbrowser
from ui.scroll import ServiceDetailsDialog
from functools import partial


class CompletedRequestsTab(QWidget):
    def __init__(self, db, user):
        super().__init__()
        self.db = db
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.completed_table = QTableWidget(0, 9)
        self.completed_table.setHorizontalHeaderLabels([
            'Request ID', 'Customer Info', 'Start Date', 'End Date', 'Bill',
            'Status', 'Open PDF', 'Show Visits', '---'
        ])
        layout.addWidget(self.completed_table)

        self.setLayout(layout)
        self.load_completed_requests()

    def load_completed_requests(self):
        self.completed_table.setRowCount(0)
        completed_requests = (
            self.db.query(ServiceRequest)
            .join(Customer)
            .filter(ServiceRequest.status == 'Completed', Customer.company_id == self.user.company_id)
            .options(joinedload(ServiceRequest.visits), joinedload(ServiceRequest.items))
            .all()
        )

        for req in completed_requests:
            customer = req.customer
            start = req.start_time.strftime('%Y-%m-%d') if req.start_time else '-'
            end = req.end_time.strftime('%Y-%m-%d') if req.end_time else '-'

            row = self.completed_table.rowCount()
            self.completed_table.insertRow(row)

            customer_info = f"{customer.name}\n{customer.phone}\n{customer.email}\n{customer.address}"
            self.completed_table.setItem(row, 0, QTableWidgetItem(str(req.id)))
            self.completed_table.setItem(row, 1, QTableWidgetItem(customer_info))
            self.completed_table.setItem(row, 2, QTableWidgetItem(start))
            self.completed_table.setItem(row, 3, QTableWidgetItem(end))
            self.completed_table.setItem(row, 4, QTableWidgetItem(req.bill_file or 'N/A'))
            self.completed_table.setItem(row, 5, QTableWidgetItem(req.status))

            pdf_btn = QPushButton("Open PDF")
            if req.bill_file and os.path.exists(req.bill_file):
                pdf_btn.clicked.connect(lambda _, f=req.bill_file: self.open_pdf(f))
            else:
                pdf_btn.setEnabled(False)
            self.completed_table.setCellWidget(row, 6, pdf_btn)

            visits_btn = QPushButton("Show Visits")
            visits_btn.clicked.connect(partial(self.show_visits, req))
            self.completed_table.setCellWidget(row, 7, visits_btn)

    def open_pdf(self, filepath):
        if os.path.exists(filepath):
            abs_path = os.path.abspath(filepath)
            webbrowser.open(f'file:///{abs_path.replace(os.sep, "/")}')
        else:
            QMessageBox.warning(self, "File Error", "PDF file does not exist.")

    def show_visits(self, request):
        message = ""
        for item in request.items:
            message += f"<b>{item.category}:</b> {item.brand} - {item.type} | Qty: {item.quantity} | AMC: {item.amc_years} Years | Rs. {item.total_price}<br>"

            visits = [v for v in request.visits if v.service_item_id == item.id]
            for visit in visits:
                status = 'Completed' if visit.completed else 'Pending'
                date = visit.scheduled_date.strftime('%d-%m-%Y') if visit.scheduled_date else 'N/A'
                message += f"&emsp;➡ Visit {visit.visit_number}: {date} | Status: {status}<br>"

            message += "<hr>"

        if not message.strip():
            message = "No visits recorded."

        dialog = ServiceDetailsDialog(message, parent=self)
        dialog.exec_()
