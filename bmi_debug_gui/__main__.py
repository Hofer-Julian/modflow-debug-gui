import sys

from PyQt5.QtWidgets import QApplication

from bmi_debug_gui.application import ApplicationWindow


def main():
    app = QApplication(sys.argv)
    window = ApplicationWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
