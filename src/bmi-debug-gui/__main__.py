from application import ApplicationWindow
from matplotlib.backends.qt_compat import QtWidgets
import sys


if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow()
    app.show()
    qapp.exec_()
