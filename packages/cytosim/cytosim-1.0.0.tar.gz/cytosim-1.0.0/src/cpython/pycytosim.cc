// Cytosim was created by Francois Nedelec. Copyright 2007-2017 EMBL.
#include "pycytosim.h"

namespace py = pybind11;
//void gonna_callback(void) {};

/**
 * @brief Open the simulation from the .cmo files
 * @return 
 */
 
/// Opens an existing simulation and returns a parser
/**
 * @brief Opens an existing simulation in the current folder
 
  [python]>>> `import pycytosim3D as ct` \n
  [python]>>> `parser = ct.open()` \n

 * @return Parser 

 
 @ingroup PyCytosim
 */ 
PythonParser * open()
{   
    
    int verbose = 1;
    int prefix = 0;
    
    Glossary arg;

    
    std::string str;

    Simul * sim = new Simul;
    std::string input = Simul::TRAJECTORY;
    unsigned period = 1;

    arg.set(input, ".cmo") || arg.set(input, "input");    
    if ( arg.use_key("-") ) verbose = 0;

    PythonParser * pyParse = new PythonParser(*sim);

    try
    {
        RNG.seed();
        sim->loadProperties();
        pyParse->activate(input);
        Cytosim::silent();
        
    }
    catch( Exception & e )
    {
        std::clog << "Aborted: " << e.what() << '\n';
        return nullptr;
    }

    return pyParse;
}

/// Starts a new simulation and returns a parser
/**
 * @brief Starts a new simulation
 
  [python]>>> `import pycytosim3D as ct` \n
  [python]>>> `parser = ct.start("example.cym")` \n

 * @param String : Config file name
 * @return Parser 

 
 @ingroup PyCytosim
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
    
    Simul * simul = new Simul;
    
    try {
        //simul->initialize(arg);
        simul->prop.read(arg);
        simul->initCytosim();
    }
    catch( Exception & e ) {
        print_magenta(stderr, e.brief());
        std::cerr << '\n' << e.info() << '\n';
    }
    catch(...) {
        print_red(stderr, "Error: an unknown exception occurred during initialization\n");
    }
    
    PythonParser * pyParse = new PythonParser(*simul);
    pyParse->activate();
    
    return pyParse;
}

/**
 * @brief A python module to run or play cytosim
 * @return 
 */
#if DIM==1
PYBIND11_MODULE(cytosim1D, m) {
#elif DIM==2
PYBIND11_MODULE(cytosim2D, m) {
#elif DIM==3
PYBIND11_MODULE(cytosim3D, m) {
#endif

    m.doc() = 
				"A python module to simulate cytoskeleton mechanics. \n"
                "Visit https://gitlab.com/f-nedelec/cytosim for information";
    
    prepare_module(m);  
    
    /// Opens the simulation from *.cmo files
    m.def("open", &open, "@PYD;C:PyCytosim;T:loads simulation from object files", PYREF);
    m.def("start", &start, "@PYD;C:PyCytosim;T:loads simulation from config files", PYREF);
    
}

