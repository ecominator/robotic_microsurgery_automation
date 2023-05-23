/*****************************************************************************
* File name:	smaract_main.cpp
* Project:		Robotic Surgery Software
* Part:   		SmarAct
* Editor:		Erfan ETESAMI and Ece OZELCI, MICROBS, EPFL, 2022
*				erfan.etesami@epfl.ch, ece.ozelci@epfl.ch
* Version:		22.0
* Description:	This file provides the bindings between the C++ code 
*               and the Python code responsible for controlling the
*               SmarAct channels.
*****************************************************************************/


#include "../Cpp/include/headers/smaract.h"
#include <pybind11/pybind11.h>
namespace py = pybind11;


void init_smaract(py::module &m) {
    py::class_<SmarAct>(m, "SmarAct")
    .def(py::init<>()) // for constructor and destructor
    .def("initialize", &SmarAct::initialize)
    .def("close", &SmarAct::close)
    .def("get_mcs_handle", &SmarAct::getMCSHandle)
    .def("get_is_found", &SmarAct::getIsFound)
    .def("get_referencing_status", &SmarAct::getReferencingStatus)
    .def("get_usb_locator", &SmarAct::getUSBLocator)
    .def("get_channel_position", &SmarAct::getChannelPosition)
    .def("set_is_found", &SmarAct::setIsFound)
    .def("set_referencing_status", &SmarAct::setReferencingStatus)
    .def("wait_calibration", &SmarAct::waitUntilCalibrationIsDone)
    .def("wait_referencing", &SmarAct::waitUntilReferencingIsDone)
    .def("is_channel_referenced", &SmarAct::isChannelReferenced)
    .def("reference_channel", &SmarAct::referenceChannel)
    .def("move_channel", &SmarAct::moveChannel)
    .def("move_channel_to_position", &SmarAct::moveChannelToPosition)
    .def("stop_channel", &SmarAct::stopChannel);
    // m.def("add", &add, "A function which adds two numbers", py::arg("i"), py::arg("j"));
}
