#ifndef PYTHON_FRAME_H
#define PYTHON_FRAME_H

#include <fstream>
#include <sstream>
#include "sim_thread.h"
#include "stream_func.h"
#include "iowrapper.h"
#include "glossary.h"
#include "messages.h"
#include "organizer.h"
#include "parser.h"
#include "simul.h"
#include "simul_prop.h"
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "python_utilities.h"
namespace py = pybind11;

class Simul;
class SimulProp;
class Organizer;

void void_callback(void) {};

/**
 @defgroup PyCytosim PyCytosim
  * @brief A group of classes and functions to facilitate usage of cytosim in python 
  
  A group of classes and functions to facilitate usage of cytosim in python
   
 */
 
/**
 @defgroup PyCytoplay PyCytoplay
  * @brief A group of classes and functions to facilitate usage of cytosim in python 
  
  A group of classes and functions to facilitate usage of cytosim in python.
  PyCytoplay is a super-set of PyCytosim with a graphical interface.

  It is mostly experimental !
   
 */ 

/**
 @defgroup PyUtilities Utilities
  A group functions to facilitate usage of cytosim in python
   
    @ingroup PyCytosim
 */


/// ObjGroup : a vector of objects of same type having the same property
/** 
 Behaves mostly as a python list of objects of the same type :

[python]>>> `fiber_0 = group[0]` \n
[python]>>> `for fiber in group:  print(fiber.points())`
  
 Also contains a pointer the properties of this group :
  
[python]>>> `prop = group.prop`

 @ingroup PyCytosim
 */
template<typename Obj, typename Prp> 
class ObjGroup : public std::vector<Obj*>{
public:
    /// The property associated to the group's objects
    Prp * prop;
    ObjGroup() = default;
    /// Creator \private
    ObjGroup(Prp * p) : ObjGroup() {prop = p ;};
    ~ObjGroup() = default;
};

/// ObjMap : a map between a string and and ObjGroup  
/** 
 Behaves as a python dictionnary associating a name to an ObjGroup of the same category.
  
[python]>>> `actin_fibers = objmap["actin"]`
  
[python]>>> `microtubules = objmap["microtubules"]`
 @ingroup PyCytosim
 */
template<typename Obj, typename Prp> 
using ObjMap = std::map<std::string,ObjGroup<Obj,Prp>> ;

/// ObjVec : a vec <Obj*>
template<typename Obj> 
using ObjVec = std::vector<Obj*> ;

/// Distribute the objects (pointers) in the groups and in the dict.
template<typename Obj, typename Prp, typename Set> 
void distribute_objects(Simul * sim, py::dict & objects, ObjMap<Obj,Prp> & mappe, Set & set, std::string categ ) {
    // First we list all objects in category, and create the ObjGroups in the map
    PropertyList plist = sim->properties.find_all(categ);
    if (!plist.empty()) {
        for ( Property * i : plist )
            {
                Prp * fp = static_cast<Prp*>(i);
                mappe[fp->name()] = ObjGroup<Obj,Prp>(fp);
            }
        // Then we assign all objects to their groups
        Obj * obj = set.first();
        while (obj) {
            mappe[obj->property()->name()].push_back(obj);
            obj = obj->next();
        }
        // Then we fill the dictionnary
        for (const auto &[name, group] : mappe) {
            objects[py::cast(name)] = group;
        }
        
    }
}
 
/// Distribute the objects (pointers) in the groups and in the dict ; 
// special case for couple, single, where firstID needs to be used
template<typename Obj, typename Prp, typename Set> 
void distribute_objects_wID(Simul * sim, py::dict & objects, ObjMap<Obj,Prp> & mappe, Set & set, std::string categ )
{
    // First we list all objects in category, and create the ObjGroups in the map
    PropertyList plist = sim->properties.find_all(categ);
    if (!plist.empty()) {
        for ( Property * i : plist )
            {
                Prp * fp = static_cast<Prp*>(i);
                mappe[fp->name()] = ObjGroup<Obj,Prp>(fp);
            }
        // Then we assign all objects to their groups
        Obj* obj = set.firstID();
        while (obj) 
       {
            mappe[obj->property()->name()].push_back(obj);
            obj = set.nextID(obj);
        }
        // Then we fill the dictionnary
        for (const auto &[name, group] : mappe) {
            objects[py::cast(name)] = group;
        }
        
    }
}

/// declare_group() : creates a python interface for an ObjGroup
/// Unused for now, but should be used to benefit of pybind11's stl containers interface
template<typename Group, typename Obj>
auto declare_group(py::module &mod, Group group, std::vector<Obj*> gg , std::string name) { 
        py::class_<std::vector<Obj*>  >(mod, ("Vector"+name).c_str(), 
                    "Behaves as a list of objects ");
        return py::class_<Group, std::vector<Obj*>  >(mod, (name+"Group").c_str(),
                    "Behaves as a list of objects with the same properties")
            .def_readwrite("prop",   &Group::prop , PYREF);
}

