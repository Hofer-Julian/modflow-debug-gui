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
import pyqtgraph as pg
from pathlib import Path
from graphics_objects import HeatMap, ColorBar
import numpy as np


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        ui_path = Path(__file__).absolute().parent / "assets" / "ui"
        # Switch to using white background and black foreground
        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")
        uic.loadUi(ui_path / "mainwindow.ui", self)

        self.btn_continue.pressed.connect(self.btn_continue_pressed)
        self.widget_input.textChanged.connect(self.widget_input_textChanged)
        self.box_pltgrid.stateChanged.connect(self.box_pltgrid_stateChanged)
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
            worker.signals.result.connect(self.evaluate_loop_data)
            self.threadpool.start(worker)

    def btn_getval_pressed(self):
        worker = Worker(
            self.bmi_state.get_value,
            self.widget_input.text(),
            self.box_datatype.currentText(),
        )
        worker.signals.result.connect(
            lambda array: self.widget_output.setText(repr(array["array"]))
        )
        self.threadpool.start(worker)

    def widget_input_textChanged(self):
        if len(self.widget_input.text()):
            self.btn_getval.setEnabled(True)
        else:
            self.btn_getval.setEnabled(False)

    def box_pltgrid_stateChanged(self, enabled):
        self.draw_canvas()

    def evaluate_loop_data(self, loop_data):
        # make colormap
        self.loop_data = loop_data
        stops = np.linspace(np.min(loop_data["head"]), np.max(loop_data["head"]), 4)
        # blue, cyan, yellow, red
        colors = np.array(
            [
                [0.0, 0.0, 1.0, 1.0],
                [0.0, 1.0, 1.0, 1.0],
                [1.0, 1.0, 0.0, 1.0],
                [1.0, 0.0, 0.0, 1.0],
            ]
        )
        self.colormap = pg.ColorMap(stops, colors)
        if hasattr(self, "colorbar") and self.colorbar in self.graphWidget.scene().items():
            self.graphWidget.scene().removeItem(self.colorbar)

        self.colorbar = ColorBar(self.colormap, 10, 200, label="head")
        # TODO_JH: Adjust colorbar when window is resized (translate is probably not suitable for that)
        self.colorbar.translate(700.0, 150.0)
        self.draw_canvas()

    def draw_canvas(self):
        self.heatmap = HeatMap(
            self.bmi_state, self.colormap, self.box_pltgrid.isChecked(), self.loop_data
        )
        self.graphWidget.clear()
        self.graphWidget.addItem(self.heatmap)
        if self.colorbar not in self.graphWidget.scene().items():
            self.graphWidget.scene().addItem(self.colorbar)
