#include "couple.h"
#include "couple_prop.h"
#include "fiber.h"
#include "couple_long.h"
#include "bridge.h"
#include "bridge_prop.h"
#include "crosslink.h"
#include "crosslink_prop.h"
#include "crosslink_long.h"
#include "duo.h"
#include "duo_prop.h"
#include "duo_long.h"
#include "fork.h"
#include "fork_prop.h"
#include "shackle.h"
#include "shackle_prop.h"
#include "shackle_long.h"

#include <pybind11/pybind11.h>
#include "python_utilities.h"
namespace py = pybind11;

class Couple;
class Object;
class CoupleProp;

/**
 @defgroup PyCouple Couple
  * @brief A group functions to facilitate usage of Couple in PyCytosim
    
    In PyCytosim, a Couple is also a list of (two) hands
 
  [python]>>> `hand1 = couple[0]` \n
  [python]>>> `hand2 = couple[1]` \n
   
    @ingroup PyUtilities
 */

/// Converts an object to a Couple if possible;
/**
 * @brief Converts an object to a Couple if possible
 
  [python]>>> `couple = cytosim.Couple.toCouple(obj) ` \n
 * @param obj
 * @return Couple 

 
 @ingroup PyCouple
 */
static Couple* toCouple(Object * obj)
{
    if ( obj  &&  obj->tag() == 'c' )
        return static_cast<Couple*>(obj);
    return nullptr;
}

