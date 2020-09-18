# BMI Debug GUI

![screenshot](bmi_debug_gui/assets/screenshots/unstructured_big_model.PNG)

## How to create an executable with pyinstaller

To create a single executable run

```
pyinstaller -F /path/to/__main__.py
```

or to create an executable which starts up faster but consists of multiple files, run

```
pyinstaller /path/to/__main__.py
```

## How to convert .ui files to .py files

```
pyuic5 -o [name].py [name].ui
```

## PyQtGraph

This GUI uses the [pyqtgraph](http://www.pyqtgraph.org/) package for its plotting capabilities. In order to display 3D graphics, install `pyopengl` via conda.
However, take care **not** to install `pyopengl-accelerate` as it seems to make problems.
