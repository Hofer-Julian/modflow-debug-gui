from application import ApplicationWindow
from matplotlib.backends.qt_compat import QtWidgets
import sys


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ApplicationWindow()
    window.show()
    sys.exit(app.exec_())