/// a utility to enrich the cytosim python module
void load_couple_classes(py::module_ &m) {
     /// Python interface to couple
    py::class_<Couple,Object,HandMonitor>(m, "Couple")
        .def("changeProperty", &Couple::changeProperty)
        .def("setInteractions", &Couple::setInteractions)
        .def("setInteractionsAF", &Couple::setInteractionsAF)
        .def("setInteractionsFA", &Couple::setInteractionsFA)
        //
        .def("position",  [](Couple * s) {return to_numpy(s->position());}, PYOWN)
        .def("mobile",  &Couple::mobile)
        .def("translate",  [](Couple * s, pyarray vec) {s->translate(to_vector(vec));})
        .def("setPosition",  [](Couple * s, pyarray vec) {s->setPosition(to_vector(vec));})
        .def("randomizePosition",  &Couple::randomizePosition)
        //  
        .def("active",  &Couple::active)
        .def("activate",  &Couple::activate)
        .def("state",  &Couple::state)
        .def("attached",  &Couple::attached)
        .def("configuration",  &Couple::configuration)
        .def("attachedHand",  &Couple::attachedHand, PYREF)
        .def("cosAngle",  &Couple::cosAngle)
        .def("posFree",  [](Couple * s) {return to_numpy(s->posFree());}, PYOWN)
        .def("stretch",  [](Couple * s) {return to_numpy(s->stretch());}, PYOWN)
        .def("sidePos1",  [](Couple * s) {return to_numpy(s->sidePos1());}, PYOWN)
        .def("sidePos2",  [](Couple * s) {return to_numpy(s->sidePos2());}, PYOWN)
        .def("force",  [](Couple * s) {return to_numpy(s->force());}, PYOWN)
        //
        .def("stepFF",  &Couple::stepFF)
        .def("stepAF",  &Couple::stepAF)
        .def("stepFA",  &Couple::stepFA)
        .def("stepAA",  &Couple::stepAA)
        .def("stepHand1",  &Couple::stepHand1)
        .def("stepHand2",  &Couple::stepHand2)
        //
        .def("hand1",  [](Couple *s) {return s->hand1();}, PYREF)
        .def("attached1",  &Couple::attached1)
        .def("fiber1",  &Couple::fiber1, PYREF)
        .def("abscissa1",  &Couple::abscissa1)
        .def("posHand1",  [](Couple * s) {return to_numpy(s->posHand1());}, PYOWN)
        .def("dirFiber1",  [](Couple * s) {return to_numpy(s->dirFiber1());}, PYOWN)
        .def("attach1",  &Couple::attach1)
        .def("attachEnd1",  [](Couple * s, Fiber * fib, int end) {return s->attachEnd1(fib, static_cast<FiberEnd>(end));})
        .def("moveToEnd1",  [](Couple * s,int end) {return s->moveToEnd1(static_cast<FiberEnd>(end));})
        //
        .def("hand2",  [](Couple *s) {return s->hand2();}, PYREF)
        .def("attached2",  &Couple::attached2)
        .def("fiber2",  &Couple::fiber2, PYREF)
        .def("abscissa2",  &Couple::abscissa2)
        .def("posHand2",  [](Couple * s) {return to_numpy(s->posHand2());}, PYOWN)
        .def("dirFiber2",  [](Couple * s) {return to_numpy(s->dirFiber2());}, PYOWN)
        .def("attach2",  &Couple::attach1)
        .def("attachEnd2",  [](Couple * s, Fiber * fib, int end) {return s->attachEnd2(fib, static_cast<FiberEnd>(end));})
        .def("moveToEnd2",  [](Couple * s,int end) {return s->moveToEnd2(static_cast<FiberEnd>(end));})
        //
        .def("toCouple",  [](Object * s) {return toCouple(s);}, PYREF)
        /// Pycytosim specific : Couple also behaves like a list of two hands
        .def("__len__",  [](Couple * s) {return (int)2;})
        /// Pycytosim specific : Couple also behaves like a list of two hands
        .def("__getitem__",[](const Couple *s, int i) { // We can call couple[0]  to get the first hand ! thus couple[0].attachEnd(...) is available
            if (i==0) {return s->hand1();}
            else if (i==1) {return s->hand2();}
            else {  throw py::index_error();}
            return (const Hand*) nullptr; }
            , PYREF);
        
    py::enum_<CoupleProp::Specificity>(m,"Specificity")
        .value("BIND_ALWAYS", CoupleProp::BIND_ALWAYS)
        .value("BIND_PARALLEL", CoupleProp::BIND_PARALLEL)
        .value("BIND_NOT_PARALLEL", CoupleProp::BIND_NOT_PARALLEL)
        .value("BIND_ANTIPARALLEL", CoupleProp::BIND_ANTIPARALLEL)
        .value("BIND_NOT_ANTIPARALLEL", CoupleProp::BIND_NOT_ANTIPARALLEL)
        .value("BIND_ORTHOGONAL", CoupleProp::BIND_ORTHOGONAL)
        .export_values();
    
    py::class_<CoupleProp,Property>(m, "CoupleProp")
        .def_readwrite("hand1", &CoupleProp::hand1)
        .def_readwrite("hand2", &CoupleProp::hand2)
        .def_readwrite("stiffness", &CoupleProp::stiffness)
        .def_readwrite("length", &CoupleProp::length)
        .def_readwrite("diffusion", &CoupleProp::diffusion)
        .def_readwrite("fast_diffusion", &CoupleProp::fast_diffusion)
        .def_readwrite("fast_reservoir", &CoupleProp::fast_reservoir)
        .def_readwrite("trans_activated", &CoupleProp::trans_activated)
        .def_readwrite("min_loop", &CoupleProp::min_loop)
        .def_readwrite("specificity", &CoupleProp::specificity)
        .def_readwrite("confine", &CoupleProp::confine)
        .def_readwrite("activity", &CoupleProp::activity)
        .def_readwrite("hand1_prop", &CoupleProp::hand1_prop, PYREF)
        .def_readwrite("hand2_prop", &CoupleProp::hand2_prop, PYREF)
        .def_readwrite("uni_counts", &CoupleProp::uni_counts)
        //
        .def("newCouple", &CoupleProp::newCouple, PYREF)
        .def("category", &CoupleProp::category)   
        .def("clear", &CoupleProp::clear)   
        .def("read", [](CoupleProp * p, std::string & how) {
            Glossary glos = Glossary(how);
            p->read(glos); })
        .def("complete", &CoupleProp::complete)        
        .def("clone", &CoupleProp::clone, PYREF)
        .def("spaceVolume", &CoupleProp::spaceVolume);
            
    py::class_<Bridge,Couple>(m, "Bridge");
    py::class_<CoupleLong,Couple>(m, "CoupleLong");
    py::class_<Crosslink,Couple>(m, "Crosslink");
    py::class_<CrosslinkLong,Crosslink>(m, "CrosslinkLong");
    py::class_<Duo,Couple>(m, "Duo");
    py::class_<DuoLong,Duo>(m, "DuoLong");
    py::class_<Fork,Couple>(m, "Fork");
    py::class_<Shackle,Couple>(m, "Shackle");
    py::class_<ShackleLong,Shackle>(m, "ShackleLong");
        
    py::class_<BridgeProp,CoupleProp>(m, "BridgeProp");
    py::class_<CrosslinkProp,CoupleProp>(m, "CrosslinkProp");
    py::class_<DuoProp,CoupleProp>(m, "DuoProp");
    py::class_<ForkProp,CoupleProp>(m, "ForkProp");
    py::class_<ShackleProp,CoupleProp>(m, "ShackleProp");        
            
    py::class_<CoupleSet,ObjectSet>(m, "CoupletSet")
		.def("__getitem__",[](CoupleSet * set, int i) {
				int s = set->size();
                if (i<0) {i+=s;} // Python time negative indexing
				if (i >= s or i<0) {
					 throw py::index_error();
				}
				Couple * obj = set->firstID();
				while (i) {
					--i; // I know this is slow, but ...
					obj = set->nextID(obj); // Maybe objectSet should derive from std::vect ?
				}
				return obj;
             }, PYREF);
}

