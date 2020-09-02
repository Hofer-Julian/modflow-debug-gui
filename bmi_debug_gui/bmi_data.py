import ctypes
from collections import defaultdict

import numpy as np


class BMI:
    def __init__(self, bmi_dll, model_name):
        self.model_name = model_name
        self.ct = bmi_dll.get_current_time()
        self.et = bmi_dll.get_end_time()

        k11_tag = bmi_dll.get_var_address("K11", model_name, "NPF")
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
            # TODO JH: Move to xmipy
            self.grid_x = np.empty(shape=(self.grid_size,), dtype="double", order="F")
            bmi_dll.get_grid_x(self.grid_id, self.grid_x)
            print(f"grid_x: {self.grid_x}")

            self.grid_y = np.empty(shape=(self.grid_size,), dtype="double", order="F")
            bmi_dll.get_grid_y(self.grid_id, self.grid_y)
            print(f"grid_y: {self.grid_y}")

            # TODO_JH: Implement get_grid_rank for unstructured grids
            # in order to determine if grid_z exists.

        if self.grid_type == "unstructured":
            # TODO JH: Move to xmipy
            # get grid_node_count (node in BMI-context means vertex in Modflow context)
            grid_node_count = ctypes.c_int(0)
            bmi_dll.get_grid_node_count(
                ctypes.byref(self.grid_id), ctypes.byref(grid_node_count)
            )
            self.grid_node_count = grid_node_count.value
            print(f"grid_node_count: {self.grid_node_count}")

            # get grid_face_count
            grid_face_count = ctypes.c_int(0)
            bmi_dll.get_grid_face_count(
                ctypes.byref(self.grid_id), ctypes.byref(grid_face_count)
            )
            self.grid_face_count = grid_face_count.value
            print(f"grid_face_count: {self.grid_face_count}")

            # get grid_node_per_face
            nodes_per_face = np.ctypeslib.ndpointer(
                dtype="int", ndim=1, shape=(self.grid_face_count,), flags="F"
            )()
            bmi_dll.get_grid_nodes_per_face(
                ctypes.byref(self.grid_id), ctypes.byref(nodes_per_face)
            )
            self.nodes_per_face = nodes_per_face.contents
            print(f"nodes_per_face: {self.nodes_per_face}")

            # get grid_face_nodes
            face_nodes_size = np.sum(self.nodes_per_face + 1)
            face_nodes = np.ctypeslib.ndpointer(
                dtype="int", ndim=1, shape=(face_nodes_size,), flags="F"
            )()
            bmi_dll.get_grid_face_nodes(
                ctypes.byref(self.grid_id), ctypes.byref(face_nodes)
            )
            # Subtract 1 so that 0 describes the first element
            self.face_nodes = face_nodes.contents - 1
            print(f"face_nodes: {self.face_nodes}")

        # Currently it is only used for the head values,
        # but it could be extended for multiple values
        self.head_tag = bmi_dll.get_var_address("X", "SLN_1")
        self.plotarray = bmi_dll.get_value_ptr(self.head_tag)

    def eval_time_loop(self, bmi_dll):
        # update time
        self.ct = bmi_dll.get_current_time()
        self.plotarray = bmi_dll.get_value_ptr(self.head_tag)

    def get_value(self, bmi_dll, value_name, value_type):
        complete_name = self.model_name + " " + value_name
        name = ctypes.c_char_p(complete_name.encode())

        elsize = ctypes.c_int(0)
        nbytes = ctypes.c_int(0)

        bmi_dll.get_var_itemsize(name, ctypes.byref(elsize))
        bmi_dll.get_var_nbytes(name, ctypes.byref(nbytes))
        nsize = int(nbytes.value / elsize.value)

        array = np.ctypeslib.ndpointer(
            dtype=value_type, ndim=1, shape=(nsize,), flags="F"
        )()

        if value_type == "double":
            bmi_dll.get_value_ptr_double(name, ctypes.byref(array))
        elif value_type == "int":
            bmi_dll.get_value_ptr_int(name, ctypes.byref(array))
        else:
            raise ValueError("The type is neither double nor int")

        return array.contents
