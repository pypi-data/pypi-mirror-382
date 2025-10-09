#include "glossary.h"
#include <pybind11/pybind11.h>
#include "python_utilities.h"
//#include <pybind11/numpy.h>
//#include <pybind11/stl.h>
namespace py = pybind11;

/// a utility to enrich the cytosim python module
void load_glossary_classes(py::module_ &m) {
     /// Python interface to Glossarys
    py::class_<Glossary::val_type>(m, "Glossary::val_type")
        .def_readwrite("value_",   &Glossary::val_type::value_ )
        .def_readwrite("defined_",   &Glossary::val_type::defined_ )
        .def_readwrite("read_",   &Glossary::val_type::read_ )
        .def("__repr__",  [](Glossary::val_type & val) {return val.value_;});
    
    
    py::class_<Glossary>(m, "Glossary")
    .def("terms",  [](Glossary & glos) { Glossary::map_type terms = glos.terms() ; return terms ;}, PYREF)
    .def("__repr__",  [](Glossary & glos) {
        auto t = py::cast(glos.terms());
        return t.attr("__repr__")();})
    .def("__getitem__",[](Glossary & glos, std::string s) {
        return glos.values(s);
        }, PYREF)
    .def("__setitem__",[](Glossary & glos, std::string s, std::string r) {
        return glos.add_value(s,r);
        }, PYREF)
    .def("keys", [](Glossary & glos) {
        auto t = py::cast(glos.terms());
        return t.attr("keys")() ; }, PYREF)
    .def("items", [](Glossary & glos) {
        auto t = py::cast(glos.terms());
        return t.attr("items")() ; }, PYREF);
}

