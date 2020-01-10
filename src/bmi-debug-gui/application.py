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
        uic.loadUi(ui_path / 'mainwindow.ui', self)
    #     self.setCentralWidget(self._main)
    #     main_layout = QtWidgets.QVBoxLayout(self._main)

    #     figure_canvas = FigureCanvas(Figure(figsize=(5, 3)))
    #     main_layout.addWidget(figure_canvas)
    #     self.addToolBar(
    #         QtCore.Qt.TopToolBarArea, NavigationToolbar(figure_canvas, self)
    #     )

    #     self.fig = figure_canvas.figure
    #     self.ax = self.fig.subplots()

    #     button_continue = QtWidgets.QPushButton("Continue time loop")
    #     button_continue.pressed.connect(self.button_continue_pressed)
    #     main_layout.addWidget(button_continue)

    #     # TODO_JH: Fix erro message "Attempting to add QLayout "" to QWidget "", which already has a layout"
    #     inner_layout = QtWidgets.QHBoxLayout(self._main)
    #     main_layout.addLayout(inner_layout)

    #     self.input_widget = QtWidgets.QLineEdit()
    #     self.input_widget.setPlaceholderText("Input variable name")
    #     self.input_widget.textChanged.connect(self.input_widget_textChanged)

    #     self.combo_box = QtWidgets.QComboBox()
    #     self.combo_box.addItems(["double", "int"])

    #     self.button_get_value = QtWidgets.QPushButton("Get value")
    #     self.button_get_value.setEnabled(False)
    #     self.button_get_value.pressed.connect(self.button_get_value_pressed)

    #     inner_layout.addWidget(self.input_widget)
    #     inner_layout.addWidget(self.combo_box)
    #     inner_layout.addWidget(self.button_get_value)

    #     self.bmi = BMI()
    #     self.threadpool = QThreadPool()
    #     # TODO_JH: Jobs can still queue. Is this the wanted behaviour?
    #     self.threadpool.setMaxThreadCount(1)

    # def closeEvent(self, event):
    #     self.bmi.mf6_dll.finalize()
    #     event.accept()

    # def button_continue_pressed(self):
    #     if self.bmi.ct.value < self.bmi.et.value:
    #         worker = Worker(self.bmi.advance_time_loop, self.ax, self.fig)
    #         worker.signals.result.connect(self.draw_canvas)
    #         self.threadpool.start(worker)

    # def button_get_value_pressed(self):
    #     worker = Worker(
    #         self.bmi.get_value, self.input_widget.text(), self.combo_box.currentText()
    #     )
    #     worker.signals.result.connect(lambda x: x)
    #     self.threadpool.start(worker)

    # def input_widget_textChanged(self):
    #     if len(self.input_widget.text()):
    #         self.button_get_value.setEnabled(True)
    #     else:
    #         self.button_get_value.setEnabled(False)

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



