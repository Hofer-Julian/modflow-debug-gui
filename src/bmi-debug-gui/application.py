"""
===============
Embedding in Qt
===============

Simple Qt application embedding Matplotlib canvases.  This program will work
equally well using Qt4 and Qt5.  Either version of Qt can be selected (for
example) by setting the ``MPLBACKEND`` environment variable to "Qt4Agg" or
"Qt5Agg", or by first importing the desired version of PyQt.
"""


from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)

from bmi_data import BMI
from PyQt5 import uic
from PyQt5.QtCore import QThreadPool
from utils import Worker
from matplotlib.collections import LineCollection
import pyqtgraph as pg
from pathlib import Path


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        ui_path = Path(__file__).absolute().parent / "assets" / "ui"
        uic.loadUi(ui_path / "mainwindow.ui", self)

        self.btn_continue.pressed.connect(self.btn_continue_pressed)
        self.widget_input.textChanged.connect(self.widget_input_textChanged)
        self.btn_getval.pressed.connect(self.btn_getval_pressed)

        data = [  ## fields are (time, open, close, min, max).
            (1.0, 10, 13, 5, 15),
            (2.0, 13, 17, 9, 20),
            (3.0, 17, 14, 11, 23),
            (4.0, 14, 15, 5, 19),
            (5.0, 15, 9, 8, 22),
            (6.0, 9, 15, 8, 16),
        ]
        from test import MeshItem

        item = MeshItem(data)
        self.graphWidget.addItem(item)



        self.bmi = BMI()
        self.threadpool = QThreadPool()
        # TODO_JH: Jobs can still queue. Is this the wanted behaviour?
        self.threadpool.setMaxThreadCount(1)

    def closeEvent(self, event):
        self.bmi.mf6_dll.finalize()
        event.accept()

    def btn_continue_pressed(self):
        if self.bmi.ct.value < self.bmi.et.value:
            worker = Worker(self.bmi.advance_time_loop, self.ax, self.fig)
            worker.signals.result.connect(self.draw_canvas)
            self.threadpool.start(worker)

    def btn_getval_pressed(self):
        worker = Worker(
            self.bmi.get_value, self.widget_input.text(), self.box_datatype.currentText()
        )
        worker.signals.result.connect(lambda x: x)
        self.threadpool.start(worker)

    def widget_input_textChanged(self):
        if len(self.widget_input.text()):
            self.btn_getval.setEnabled(True)
        else:
            self.btn_getval.setEnabled(False)

    # def draw_canvas(self, args):
    #     (grid_x, grid_y, head_values) = args
    #     self.ax.clear()
    #     self.plot_grid()
    #     if (grid_x, grid_y, head_values) == (None, None, None):
    #         pass
    #     else:
    #         pc = self.ax.pcolormesh(grid_x, grid_y, head_values)
    #         if hasattr(self, "colorbar"):
    #             self.colorbar.update_normal(pc)
    #         else:
    #             self.colorbar = self.fig.colorbar(pc, ax=self.ax)
    #     self.ax.figure.canvas.draw()

    # def plot_grid(self):
    #     """
    #     Plot the grid lines.

    #     Returns
    #     -------
    #     lc : matplotlib.collections.LineCollection

    #     """

    #     lc = LineCollection(self.bmi.grid_lines)
    #     self.ax.add_collection(lc)
    #     self.ax.set_xlim(self.bmi.extent[0], self.bmi.extent[1])
    #     self.ax.set_ylim(self.bmi.extent[2], self.bmi.extent[3])
    #     return lc

