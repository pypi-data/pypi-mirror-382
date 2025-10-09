#include "lattice.h"
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "python_utilities.h"
namespace py = pybind11;

/// A utility to declare various types of lattices
template<typename CELL>
void declare_lattice(py::module &mod, CELL cell, std::string name) { 
        py::class_<Lattice<CELL>>(mod, name.c_str(),  "a lattice of a given type")
            .def("setUnit", &Lattice<CELL>::setUnit)
            .def("ready", &Lattice<CELL>::ready)
            .def("changeUnit", &Lattice<CELL>::changeUnit)
            .def("markEdges",  [](Lattice<CELL> * lat, const CELL val) { lat->markEdges(val);})
            .def("indexM", &Lattice<CELL>::indexM)
            .def("indexP", &Lattice<CELL>::indexP)
            .def("inf", &Lattice<CELL>::inf)
            .def("sup", &Lattice<CELL>::sup)
            .def("unit", &Lattice<CELL>::unit)
            .def("index", &Lattice<CELL>::index)
            .def("index_sup", &Lattice<CELL>::index_sup)
            .def("index_round", &Lattice<CELL>::index_round)
            .def("valid", &Lattice<CELL>::valid)
            .def("invalid", &Lattice<CELL>::invalid)
            .def("betweenMP", &Lattice<CELL>::betweenMP)
            .def("outsideMP", &Lattice<CELL>::outsideMP)
            .def("abscissa", &Lattice<CELL>::abscissa)
            .def("data",  [](Lattice<CELL> * lat, int s) {return lat->data(s);})
            .def("data", [](Lattice<CELL> * lat) { 
                return to_numpy_raw(lat->data(), lat->sup()-lat->inf(), (int) DIM ); } , PYOWN);
}
            
            