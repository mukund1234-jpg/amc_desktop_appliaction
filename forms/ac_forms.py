from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox
from database import SessionLocal
from models import ACRequest, RequestForm, Customer
from datetime import date, timedelta

class ACForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add AC Request")
        layout = QVBoxLayout()

        self.customer_id_input = QLineEdit()
        self.customer_id_input.setPlaceholderText("Customer ID")
        layout.addWidget(self.customer_id_input)

        self.brand_input = QComboBox()
        self.brand_input.addItems(["Voltas", "LG", "Samsung", "Daikin", "Hitachi"])
        layout.addWidget(QLabel("Brand"))
        layout.addWidget(self.brand_input)

        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Quantity")
        layout.addWidget(self.quantity_input)

        self.year_input = QComboBox()
        self.year_input.addItems(["1", "3"])
        layout.addWidget(QLabel("AMC Years"))
        layout.addWidget(self.year_input)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_request)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

    def save_request(self):
        db = SessionLocal()
        customer_id = int(self.customer_id_input.text())
        brand = self.brand_input.currentText()
        quantity = int(self.quantity_input.text())
        years = int(self.year_input.currentText())

        # Create main request
        req = RequestForm(
            customer_id=customer_id,
            category="AC",
            comprensive="Comprensive",
            status="Completed",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365 * years),
            visit_count=3 if years == 1 else 9,
            price=(1000 if years == 1 else 3000) * quantity
        )
        db.add(req)
        db.commit()

        # Add AC specific
        ac = ACRequest(
            request_form_id=req.id,
            ac_type="SAC",
            product_brand=brand,
            amc_years=years,
            quantity=quantity
        )
        db.add(ac)
        db.commit()
        QMessageBox.information(self, "Saved", "AC Request Saved")
