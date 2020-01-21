import sys

from PyQt5.QtWidgets import QApplication

from application import ApplicationWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ApplicationWindow()
    sys.exit(app.exec_())
