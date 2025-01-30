import sys
from PyQt5 import QtWidgets
from src.gui import EmailValidatorApp

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = EmailValidatorApp()
    window.show()
    sys.exit(app.exec_())