# robotic_microsurgery_automation
Software of the robotic microsurgery platform.
For detailed installation requirements please contact ece.ozelci@epfl.ch
## Virtual Environment
1. In addition to setting up the virtual environment install required software suites: SmarAct MCS, SmarAct PTC, Arduino, Basler Pylon, and PISoftwareSuite. These installations provide the necessary DLL files for the modules.
2. Install the required packages in the virtual environment: pip, Numpy, pybind11, PyQt5, PyQtGraph, PySerial, PyPylon, PIPython, OpenCV, TensorFlow, Pygame, matplotlib
## C++ to Python binding
SmarAct_CppBinding: the directory that contains the C++ codes and the subsequently generated python module.

Directories inside SmarAct_CppBinding:
- Cpp/src: The SmarAct.cpp source file
- Cpp/include/3rdParty: MCSControl.dll, MCSControl.lib, and SmarActIO.dll (These files are from the SmarAct installation folder.)
- Cpp/include/headers: The SmarAct.h header file, MCSControl.h (from the SmarAct installation folder)
- build: Leave it empty for now.
- Binding: SmarAct.cpp and SmarAct_Main.cpp source files. These two files contain the syntax required by pybind11.
- CMakeLists.txt
## Software
- asm: arduino file to drive the stepper motor
- deep-networks: the model file of the deep-noto network 
- asm.py: fucntions to control the stepper motor via Arduino (works with .ino file in asm folder) 
- auxilary.py: functions used in the software
- computer_vision.py: methods that are used in computer vision tasks
- configuration.py: settings that are used to configure the components and functions of the robotic platform
- deep_network.py: u-net architecture and the function to load the model generated elsewhere
- gamepad.py: the communication between the gamepad and the software
- gui.py: GUI of the robotic surgery platform
- pistage.py: PIStage positioning axes and controls
- run.py: initializes the necessary modules and runs the software
- worker_threads.py: worker threads that run in parallel with the GUI thread 