/// declare_group() : creates a python interface for an ObjGroup
template<typename Group>
auto declare_group(py::module &mod, Group group, std::string name) { 
        return py::class_<Group>(mod, name.c_str(),  "Behaves as a list of objects with the same properties")
            .def("__len__", [](const Group &v) { return v.size(); })
            .def("size", &Group::size)
            .def_readwrite("prop",   &Group::prop , PYREF)
            .def("__iter__", [](Group &v) {
                return py::make_iterator(v.begin(), v.end());
            }, py::keep_alive<0, 1>())
            .def("__getitem__",[](const Group &v, size_t i) {
                int s = v.size();
                if (i<0) {i+=s;} // Python time negative indexing
				if (i >= s or i<0) {
                         throw py::index_error();
                     }
                     return v[i];
                 }, PYREF);
}


/// A python-only class to facilitate the handling of the current state of the simulation
/** 
Frame behaves mostly as a python dictionnary of (name, ObjGroup )
  
 [python]>>> `actin_fibers = frame["actin"]`
  
As a redundant mechanism to find objects, for each type of objects, Frame also contains an ObjMap (dictionary of {type, ObjGroup}).

 [python]>>> `actin_fibers = frame.fibers["actin"]`  \n
 [python]>>> `cells = frame.spaces["cell"]`
   
A frame should be updated after a timestep is run, or when a new Frame is loaded
 
 @ingroup PyCytosim
 */
class Frame 
{
public:
        // ObjMaps are maps of (string,objectgroup)
        
        /// a dictionnary of all Fiber types in the simulation 
        ObjMap<Fiber,FiberProp> fibers;
        
        /// a dictionnary of all Solid types in the simulation 
        ObjMap<Solid,SolidProp> solids;
        
        /// a dictionnary of all Bead types in the simulation 
        ObjMap<Bead,BeadProp> beads;
        
        /// a dictionnary of all Sphere types in the simulation 
        ObjMap<Sphere,SphereProp> spheres;
        
        /// a dictionnary of all Organizer types in the simulation 
        ObjMap<Organizer,Property> organs;
        
        /// a dictionnary of all Space types in the simulation 
        ObjMap<Space,SpaceProp> spaces;
        
        /// a dictionnary of all Couple types in the simulation 
        ObjMap<Couple,CoupleProp> couples;
        
        /// a dictionnary of all Single types in the simulation 
        ObjMap<Single,SingleProp> singles;

        /// Current time
        real time;
        
        /// Index of the timeframe (if loaded from a replay)
        int index;
        
        /// Whether the simulation is loaded from replay
        int loaded;
        
        /// pointer to the current instance of Simul
        Simul * simul;
        
        /// A python dictionary of (name, ObjMap) \private
        py::dict objects;

        /// Default constr and destrc
        Frame(Simul * sim) {
            simul = sim;
            update();
        }
        
        /// Updates the frame to the current state of the simulation
        /**
         * @brief  Updates the simulations objects stored in the frame.
         *
         * This is important if objects have been added or deleted !
         */
        void update() {
            std::vector<std::string> categories = std::vector<std::string>{"aster","nucleus","bundle","fake"};
            
            distribute_objects(simul, objects, fibers, simul->fibers, std::string("fiber") ) ;
            distribute_objects(simul, objects, solids, simul->solids, std::string("solid") ) ;
            distribute_objects(simul, objects, spaces, simul->spaces, std::string("space") ) ;
            distribute_objects(simul, objects, beads, simul->beads, std::string("bead") ) ;
            distribute_objects(simul, objects, spheres, simul->spheres, std::string("sphere") ) ;
            // For organizer, the we have to check the different categories
            for (auto categ : categories) {
                distribute_objects(simul, objects, organs, simul->organizers, std::string(categ) ) ;
            }
            // for couple and single we need to use firstID, nextID
            distribute_objects_wID(simul, objects, couples, simul->couples, std::string("couple") ) ;
            distribute_objects_wID(simul, objects, singles, simul->singles, std::string("single") ) ;
            
            time = simul->time();
            loaded = 1;
        };
        
        
        /// Default constructor \private
        Frame() = default;
        ~Frame() = default;
};

/// A wrapper around Cytosim's Parser to facilitate python interfacing
/** 
 PythonParser is A wrapper around Cytosim's Parser to facilitate python interfacing.
 There should be a single python parser bound to a simulation.
   

 @ingroup PyCytosim
 */
class PythonParser : public Parser
{
public:
    

    /// construct a Parser with given permissions
    PythonParser(Simul& simul) :Parser(&simul,  0, 1, 0, 0, 0, 0) {
        // Has not been loaded yet
        is_loaded = 0;
        // Has not been saved yet
        is_saved = 0;
        // Creating a SimThread, maybe
        sim = &simul;
    }

