from pathlib import Path
import ctypes
import numpy as np
from collections import defaultdict
import os
import re


class BMI:
    def __init__(self):
        self.dllpath = Path(
            "c:/checkouts/modflow6-martijn-fork/msvs/dll/x64/Debug/mf6.dll"
        )
        self.simpath = ui_path = Path(__file__).parent.parent.parent / "data" / "ex_3x3_disu"
        self.var_names = {b"SLN_1/X": "double"}
        self.mf6_dll = ctypes.cdll.LoadLibrary(str(self.dllpath))

        os.chdir(self.simpath)

        # initialize the model
        self.mf6_dll.initialize()

        self.ct = ctypes.c_double(0.0)
        self.mf6_dll.get_current_time(ctypes.byref(self.ct))

        self.et = ctypes.c_double(0.0)
        self.mf6_dll.get_end_time(ctypes.byref(self.et))

        # acessing exported value from dll
        self.maxstrlen = ctypes.c_int.in_dll(self.mf6_dll, "MAXSTRLEN").value

        # TODO_JH: Find a better way to get the grid_id
        # then parsing the model_name from the mfsim.nam file
        # and then searching for the grid_id of a specific parameter
        # this additionally only works when only one model is present
        with open(self.simpath / "mfsim.nam", "r") as namefile:
            content = namefile.read()
            match = re.search(r"\s(\w+)\nEND MODELS", content, re.IGNORECASE)
            if match:
                model_name = match.group(1).upper()
            else:
                raise Exception("The model name could not be parsed")

        c_var_name = ctypes.c_char_p((model_name + " NPF/K11").encode())
        self.grid_id = ctypes.c_int(0)
        self.mf6_dll.get_var_grid(c_var_name, ctypes.byref(self.grid_id))
        print(f"grid id: {self.grid_id.value}")

        # get grid type
        self.grid_type = ctypes.create_string_buffer(self.maxstrlen)
        self.mf6_dll.get_grid_type(ctypes.byref(self.grid_id), self.grid_type)
        self.grid_type = self.grid_type.value.decode("ASCII")
        print(f"grid type: {self.grid_type}")

        # get grid size
        grid_size = ctypes.c_int(0)
        self.mf6_dll.get_grid_size(ctypes.byref(self.grid_id), ctypes.byref(grid_size))
        self.grid_size = grid_size.value
        print(f"grid size: {self.grid_size}")

        if self.grid_type in (
            "uniform rectilinear",
            "rectilinear",
            "structured quadrilaterals",
        ):
            # get grid rank
            grid_rank = ctypes.c_int(0)
            self.mf6_dll.get_grid_rank(
                ctypes.byref(self.grid_id), ctypes.byref(grid_rank)
            )
            self.grid_rank = grid_rank.value
            print(f"grid rank: {self.grid_rank}")

            # get grid shape
            grid_shape = np.ctypeslib.ndpointer(
                dtype="int", ndim=1, shape=(self.grid_rank,), flags="F"
            )()
            self.mf6_dll.get_grid_shape(
                ctypes.byref(self.grid_id), ctypes.byref(grid_shape)
            )
            self.grid_shape = grid_shape.contents
            print(f"grid shape: {self.grid_shape}")

        # get grid_x, grid_y and grid_z
        if self.grid_type == "rectilinear":
            grid_x = np.ctypeslib.ndpointer(
                dtype="double", ndim=1, shape=(self.grid_shape[-1] + 1,), flags="F"
            )()
            self.mf6_dll.get_grid_x(ctypes.byref(self.grid_id), ctypes.byref(grid_x))
            self.grid_x = grid_x.contents
            print(f"grid x: {self.grid_x}")

            grid_y = np.ctypeslib.ndpointer(
                dtype="double", ndim=1, shape=(self.grid_shape[-2] + 1,), flags="F"
            )()
            self.mf6_dll.get_grid_y(ctypes.byref(self.grid_id), ctypes.byref(grid_y))
            self.grid_y = grid_y.contents
            print(f"grid y: {self.grid_y}")

            if len(grid_shape) == 3:
                grid_z = np.ctypeslib.ndpointer(
                    dtype="double", ndim=1, shape=(self.grid_shape[-3] + 1,), flags="F"
                )()
                self.mf6_dll.get_grid_z(
                    ctypes.byref(self.grid_id), ctypes.byref(grid_z)
                )
                self.grid_z = grid_z.contents
                print(f"grid z: {self.grid_z}")
        elif self.grid_type in ("structured quadrilaterals", "unstructured"):
            grid_x = np.ctypeslib.ndpointer(
                dtype="double", ndim=1, shape=(self.grid_size,), flags="F"
            )()
            self.mf6_dll.get_grid_x(ctypes.byref(self.grid_id), ctypes.byref(grid_x))
            self.grid_x = grid_x.contents
            print(f"grid x: {self.grid_x}")

            grid_y = np.ctypeslib.ndpointer(
                dtype="double", ndim=1, shape=(self.grid_size,), flags="F"
            )()
            self.mf6_dll.get_grid_y(ctypes.byref(self.grid_id), ctypes.byref(grid_y))
            self.grid_y = grid_y.contents
            print(f"grid y: {self.grid_y}")

            # TODO_JH: Implement get_grid_ramk for unstructured grids in order to determine if grid_z exists.

        if self.grid_type == "unstructured":
            # get grid_node_count (node in BMI-context means vertex in Modflow context)
            grid_node_count = ctypes.c_int(0)
            self.mf6_dll.get_grid_node_count(
                ctypes.byref(self.grid_id), ctypes.byref(grid_node_count)
            )
            self.grid_node_count = grid_node_count.value
            print(f"grid_node_count: {self.grid_node_count}")

            # get grid_face_count
            grid_face_count = ctypes.c_int(0)
            self.mf6_dll.get_grid_face_count(
                ctypes.byref(self.grid_id), ctypes.byref(grid_face_count)
            )
            self.grid_face_count = grid_face_count.value
            print(f"grid_face_count: {self.grid_face_count}")

            # get grid_node_per_face
            nodes_per_face = np.ctypeslib.ndpointer(
                dtype="int", ndim=1, shape=(self.grid_face_count,), flags="F"
            )()
            self.mf6_dll.get_grid_nodes_per_face(
                ctypes.byref(self.grid_id), ctypes.byref(nodes_per_face)
            )
            self.nodes_per_face = nodes_per_face.contents
            print(f"nodes_per_face: {self.nodes_per_face}")

            # get grid_face_nodes
            face_nodes_size = np.sum(self.nodes_per_face + 1)
            face_nodes = np.ctypeslib.ndpointer(
                dtype="int", ndim=1, shape=(face_nodes_size,), flags="F"
            )()
            self.mf6_dll.get_grid_face_nodes(
                ctypes.byref(self.grid_id), ctypes.byref(face_nodes)
            )
            # Subtract 1 so that 0 describes the first element
            self.face_nodes = face_nodes.contents - 1
            print(f"face_nodes: {self.face_nodes}")

        # initialize dictionary
        self.var_dict = defaultdict(dict)
        for key in self.var_names:
            # get variable size(s)
            elsize = ctypes.c_int(0)
            nbytes = ctypes.c_int(0)
            self.var_dict[key]["name"] = ctypes.c_char_p(key)

            self.mf6_dll.get_var_itemsize(
                self.var_dict[key]["name"], ctypes.byref(elsize)
            )
            self.mf6_dll.get_var_nbytes(
                self.var_dict[key]["name"], ctypes.byref(nbytes)
            )
            nsize = int(nbytes.value / elsize.value)

            self.var_dict[key]["type"] = self.var_names[key]

            # declare the receiving pointers-to-array
            self.var_dict[key]["array"] = np.ctypeslib.ndpointer(
                dtype=self.var_dict[key]["type"], ndim=1, shape=(nsize,), flags="F"
            )()

    """
    grid_lines : (point_type=PointType.spatialxyz) : list
    returns the model grid lines in a list.  each line is returned as a
    list containing two tuples in the format [(x1,y1), (x2,y2)] where
    x1,y1 and x2,y2 are the endpoints of the line.
    CURRENTLY ONLY USABLE OR UNSTRUCTURED GRIDS
    """

    @property
    def grid_lines(self):
        lines = []
        j = -1
        for i, face_node in enumerate(self.face_nodes):
            if i % (self.nodes_per_face[j] + 1):
                lines.append(
                    [
                        (self.grid_x[face_node_old], self.grid_y[face_node_old]),
                        (self.grid_x[face_node], self.grid_y[face_node]),
                    ]
                )
            else:
                j += 1
            face_node_old = face_node
        return lines

    @property
    def extent(self):
        return (np.min(self.grid_x),
                np.max(self.grid_x),
                np.min(self.grid_y),
                np.max(self.grid_y))

    def get_value(self, value_name, value_type):
        name = ctypes.c_char_p(value_name.encode())

        elsize = ctypes.c_int(0)
        nbytes = ctypes.c_int(0)

        self.mf6_dll.get_var_itemsize(name, ctypes.byref(elsize))
        self.mf6_dll.get_var_nbytes(name, ctypes.byref(nbytes))
        nsize = int(nbytes.value / elsize.value)

        array = np.ctypeslib.ndpointer(
            dtype=value_type, ndim=1, shape=(nsize,), flags="F"
        )()

        if value_type == "double":
            self.mf6_dll.get_value_ptr_double(name, ctypes.byref(array))
        elif value_type == "int":
            self.mf6_dll.get_value_ptr_int(name, ctypes.byref(array))
        else:
            raise ValueError("The type is neither double nor int")

        values = array.contents
        print(values)
        return ()

    def advance_time_loop(self):

        # calculate
        self.mf6_dll.update()
        # update time
        self.mf6_dll.get_current_time(ctypes.byref(self.ct))

        for key in self.var_names:
            # get data
            if self.var_dict[key]["type"] == "double":
                self.mf6_dll.get_value_ptr_double(
                    self.var_dict[key]["name"],
                    ctypes.byref(self.var_dict[key]["array"]),
                )
            elif self.var_dict[key]["type"] == "int":
                self.mf6_dll.get_value_ptr_int(
                    self.var_dict[key]["name"],
                    ctypes.byref(self.var_dict[key]["array"]),
                )
            else:
                raise ValueError("The type is neither double nor int")

            vararray = self.var_dict[key]["array"].contents
            if key == b"SLN_1/X" and self.grid_type == "rectilinear":
                # TODO_JH only send vararray
                return (
                    self.grid_x,
                    self.grid_y,
                    vararray.reshape(self.grid_shape, order="A"),
                )

        return (None, None, None)
