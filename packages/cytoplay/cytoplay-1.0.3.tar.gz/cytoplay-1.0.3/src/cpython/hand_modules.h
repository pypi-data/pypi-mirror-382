#include "hand.h"
#include "fiber.h"
#include "motor.h"
#include <pybind11/pybind11.h>
#include "python_utilities.h"

#include "actor.h"
#include "chewer.h"
#include "cutter.h"
#include "dynein.h"
#include "kinesin.h"
#include "myosin.h"
#include "mighty.h"
#include "nucleator.h"
#include "regulator.h"
#include "rescuer.h"
#include "slider.h"
#include "tracker.h"
#include "walker.h"

#include "actor_prop.h"
#include "chewer_prop.h"
#include "cutter_prop.h"
#include "dynein_prop.h"
#include "kinesin_prop.h"
#include "myosin_prop.h"
#include "mighty_prop.h"
#include "nucleator_prop.h"
#include "regulator_prop.h"
#include "rescuer_prop.h"
#include "slider_prop.h"
#include "tracker_prop.h"
#include "walker_prop.h"

namespace py = pybind11;

class Hand;
class FiberSite;
class Object;

/// a utility to enrich the cytosim python module
void load_hand_classes(py::module_ &m) {
     /// Python interface to couple
    py::class_<FiberSite>(m,"FiberSite")
        .def("FiberSite", [](Fiber * fib, real a) {return FiberSite(fib, a);}, PYOWN)
        .def("clear", &FiberSite::clear)
        .def("lattice", &FiberSite::lattice, PYREF)
#if FIBER_HAS_LATTICE
        .def("lati_t", &FiberSite::lati_t)
        .def("setAbscissa", &FiberSite::setAbscissa)
        .def("engageLattice", &FiberSite::engageLattice)
#endif       
        .def("moveTo",  [](FiberSite * h, real a) {return h->moveTo(a);})
        .def("relocateM",  [](FiberSite * h) {return h->relocateM();})
        .def("relocateP",  [](FiberSite * h) {return h->relocateP();})
        .def("unattached",  [](FiberSite * h) {return h->unattached();})
        .def("attached",  [](FiberSite * h) {return h->attached();})
        .def("fiber",  [](FiberSite * h) {return h->fiber();})
        .def("position",  [](FiberSite * h) {return to_numpy(h->pos());}, PYOWN)
        .def("posHand",  [](FiberSite * h, real x) {return to_numpy(h->posHand(x));}, PYOWN)
        .def("direction",  [](FiberSite * h) {return to_numpy(h->dir());}, PYOWN) // direction because dir has a python meaning
        .def("dirFiber",  [](FiberSite * h) {return to_numpy(h->dirFiber());}, PYOWN)
        .def("abscissa",  [](FiberSite * h) {return h->abscissa();})
        .def("abscissaFromM",  [](FiberSite * h) {return h->abscissaFromM();})
        .def("abscissaFromP",  [](FiberSite * h) {return h->abscissaFromP();})
        .def("abscissaFrom",  [](FiberSite * h, int end) {return h->abscissaFrom(static_cast<FiberEnd>(end));})
        .def("nearestEnd",  [](FiberSite * h) {return static_cast<int>(h->nearestEnd());})
        .def("distanceToEnd",  [](FiberSite * h, int end) {return h->distanceToEnd(static_cast<FiberEnd>(end));});
        
    py::class_<Hand,FiberSite>(m, "Hand")
        .def("next",  [](Hand * h) {return  h->next();}, PYREF)
        .def("prev",  [](Hand * h) {return h->prev();}, PYREF)
        .def("unbindingPositions",  [](Hand * h) {return to_numpy(h->unbindingPosition());}, PYOWN)
        .def("relocate",  &Hand::relocate)
        .def("property",  [](Hand * h) {return h->property();})
        .def("relocate",  [](Hand * h, Fiber * fib, real a) {return h->relocate(fib,a);})
        .def("moveToEnd",  [](Hand * h, int end) {return h->moveToEnd(static_cast<FiberEnd>(end));})
        .def("keysMatch",  &Hand::keysMatch)
        .def("monitor", &Hand::monitor, PYREF)
        .def("otherHand",  [](Hand * h) {return h->otherHand();}, PYREF)
        .def("attachmentAllowed",  &Hand::attachmentAllowed)
        .def("attach",  [](Hand * h, FiberSite & fs) {return h->attach(fs);})
        .def("detach",  [](Hand * h) {return h->detach();})
        .def("stepUnattached",  [](Hand * h, Simul& sim, pyarray pos) {auto p = to_vector(pos) ; return h->stepUnattached(sim, p);})
        .def("stepUnloaded", &Hand::stepUnloaded)
        .def("stepLoaded",  [](Hand * h, pyarray force) {auto f = to_vector(force) ; return h->stepLoaded(f);})
        .def("handleDisassemblyM", &Hand::handleDisassemblyM)
        .def("handleDisassemblyP", &Hand::handleDisassemblyP)
        .def("checkFiberRange", &Hand::checkFiberRange)
        .def("attach",  [](Hand * h, Fiber * fib, real a,  int end) {return h->attach(fib, a, static_cast<FiberEnd>(end));})
        .def("attachEnd",  [](Hand * h, Fiber * fib, int end) {return h->attachEnd(fib, static_cast<FiberEnd>(end));})
        .def("detachHand", &Hand::detachHand)
        .def("attachTo",  [](Hand * h, Fiber * fib, real a) {return h->attachTo(fib, a);})
        .def("attachTo",  [](Hand * h, Fiber * fib, real a,  int end) {return h->attachTo(fib, a, static_cast<FiberEnd>(end));})
        .def("attachToEnd",  [](Hand * h, Fiber * fib, int end) {return h->attachToEnd(fib, static_cast<FiberEnd>(end));})
        .def("valLattice",  [](Digit * h, int site) {return h->valLattice(static_cast<FiberLattice::lati_t>(site));})
#if FIBER_HAS_LATTICE
        .def("valLattice",  [](Digit * h, FiberLattice * lat, int site) 
            {return h->valLattice(lat, static_cast<FiberLattice::lati_t>(site));})
#endif        
        .def("incLattice",  &Hand::incLattice)
        .def("decLattice",  &Hand::decLattice)
        .def("hopLattice",  [](Digit * h, int site) {return h->hopLattice(static_cast<FiberLattice::lati_t>(site));})
        .def("linkStiffness",  [](Hand * h) {return h->linkStiffness();})
        .def("linkFoot",  [](Hand * h) {return to_numpy(h->linkFoot());}, PYOWN)
        /* 
         These should be in FiberSite, but there might be some memory issue
        */
        .def("moveTo",  [](Hand * h, real a) {return h->moveTo(a);})
        .def("relocateM",  [](Hand * h) {return h->relocateM();})
        .def("relocateM",  [](Hand * h) {return h->relocateM();})
        .def("relocateP",  [](Hand * h) {return h->relocateP();})
        .def("unattached",  [](Hand * h) {return h->unattached();})
        .def("attached",  [](Hand * h) {return h->attached();})
        .def("interpolation",  &Hand::interpolation, PYREF)
        .def("fiber",  [](Hand * h) {return h->fiber();}, PYREF)
        .def("position",  [](Hand * h) {return to_numpy(h->pos());}, PYOWN)
        .def("direction",  [](Hand * h) {return to_numpy(h->dir());}, PYOWN) // direction because dir has a python meaning
        .def("dirFiber",  [](Hand * h) {return to_numpy(h->dirFiber());}, PYOWN)
        .def("abscissa",  [](Hand * h) {return h->abscissa();})
        .def("abscissaFromM",  [](Hand * h) {return h->abscissaFromM();})
        .def("abscissaFromP",  [](Hand * h) {return h->abscissaFromP();})
        .def("abscissaFrom",  [](Hand * h, int end) {return h->abscissaFrom(static_cast<FiberEnd>(end));})
        .def("nearestEnd",  [](Hand * h) {return static_cast<int>(h->nearestEnd());})
        .def("distanceToEnd",  [](Hand * h, int end) {return h->distanceToEnd(static_cast<FiberEnd>(end));});
         
    /// Specialized hand classes
    py::class_<Actor,Hand>(m, "Actor");
    py::class_<Chewer,Hand>(m, "Chewer");
    py::class_<Cutter,Hand>(m, "Cutter")
        .def("cut", &Cutter::cut);
    py::class_<Digit,Hand>(m, "Digit")
#if !FIBER_HAS_LATTICE
        .def("site", &Digit::site)
        .def("abscissa",  [](Digit * h,  int site) {return h->abscissa_(static_cast<FiberLattice::lati_t>(site));})    
#endif
        .def("outsideMP",  [](Digit * h,  int site) {return h->outsideMP(static_cast<FiberLattice::lati_t>(site));})    
        .def("belowM",  [](Digit * h,  int site) {return h->belowM(static_cast<FiberLattice::lati_t>(site));})    
        .def("aboveP",  [](Digit * h,  int site) {return h->aboveP(static_cast<FiberLattice::lati_t>(site));})   
        .def("outsideMP",  [](Digit * h, int site) {return h->outsideMP(static_cast<FiberLattice::lati_t>(site));})
        .def("attachmentAllowed", &Digit::attachmentAllowed)
        .def("attach", &Digit::attach)
        .def("detach", &Digit::detach)
        .def("jumpTo",  [](Digit * h,  int site) {return h->jumpTo(static_cast<FiberLattice::lati_t>(site));})    
        .def("stepP", &Digit::stepP)
        .def("stepM", &Digit::stepM)
        .def("jumpP", &Digit::jumpP)
        .def("jumpM", &Digit::jumpM)
        .def("crawlP", &Digit::crawlP)
        .def("crawlM", &Digit::crawlM)
        .def("stepUnloaded", &Digit::stepUnloaded)
        .def("stepLoaded",  [](Digit * d, pyarray force) {auto f = to_vector(force) ; return d->stepLoaded(f);})
        .def("engageLattice", &Digit::engageLattice);

    py::class_<Dynein,Digit>(m, "Dynein");
    py::class_<Kinesin,Digit>(m, "Kinesin");
    py::class_<Mighty,Hand>(m, "Mighty");
    py::class_<Motor,Hand>(m, "Motor");
    py::class_<Myosin,Digit>(m, "Myosin");
    py::class_<Nucleator,Hand>(m, "Nucleator");
    //    .def("createFiber", [](Nucleator * h, Simul& sim, pyarray pos, FiberProp * prop, std::string & how) {
    //        Vector p = to_vector(pos);
    //        Glossary glos = Glossary(how);
    //        return h->createFiber(sim, p, prop, glos);}, PYOWN);
    py::class_<Regulator,Hand>(m, "Regulator");
    py::class_<Rescuer,Hand>(m, "Rescuer");
    py::class_<Slider,Hand>(m, "Slider");
    py::class_<Tracker,Hand>(m, "Tracker");
    py::class_<Walker,Digit>(m, "Walker");
    //.def("setDirectionality", &Walker::setDirectionality);
      
    py::class_<HandProp,Property>(m, "HandProp")
        .def_readwrite("binding_rate", &HandProp::binding_rate)
        .def_readwrite("binding_range", &HandProp::binding_range)
        .def_readwrite("binding_key", &HandProp::binding_key)
        .def_readwrite("unbinding_rate", &HandProp::unbinding_rate)
        //.def("unbinding_rate", [](HandProp *  hp) {return to_numpy_raw(hp->unbinding_rate,2,1);}, PYOWN)
        .def_readwrite("unbinding_force", &HandProp::unbinding_force)
        .def_readwrite("bind_also_end", &HandProp::bind_also_end)
        .def_readwrite("bind_end_range", &HandProp::bind_end_range)
        //.def("hold_growing_end", [](HandProp * hp)::hold_growing_end)
        //.def_readwrite("hold_shrinking_end", &HandProp::hold_shrinking_end)
        .def_readwrite("activity", &HandProp::activity)
        .def_readwrite("display", &HandProp::display);
        
    py::class_<ActorProp,HandProp>(m, "ActorProp");
	
    py::class_<ChewerProp,HandProp>(m, "ChewerProp")
        .def_readwrite("chewing_speed", &ChewerProp::chewing_speed)
        .def_readwrite("line_diffusion", &ChewerProp::line_diffusion);
        
    py::class_<CutterProp,HandProp>(m, "CutterProp")
        .def_readwrite("cutting_rate", &CutterProp::cutting_rate)
        .def("new_end_state",  [](CutterProp * prop) {return to_numpy_raw(prop->new_end_state, 1, 2); }, PYOWN);
        
    py::class_<DigitProp,HandProp>(m, "DigitProp")
        .def_readwrite("step_size", &DigitProp::step_size)
        .def_readwrite("footprint", &DigitProp::footprint)
        .def_readwrite("site_shift", &DigitProp::site_shift);

    py::class_<DyneinProp,DigitProp>(m, "DyneinProp");
	
    py::class_<KinesinProp,DigitProp>(m, "KinesinProp");
	
    py::class_<MightyProp,HandProp>(m, "MightyProp")
        .def_readwrite("stall_force", &MightyProp::stall_force)
        .def_readwrite("unloaded_speed", &MightyProp::unloaded_speed)
        .def_readwrite("limit_speed", &MightyProp::limit_speed);
        
    py::class_<MyosinProp,DigitProp>(m, "MyosinProp");
    
    auto nucProp = py::class_<NucleatorProp,HandProp>(m, "NucleatorProp")
        //.def_readwrite("nucleation_rate", &NucleatorProp::nucleation_rate)
        .def("nucleation_rate",  [](NucleatorProp * p) {return to_numpy_raw(p->nucleation_rate, 1, 2);}, PYOWN)
        .def_readwrite("fiber_type", &NucleatorProp::fiber_type)
        .def_readwrite("fiber_spec", &NucleatorProp::fiber_spec)
        .def_readwrite("branch_angle", &NucleatorProp::branch_angle)
        .def_readwrite("branch_direction", &NucleatorProp::branch_direction)
        .def_readwrite("hold_end", &NucleatorProp::hold_end)
        .def_readwrite("track_end", &NucleatorProp::track_end)
        .def_readwrite("addictive", &NucleatorProp::addictive);
        
    py::enum_<NucleatorProp::BranchSpecificity>(nucProp,"BranchSpecificity")
            .value("BRANCH_PARALLEL", NucleatorProp::BranchSpecificity::BRANCH_PARALLEL)
            .value("BRANCH_MOSTLY_PARALLEL", NucleatorProp::BranchSpecificity::BRANCH_MOSTLY_PARALLEL)
            .value("BRANCH_RANDOM", NucleatorProp::BranchSpecificity::BRANCH_RANDOM)
            .value("BRANCH_SPECIFIED", NucleatorProp::BranchSpecificity::BRANCH_SPECIFIED)
            .export_values();

    py::class_<RegulatorProp,HandProp>(m, "RegulatorProp")
        .def_readwrite("rate", &RegulatorProp::rate)
        .def_readwrite("rate_dt", &RegulatorProp::rate_dt);
        
    py::class_<RescuerProp,HandProp>(m, "RescuerProp")
        .def_readwrite("rescue_chance", &RescuerProp::rescue_chance);
        
    py::class_<SliderProp,HandProp>(m, "SliderProp")
        .def_readwrite("movability", &SliderProp::movability)
        .def_readwrite("line_diffusion", &SliderProp::line_diffusion)
        .def_readwrite("stiffness", &SliderProp::stiffness);
        
    py::class_<TrackerProp,HandProp>(m, "TrackerProp")
        .def_readwrite("track_end", &TrackerProp::track_end)
        .def_readwrite("bind_only_growing_hand", &TrackerProp::bind_only_growing_end);
        
    py::class_<WalkerProp,DigitProp>(m, "WalkerProp")
        .def_readwrite("stall_force", &WalkerProp::stall_force)
        .def_readwrite("unloaded_speed", &WalkerProp::unloaded_speed)
        .def_readwrite("unbinding_chance", &WalkerProp::unbinding_chance)
        .def("checkStiffness", &WalkerProp::checkStiffness);
     
    py::class_<MotorProp,HandProp>(m, "MotorProp")
        .def_readwrite("stall_force", &MotorProp::stall_force)
        .def_readwrite("unloaded_speed", &MotorProp::unloaded_speed)
        .def_readwrite("limit_speed", &MotorProp::limit_speed)
        .def("checkStiffness", &MotorProp::checkStiffness);
        
}

