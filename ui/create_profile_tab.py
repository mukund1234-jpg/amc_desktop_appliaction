from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel, QFileDialog, QMessageBox

class ProfileTab(QWidget):
    def __init__(self, session, user):
        super().__init__()
        self.session = session
        self.user = user
        self.company = user.company

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(18)

        # --- Form ---
        form = QFormLayout()
        self.gst_input = QLineEdit(self.company.gst_number or "")
        self.pan_input = QLineEdit(self.company.pan_number or "")
        self.phone_input = QLineEdit(self.user.phone or "")
        self.address_input = QLineEdit(self.user.address or "")

        form.addRow("GST Number:", self.gst_input)
        form.addRow("PAN Number:", self.pan_input)
        form.addRow("Admin Phone:", self.phone_input)
        form.addRow("Company Address:", self.address_input)

        # --- Logo & Signature ---
        self.logo_label = QLabel("Company Logo: " + (self.company.logo_path or "Not uploaded"))
        self.signature_label = QLabel("Owner Sign: " + (self.company.owner_signature_path or "Not uploaded"))

        upload_logo_btn = QPushButton("Upload Logo")
        upload_logo_btn.clicked.connect(self.upload_logo)
        upload_sign_btn = QPushButton("Upload Signature")
        upload_sign_btn.clicked.connect(self.upload_signature)

        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_profile)

        layout.addLayout(form)
        layout.addWidget(self.logo_label)
        layout.addWidget(upload_logo_btn)
        layout.addWidget(self.signature_label)
        layout.addWidget(upload_sign_btn)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def upload_logo(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Logo", "", "Images (*.png *.jpg *.jpeg)")
        if file:
            self.company.logo_path = file
            self.session.add(self.company)
            self.session.commit()
            self.logo_label.setText(f"Company Logo: {file}")

    def upload_signature(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Signature", "", "Images (*.png *.jpg *.jpeg)")
        if file:
            self.company.owner_signature_path = file
            self.session.add(self.company)
            self.session.commit()
            self.signature_label.setText(f"Owner Sign: {file}")

    def save_profile(self):
        self.company.gst_number = self.gst_input.text().strip()
        self.company.pan_number = self.pan_input.text().strip()
        self.user.phone = self.phone_input.text().strip()
        self.user.address = self.address_input.text().strip()

        self.session.add_all([self.user, self.company])
        self.session.commit()
        QMessageBox.information(self, "Saved", "Profile updated successfully!")
