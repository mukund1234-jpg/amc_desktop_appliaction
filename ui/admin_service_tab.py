from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QSpinBox, QPushButton, QTableWidget, QTableWidgetItem, QLabel
)
from models import ServiceCatalog

class ServiceTab(QWidget):
    def __init__(self, session, company_id):
        super().__init__()
        self.session = session
        self.company_id = company_id

        layout = QVBoxLayout()

        # Title
        layout.addWidget(QLabel("➕ Add AMC Service Template"))

        form_layout = QFormLayout()

        self.category_input = QLineEdit()
        self.amc_year_input = QComboBox()
        self.amc_year_input.addItems(["1", "2", "3"])

        self.price_input = QLineEdit()
        self.compressive_price_input = QLineEdit()
        self.visits_input = QSpinBox()
        self.visits_input.setRange(1, 12)

        form_layout.addRow("Category:", self.category_input)
        form_layout.addRow("AMC Years:", self.amc_year_input)
        form_layout.addRow("Total Price (₹):", self.price_input)
        form_layout.addRow("Compressive Price/Year (₹):", self.compressive_price_input)
        form_layout.addRow("Visits per Year:", self.visits_input)

        self.add_button = QPushButton("Add Service")
        self.add_button.clicked.connect(self.add_service)

        layout.addLayout(form_layout)
        layout.addWidget(self.add_button)

        layout.addWidget(QLabel("📋 Existing Services"))
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Category", "AMC Years", "Total Price (₹)", "Compressive Price", "Visits/Year"
        ])
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_services()

    def add_service(self):
        try:
            category = self.category_input.text()
            amc_years = int(self.amc_year_input.currentText())
            price = int(self.price_input.text())
            compressive_price = int(self.compressive_price_input.text()) if self.compressive_price_input.text() else None
            visits = self.visits_input.value()

            new_service = ServiceCatalog(
                company_id=self.company_id,
                category=category,
                amc_years=amc_years,
                price=price,
                visits_per_year=visits,
                comprehensive_price=compressive_price
            )
            self.session.add(new_service)
            self.session.commit()
            self.load_services()

            # Reset inputs
            self.category_input.clear()
            self.price_input.clear()
            self.compressive_price_input.clear()
            self.visits_input.setValue(1)
        except Exception as e:
            print(f"Error: {e}")

    def load_services(self):
        services = self.session.query(ServiceCatalog).filter_by(company_id=self.company_id).all()
        self.table.setRowCount(len(services))

        for row, s in enumerate(services):
            self.table.setItem(row, 0, QTableWidgetItem(s.category))
            self.table.setItem(row, 1, QTableWidgetItem(str(s.amc_years)))
            self.table.setItem(row, 2, QTableWidgetItem(str(s.price)))
            self.table.setItem(row, 3, QTableWidgetItem(str(s.comprehensive_price or '-')))
            self.table.setItem(row, 4, QTableWidgetItem(str(s.visits_per_year)))
