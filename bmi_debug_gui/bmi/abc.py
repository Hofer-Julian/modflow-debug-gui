import ctypes
from collections import defaultdict

import numpy as np
import os


class Bmi:
    def __init__(self, bmi_dll, model_name):
        self.model_name = model_name
        self.ct = bmi_dll.get_current_time()
        self.et = bmi_dll.get_end_time()
        self.bmi_dll = bmi_dll

        k11_tag = bmi_dll.get_var_address("K11", model_name, "NPF")
        self.grid_id = bmi_dll.get_var_grid(k11_tag)
        self.grid_size = bmi_dll.get_grid_size(self.grid_id)

        # Currently it is only used for the head values,
        # but it could be extended for multiple values
        self.head_tag = bmi_dll.get_var_address("X", self.model_name)
        self.plotarray = bmi_dll.get_value_ptr(self.head_tag)

    @staticmethod
    def get_bmi(bmi_dll, model_name):
        k11_tag = bmi_dll.get_var_address("K11", model_name, "NPF")
        grid_id = bmi_dll.get_var_grid(k11_tag)
        grid_type = bmi_dll.get_grid_type(grid_id)
        if grid_type == "rectilinear":
            from bmi_debug_gui.bmi.rectilinear import RectBmi

            return RectBmi(bmi_dll, model_name)
        elif grid_type == "unstructured":
            from bmi_debug_gui.bmi.unstructured import UnstrucBmi

            return UnstrucBmi(bmi_dll, model_name)
        else:
            raise Exception("Unsupported grid type")

    def draw_picture(self, painter, headcolors):
        raise NotImplementedError

    def eval_time_loop(self):
        # update time
        self.ct = self.bmi_dll.get_current_time()
        self.plotarray = self.bmi_dll.get_value_ptr(self.head_tag)

    def get_value(self, var_name, component_name):
        var_tag = self.bmi_dll.get_var_address(
            var_name, self.model_name, component_name
        )
        return self.bmi_dll.get_value_ptr(var_tag)

    def print_values(self):
        print(f"model_name: {self.model_name}")
        print(f"model_dir: {os.path.basename(self.bmi_dll.working_directory)}")
        print(f"grid_id: {self.grid_id}")
        print(f"grid_type: {self.grid_type}")
        print(f"grid_size: {self.grid_size}")
