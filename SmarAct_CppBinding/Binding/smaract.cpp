/*****************************************************************************
* File name:	smaract.cpp
* Project:		Robotic Surgery Software
* Part:   		SmarAct
* Editor:		Erfan ETESAMI and Ece OZELCI, MICROBS, EPFL, 2022
*				erfan.etesami@epfl.ch, ece.ozelci@epfl.ch
* Version:		22.0
* Description:	This file is the header file for the bindings between 
*               the C++ codes and the Python codes of SmarAct. 
*****************************************************************************/


#include <pybind11/pybind11.h>
namespace py = pybind11;


void init_smaract(py::module &);


PYBIND11_MODULE(SmarAct, m) {
    // Optional docstring
    m.doc() = "SmarAct Library";
    init_smaract(m);
}
