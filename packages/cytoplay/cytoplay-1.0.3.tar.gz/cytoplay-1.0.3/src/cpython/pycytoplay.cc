// Cytosim was created by Francois Nedelec. Copyright 2007-2017 EMBL.
#include "pycytosim.h"

#include "opengl.h"
#include "player.h"
#include "view.h"
#include "gle.h"
#include <pybind11/functional.h>
#include <thread>
namespace py = pybind11;

Player player;
Simul&      simul = player.simul;
SimThread & thread = player.worker;
SimThread & worker = player.worker;
/// Using global vars, sorry not sorry.
PlayerProp&  prop = player.prop;
DisplayProp& disp = player.disp;


#  include "glut.h"
#  include "glapp.h"
#  include "fiber_prop.h"
#  include "fiber_disp.h"
#  include "point_disp.h"
using glApp::flashText;
#  include "play_keys.cc"
#  include "play_menus.cc"
#  include "play_mouse.cc"

//extern Simul simul;
extern SimThread & thread;
extern Player player;
extern SimThread & worker;
extern PlayerProp& prop;
extern DisplayProp& disp;

/// A holder for normalKey callback
inline std::function<unsigned char(unsigned char, int, int)>& normalKey()
{
    // returns a different object for each threadthread that calls it
    static thread_local std::function<unsigned char(unsigned char, int, int)> fn;
    return fn;
}
/// A proxy for the normalKeyy callback
inline void proxyNormalKey(unsigned char c, int i, int j){ c = normalKey()(c, i ,j ); processNormalKey(c,i,j); };

inline std::function<int(int, int, const Vector3&, int)>& mouseClick()
{
    // returns a different object for each thread that calls it
    static thread_local std::function<int(int, int, const Vector3&, int)> mc;
    return mc;
}
/// A proxy for the normalKeyy callback
inline void proxyMouseClick(int i, int j, const Vector3& v, int k){int c = mouseClick()(i ,j, v, k );
    processMouseClick(i,j,v,c); };

/// A holder for runtime callback
inline std::function<void(Simul&)>& runtimeCheck()
{
    // returns a different object for each thread that calls it
    static thread_local std::function<void(Simul&)> rt;
    return rt;
}

/// 
void byebye()
{
    worker.cancel_join();
}

/// minimalistic display function
void drawMag(View& view)
{
    //std::clog << " drawMag(" << std::setprecision(3) << simul.time() << "s)\n";
    view.clearPixels();
    view.loadView();
    view.setLights();
    view.setClipping();
    player.setPixelSize(view);
    player.drawCytosim();
    view.endClipping();
}

/// Displays the simulation live
int displayLive(View& view)
{
    // Also adds a callback to an external function through caller->runtimeCheck
    if ( 0 == thread.trylock() )
    {
        // read and execute commands from incoming pipe:
        thread.read_input();
        //thread.debug("display locked");
        if ( simul.prop.display_fresh )
        {
            player.readDisplayString(view, simul.prop.display);
            simul.prop.display_fresh = false;
        }
        
        player.prepareDisplay(view);
        player.drawSystem(view);
        //player.drawCytosim();
        
        // external callback
        runtimeCheck()(simul);
        thread.unlock();
        
    }
    else
    {
        // thread.debug("display: trylock failed");
        glutPostRedisplay();
    }
    return 0;
}

/// Opens an existing simulation and returns a parser
/**
 * @brief Opens an existing simulation in the current folder
 
  [python]>>> `import pycytoplay3D as ct` \n
  [python]>>> `parser = ct.open()` \n

 * @return Parser 

 
 @ingroup PyCytoplay
 */ 
PythonParser * open()
{   
    
    int verbose = 1;
    int prefix = 0;
    
    Glossary arg;

    std::string input = Simul::TRAJECTORY;
    std::string str;

    //Simul * sim = new Simul;
    
    unsigned period = 1;

    arg.set(input, ".cmo") || arg.set(input, "input");    
    if ( arg.use_key("-") ) verbose = 0;

    PythonParser * pyParse = new PythonParser(simul);

    try
    {
        RNG.seed();
        simul.loadProperties();
        pyParse->activate(input, &thread);
        Cytosim::silent();
        
    }
    catch( Exception & e )
    {
        std::clog << "Aborted: " << e.what() << '\n';
        return nullptr;
    }
	
    
    // Default null callbacks
    normalKey() = [](unsigned char c, int i, int j) {return c;} ;
    mouseClick() = [](int i, int j, const Vector3 v, int k) {return k;} ;
    runtimeCheck() = [](Simul& sim) {};
    
    
    return pyParse;
}

/// Starts a new simulation and returns a parser
/**
 * @brief Starts a new simulation
 
  [python]>>> `import pycytoplay3D as ct` \n
  [python]>>> `parser = ct.start("example.cym")` \n

 * @param String : Config file name
 * @return Parser 

 
 @ingroup PyCytoplay
 */ 
PythonParser * start(std::string fname)
{
    Glossary arg;
    arg.read_string(fname.c_str(), 2);
    
    if ( ! arg.use_key("+") )
    {
        Cytosim::out.open("messages.cmo");
        Cytosim::log.redirect(Cytosim::out);
        Cytosim::warn.redirect(Cytosim::out);
    }
        
    try {
        simul.prop.read(arg);
        simul.initCytosim();
    }
    catch( Exception & e ) {
        print_magenta(stderr, e.brief());
        std::cerr << '\n' << e.info() << '\n';
    }
    catch(...) {
        print_red(stderr, "Error: an unknown exception occurred during initialization\n");
    }
    
    std::string file = simul.prop.config_file;
    std::string setup = file;
    
    PythonParser * pyParse = new PythonParser(simul);
    pyParse->activate(&thread);
    
   
    // Default null callbacks
    normalKey() = [](unsigned char c, int i, int j) {return c;} ;
    mouseClick() = [](int i, int j, const Vector3 v, int k) {return k;} ;
    runtimeCheck() = [](Simul& sim) {};
    
    return pyParse;
}

