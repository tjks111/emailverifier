import os
from PyQt5 import QtWidgets, QtCore
from lib.validators import is_valid_email_syntax, has_mx_record, verify_email_smtp

class EmailValidatorApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.apply_styles()
        self.verifying_timer = QtCore.QTimer()
        self.verifying_counter = 1
        self.verifying_timer.timeout.connect(self.update_verifying_text)

    def init_ui(self):
        self.setWindowTitle("Email Validator")
        self.setMinimumSize(400, 200)

        # Create widgets
        self.email_input = QtWidgets.QLineEdit(self)
        self.email_input.setPlaceholderText("Enter email address")
        
        self.validate_button = QtWidgets.QPushButton("Validate Email", self)
        self.validate_button.clicked.connect(self.validate_email)
        
        self.result_label = QtWidgets.QLabel("", self)

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.email_input)
        layout.addWidget(self.validate_button)
        layout.addWidget(self.result_label)
        self.setLayout(layout)

    def apply_styles(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        style_path = os.path.join(current_dir, 'styles.qss')
        with open(style_path, 'r') as f:
            self.setStyleSheet(f.read())

    def update_verifying_text(self):
        self.result_label.setText(f"Verifying{'.' * self.verifying_counter}")
        self.verifying_counter = (self.verifying_counter % 3) + 1

    def validate_email(self):
        email = self.email_input.text()
        if not email:
            QtWidgets.QMessageBox.warning(self, "Error", "Email parameter is required")
            return

        if not is_valid_email_syntax(email):
            QtWidgets.QMessageBox.warning(self, "Error", "Invalid email syntax")
            return

        self.verifying_counter = 1
        self.verifying_timer.start(500)
        self.result_label.setText("Verifying...")

        QtCore.QTimer.singleShot(100, lambda: self.verify_in_background(email))

    def verify_in_background(self, email):
        domain = email.split('@')[1]
        if not has_mx_record(domain):
            self.show_popup("Domain does not have MX records")
            return

        try:
            if not verify_email_smtp(email):
                self.show_popup("SMTP verification failed! Email is not valid.")
            else:
                self.show_popup("Email is valid and appears to be reachable")
        except Exception as e:
            self.show_popup(f"Error: {str(e)}")
        finally:
            self.verifying_timer.stop()

    def show_popup(self, message):
        self.verifying_timer.stop()
        self.result_label.setText("")
        QtWidgets.QMessageBox.information(self, "Validation Result", message)