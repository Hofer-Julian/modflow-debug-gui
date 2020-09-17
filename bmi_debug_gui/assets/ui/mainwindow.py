# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 601)
        MainWindow.setMinimumSize(QtCore.QSize(800, 601))
        MainWindow.setMaximumSize(QtCore.QSize(800, 601))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.graphWidget = PlotWidget(self.centralwidget)
        self.graphWidget.setObjectName("graphWidget")
        self.horizontalLayout_3.addWidget(self.graphWidget)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btn_continue = QtWidgets.QPushButton(self.centralwidget)
        self.btn_continue.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_continue.sizePolicy().hasHeightForWidth())
        self.btn_continue.setSizePolicy(sizePolicy)
        self.btn_continue.setMaximumSize(QtCore.QSize(386, 16777215))
        self.btn_continue.setObjectName("btn_continue")
        self.horizontalLayout_2.addWidget(self.btn_continue)
        self.box_pltgrid = QtWidgets.QCheckBox(self.centralwidget)
        self.box_pltgrid.setEnabled(True)
        self.box_pltgrid.setChecked(True)
        self.box_pltgrid.setObjectName("box_pltgrid")
        self.horizontalLayout_2.addWidget(self.box_pltgrid)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setEnabled(True)
        self.progressBar.setMaximum(100)
        self.progressBar.setProperty("value", -1)
        self.progressBar.setTextVisible(False)
        self.progressBar.setObjectName("progressBar")
        self.horizontalLayout_2.addWidget(self.progressBar)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.box_modelname = QtWidgets.QComboBox(self.centralwidget)
        self.box_modelname.setEnabled(False)
        self.box_modelname.setMinimumSize(QtCore.QSize(100, 0))
        self.box_modelname.setObjectName("box_modelname")
        self.horizontalLayout.addWidget(self.box_modelname)
        self.widget_input_var_name = QtWidgets.QLineEdit(self.centralwidget)
        self.widget_input_var_name.setEnabled(False)
        self.widget_input_var_name.setText("")
        self.widget_input_var_name.setObjectName("widget_input_var_name")
        self.horizontalLayout.addWidget(self.widget_input_var_name)
        self.widget_input_component_name = QtWidgets.QLineEdit(self.centralwidget)
        self.widget_input_component_name.setEnabled(False)
        self.widget_input_component_name.setText("")
        self.widget_input_component_name.setObjectName("widget_input_component_name")
        self.horizontalLayout.addWidget(self.widget_input_component_name)
        self.btn_getval = QtWidgets.QPushButton(self.centralwidget)
        self.btn_getval.setEnabled(False)
        self.btn_getval.setObjectName("btn_getval")
        self.horizontalLayout.addWidget(self.btn_getval)
        self.widget_output = QtWidgets.QLineEdit(self.centralwidget)
        self.widget_output.setEnabled(True)
        self.widget_output.setReadOnly(True)
        self.widget_output.setObjectName("widget_output")
        self.horizontalLayout.addWidget(self.widget_output)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btn_continue.setText(_translate("MainWindow", "Next time step"))
        self.box_pltgrid.setText(_translate("MainWindow", "Plot model grid"))
        self.widget_input_var_name.setPlaceholderText(_translate("MainWindow", "Input variable name"))
        self.widget_input_component_name.setPlaceholderText(_translate("MainWindow", "Input component name"))
        self.btn_getval.setText(_translate("MainWindow", "Get value"))
        self.widget_output.setPlaceholderText(_translate("MainWindow", "Output"))
from pyqtgraph import PlotWidget
