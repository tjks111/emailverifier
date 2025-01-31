import os
from PyQt5 import QtWidgets, QtCore
from lib.validators import is_valid_email_syntax, has_mx_record, verify_email_smtp
import webbrowser

class EmailValidatorApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.apply_styles()
        self.verifying_timer = QtCore.QTimer()
        self.verifying_counter = 1
        self.verifying_timer.timeout.connect(self.update_verifying_text)

    def init_ui(self):
        self.setWindowTitle("KnowEmail - Email Validator")
        self.setMinimumSize(600, 500)

        # Main layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)

        # Header Section
        header_layout = QtWidgets.QVBoxLayout()
        title = QtWidgets.QLabel("KnowEmail")
        title.setObjectName("title")
        
        subtitle = QtWidgets.QLabel("Ad-Free & Open Source")
        subtitle.setObjectName("subtitle")
        
        header_layout.addWidget(title, 0, QtCore.Qt.AlignHCenter)
        header_layout.addWidget(subtitle, 0, QtCore.Qt.AlignHCenter)
        main_layout.addLayout(header_layout)

        description = QtWidgets.QLabel(
            "Tired of dealing with invalid email addresses? KnowEmail helps you "
            "clean your email lists by ensuring every address is valid before you send that "
            "important campaign."
        )
        description.setWordWrap(True)
        description.setObjectName("description")
        main_layout.addWidget(description)

        # Input Section
        input_layout = QtWidgets.QHBoxLayout()
        self.email_input = QtWidgets.QLineEdit()
        self.email_input.setPlaceholderText("Enter Email Address")
        self.email_input.setObjectName("emailInput")
        
        self.validate_button = QtWidgets.QPushButton("Check")
        self.validate_button.setObjectName("checkButton")
        self.validate_button.clicked.connect(self.validate_email)
        
        input_layout.addWidget(self.email_input)
        input_layout.addWidget(self.validate_button)
        main_layout.addLayout(input_layout)

        # Result Label
        self.result_label = QtWidgets.QLabel("")
        self.result_label.setObjectName("resultLabel")
        main_layout.addWidget(self.result_label)

        # Support Section
        support_layout = QtWidgets.QVBoxLayout()
        support_label = QtWidgets.QLabel(
            "We've made this tool free and open-source for everyone. If you'd like to support our "
            "development efforts, consider donating."
        )
        support_label.setWordWrap(True)
        support_label.setObjectName("supportLabel")
        
        donate_button = QtWidgets.QPushButton("Support Us")
        donate_button.setObjectName("donateButton")
        donate_button.clicked.connect(lambda: webbrowser.open("https://example.com/donate"))
        
        support_layout.addWidget(support_label, 0, QtCore.Qt.AlignHCenter)
        support_layout.addWidget(donate_button, 0, QtCore.Qt.AlignHCenter)
        main_layout.addLayout(support_layout)
        main_layout.addStretch(1)

        self.setLayout(main_layout)

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
    
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Validation Result")
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        style_path = os.path.join(current_dir, 'styles.qss')
        if os.path.exists(style_path):
            with open(style_path, 'r') as f:
                msg.setStyleSheet(f.read())
        
        msg.exec_()