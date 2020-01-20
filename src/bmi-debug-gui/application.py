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
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QDialog, QTableWidgetItem
from PyQt5.QtCore import QThreadPool, Qt
from utils import Worker
import pyqtgraph as pg
from pathlib import Path
from graphics_objects import HeatMap, ColorBar
import numpy as np
import sys
import os

ui_path = Path(__file__).absolute().parent / "assets" / "ui"


class ApplicationWindow(QMainWindow):
    def __init__(self):
        self.dialog = QDirChooseDialog()

        super().__init__()
        if self.dialog.exec_():
            # Switch to using white background and black foreground
            pg.setConfigOption("background", "w")
            pg.setConfigOption("foreground", "k")
            uic.loadUi(ui_path / "mainwindow.ui", self)
            self.btn_continue.pressed.connect(self.continue_time_loop)
            self.widget_input.textChanged.connect(self.widget_input_textChanged)
            self.box_pltgrid.stateChanged.connect(self.box_pltgrid_stateChanged)
            self.btn_getval.pressed.connect(self.btn_getval_pressed)

            self.threadpool = QThreadPool()
            # TODO_JH: Jobs can still queue. Is this the wanted behaviour?
            self.threadpool.setMaxThreadCount(1)
            worker = Worker(self.init_bmi)
            worker.signals.result.connect(self.evaluate_loop_data)
            self.progressBar.setMaximum(0)
            self.threadpool.start(worker)
            self.show()
        else:
            sys.exit(0)

    def closeEvent(self, event):
        if hasattr(self, "bmi_state"):
            self.bmi_state.mf6_dll.finalize()
        event.accept()

    def init_bmi(self):
        self.bmi_state = BMI(self.dialog.dllpath, self.dialog.simpath)
        self.btn_continue.setEnabled(True)

    def continue_time_loop(self):
        self.btn_continue.setEnabled(False)
        if self.bmi_state.ct.value < self.bmi_state.et.value:
            self.progressBar.setMaximum(0)
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
            lambda array: self.widget_output.setText(repr(array))
        )
        self.threadpool.start(worker)

    def widget_input_textChanged(self):
        if len(self.widget_input.text()):
            self.btn_getval.setEnabled(True)
        else:
            self.btn_getval.setEnabled(False)

    def box_pltgrid_stateChanged(self, enabled):
        self.progressBar.setMaximum(0)
        worker = Worker(self.calc_heatmap)
        worker.signals.result.connect(self.draw_canvas)
        self.threadpool.start(worker)

    def evaluate_loop_data(self):
        # Check if there are initial plotarray values
        if np.min(self.bmi_state.plotarray) == np.max(self.bmi_state.plotarray):
            self.continue_time_loop()
        else:
            # make colormap
            stops = np.linspace(
                np.min(self.bmi_state.plotarray), np.max(self.bmi_state.plotarray), 4
            )
            # blue, cyan, yellow, red
            colors = np.array(
                [
                    [0, 0, 1, 1.0],
                    [0, 1, 1, 1.0],
                    [1, 1, 0, 1.0],
                    [1, 0, 0, 1.0],
                ]
            )
            self.colormap = pg.ColorMap(stops, colors)
            if (
                hasattr(self, "colorbar")
                and self.colorbar in self.graphWidget.scene().items()
            ):
                self.graphWidget.scene().removeItem(self.colorbar)

            self.colorbar = ColorBar(self.colormap, 10, 200, label="head")
            self.colorbar.translate(700.0, 150.0)
            worker = Worker(self.calc_heatmap)
            worker.signals.result.connect(self.draw_canvas)
            self.threadpool.start(worker)
            if self.bmi_state.ct.value < self.bmi_state.et.value:
                self.btn_continue.setEnabled(True)

    def calc_heatmap(self):
        self.heatmap = HeatMap(
            self.bmi_state, self.colormap, self.box_pltgrid.isChecked()
        )

    def draw_canvas(self):
        self.progressBar.setMaximum(100)
        self.graphWidget.clear()
        self.graphWidget.addItem(self.heatmap)
        if self.colorbar not in self.graphWidget.scene().items():
            self.graphWidget.scene().addItem(self.colorbar)


class QDirChooseDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(ui_path / "dirchoosedialog.ui", self)
        # TODO_JH: REMOVE
        self.simpath = r"C:\checkouts\modflow6-examples\mf6\test030_hani_xt3d_disu"
        self.dllpath = r"C:\checkouts\modflow6-martijn-fork\msvs\dll\x64\Debug\mf6.dll"
        self.tableWidget.setItem(0, 0, QTableWidgetItem(self.simpath))
        self.tableWidget.setItem(1, 0, QTableWidgetItem(self.dllpath))

        self.setWindowFlags(Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        self.btn_opensim.pressed.connect(self.btn_opensim_pressed)
        self.btn_opendll.pressed.connect(self.btn_opendll_pressed)

    def btn_opensim_pressed(self):
        self.simpath = QFileDialog.getExistingDirectory()
        self.tableWidget.setItem(0, 0, QTableWidgetItem(self.simpath))

    def btn_opendll_pressed(self):
        self.dllpath = QFileDialog.getOpenFileName()[0]
        self.tableWidget.setItem(1, 0, QTableWidgetItem(self.dllpath))
