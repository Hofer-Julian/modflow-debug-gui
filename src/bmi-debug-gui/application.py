"""
===============
Embedding in Qt
===============

Simple Qt application embedding Matplotlib canvases.  This program will work
equally well using Qt4 and Qt5.  Either version of Qt can be selected (for
example) by setting the ``MPLBACKEND`` environment variable to "Qt4Agg" or
"Qt5Agg", or by first importing the desired version of PyQt.
"""

import time

import numpy as np


from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)

from bmi_data import BMIState


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(dynamic_canvas)
        self.addToolBar(
            QtCore.Qt.TopToolBarArea, NavigationToolbar(dynamic_canvas, self)
        )

        self._dynamic_ax = dynamic_canvas.figure.subplots()
        button_continue = QtWidgets.QPushButton("Continue time loop")
        button_continue.pressed.connect(self._update_canvas)
        layout.addWidget(button_continue)

        self.bmistate = BMIState()

    def _update_canvas(self):
        self._dynamic_ax.clear()
        t = np.linspace(0, 10, 101)
        # Shift the sinusoid as a function of time.
        self._dynamic_ax.plot(t, np.sin(t + time.time()))
        # self.bmistate.advance_time_loop(self._dynamic_ax)
        self._dynamic_ax.figure.canvas.draw()
