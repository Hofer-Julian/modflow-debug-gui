import sys

from PyQt5.QtWidgets import QApplication

from application import ApplicationWindow


def main():
    app = QApplication(sys.argv)
    ApplicationWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
