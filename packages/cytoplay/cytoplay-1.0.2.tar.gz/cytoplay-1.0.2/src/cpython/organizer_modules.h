#include "aster.h"
#include "bundle.h"
#include "bundle_prop.h"
#include "fake.h"
#include "fake_prop.h"
#include "nucleus.h"
#include "nucleus_prop.h"
#include <pybind11/pybind11.h>
#include "python_utilities.h"
namespace py = pybind11;

class Aster;
class Organizer;
class Object;

/// Converts an object to an aster if possible
static Aster* toAster(Object * obj)
{
    if ( obj  &&  obj->tag() == Organizer::ASTER_TAG )
        return static_cast<Aster*>(obj);
    return nullptr;
}

/// a utility to enrich the cytosim python module
void load_organizer_classes(py::module_ &m) {
     /// Python interface to Organizer
    py::class_<Organizer,Object>(m, "Organizer")
        .def("build", [](Organizer * org, std::string how, Simul & sim) {
            Glossary glos = Glossary(how); return org->build(glos, sim); }, PYOWN)
        .def("nbOrganized",  [](const Organizer * org) {return org->nbOrganized() ;})
        .def("nbOrganized",  [](Organizer * org, size_t n) {return org->nbOrganized(n) ;})
        .def("organized", &Organizer::organized)
        .def("grasp",  [](Organizer * org, Mecable * mec) {return org->grasp(mec) ;})
        .def("grasp",  [](Organizer * org, Mecable * mec, size_t n) {return org->grasp(mec,n) ;})
        .def("check", &Organizer::check)
        .def("goodbye", &Organizer::goodbye)
        .def("checkOrganized", &Organizer::checkOrganized)
        .def("mobile", &Organizer::mobile)
        .def("position", [](const Organizer * org) {return to_numpy(org->position());}, PYOWN)
        .def("positionP", [](const Organizer * org, unsigned i) {return to_numpy(org->positionP(i));}, PYOWN)
        .def("step", &Organizer::step)
        .def("setInteractions", &Organizer::setInteractions)
        .def("nbLinks", &Organizer::nbLinks)
        .def("sumDragCoefficient",  [](Organizer * org) {return org->sumDragCoefficient() ;})
        .def("getLink",  [](const Organizer * org, int n) {
            Vector V,W; 
            org->getLink((size_t)n,V,W);
            return std::vector<pyarray>{to_numpy(V),to_numpy(W)}; }, PYOWN)
        .def("solid", &Organizer::solid, PYREF)
        .def("sphere", &Organizer::sphere, PYREF)
        .def("next",  [](Organizer * org) {return org->next() ;}, PYREF)
        .def("prev",  [](Organizer * org) {return org->prev() ;}, PYREF);

    py::class_<Aster,Organizer>(m, "Aster")
        .def("build",  [](Aster * org, std::string & how, Simul & sim) {
                auto glos = Glossary(how);
                return org->build(glos, sim) ;})
        .def("solid",  [](const Aster * org) {return org->solid() ;})
        .def("position", [](const Aster * org) {return to_numpy(org->position());}, PYOWN)
        .def("nbFibers",  [](const Aster * org) {return org->nbFibers() ;})
        .def("fiber",  [](const Aster * org, int n) {return org->fiber((size_t)n) ;})
        .def("step", &Aster::step)
        .def("setInteractions", &Aster::setInteractions)
        .def("nbLinks", &Aster::nbLinks)
        .def("getLink1",  [](const Aster * org, int n)
            {Vector V,W; 
            org->getLink1((size_t)n,V,W);
                return std::vector<pyarray>{to_numpy(V),to_numpy(W)};
                }, PYOWN)
        .def("getLink2",  [](const Aster * org, int n)
            {Vector V,W; 
            org->getLink2((size_t)n,V,W);
                return std::vector<pyarray>{to_numpy(V),to_numpy(W)};
                }, PYOWN)
        .def("getLink",  [](const Aster * org, int n)
            {Vector V,W; 
            org->getLink((size_t)n,V,W);
                return std::vector<pyarray>{to_numpy(V),to_numpy(W)};
                }, PYOWN)
        .def("tag", &Aster::tag, PYREF)
        .def("toAster",  [](Object * s) {return toAster(s);}, PYREF)
        .def("property",  [](const Aster * org) {return org->property() ;}, PYREF); 
        
        
    py::class_<Bundle,Organizer>(m, "Bundle");
    
    py::class_<Fake,Organizer>(m, "Fake")
        .def("solid", &Fake::solid, PYREF);
        
    py::class_<Nucleus,Organizer>(m, "Nucleus")
        .def("sphere", &Nucleus::sphere, PYREF) 
        .def("fiber", &Nucleus::fiber, PYREF);
    
    py::class_<AsterProp,Property>(m, "AsterProp")
        .def("stiffness",  [](AsterProp * prop) {return to_numpy_raw(prop->stiffness, 1, 2); }, PYOWN)
        .def_readwrite("pole", &AsterProp::pole)
        .def_readwrite("fiber_type", &AsterProp::fiber_type)
        .def_readwrite("fiber_rate", &AsterProp::fiber_rate)
        .def_readwrite("fiber_spec", &AsterProp::fiber_spec);
    
    py::class_<BundleProp,Property>(m, "BundleProp")
        .def_readwrite("stiffness", &BundleProp::stiffness)
        .def_readwrite("overlap", &BundleProp::overlap)
        .def_readwrite("pole", &BundleProp::pole)
        .def_readwrite("fiber_rate", &BundleProp::fiber_rate)
        .def_readwrite("fiber_type", &BundleProp::fiber_type)
        .def_readwrite("fiber_spec", &BundleProp::fiber_spec)
        .def_readwrite("fiber_prob", &BundleProp::fiber_prob);
        
    py::class_<FakeProp,Property>(m, "FakeProp")
        .def_readwrite("stiffness", &FakeProp::stiffness);
    
    py::class_<NucleusProp,Property>(m, "NucleusProp")
        .def_readwrite("stiffness", &NucleusProp::stiffness);
}

