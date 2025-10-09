#include <pybind11/pybind11.h>
#include "python_utilities.h"
namespace py = pybind11;

void load_interface_classes(py::module_ &m) {
    /// Python interface to cytosim
    py::class_<Interface>(m, "Interface","an interface to cytosim")
        .def("hold", &Interface::hold)    
        .def("execute_new",  [](Interface * inter, std::string &cat, std::string &name, std::string opt, int cnt   )  { // @PYD;C:Interface;T: adds objects to simulation, see provided examples 
            Glossary glos = Glossary(opt);
            return inter->execute_new(cat, name, glos, static_cast<size_t>(cnt) );
        }, PYOWN)
        .def("execute_run",  [](Interface * inter, int many, std::string & how, bool strict) { // @PYD;C:Interface;T: runs simulation a given number of steps, see provided examples 
            Glossary glos = Glossary(how);
            return inter->execute_run(many, glos,strict);}, PYREF )
        .def("execute_set",  [](Interface * inter, std::string & cat, std::string & name, std::string & how) { // @PYD;C:Interface;T: defines objects to simulation, see provided examples 
            Glossary glos = Glossary(how);
            return inter->execute_set(cat, name, glos);
        }, PYREF)
        .def("execute_change",  [](Interface * inter, std::string & name, std::string & how, bool strict) { // @PYD;C:Interface;T: changes objects properties in  simulation, see provided examples 
            Glossary glos = Glossary(how);
            return inter->execute_change(name, glos, strict); }, PYREF)
        .def("execute_cut",  [](Interface * inter, std::string & name, std::string & where, int cnt) { // @PYD;C:Simul;T: performes a cut : sim.cut(filament_name, where), see Parser.execute_cut  (C++)
            Glossary glos = Glossary(where);
            inter->execute_cut(name, glos, static_cast<size_t>(cnt));
            })
        .def("execute_delete",  [](Interface * inter, std::string & name, std::string & how, int number) { // @PYD;C:Simul;T: deletes objects from simulation, see provided examples
            Glossary glos = Glossary(how);
            inter->execute_delete(name, glos, number);
            })
        .def("execute_import",  [](Interface * inter, std::string & file, std::string & what, std::string & how) { // @PYD;C:Simul;T: imports objects from text file, see provided examples
            Glossary glos = Glossary(how);
            inter->execute_import(file, what, glos);
            })
        .def("execute_export",  [](Interface * inter, std::string & file, std::string & what, std::string & how) { // @PYD;C:Simul;T: export objects to text file, see provided examples
            Glossary glos = Glossary(how);
            inter->execute_export(file, what, glos);
            })
       ;           
         
    py::class_<Parser,Interface>(m, "Parser","a cytosim parser")
        .def("evaluate", [](Parser &p, std::string& str) {return p.evaluate(str);} );
        
    py::class_<PythonParser,Parser>(m, "PythonParser","Python interface to a parser")
        .def("add", &PythonParser::add, PYMOV)    // @PYD;C:PythonParser;T: adds objects to simulation
        .def("run", &PythonParser::run, PYREF)    // @PYD;C:PythonParser;T: runs the simulation
        .def("set", &PythonParser::set, PYREF)    // @PYD;C:PythonParser;T: sets a new property
        .def("change", &PythonParser::change, PYREF)    // @PYD;C:PythonParser;T: changes an existing property
        .def_readwrite("simul", &PythonParser::sim)
        .def_readwrite("thread", &PythonParser::thread, PYREF)
        .def("once", &PythonParser::once) // @PYD;C:PythonParser;T: runs the simulation for a single timestep, without 'prepare'
        .def("load", &PythonParser::load)
        .def("frame", &PythonParser::frame, PYMOV)
        .def("next", &PythonParser::next)    
        .def("save", [](PythonParser & pyparse) { // @PYD;C:PythonParser;T: saves current state to trajectory file
            pyparse.sim->writeObjects(pyparse.sim->prop.system_file,pyparse.is_saved,1);
            if (!pyparse.is_saved) {pyparse.is_saved = 1;};
            pyparse.sim->writeProperties(1);
        });
    
    ///  Python interface to timeframe : behaves roughly as a Python dict of ObjectGroup
    py::class_<Frame>(m, "Timeframe","Python interface to timeframe : behaves as a Python dictionary of Objectsets")
        .def_readwrite("fibers", &Frame::fibers, PYREF) // @PYD;C:Frame;T: a dictionnary of all fiber types in the simulation
        .def_readwrite("solids", &Frame::solids, PYREF) // @PYD;C:Frame;T: a dictionnary of all solid types in the simulation
        .def_readwrite("beads", &Frame::beads, PYREF) // @PYD;C:Frame;T: a dictionnary of all bead types in the simulation
        .def_readwrite("spheres", &Frame::spheres, PYREF) // @PYD;C:Frame;T: a dictionnary of all sphere types in the simulation
        .def_readwrite("organs", &Frame::organs, PYREF) // @PYD;C:Frame;T: a dictionnary of all organizer types in the simulation
        .def_readwrite("spaces", &Frame::spaces, PYREF) // @PYD;C:Frame;T: a dictionnary of all space types in the simulation
        .def_readwrite("couples", &Frame::couples, PYREF) // @PYD;C:Frame;T: a dictionnary of all couple types in the simulation
        .def_readwrite("singles", &Frame::singles, PYREF) // @PYD;C:Frame;T: a dictionnary of all single types in the simulation
        .def_readwrite("time", &Frame::time) // @PYD;C:Frame;T: Current simulation time
        .def_readwrite("simul", &Frame::simul) // @PYD;C:Frame;T: The simulation object
        .def_readwrite("index", &Frame::index) // @PYD;C:Frame;T: The index of the current frame
        .def_readwrite("loaded", &Frame::loaded) // @PYD;C:Frame;T: whether a frame is loaded
        .def("update", &Frame::update) // @PYD;C:Frame;T: updates the frame with the current simulation state
        .def("__iter__", [](Frame &f) {
            return py::make_iterator(f.objects.begin(), f.objects.end());
        }, py::keep_alive<0, 1>())
        .def("keys", [](Frame &f) {  return f.objects.attr("keys")() ; })
        .def("items", [](Frame &f) { return f.objects.attr("items")() ; })
        .def("__getitem__",[](const Frame &f, std::string s) {
                 return f.objects[py::cast(s)];
             }, PYREF);

}
