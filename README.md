# robotic_microsurgery_automation
Software of the robotic microsurgery platform.
For detailed installation requirements please contact ece.ozelci@epfl.ch
## Virtual Environment
1. In addition to setting up the virtual environment install required software suites: SmarAct MCS, SmarAct PTC, Arduino, Basler Pylon, and PISoftwareSuite. These installations provide the necessary DLL files for the modules.
2. Install the required packages in the virtual environment: pip, Numpy, pybind11, PyQt5, PyQtGraph, PySerial, PyPylon, PIPython, OpenCV, TensorFlow, Pygame, matplotlib
## C++ to Python binding
SmarAct_CppBinding: the directory that contains the C++ codes and the subsequently generated python module.
- Directories inside SmarAct_CppBinding:
- Cpp/src: The SmarAct.cpp source file
- Cpp/include/3rdParty: MCSControl.dll, MCSControl.lib, and SmarActIO.dll (These files are from the SmarAct installation folder.)
- Cpp/include/headers: The SmarAct.h header file, MCSControl.h (from the SmarAct installation folder)
- build: Leave it empty for now.
- Binding: SmarAct.cpp and SmarAct_Main.cpp source files. These two files contain the syntax required by pybind11.
