# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\dirchoosedialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(417, 147)
        Dialog.setMinimumSize(QtCore.QSize(417, 147))
        Dialog.setMaximumSize(QtCore.QSize(417, 147))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableWidget = QtWidgets.QTableWidget(Dialog)
        self.tableWidget.setShowGrid(True)
        self.tableWidget.setGridStyle(QtCore.Qt.SolidLine)
        self.tableWidget.setRowCount(2)
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setObjectName("tableWidget")
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        self.tableWidget.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        self.tableWidget.setItem(1, 0, item)
        self.tableWidget.horizontalHeader().setMinimumSectionSize(39)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.tableWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btn_opensim = QtWidgets.QPushButton(Dialog)
        self.btn_opensim.setObjectName("btn_opensim")
        self.horizontalLayout.addWidget(self.btn_opensim)
        self.btn_opendll = QtWidgets.QPushButton(Dialog)
        self.btn_opendll.setObjectName("btn_opendll")
        self.horizontalLayout.addWidget(self.btn_opendll)
        self.btn_box = QtWidgets.QDialogButtonBox(Dialog)
        self.btn_box.setOrientation(QtCore.Qt.Horizontal)
        self.btn_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.btn_box.setObjectName("btn_box")
        self.horizontalLayout.addWidget(self.btn_box)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Dialog)
        self.btn_box.accepted.connect(Dialog.accept)
        self.btn_box.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        item = self.tableWidget.verticalHeaderItem(0)
        item.setText(_translate("Dialog", "Model"))
        item = self.tableWidget.verticalHeaderItem(1)
        item.setText(_translate("Dialog", "BMI-DLL"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "Path"))
        __sortingEnabled = self.tableWidget.isSortingEnabled()
        self.tableWidget.setSortingEnabled(False)
        self.tableWidget.setSortingEnabled(__sortingEnabled)
        self.btn_opensim.setText(_translate("Dialog", "Open Simulation Directory"))
        self.btn_opendll.setText(_translate("Dialog", "Open BMI-DLL File"))