    /// A utility function to add objects to the simulation 
    /**
     * @brief Adds objects ; takes a variable number of arguments.
     *  - name : a string with the name of the objects to add
     *  - (optional) number : a number of objects to add (default : 1)
     *  - (optional) specs : a string, containing specification on the object to add (default : "")
     * 
     * Example :
     * 
     * [python]>>> `fibers = parser.add("actin", 1, "length = 2")`
     * @param name ,( number ,( specs )) 
     * @return Returns a list of objects
     
     */
    ObjectList add(py::args args) {

        std::string name = "";
        std::string how = "";
        int many = 1;
        int nargs = args.size();
        
        if (nargs>0) {
            name = py::cast<std::string>(args[0]);
        }
        if (nargs>1) {
            many = py::cast<int>(args[1]);
        }
        if (nargs>2) {
            how = py::cast<std::string>(args[2]);
        }
        
        Property const* pp = sim->properties.find_or_die(name);    
        Glossary glos = Glossary(how);
        
        return Interface::execute_new(pp->category(), name, glos, many);
    }

     /// A utility function to run simulation 
    /**
     * @brief runs cytosim ; takes a variable number of arguments.
     *  - (optional) duration : a duration (in seconds) (default : a timestep)
     *  - (optional) how : a string, containing specification on the run (default : "")
     * 
     * Example :
     * 
     * [python]>>> `parser.run(10)`
     * @param (duration ,( how )) 
     * @return None
     
     */
    void run(py::args args) {
        std::string how = "";
        real many = sim->time_step();
        int nargs = args.size();
        if (nargs>0) {
            many = py::cast<real>(args[0]);
        }
        if (nargs>1) {
            how = py::cast<std::string>(args[1]);
        }
        Glossary glos = Glossary(how);
        Interface::execute_run(many, glos,0);
    }

    /// A utility function to change a property
    /**
     * @brief changes a property ; takes two arguments
     *  - name : a string with the name of the objects to change
     *  - how : a string describing what to change
     * 
     * Example :
     * 
     * [python]>>> `parser.change("actin", "rigidity=2")`
     * @param name ,how
     * @return Returns a property
     
     */
    Property * change(std::string & name, std::string & how) {   
        Glossary glos = Glossary(how);
        return Interface::execute_change(name, glos, 1);
    }
    
    /// A utility function to set a new property
    /**
     * @brief sets a new property ; takes three arguments
     *  - category : a strong containing the object category
     *  - name : a string with the name of the objects to change
     *  - how : a string describing what to change
     * 
     * Example :
     * 
     * [python]>>> `parser.set("fiber", "actin", "rigidity=2 ; segmentation = 0.1")`
     * @param name ,how
     * @return Returns a property
     
     */
    Property * set(std::string & cat, std::string & name, std::string & how) {
        Glossary * glos = new Glossary(how);
        return Interface::execute_set(cat, name, *glos);
    }
    
    
    
    /// Returns a Frame of the current simulation state
    Frame frame() {
        return Frame(sim);
    }
    
    /// Pointer to the current instance of FrameReader
    FrameReader reader;
    
    /// Check if simulation is loaded \private
    int is_loaded ;
    
    /// Returns the current instance of SimThread
    SimThread * thread;
    
    /// Informs wether the simulation has been saved \private
    bool is_saved ;
    
    /// Pointer to the current instance of Simul
    Simul * sim;

    /// Loads the simulation at a given timeframe (only for simulation replay)
    int load(int fr) {
        int loader = 1;
        if (is_loaded == 1) {
            try 
            {
                //loader = thread->loadFrame(fr);
                loader = reader.loadFrame(*sim,fr);
                if (loader!=0) {
                    std::clog << "Unable to load frame " << fr << ". Maybe frame does not exist." << std::endl;
                } 
                    
            }
            catch( Exception & e )
            {
                std::clog << "Aborted: " << e.what() << '\n';
            }
        }
        else{
            std::clog << "Simulation not loaded : use cytosim.open() first" << std::endl;
        }
        
        return loader;
    }
    
    int next() {
        return reader.loadNextFrame(*sim);
    }

    /// activates the parser (from existing sim) \private
    void activate(std::string & input, SimThread * existing_thread) {
        thread = existing_thread;
        //thread->start();
        reader.openFile(input);
        is_loaded = 1;
    }

   /// activates the parser (from existing sim)  \private
    void activate(std::string & input) {
        thread = new SimThread(sim);
        //thread->start();
        reader.openFile(input);
        is_loaded = 1;
    }
    
    /// activates the parser (new sim)  \private
    void activate(SimThread * existing_thread) {
        //Parser::readConfig(); // Already read in this version of cytosim
        thread = existing_thread;
        thread->start();    
        // Waiting for the config file to be read
        while ( thread -> did_run() == 0 ) { is_loaded = 0 ;};
        is_loaded = 2;
    }
    
    /// activates the parser (new sim)  \private
    void activate() {
        //Parser::readConfig(); // Already read in this version of cytosim
        thread = new SimThread(sim);
        thread->start();
        // Waiting for the config file to be read
        while ( thread -> did_run() == 0 ) { is_loaded = 0 ;};
        is_loaded = 2;
    }
    
    /// Runs the simulation for a single timestep
    void once() {
        sim->solve_meca();
        sim->steps();
    }
};

#endif
