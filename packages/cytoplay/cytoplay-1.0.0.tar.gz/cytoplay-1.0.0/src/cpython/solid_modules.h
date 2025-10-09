#include "solid.h"
#include <pybind11/pybind11.h>
#include "python_utilities.h"
//#include <pybind11/numpy.h>
//#include <pybind11/stl.h>
namespace py = pybind11;

class Solid;
class Object;

/// a utility to enrich the cytosim python module
void load_solid_classes(py::module_ &m) {
    /// Python interface to Solid
    py::class_<Mecable,Object>(m, "Mecable")
        .def("addrPoints",   [](Mecable * mec) {return get_obj_data(mec);}, PYOWN)
        .def("nbPoints", &Mecable::nbPoints)
        .def("allocated", &Mecable::allocated)
        .def("points",  [](Mecable * mec) {return get_obj_points(mec);}, PYOWN)
        .def("posPoint",  [](Mecable * mec,int p) {return to_numpy(mec->posPoint(p));}, PYOWN)
        .def("setPoint",  [](Mecable * mec, int i, pyarray vec) 
            {   Vector p = to_vector(vec);
                return mec->setPoint(i,p);})
        .def("setPoint",  [](Mecable * mec, int i, pyarray vec) 
            {   Vector p = to_vector(vec);
                return mec->movePoint(i,p);})
        .def("addPoint",  [](Mecable * mec, pyarray vec) 
            {   Vector p = to_vector(vec);
                return mec->addPoint(p);})
        .def("removePoints", &Mecable::removePoints)
        .def("clearPoints", &Mecable::clearPoints)
        .def("shiftPoints", &Mecable::shiftPoints)
        .def("truncateM", &Mecable::truncateM)
        .def("truncateP", &Mecable::truncateP)
        .def("calculateMomentum",  [](Mecable * mec)
            {Vector V,W; 
            mec->calculateMomentum(V,W);
                return std::vector<pyarray>{to_numpy(V),to_numpy(W)};
                }, PYOWN)
        .def("netForce",  [](Mecable * mec,int p) {return to_numpy(mec->netForce(p));}, PYOWN)
        .def("position",  [](Mecable * mec) {return to_numpy(mec->position());}, PYOWN)
        .def("translate",  [](Mecable * mec, pyarray vec) 
            {   Vector p = to_vector(vec);
                return mec->translate(p);});
        
    py::class_<Sphere,Mecable>(m, "Sphere")
        .def("position",  [](Sphere * bed) {return to_numpy(bed->position());}, PYOWN)
        .def("pos",  [](Sphere * bed) {return to_numpy(bed->position());}, PYOWN)
        .def("radius", &Sphere::radius)
        .def("resize", &Sphere::resize)
        .def("reshape", &Sphere::reshape)
        .def("orthogonalize", &Sphere::orthogonalize)
        .def("addSurfacePoint", [](Sphere & bed, pyarray pos) {bed.addSurfacePoint(to_vector(pos));})
        .def("nbbSurfacePoints", &Sphere::nbSurfacePoints)
        .def("dragCoefficient", &Sphere::dragCoefficient)
        .def("next", &Sphere::next, PYREF)
        .def("prev", &Sphere::prev, PYREF)
        .def("toSphere",  [](Object * obj) {return Sphere::toSphere(obj);},  PYREF);
        
    
    py::class_<Bead,Mecable>(m, "Bead")
        .def("position",  [](Bead * bed) {return to_numpy(bed->position());}, PYOWN)
        .def("pos",  [](Bead * bed) {return to_numpy(bed->position());}, PYOWN)
        .def("setPosition",  [](Bead * bed, pyarray pos) {bed->setPosition(to_vector(pos));})
        .def("radius", &Bead::radius)
        .def("radiusSqr", &Bead::radiusSqr)
        .def("resize", &Bead::resize)
        .def("volume", &Bead::volume)
        .def("dragCoefficient", &Bead::dragCoefficient)
        .def("next", &Bead::next, PYREF)
        .def("prev", &Bead::prev, PYREF)
        .def("toBead",  [](Object * obj) {return Bead::toBead(obj);},  PYREF);
          
    
    py::class_<Solid,Object>(m, "Solid")
        .def("position", [](const Solid * sol) {return to_numpy(sol->position());}, PYOWN)
        .def("points",  [](Solid * sol) {return get_obj_points(sol);}, PYOWN)
        .def("dragCoefficient",  [](Solid * sol) {return sol->dragCoefficient() ;}, PYOWN)
        .def("addSphere",  [](Solid * sol, pyarray pts, real radius) {return sol->addSphere(to_vector(pts), radius) ;})
        .def("centroid", [](const Solid * sol) {return to_numpy(sol->centroid());}, PYOWN)
        .def("next",  [](Solid * sol) {return sol->next() ;})
        .def("prev",  [](Solid * sol) {return sol->prev() ;})
        .def("tag",  [](Solid * sol) {return sol->tag() ;})
        .def("property",  [](Solid * sol) {return sol->property() ;})
        .def("nbPoints", [](const Solid * sol) {return sol->nbPoints();})
        .def("toSolid",  [](Object * obj) {return Solid::toSolid(obj);},  PYREF);
          
    py::class_<SolidProp,Property>(m, "SolidProp")
        .def_readwrite("drag", &SolidProp::drag)
        .def_readwrite("viscosity", &SolidProp::viscosity)
        .def_readwrite("steric_key", &SolidProp::steric_key)
        .def_readwrite("steric_range", &SolidProp::steric_range)
        .def_readwrite("confine", &SolidProp::confine)
        .def_readwrite("confine_stiff", &SolidProp::confine_stiff)
        .def_readwrite("display", &SolidProp::display)
        .def_readwrite("display_fresh", &SolidProp::display_fresh);
        
     py::class_<SphereProp,Property>(m, "SphereProp")
        .def_readwrite("point_mobility", &SphereProp::point_mobility)
        .def_readwrite("viscosity", &SphereProp::viscosity)
        .def_readwrite("piston_effect", &SphereProp::piston_effect)
        .def_readwrite("steric_key", &SphereProp::steric_key)
        .def_readwrite("steric_range", &SphereProp::steric_range)
        .def_readwrite("confine", &SphereProp::confine)
        .def_readwrite("confine_spec", &SphereProp::confine_spec)
        .def_readwrite("display", &SphereProp::display)
        .def_readwrite("display_fresh", &SphereProp::display_fresh)
        .def("category", &SphereProp::category);
        
}

