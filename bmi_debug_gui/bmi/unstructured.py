from bmi_debug_gui.bmi.abc import Bmi
import numpy as np
from pyqtgraph import QtCore, QtGui
import pyqtgraph as pg


class UnstrucBmi(Bmi):
    def __init__(self, bmi_dll, model_name):
        super().__init__(bmi_dll, model_name)

        self.grid_x = np.empty(shape=(self.grid_size,), dtype="double", order="F")
        bmi_dll.get_grid_x(self.grid_id, self.grid_x)

        self.grid_y = np.empty(shape=(self.grid_size,), dtype="double", order="F")
        bmi_dll.get_grid_y(self.grid_id, self.grid_y)

        # node in BMI-context means vertex in Modflow context
        self.grid_node_count = bmi_dll.get_grid_node_count(self.grid_id)

        # get face_count
        self.face_count = bmi_dll.get_grid_face_count(self.grid_id)

        # get grid_node_per_face
        self.nodes_per_face = np.empty(shape=(self.face_count,), dtype="int", order="F")
        bmi_dll.get_grid_nodes_per_face(self.grid_id, self.nodes_per_face)

        # get grid_face_nodes
        face_nodes_count = np.sum(self.nodes_per_face + 1)
        face_nodes = np.empty(shape=(face_nodes_count,), dtype="int", order="F")
        bmi_dll.get_grid_face_nodes(self.grid_id, face_nodes)
        # Subtract 1 so that 0 describes the first element
        self.face_nodes = face_nodes - 1

    def print_values(self):
        super().print_values()
        print(f"grid_x: {self.grid_x}")
        print(f"grid_y: {self.grid_y}")
        print(f"grid_node_count: {self.grid_node_count}")
        print(f"face_count: {self.face_count}")
        print(f"nodes_per_face: {self.nodes_per_face}")
        print(f"face_nodes: {self.face_nodes}")

    def draw_picture(self, painter, headcolors):
        face_index = 0
        for i, node_count in enumerate(self.nodes_per_face):
            polygon = QtGui.QPolygonF()
            for j in range(node_count):
                face_node = self.face_nodes[face_index + j]
                polygon.append(
                    QtCore.QPointF(self.grid_x[face_node], self.grid_y[face_node])
                )
            face_index += node_count + 1
            painter.setBrush(pg.mkBrush(headcolors[i]))
            painter.drawPolygon(polygon)
