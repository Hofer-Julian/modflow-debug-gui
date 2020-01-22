import ctypes
import os
import re
import sys
from pathlib import Path

import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtWidgets import QDialog, QFileDialog, QMainWindow, QTableWidgetItem

from assets.ui import dirchoosedialog, mainwindow
from bmi_data import BMI
from graphics_objects import ColorBar, HeatMap
from utils import Worker


class ApplicationWindow(QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self):
        self.dialog = QDirChooseDialog()
        super().__init__()

        if self.dialog.exec_():
            # Switch to using white background and black foreground
            pg.setConfigOption("background", "w")
            pg.setConfigOption("foreground", "k")
            self.setupUi(self)
            self.btn_continue.pressed.connect(self.continue_time_loop)
            self.widget_input.textChanged.connect(self.widget_input_textChanged)
            self.box_pltgrid.stateChanged.connect(self.box_pltgrid_stateChanged)
            self.btn_getval.pressed.connect(self.btn_getval_pressed)

            self.threadpool = QThreadPool()
            # TODO_JH: Jobs can still queue. Is this the wanted behaviour?
            self.threadpool.setMaxThreadCount(1)
            worker = Worker(self.init_bmi)
            worker.signals.result.connect(self.continue_time_loop)
            self.progressBar.setMaximum(0)
            self.threadpool.start(worker)
            self.show()
        else:
            sys.exit(0)

    def closeEvent(self, event):
        if hasattr(self, "bmi_dll"):
            self.bmi_dll.finalize()
        event.accept()

    def init_bmi(self):
        self.bmi_dll = ctypes.cdll.LoadLibrary(str(self.dialog.dllpath))
        self.simpath = Path(self.dialog.simpath)
        os.chdir(self.simpath)
        self.bmi_dll.initialize()
        self.get_model_names()
        self.bmi_states = []

        for model_name in self.model_names:
            self.bmi_states.append(BMI(self.bmi_dll, model_name))
            self.box_modelname.addItem(model_name)

        self.box_modelname.setEnabled(True)
        self.widget_input.setEnabled(True)

    def get_model_names(self):
        # TODO_JH: Find a better way to get the grid_id
        # then parsing the model_name from the mfsim.nam file
        # and then searching for the grid_id of a specific parameter
        # this additionally only works when only one model is present
        with open(self.simpath / "mfsim.nam", "r") as namefile:
            content = namefile.read()
            matches = re.findall(r"\.nam\s+(\S+)\n", content)
            if matches:
                self.model_names = [model.upper() for model in matches]
            else:
                raise Exception("The model names could not be parsed")

    def continue_time_loop(self):
        self.btn_continue.setEnabled(False)
        if self.bmi_states[0].ct.value < self.bmi_states[0].et.value:
            self.progressBar.setMaximum(0)
            worker = Worker(self.bmi_dll.update)
            worker.signals.result.connect(self.evaluate_loop_data)
            self.threadpool.start(worker)

    def btn_getval_pressed(self):
        for bmi_state in self.bmi_states:
            if bmi_state.model_name == self.box_modelname.currentText():
                worker = Worker(
                    bmi_state.get_value,
                    self.bmi_dll,
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
        self.heatmaps = []
        worker = Worker(self.calc_heatmap)
        worker.signals.result.connect(self.draw_canvas)
        self.threadpool.start(worker)

    def evaluate_loop_data(self):
        min = np.min([np.min(bmi_state.plotarray) for bmi_state in self.bmi_states])
        max = np.max([np.max(bmi_state.plotarray) for bmi_state in self.bmi_states])

        # make colormap
        stops = np.linspace(
            min, max, 4
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

        self.heatmaps = []
        for bmi_state in self.bmi_states:
            bmi_state.eval_time_loop(self.bmi_dll)
        worker = Worker(self.calc_heatmap)
        worker.signals.result.connect(self.draw_canvas)
        self.threadpool.start(worker)
        if bmi_state.ct.value < bmi_state.et.value:
            self.btn_continue.setEnabled(True)

    def calc_heatmap(self):
        for bmi_state in self.bmi_states:
            self.heatmaps.append(HeatMap(
                bmi_state, self.colormap, self.box_pltgrid.isChecked())
            )

    def draw_canvas(self):
        self.progressBar.setMaximum(100)
        self.graphWidget.clear()
        for heatmap in self.heatmaps:
            self.graphWidget.addItem(heatmap)
        if self.colorbar not in self.graphWidget.scene().items():
            self.graphWidget.scene().addItem(self.colorbar)


class QDirChooseDialog(QDialog, dirchoosedialog.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowFlags(Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        self.btn_opensim.pressed.connect(self.btn_opensim_pressed)
        self.btn_opendll.pressed.connect(self.btn_opendll_pressed)

    def btn_opensim_pressed(self):
        self.simpath = QFileDialog.getExistingDirectory()
        self.tableWidget.setItem(0, 0, QTableWidgetItem(self.simpath))

    def btn_opendll_pressed(self):
        self.dllpath = QFileDialog.getOpenFileName()[0]
        self.tableWidget.setItem(1, 0, QTableWidgetItem(self.dllpath))
