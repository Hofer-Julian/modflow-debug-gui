import sys
from setuptools import find_namespace_packages, setup
import codecs
import os.path


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


long_description = read("README.md")

# ensure minimum version of Python is running
if sys.version_info[0:2] < (3, 6):
    raise RuntimeError("The BMI Debug GUI requires Python >= 3.6")

setup(
    name="bmi_debug_gui",
    description="The BMI Debug GUI is used to debug the BMI of hydrological kernels.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Julian Hofer",
    url="",
    license="",
    platforms="Windows, Mac OS-X, Linux",
    install_requires=["numpy", "PyQt5", "pyqtgraph", "xmipy"],
    packages=find_namespace_packages(exclude=("tests", "examples")),
    version=get_version("bmi_debug_gui/__init__.py"),
    classifiers=["Topic :: Scientific/Engineering :: Hydrology"],
    entry_points={"gui_scripts": ["bmigui = bmi_debug_gui.__main__:main"]},
)
