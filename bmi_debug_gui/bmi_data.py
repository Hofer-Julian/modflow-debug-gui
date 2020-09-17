import ctypes
from collections import defaultdict

import numpy as np
import os


class BMI:
    def __init__(self, bmi_dll, model_name):
        self.model_name = model_name
        self.ct = bmi_dll.get_current_time()
        self.et = bmi_dll.get_end_time()
        self.bmi_dll = bmi_dll

        print(f"model_name: {self.model_name}")

        k11_tag = bmi_dll.get_var_address("K11", model_name, "NPF")
        print(f"model_dir: {os.path.basename(bmi_dll.working_directory)}")
        self.grid_id = bmi_dll.get_var_grid(k11_tag)
        print(f"grid_id: {self.grid_id}")

        # get grid type
        self.grid_type = bmi_dll.get_grid_type(self.grid_id)
        print(f"grid_type: {self.grid_type}")

        # get grid size
        self.grid_size = bmi_dll.get_grid_size(self.grid_id)
        print(f"grid_size: {self.grid_size}")

        if self.grid_type in (
            "uniform rectilinear",
            "rectilinear",
            "structured quadrilaterals",
        ):
            # get grid rank
            self.grid_rank = bmi_dll.get_grid_rank(self.grid_id)
            print(f"grid_rank: {self.grid_rank}")

            # get grid shape
            self.grid_shape = np.empty(shape=(self.grid_rank,), dtype="int", order="F")
            bmi_dll.get_grid_shape(self.grid_id, self.grid_shape)
            print(f"grid_shape: {self.grid_shape}")

        # get grid_x, grid_y and grid_z
        if self.grid_type == "rectilinear":
            self.grid_x = np.empty(
                shape=(self.grid_shape[-1] + 1,), dtype="double", order="F"
            )
            bmi_dll.get_grid_x(self.grid_id, self.grid_x)
            print(f"grid_x: {self.grid_x}")

            self.grid_y = np.empty(
                shape=(self.grid_shape[-2] + 1,), dtype="double", order="F"
            )
            bmi_dll.get_grid_y(self.grid_id, self.grid_y)
            print(f"grid_y: {self.grid_y}")

            # TODO_JH Implement get_grid_z in the bmi
        elif self.grid_type in ("structured quadrilaterals", "unstructured"):
            self.grid_x = np.empty(shape=(self.grid_size,), dtype="double", order="F")
            bmi_dll.get_grid_x(self.grid_id, self.grid_x)
            print(f"grid_x: {self.grid_x}")

            self.grid_y = np.empty(shape=(self.grid_size,), dtype="double", order="F")
            bmi_dll.get_grid_y(self.grid_id, self.grid_y)
            print(f"grid_y: {self.grid_y}")

            # TODO_JH: Implement get_grid_rank for unstructured grids
            # in order to determine if grid_z exists.

        if self.grid_type == "unstructured":
            # get grid_node_count (node in BMI-context means vertex in Modflow context)
            self.grid_node_count = bmi_dll.get_grid_node_count(self.grid_id)
            print(f"grid_node_count: {self.grid_node_count}")

            # get face_count
            self.face_count = bmi_dll.get_grid_face_count(self.grid_id)
            print(f"face_count: {self.face_count}")

            # get grid_node_per_face
            self.nodes_per_face = np.empty(
                shape=(self.face_count,), dtype="int", order="F"
            )
            bmi_dll.get_grid_nodes_per_face(self.grid_id, self.nodes_per_face)
            print(f"nodes_per_face: {self.nodes_per_face}")

            # get grid_face_nodes
            face_nodes_count = np.sum(self.nodes_per_face + 1)
            face_nodes = np.empty(shape=(face_nodes_count,), dtype="int", order="F")
            bmi_dll.get_grid_face_nodes(self.grid_id, face_nodes)
            # Subtract 1 so that 0 describes the first element
            self.face_nodes = face_nodes - 1
            print(f"face_nodes: {self.face_nodes}")

        # Currently it is only used for the head values,
        # but it could be extended for multiple values
        self.head_tag = bmi_dll.get_var_address("X", self.model_name)
        self.plotarray = bmi_dll.get_value_ptr(self.head_tag)

    def eval_time_loop(self):
        # update time
        self.ct = self.bmi_dll.get_current_time()
        self.plotarray = self.bmi_dll.get_value_ptr(self.head_tag)

    def get_value(self, var_name, component_name):
        var_tag = self.bmi_dll.get_var_address(
            var_name, self.model_name, component_name
        )
        return self.bmi_dll.get_value_ptr(var_tag)
