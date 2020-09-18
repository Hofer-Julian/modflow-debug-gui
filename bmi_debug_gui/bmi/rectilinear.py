from bmi_debug_gui.bmi.abc import Bmi
import numpy as np
from pyqtgraph import QtCore, QtGui
import pyqtgraph as pg


class RectBmi(Bmi):
    def __init__(self, bmi_dll, model_name):
        super().__init__(bmi_dll, model_name)

        self.grid_rank = bmi_dll.get_grid_rank(self.grid_id)

        self.grid_shape = np.empty(shape=(self.grid_rank,), dtype="int", order="F")
        bmi_dll.get_grid_shape(self.grid_id, self.grid_shape)

        self.grid_x = np.empty(
            shape=(self.grid_shape[-1] + 1,), dtype="double", order="F"
        )
        bmi_dll.get_grid_x(self.grid_id, self.grid_x)

        self.grid_y = np.empty(
            shape=(self.grid_shape[-2] + 1,), dtype="double", order="F"
        )
        bmi_dll.get_grid_y(self.grid_id, self.grid_y)

    def print_values(self):
        super().print_values()
        print(f"grid_rank: {self.grid_rank}")
        print(f"grid_shape: {self.grid_shape}")
        print(f"grid_x: {self.grid_x}")
        print(f"grid_y: {self.grid_y}")

    def draw_picture(self, painter, headcolors):
        for i_x in range(len(self.grid_x) - 1):
            for i_y in range(len(self.grid_y) - 1):
                polygon = QtGui.QPolygonF()
                polygon.append(QtCore.QPointF(self.grid_x[i_x], self.grid_y[i_y]))
                polygon.append(QtCore.QPointF(self.grid_x[i_x + 1], self.grid_y[i_y]))
                polygon.append(
                    QtCore.QPointF(self.grid_x[i_x + 1], self.grid_y[i_y + 1])
                )
                polygon.append(QtCore.QPointF(self.grid_x[i_x], self.grid_y[i_y + 1]))

                color = headcolors[i_x * (len(self.grid_y) - 1) + i_y]
                painter.setBrush(pg.mkBrush(color))
                painter.drawPolygon(polygon)
