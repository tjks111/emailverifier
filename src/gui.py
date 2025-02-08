import os
import webbrowser
from PyQt5 import QtWidgets, QtCore, QtGui
from lib.validators import is_valid_email_syntax, has_mx_record, verify_email_smtp
import pandas as pd

class ResultDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("KnowEmail - Verifying Bulk Emails")
        self.setMinimumSize(600, 400)deac
        self.layout = QtWidgets.QVBoxLayout()
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Email", "Status"])
        self.table.horizontalHeader().setStretchLastSection(True)
        
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)


    # Enable the "?" help button
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowContextHelpButtonHint)

        

    def add_row(self, email, status):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        
        email_item = QtWidgets.QTableWidgetItem(email)
        status_item = QtWidgets.QTableWidgetItem(status)
        
        if status == "Valid":
            status_item.setForeground(QtGui.QColor('#27ae60'))  # Green
        elif status.startswith("Invalid"):
            status_item.setForeground(QtGui.QColor('#e74c3c'))  # Red
        else:
            status_item.setForeground(QtGui.QColor('#f1c40f'))  # Yellow
        
        self.table.setItem(row_position, 0, email_item)
        self.table.setItem(row_position, 1, status_item)
    
    def showEvent(self, event):
        """Override showEvent to ensure the help button is available."""
        super().showEvent(event)
        
        # Find the help button after the dialog is shown
        help_button = self.findChild(QtWidgets.QAbstractButton, "qt_help_button")
        if help_button:
            help_button.clicked.connect(self.show_status_help)

    def show_status_help(self):
        help_text = """
        <b>Verification Status Explanations:</b><br><br>
        
        <span style='color:#27ae60; font-weight:bold'>Valid</span>: 
        - Email address is valid and reachable<br>
        - Domain has proper MX records<br>
        - SMTP server confirmed the mailbox exists<br><br>
        
        <span style='color:#e74c3c; font-weight:bold'>Invalid (Syntax)</span>: 
        - Email format is incorrect<br>
        - Missing @ symbol or invalid domain structure<br>
        - Example: <i>user@domain</i> (missing .com)<br><br>
        
        <span style='color:#e74c3c; font-weight:bold'>Invalid (No MX)</span>: 
        - Domain does not have mail exchange records<br>
        - Domain might not exist or is not configured for email<br>
        - Example: <i>user@nonexistentdomain.xyz</i><br><br>
        
        <span style='color:#e74c3c; font-weight:bold'>Invalid (SMTP)</span>: 
        - Domain exists, but the mailbox does not<br>
        - SMTP server rejected the recipient address<br>
        - Example: <i>nonexistentuser@gmail.com</i><br><br>
        
        <span style='color:#f1c40f; font-weight:bold'>Error</span>: 
        - Temporary network issues<br>
        - SMTP server timeout or connection error<br>
        - Unexpected verification errors<br><br>
        
        <i>Note: Some email servers may block verification attempts for privacy reasons.</i>
        """
        help_dialog = QtWidgets.QMessageBox(self)
        help_dialog.setWindowTitle("Verification Status Help")
        help_dialog.setTextFormat(QtCore.Qt.RichText)  # Enable HTML formatting
        help_dialog.setText(help_text)
        help_dialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
        help_dialog.exec_()

class BulkVerificationThread(QtCore.QThread):
    result_signal = QtCore.pyqtSignal(str, str)
    all_done = QtCore.pyqtSignal()
    
    def __init__(self, emails):
        super().__init__()
        self.emails = emails
        
    def run(self):
        for email in self.emails:
            if not email:
                continue
                
            try:
                if not is_valid_email_syntax(email):
                    status = "Invalid (Syntax)"
                elif not has_mx_record(email.split('@')[1]):
                    status = "Invalid (No MX)"
                elif not verify_email_smtp(email):
                    status = "Invalid (SMTP)"
                else:
                    status = "Valid"
            except Exception as e:
                status = f"Error: {str(e)}"
                
            self.result_signal.emit(email, status)
        self.all_done.emit()  # Signal completion after all emails

class EmailValidatorApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.apply_styles()
        self.verifying_timer = QtCore.QTimer()
        self.verifying_counter = 1
        self.verifying_timer.timeout.connect(self.update_verifying_text)
        self.verification_thread = None

    def init_ui(self):
        self.setWindowTitle("KnowEmail")
        self.setMinimumSize(600, 500)

        # Main layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(15)

        # Header Section
        header_layout = QtWidgets.QVBoxLayout()
        title = QtWidgets.QLabel("KnowEmail")
        title.setObjectName("title")
        
        subtitle = QtWidgets.QLabel("Ad-Free & Open Source Bulk Email Verifier")
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

        # Bulk Verify Button
        self.bulk_button = QtWidgets.QPushButton("Check Multiple Emails")
        self.bulk_button.setObjectName("bulkButton")
        self.bulk_button.clicked.connect(self.bulk_verify)
        main_layout.addWidget(self.bulk_button)

        # Support Section
        support_layout = QtWidgets.QVBoxLayout()
        support_label = QtWidgets.QLabel(
            "We've made this tool free and open-source for everyone."
            "If you'd like to support our development efforts, consider donating."
        )
        support_label.setWordWrap(True)
        support_label.setObjectName("supportLabel")
        
        donate_button = QtWidgets.QPushButton("Support Us")
        donate_button.setObjectName("donateButton")
        donate_button.clicked.connect(lambda: webbrowser.open("https://example.com/donate"))
        
        support_layout.addWidget(support_label, 0, QtCore.Qt.AlignHCenter)
        support_layout.addWidget(donate_button, 0, QtCore.Qt.AlignHCenter)
        main_layout.addLayout(support_layout)

        # Add spacer to push support section to bottom
        main_layout.addStretch(1)

        self.setLayout(main_layout)

    def bulk_verify(self):
        file_dialog = QtWidgets.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Email List",
            "",
            "Text File (*.txt);; Excel File (*.xlsx)"
        )
        
        if not file_path:
            return
            
        try:
            if file_path.endswith('.txt'):
                with open(file_path, 'r') as f:
                    emails = [line.strip() for line in f.readlines() if line.strip()]
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
                emails = df.iloc[:, 0].astype(str).tolist()
            else:
                raise ValueError("Unsupported file format")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to read file: {str(e)}")
            return
            
        self.results_dialog = ResultDialog(self)
        self.results_dialog.show()
        
        # Start verification in background
        self.verification_thread = BulkVerificationThread(emails)
        self.verification_thread.result_signal.connect(self.update_results)
        self.verification_thread.all_done.connect(self.show_completion_popup)  # Add this
        self.verification_thread.start()

    def show_completion_popup(self):
        QtWidgets.QMessageBox.information(
            self,
            "Process Complete",
            "All emails from the file have been checked!",
            QtWidgets.QMessageBox.Ok
        )

    def update_results(self, email, status):
        self.results_dialog.add_row(email, status)

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