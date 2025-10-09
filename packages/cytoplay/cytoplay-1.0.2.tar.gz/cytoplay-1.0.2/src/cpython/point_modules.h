#include "interpolation.h"
#include "mecable.h"
#include <pybind11/pybind11.h>
#include "python_utilities.h"
namespace py = pybind11;

class Interpolation;

/// a utility to enrich the cytosim python module
void load_point_classes(py::module_ &m) {
    /// Python interface to Mecapoint and Interpolation
    py::class_<Mecapoint>(m, "Mecapoint")
        .def(py::init([](Mecable * mec, int pt) 
            {Mecable::SIZE_T pti = pt; return Mecapoint(mec, pti);}),  PYOWN)
        .def("Mecapoint",  [](Mecable * mec, int pt) 
            {Mecable::SIZE_T pti = pt; return Mecapoint(mec, pti);},  PYOWN)
        .def("set", &Mecapoint::set)
        .def("mecable", &Mecapoint::mecable, PYREF)
        .def("valid", &Mecapoint::valid)
        .def("position", [](const Mecapoint * pol) {return to_numpy(pol->pos());}, PYOWN)
        .def("pos", [](const Mecapoint * pol) {return to_numpy(pol->pos());}, PYOWN)
        .def("overlapping", &Mecapoint::overlapping)
        .def("adjacent", &Mecapoint::adjacent);
        
    py::class_<Interpolation>(m, "Interpolation")
        .def(py::init([](Chain * chn, real c, int pt) 
            {return Interpolation(chn, c, pt);}),  PYOWN)
        .def(py::init([](Mecable * mec, real c, int pt, int qt) 
            {return Interpolation(mec, c, pt, qt);}),  PYOWN)
        .def("clear", &Interpolation::clear)
        .def("valid", &Interpolation::valid)
        .def("mecable", &Interpolation::mecable, PYREF)
        .def("vertex1", &Interpolation::vertex1, PYOWN)
        .def("vertex2", &Interpolation::vertex2, PYOWN)
        .def("coef1", &Interpolation::coef1)
        .def("coef", &Interpolation::coef)
        .def("position", [](const Interpolation * pol) {return to_numpy(pol->pos());}, PYOWN)
        .def("pos", [](const Interpolation * pol) {return to_numpy(pol->pos());}, PYOWN)
        .def("pos1", [](const Interpolation * pol) {return to_numpy(pol->pos1());}, PYOWN)
        .def("pos2", [](const Interpolation * pol) {return to_numpy(pol->pos2());}, PYOWN)
        .def("diff", [](const Interpolation * pol) {return to_numpy(pol->diff());}, PYOWN)
        .def("len", &Interpolation::len)
        .def("lenSqr", &Interpolation::lenSqr)
        .def("dir", [](const Interpolation * pol) {return to_numpy(pol->dir());}, PYOWN)
        .def("inside", &Interpolation::inside)
        .def("overlapping", [](const Interpolation * pol, const Interpolation & pal) {return pol->overlapping(pal);})
        .def("overlapPoint", [](const Interpolation * pol, const Mecapoint & pal) {return pol->overlapping(pal);});

}
