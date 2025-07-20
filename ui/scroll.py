from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt

class ServiceDetailsDialog(QDialog):
    def __init__(self, details_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Service Details")
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        label = QLabel()
        label.setTextFormat(Qt.RichText)  # Ensure it treats the text as HTML
        label.setWordWrap(True)
        label.setText(details_text)
        content_layout.addWidget(label)

        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        # Add Close Button
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
