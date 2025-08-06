from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QSpinBox, QGroupBox, QFormLayout
)
from models import Customer, ServiceRequest, ServiceItem, ServiceCatalog
from sqlalchemy.orm import Session
from datetime import date


class ServiceFormTab(QWidget):
    def __init__(self, db: Session, user, reload_pending_callback):
        super().__init__()
        self.db = db
        self.user = user
        self.reload_pending = reload_pending_callback
        self.service_items = []
        self.catalog_map = {}
        self.current_edit_index = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # --- Customer Details ---
        customer_group = QGroupBox("Customer Details")
        customer_form = QFormLayout()
        self.customer_input = QLineEdit()
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.address_input = QLineEdit()
        customer_form.addRow("Name:", self.customer_input)
        customer_form.addRow("Email:", self.email_input)
        customer_form.addRow("Phone:", self.phone_input)
        customer_form.addRow("Address:", self.address_input)
        customer_group.setLayout(customer_form)
        main_layout.addWidget(customer_group)

        # --- Service Item Entry ---
        service_group = QGroupBox("Service Item Details")
        service_form = QFormLayout()

        self.catalog_input = QComboBox()
        catalogs = self.db.query(ServiceCatalog).filter_by(company_id=self.user.company_id).all()
        for catalog in catalogs:
            key = f"{catalog.category} - {catalog.amc_years} Years"
            self.catalog_map[key] = catalog
            self.catalog_input.addItem(key)

        self.comprehensive_input = QComboBox()
        self.comprehensive_input.addItems(["Yes", "No"])

        self.brand_input = QLineEdit()
        self.type_input = QLineEdit()
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 100)

        self.add_item_btn = QPushButton("Add Service Item")
        self.add_item_btn.clicked.connect(self.add_or_update_service_item)

        service_form.addRow("AMC Plan:", self.catalog_input)
        service_form.addRow("Comprehensive:", self.comprehensive_input)
        service_form.addRow("Brand:", self.brand_input)
        service_form.addRow("Type:", self.type_input)
        service_form.addRow("Quantity:", self.quantity_input)
        service_form.addRow(self.add_item_btn)

        service_group.setLayout(service_form)
        main_layout.addWidget(service_group)

        # --- Table ---
        self.items_table = QTableWidget(0, 13)
        self.items_table.setHorizontalHeaderLabels([
            'Category', 'Brand', 'Type', 'Comprehensive', 'Qty', 'AMC Years',
            'Customer', 'Email', 'Phone', 'Address', 'Total Price', 'Update', 'Delete'
        ])
        main_layout.addWidget(self.items_table)

        # --- Final Submit ---
        self.submit_form_btn = QPushButton("Submit Full Service Request")
        self.submit_form_btn.clicked.connect(self.submit_full_service_request)
        main_layout.addWidget(self.submit_form_btn)

        self.setLayout(main_layout)
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QPushButton { background-color: #007bff; color: white; }
            QPushButton:hover { background-color: #0056b3; }
            QLineEdit, QComboBox, QSpinBox { padding: 4px; }
        """)

    def add_or_update_service_item(self):
        key = self.catalog_input.currentText()
        catalog = self.catalog_map.get(key)
        if not catalog:
            QMessageBox.warning(self, "Invalid Plan", "Please select a valid AMC plan.")
            return

        comprehensive_choice = self.comprehensive_input.currentText()

        item_data = {
            'catalog': catalog,
            'brand': self.brand_input.text(),
            'type': self.type_input.text(),
            'quantity': self.quantity_input.value(),
            'comprehensive': comprehensive_choice,
            'customer_name': self.customer_input.text(),
            'email': self.email_input.text(),
            'phone': self.phone_input.text(),
            'address': self.address_input.text()
        }

        if not all([item_data['brand'], item_data['type'], item_data['customer_name'], item_data['email']]):
            QMessageBox.warning(self, "Incomplete", "Please fill all required fields.")
            return

        service_item = ServiceItem(
            category=catalog.category,
            brand=item_data['brand'],
            type=item_data['type'],
            quantity=item_data['quantity'],
            amc_years=catalog.amc_years,
            visits_per_year=catalog.visits_per_year,
            comprehensive=comprehensive_choice,
            company_id=self.user.company_id
        )

        # Manual pricing logic
        base_price = catalog.price
        comp_price = catalog.comprehensive_price if comprehensive_choice.lower() == 'yes' else 0
        total_price = (base_price + comp_price) * item_data['quantity']

        service_item.base_price = base_price
        service_item.comprehensive_charge = comp_price
        service_item.total_price = total_price

        item_data.update({
            'amc_years': catalog.amc_years,
            'price_per_unit': base_price,
            'comprehensive_price': comp_price,
            'total_price': total_price,
            'service_item': service_item
        })

        if self.current_edit_index is not None:
            self.service_items[self.current_edit_index] = item_data
            self.current_edit_index = None
            self.add_item_btn.setText("Add Service Item")
        else:
            self.service_items.append(item_data)

        self.update_items_table()
        self.clear_item_fields()

    def update_items_table(self):
        self.items_table.setRowCount(0)
        for idx, item in enumerate(self.service_items):
            self.items_table.insertRow(idx)
            self.items_table.setItem(idx, 0, QTableWidgetItem(item['catalog'].category))
            self.items_table.setItem(idx, 1, QTableWidgetItem(item['brand']))
            self.items_table.setItem(idx, 2, QTableWidgetItem(item['type']))
            self.items_table.setItem(idx, 3, QTableWidgetItem(item['comprehensive']))
            self.items_table.setItem(idx, 4, QTableWidgetItem(str(item['quantity'])))
            self.items_table.setItem(idx, 5, QTableWidgetItem(str(item['amc_years'])))
            self.items_table.setItem(idx, 6, QTableWidgetItem(item['customer_name']))
            self.items_table.setItem(idx, 7, QTableWidgetItem(item['email']))
            self.items_table.setItem(idx, 8, QTableWidgetItem(item['phone']))
            self.items_table.setItem(idx, 9, QTableWidgetItem(item['address']))
            self.items_table.setItem(idx, 10, QTableWidgetItem(f"Rs. {item['total_price']}"))

            update_btn = QPushButton("Update")
            update_btn.clicked.connect(lambda _, i=idx: self.load_item_for_update(i))
            self.items_table.setCellWidget(idx, 11, update_btn)

            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda _, i=idx: self.delete_service_item(i))
            self.items_table.setCellWidget(idx, 12, delete_btn)

    def load_item_for_update(self, index):
        item = self.service_items[index]
        key = f"{item['catalog'].category} - {item['catalog'].amc_years} Years"
        self.catalog_input.setCurrentText(key)
        self.comprehensive_input.setCurrentText(item['comprehensive'])
        self.brand_input.setText(item['brand'])
        self.type_input.setText(item['type'])
        self.quantity_input.setValue(item['quantity'])

        self.customer_input.setText(item['customer_name'])
        self.email_input.setText(item['email'])
        self.phone_input.setText(item['phone'])
        self.address_input.setText(item['address'])

        self.current_edit_index = index
        self.add_item_btn.setText("Apply Update")

    def delete_service_item(self, index):
        del self.service_items[index]
        self.update_items_table()

    def submit_full_service_request(self):
        if not self.customer_input.text() or not self.email_input.text():
            QMessageBox.warning(self, "Incomplete", "Customer name and email are required.")
            return
        if not self.service_items:
            QMessageBox.warning(self, "No Items", "Add at least one service item.")
            return

        customer = self.db.query(Customer).filter_by(
            company_id=self.user.company_id,
            email=self.email_input.text()
        ).first()

        if not customer:
            customer = Customer(
                name=self.customer_input.text(),
                email=self.email_input.text(),
                phone=self.phone_input.text(),
                address=self.address_input.text(),
                company_id=self.user.company_id
            )
            self.db.add(customer)
            self.db.commit()
        
        create_service_request = self.user.id  # Assuming user has a company_id attribute
        request = ServiceRequest(
            customer_id=customer.id,
            company_id=self.user.company_id,
            created_by=create_service_request,  # Assuming user has an id attribute
            status='Pending'
        )
        self.db.add(request)
        self.db.commit()

        for item in self.service_items:
            service_item = item['service_item']
            service_item.request_id = request.id
            self.db.add(service_item)

        self.db.commit()

        QMessageBox.information(self, "Success", "Service Request created.")
        self.service_items.clear()
        self.update_items_table()
        self.clear_all_fields()
        self.reload_pending()

    def clear_item_fields(self):
        self.catalog_input.setCurrentIndex(0)
        self.comprehensive_input.setCurrentIndex(0)
        self.brand_input.clear()
        self.type_input.clear()
        self.quantity_input.setValue(1)

    def clear_all_fields(self):
        self.customer_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        self.address_input.clear()
        self.clear_item_fields()
