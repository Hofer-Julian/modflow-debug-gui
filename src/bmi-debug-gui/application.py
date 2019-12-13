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
from PyQt5.QtCore import QThreadPool
from utils import Worker


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        figure_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(figure_canvas)
        self.addToolBar(
            QtCore.Qt.TopToolBarArea, NavigationToolbar(figure_canvas, self)
        )

        self.fig = figure_canvas.figure
        self.ax = self.fig.subplots()
        # self.colorbar = self.fig.colorbar(pc, ax=ax)

        button_continue = QtWidgets.QPushButton("Continue time loop")
        button_continue.pressed.connect(self.button_pressed)
        layout.addWidget(button_continue)

        self.bmi = BMI()
        self.threadpool = QThreadPool()
        # TODO_JH: Jobs can still queue. Is this the wanted behaviour?
        self.threadpool.setMaxThreadCount(1)

    def closeEvent(self, event):
        self.bmi.mf6_dll.finalize()
        event.accept()

    def button_pressed(self):
        if self.bmi.ct.value < self.bmi.et.value:
            worker = Worker(self.bmi.advance_time_loop, self.ax, self.fig)
            worker.signals.result.connect(self.draw_canvas)
            self.threadpool.start(worker)

    def draw_canvas(self, args):
        (grid_x, grid_y, head_values) = args
        self.ax.clear()
        pc = self.ax.pcolormesh(grid_x, grid_y, head_values)
        if hasattr(self, "colorbar"):
            self.colorbar.update_normal(pc)
        else:
            self.colorbar = self.fig.colorbar(pc, ax=self.ax)
        self.ax.figure.canvas.draw()
