import ctypes
import os
import re
import sys
from pathlib import Path

import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import QSettings, Qt, QThreadPool
from PyQt5.QtWidgets import QDialog, QFileDialog, QMainWindow, QTableWidgetItem

from bmi_debug_gui.assets.ui import dirchoosedialog, mainwindow
from bmi_debug_gui.bmi.abc import Bmi
from bmi_debug_gui.graphics_objects import ColorBar, HeatMap
from bmi_debug_gui.utils import Worker
from xmipy import XmiWrapper


class ApplicationWindow(QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self):
        self.settings = QSettings("Deltares", "bmi_debug_gui")
        self.dialog = DirChooseDialog(self.settings)
        super().__init__()

        if self.dialog.exec_():
            # Switch to using white background and black foreground
            pg.setConfigOption("background", "w")
            pg.setConfigOption("foreground", "k")
            self.setupUi(self)
            self.btn_continue.pressed.connect(self.continue_time_loop)
            self.widget_input_var_name.textChanged.connect(
                self.widget_input_textChanged
            )
            self.widget_input_component_name.textChanged.connect(
                self.widget_input_textChanged
            )
            self.box_pltgrid.stateChanged.connect(self.box_pltgrid_stateChanged)
            self.btn_getval.pressed.connect(self.btn_getval_pressed)

            self.threadpool = QThreadPool()
            # Jobs queue, but never run concurrently.
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
        self.simpath = Path(self.dialog.simpath)
        self.bmi_dll = XmiWrapper(
            lib_path=str(self.dialog.dllpath),
            working_directory=str(self.simpath),
        )

        self.bmi_dll.initialize()
        self.get_model_names()
        self.bmi_states = []

        for model_name in self.model_names:
            self.bmi_states.append(Bmi.get_bmi(self.bmi_dll, model_name))
            self.box_modelname.addItem(model_name)

        self.box_modelname.setEnabled(True)
        self.widget_input_var_name.setEnabled(True)
        self.widget_input_component_name.setEnabled(True)

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
        if self.bmi_states[0].ct < self.bmi_states[0].et:
            self.progressBar.setMaximum(0)
            worker = Worker(self.bmi_dll.update)
            worker.signals.result.connect(self.evaluate_loop_data)
            self.threadpool.start(worker)

    def btn_getval_pressed(self):
        for bmi_state in self.bmi_states:
            if bmi_state.model_name == self.box_modelname.currentText():
                worker = Worker(
                    bmi_state.get_value,
                    self.widget_input_var_name.text(),
                    self.widget_input_component_name.text(),
                )
                worker.signals.result.connect(
                    lambda array: self.widget_output.setText(repr(array))
                )
                self.threadpool.start(worker)

    def widget_input_textChanged(self):
        if self.widget_input_exists():
            self.btn_getval.setEnabled(True)
        else:
            self.btn_getval.setEnabled(False)

    def widget_input_exists(self):
        return len(self.widget_input_var_name.text()) > 0

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
        stops = np.linspace(min, max, 4)
        # blue, cyan, yellow, red
        colors = np.array(
            [[0, 0, 1, 1.0], [0, 1, 1, 1.0], [1, 1, 0, 1.0], [1, 0, 0, 1.0]]
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
            bmi_state.eval_time_loop()
        worker = Worker(self.calc_heatmap)
        worker.signals.result.connect(self.draw_canvas)
        self.threadpool.start(worker)
        if bmi_state.ct < bmi_state.et:
            self.btn_continue.setEnabled(True)

    def calc_heatmap(self):
        for bmi_state in self.bmi_states:
            self.heatmaps.append(
                HeatMap(bmi_state, self.colormap, self.box_pltgrid.isChecked())
            )

    def draw_canvas(self):
        self.progressBar.setMaximum(100)
        self.graphWidget.clear()
        for heatmap in self.heatmaps:
            self.graphWidget.addItem(heatmap)
        if self.colorbar not in self.graphWidget.scene().items():
            self.graphWidget.scene().addItem(self.colorbar)


class DirChooseDialog(QDialog, dirchoosedialog.Ui_Dialog):
    def __init__(self, settings):
        super().__init__()
        self.setupUi(self)
        self.settings = settings

        self.get_last_state()

        # Set flags and connect signals
        self.setWindowFlags(Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        self.btn_opensim.pressed.connect(self.btn_opensim_pressed)
        self.btn_opendll.pressed.connect(self.btn_opendll_pressed)

    def get_last_state(self):
        dllpath = self.settings.value("dllpath", "")
        simpath = self.settings.value("simpath", "")

        self.set_dllpath(dllpath)
        self.set_simpath(simpath)

    def btn_opensim_pressed(self):
        simpath = QFileDialog.getExistingDirectory()
        self.settings.setValue("simpath", simpath)
        self.set_simpath(simpath)

    def btn_opendll_pressed(self):
        dllpath = QFileDialog.getOpenFileName()[0]
        self.settings.setValue("dllpath", dllpath)
        self.set_dllpath(dllpath)

    def set_simpath(self, simpath):
        self.simpath = simpath
        self.tableWidget.setItem(0, 0, QTableWidgetItem(self.simpath))

    def set_dllpath(self, dllpath):
        self.dllpath = dllpath
        self.tableWidget.setItem(1, 0, QTableWidgetItem(self.dllpath))
