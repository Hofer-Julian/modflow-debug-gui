"""
===============
Embedding in Qt
===============

Simple Qt application embedding Matplotlib canvases.  This program will work
equally well using Qt4 and Qt5.  Either version of Qt can be selected (for
example) by setting the ``MPLBACKEND`` environment variable to "Qt4Agg" or
"Qt5Agg", or by first importing the desired version of PyQt.
"""



from bmi_data import BMI
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import QThreadPool
from utils import Worker
from matplotlib.collections import LineCollection
import pyqtgraph as pg
from pathlib import Path
from graphics_objects import HeatMap, ColorBar
import numpy as np


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        ui_path = Path(__file__).absolute().parent / "assets" / "ui"
        ## Switch to using white background and black foreground
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        uic.loadUi(ui_path / "mainwindow.ui", self)

        self.btn_continue.pressed.connect(self.btn_continue_pressed)
        self.widget_input.textChanged.connect(self.widget_input_textChanged)
        self.btn_getval.pressed.connect(self.btn_getval_pressed)
        
        self.bmi_state = BMI()
        self.threadpool = QThreadPool()
        # TODO_JH: Jobs can still queue. Is this the wanted behaviour?
        self.threadpool.setMaxThreadCount(1)

    def closeEvent(self, event):
        self.bmi_state.mf6_dll.finalize()
        event.accept()

    def btn_continue_pressed(self):
        if self.bmi_state.ct.value < self.bmi_state.et.value:
            worker = Worker(self.bmi_state.advance_time_loop)
            worker.signals.result.connect(self.draw_canvas)
            self.threadpool.start(worker)

    def btn_getval_pressed(self):
        worker = Worker(
            self.bmi_state.get_value,
            self.widget_input.text(),
            self.box_datatype.currentText(),
        )
        worker.signals.result.connect(lambda x: x)
        self.threadpool.start(worker)

    def widget_input_textChanged(self):
        if len(self.widget_input.text()):
            self.btn_getval.setEnabled(True)
        else:
            self.btn_getval.setEnabled(False)

    def draw_canvas(self, kwargs):
        self.graphWidget.clear()
        # make colormap
        head = kwargs["head"]
        stops = np.linspace(np.min(head), np.max(head), 4)
        # blue, cyan, yellow, red
        colors = np.array([[0., 0., 1., 1.], [0., 1., 1., 1.], [1., 1., 0., 1.], [1, 0, 0, 1.]])
        cm = pg.ColorMap(stops, colors)
        heatmap = HeatMap(self.bmi_state, cm, kwargs)
        self.graphWidget.addItem(heatmap)
        colorbar = ColorBar(cm, 10, 200, label='head')
        self.graphWidget.scene().addItem(colorbar)
        # TODO_JH: Adjust colorbar when window is resized (translate is probably not suitable for that)
        colorbar.translate(700.0, 150.0)