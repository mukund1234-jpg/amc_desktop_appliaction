from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QSpinBox, QGroupBox, QFormLayout
)
from models import Customer, ServiceRequest, ServiceItem


class ServiceFormTab(QWidget):
    def __init__(self, db, user, reload_pending_callback):
        super().__init__()
        self.db = db
        self.user = user
        self.reload_pending = reload_pending_callback
        self.service_items = []
        self.current_edit_index = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- Customer Details ---
        customer_group = QGroupBox("Customer Details")
        customer_form = QFormLayout()

        self.customer_input = QLineEdit()
        customer_form.addRow("Name:", self.customer_input)

        self.email_input = QLineEdit()
        customer_form.addRow("Email:", self.email_input)

        self.phone_input = QLineEdit()
        customer_form.addRow("Phone Number:", self.phone_input)

        self.address_input = QLineEdit()
        customer_form.addRow("Address:", self.address_input)

        customer_group.setLayout(customer_form)
        main_layout.addWidget(customer_group)

        # --- Service Item Details ---
        service_group = QGroupBox("Service Item Details")
        service_form = QFormLayout()

        self.category_input = QComboBox()
        self.category_input.addItems(['Air Conditioner', 'Chimney', 'Water Purifier', 'Washing Machine', 'Refrigerator', 'Hub'])
        service_form.addRow("Category:", self.category_input)

        self.brand_input = QLineEdit()
        service_form.addRow("Brand:", self.brand_input)

        self.type_input = QLineEdit()
        service_form.addRow("Type:", self.type_input)

        self.comprehensive_input = QComboBox()
        self.comprehensive_input.addItems(['Yes', 'No'])
        service_form.addRow("Comprehensive Type:", self.comprehensive_input)

        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 100)
        service_form.addRow("Quantity:", self.quantity_input)

        self.amc_years_input = QComboBox()
        self.amc_years_input.addItems(['1', '3'])
        service_form.addRow("AMC Years:", self.amc_years_input)

        self.add_item_btn = QPushButton("Add Service Item")
        self.add_item_btn.clicked.connect(self.add_or_update_service_item)
        service_form.addRow(self.add_item_btn)

        service_group.setLayout(service_form)
        main_layout.addWidget(service_group)

        # --- Service Items Table ---
        self.items_table = QTableWidget(0, 13)
        self.items_table.setHorizontalHeaderLabels([
            'Category', 'Brand', 'Type', 'Comprehensive', 'Qty', 'AMC Years',
            'Customer', 'Email', 'Phone', 'Address', 'Total Price', 'Update', 'Delete'
        ])
        main_layout.addWidget(self.items_table)

        # --- Final Submit Button ---
        self.submit_form_btn = QPushButton("Submit Full Service Request")
        self.submit_form_btn.clicked.connect(self.submit_full_service_request)
        main_layout.addWidget(self.submit_form_btn)

        self.setLayout(main_layout)
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f9f9f9;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004080;
            }
            QLineEdit, QComboBox, QSpinBox {
                padding: 4px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #ddd;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)

    def calculate_total_price(self, quantity, amc_years, comprehensive):
        base_price = 1000 if amc_years == 1 else 3000
        comprehensive_charge = 300 if comprehensive.lower() == 'yes' else 0
        return (base_price + comprehensive_charge) * quantity

    def add_or_update_service_item(self):
        quantity = self.quantity_input.value()
        amc_years = int(self.amc_years_input.currentText())
        comprehensive = self.comprehensive_input.currentText()
        total_price = self.calculate_total_price(quantity, amc_years, comprehensive)

        item = {
            'category': self.category_input.currentText(),
            'brand': self.brand_input.text(),
            'type': self.type_input.text(),
            'comprehensive': comprehensive,
            'quantity': quantity,
            'amc_years': amc_years,
            'customer_name': self.customer_input.text(),
            'email': self.email_input.text(),
            'phone': self.phone_input.text(),
            'address': self.address_input.text(),
            'total_price': total_price
        }

        if self.current_edit_index is not None:
            self.service_items[self.current_edit_index] = item
            self.current_edit_index = None
            self.add_item_btn.setText("Add Service Item")
        else:
            self.service_items.append(item)

        self.update_items_table()
        self.clear_item_fields()

    def update_items_table(self):
        self.items_table.setRowCount(0)
        for idx, item in enumerate(self.service_items):
            self.items_table.insertRow(idx)
            self.items_table.setItem(idx, 0, QTableWidgetItem(item['category']))
            self.items_table.setItem(idx, 1, QTableWidgetItem(item['brand']))
            self.items_table.setItem(idx, 2, QTableWidgetItem(item['type']))
            self.items_table.setItem(idx, 3, QTableWidgetItem(item['comprehensive']))
            self.items_table.setItem(idx, 4, QTableWidgetItem(str(item['quantity'])))
            self.items_table.setItem(idx, 5, QTableWidgetItem(str(item['amc_years'])))
            self.items_table.setItem(idx, 6, QTableWidgetItem(item['customer_name']))
            self.items_table.setItem(idx, 7, QTableWidgetItem(item['email']))
            self.items_table.setItem(idx, 8, QTableWidgetItem(item['phone']))
            self.items_table.setItem(idx, 9, QTableWidgetItem(item['address']))
            self.items_table.setItem(idx, 10, QTableWidgetItem(f'Rs. {item["total_price"]}'))

            update_btn = QPushButton("Update")
            update_btn.setStyleSheet("background-color: #ffc107; color: black;")
            update_btn.clicked.connect(lambda _, i=idx: self.load_item_for_update(i))
            self.items_table.setCellWidget(idx, 11, update_btn)

            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("background-color: #dc3545; color: white;")
            delete_btn.clicked.connect(lambda _, i=idx: self.delete_service_item(i))
            self.items_table.setCellWidget(idx, 12, delete_btn)

    def load_item_for_update(self, index):
        item = self.service_items[index]
        self.category_input.setCurrentText(item['category'])
        self.brand_input.setText(item['brand'])
        self.type_input.setText(item['type'])
        self.comprehensive_input.setCurrentText(item['comprehensive'])
        self.quantity_input.setValue(item['quantity'])
        self.amc_years_input.setCurrentText(str(item['amc_years']))

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
        if not self.customer_input.text().strip() or not self.email_input.text().strip():
            QMessageBox.warning(self, "Missing Info", "Please fill in all customer details.")
            return

        if not self.service_items:
            QMessageBox.warning(self, "Missing Info", "Please add at least one service item before submitting.")
            return

        customer = self.db.query(Customer).filter_by(email=self.email_input.text().strip()).first()
        if not customer:
            customer = Customer(
                company_id=self.user.company_id,
                name=self.customer_input.text().strip(),
                email=self.email_input.text().strip(),
                phone=self.phone_input.text().strip(),
                address=self.address_input.text().strip()
                
            )
            self.db.add(customer)
            self.db.commit()

        # Check if a pending request exists for this customer
        existing_request = self.db.query(ServiceRequest).filter_by(customer_id=customer.id, status='Pending').first()

        if not existing_request:
            existing_request = ServiceRequest(customer_id=customer.id, 
                                          company_id=self.user.company_id,
                                             start_time=None, end_time=None,
                                              status='Pending')
            self.db.add(existing_request)
            self.db.commit()

        # Add all service items to the existing or new request
        for item in self.service_items:
            service_item = ServiceItem(
                request_id=existing_request.id,
                category=item['category'],
                brand=item['brand'],
                type=item['type'],
                quantity=item['quantity'],
                amc_years=item['amc_years'],
                comprehensive=item['comprehensive'],
                base_price=1000 if item['amc_years'] == 1 else 3000,
                comprehensive_charge=300 if item['comprehensive'].lower() == 'yes' else 0,
                total_price=item['total_price'],
                company_id=self.user.company_id    

            )
            self.db.add(service_item)

        self.db.commit()

        QMessageBox.information(self, "Success", "Service Items added to request successfully.")
        self.service_items.clear()
        self.update_items_table()
        self.clear_all_fields()
        self.reload_pending()


    def clear_item_fields(self):
        self.category_input.setCurrentIndex(0)
        self.brand_input.clear()
        self.type_input.clear()
        self.comprehensive_input.setCurrentIndex(0)
        self.quantity_input.setValue(1)
        self.amc_years_input.setCurrentIndex(0)

    def clear_all_fields(self):
        self.customer_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        self.address_input.clear()
        self.clear_item_fields()