void print_error(Exception const& e)
{
    print_magenta(stderr, e.brief());
    fputs(e.info().c_str(), stderr);
    putc('\n', stderr);
}

void play_default(std::string opt){
//#ifdef __APPLE__
#if (1)
    int argc = 1 ;
    char * str1 = (char*) malloc(10);
    strcpy(str1," ");
    char ** test = &str1;
    glutInit(&argc, test);
#endif
    Glossary arg = Glossary(opt);
    std::string name = "PyCytoplay     ";
    glApp::setDimensionality(DIM);
    if ( arg.use_key("fullscreen") )
        glApp::toggleFullScreen();
    //View& view = glApp::views[0];
    
    int menu = 1;
    arg.set(menu, "menu");
    int fullscreen = 0;
    if ( arg.use_key("fullscreen") )
        fullscreen = 1;
#if HEADLESS_PLAYER
    View view("*", DIM==3);
    view.setDisplayFunc(displayLive);
#else
    glApp::setDimensionality(DIM);
    View& view = glApp::views[0];
#endif    
    view.read(arg);
    disp.read(arg);
    simul.prop.read(arg);
    //view.setDisplayFunc(displayLive);
    // Definining the callbacks
    glApp::actionFunc(proxyMouseClick);
    glApp::actionFunc(processMouseDrag);
    glApp::normalKeyFunc(proxyNormalKey);
    //glApp::createWindow(displayLive);
    glApp::newWindow(name.c_str(), displayLive, drawMag);

    try
    {
        gle::initialize();
        player.setStyle(disp.style);
        if ( menu )
            buildMenus();
        if ( fullscreen )
            glutFullScreen();
        glutTimerFunc(100, timerCallback, 0);
    }
    catch ( Exception & e )
    {
        print_error(e);
        return ;
    }
    
    size_t frm = 0;
    bool has_frame = false;

    try
    {
        seed_pcg32();
        RNG.seed(pcg32());
        has_frame = arg.set(frm, "frame");
    }
    catch( Exception & e )
    {
        print_error(e);
        return ;
    }
    
    if ( player.goLive )
    {
        worker.period(prop.period);
        try
        {
            if ( has_frame )
                worker.prolong();
            else
                worker.start();
        }
        catch( Exception & e )
        {
            print_error(e);
            return ;
        }
    }

    std::atexit(byebye);
    //start the GLUT event handler:
    glutMainLoop();
}

/// Simulate and displays a simulation
/**
 * @brief  Simulate and displays a simulation
 
  [python]>>> `import pycytoplay3D as ct` \n
  [python]>>> `parser = ct.start("example.cym")` \n
  [python]>>> `ct.play()` \n

 * @param Strings : any number of options
 * @return Parser 

 
 @ingroup PyCytoplay
 */ 
void play(py::args args) {
    int nargs = args.size();
    if (nargs == 0) { play_default("")  ; }
    else {
        std::string opt;
        for (auto arg : args) {
            opt += py::cast<std::string>(arg);
            }
        std::cout << opt << std::endl;
        play_default(opt);
    }
};

/// Sets the callback function for a normal key
/**
 * @brief  Sets the callback function for a normal key
 
  See the provided examples.

 * @param function(i,j,key)->key   [with k the key being pressed]

 @ingroup PyCytoplay
 */ 
void setNormalKey(py::function f) { 
    normalKey() = py::cast<std::function<unsigned char(unsigned char, int, int)>>(f);
}

/// Sets the callback function for runtime check
/**
 * @brief  Sets the callback function for runtime check
 
  See the provided examples.

 * @param function(simul)

 @ingroup PyCytoplay
 */ 
void setRuntimeCheck(py::function f) { 
    runtimeCheck() = py::cast<std::function<void(Simul&)>>(f);
}

/// Sets the callback function for mouseclicks
/**
 * @brief  Sets the callback function for mouseclicks
 
  See the provided examples. 

 * @param function(i,j,v,k)  [with v the mouse coordinates]

 @ingroup PyCytoplay
 */ 
void setMouseClick(py::function f) { 
    mouseClick() = py::cast<std::function<int(int, int, Vector3, int)>>(f);
}

/// A python module to run or play cytosim
#if DIM==1
PYBIND11_MODULE(cytoplay1D, m) {
#elif DIM==2
PYBIND11_MODULE(cytoplay2D, m) {
#elif DIM==3
PYBIND11_MODULE(cytoplay3D, m) {
#endif

    m.doc() =   "A python module to simulate cytoskeleton mechanics. \n"
                "Visit https://gitlab.com/f-nedelec/cytosim for information"; 
                 
    prepare_module(m);

    /// Python interface to play/start a simulation
    m.def("open", &open, PYREF); // @PYD;C:PyCytoplay;T:loads simulation from object files
    m.def("start", &start, PYREF); // @PYD;C:PyCytoplay;T:loads simulation from config files
    m.def("play", &play, py::call_guard<py::gil_scoped_release>()); // @PYD;C:PyCytoplay;T: plays a simulation in live"
        
    m.def("setNormalKey", &setNormalKey); // @PYD;C:PyCytoplay;T: sets the callback function for normal keys
    m.def("setRuntimeCheck",&setRuntimeCheck);  // @PYD;C:PyCytoplay;T: sets the callback function for runtime checks
    m.def("setMouseClick", &setMouseClick);  // @PYD;C:PyCytoplay;T: sets the callback function for mouse clicks
    

}



