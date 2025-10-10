#include "single.h"
#include "picket.h"
#include "picket_long.h"
#include "wrist.h"
#include "wrist_long.h"

#include <pybind11/pybind11.h>
#include "python_utilities.h"
namespace py = pybind11;

class Single;
class Object;


/**
 @defgroup PySingle Single
* @brief  A group functions to facilitate usage of Single in PyCytosim

 In PyCytosim, a Single is also a list of (one) hand
 
  [python]>>> `hand = single[0] ` \n
   
    @ingroup PyUtilities
 */

/// Converts an object to a Single if possible;
/**
 * @brief Converts an object to a Single if possible
 
  [python]>>> `single = cytosim.Single.toSingle(obj) ` \n
 * @param obj
 * @return Single 

 
 @ingroup PySingle
 */
static Single* toSingle(Object * obj)
{
    if ( obj  &&  obj->tag() == 's' )
        return static_cast<Single*>(obj);
    return nullptr;
}

/// a utility to enrich the cytosim python module
void load_single_classes(py::module_ &m) {
        /// Python interface to HandMonitor
	py::class_<HandMonitor>(m, "HandMonitor")
		.def("permitAttachment", &HandMonitor::permitAttachment)
		.def("afterAttachment", &HandMonitor::afterAttachment)
		.def("otherHand", &HandMonitor::otherHand, PYREF)
        .def("toSingle", &HandMonitor::toSingle, PYREF)
        .def("toCouple", &HandMonitor::toCouple, PYREF)
        .def("linkFoot",  [](HandMonitor * s, Hand * h) {return to_numpy(s->linkFoot(h));}, PYOWN)
        .def("linkDir",  [](HandMonitor * s, Hand * h) {return to_numpy(s->linkDir(h));}, PYOWN)
        .def("linkRestingLength", &HandMonitor::linkRestingLength)
		.def("linkStiffness", &HandMonitor::linkStiffness);
        
        
     /// Python interface to single
    py::class_<Single,Object,HandMonitor>(m, "Single")
        /// PyCytosim specific
        .def("toSingle",  [](Object * s) {return toSingle(s);}, PYREF)
        /// A Single is like a list of length 1 containing ahand
        .def("__len__",  [](Single * s) {return (int)1;})
        .def("__getitem__",[](Single *s, int i) { // We can call Single[0]  to get the first hand ! thus couple[0].attachEnd(...) is available
            if (i==0) {return s->hand();} else {throw py::index_error(); }
            return (Hand*)nullptr;} 
            , PYREF)
        //
        .def("hand", &Single::hand, PYREF)
        .def("attached", &Single::attached)
        .def("state", &Single::state)
        .def("fiber", &Single::fiber, PYREF)
        .def("abscissa", &Single::abscissa)
        .def("posHand",  [](Single * s) {return to_numpy(s->posHand());}, PYOWN)
        .def("dirFiber",  [](Single * s) {return to_numpy(s->dirFiber());}, PYOWN)
        .def("attach", &Single::attach)
        .def("attachEnd",  [](Single * s, Fiber *f, int end) {return s->attachEnd(f,static_cast<FiberEnd>(end));})
        .def("moveToEnd",  [](Single * s, int end) {return s->moveToEnd(static_cast<FiberEnd>(end));})
        .def("detach", &Single::detach)
        //
        .def("position",  [](Single * s) {return to_numpy(s->position());}, PYOWN)
        .def("mobile", &Single::mobile)
        .def("translate",  [](Single * s, pyarray vec) 
            {   Vector p = to_vector(vec);
                return s->translate(p);})
        .def("setPosition",  [](Single * s, pyarray vec) 
            {   Vector p = to_vector(vec);
                return s->setPosition(p);})
        .def("randomizePosition", &Single::randomizePosition)
        //
        .def("posFoot",  [](Single * s) {return to_numpy(s->posFoot());}, PYOWN)
        .def("sidePos",  [](Single * s) {return to_numpy(s->sidePos());}, PYOWN)
        .def("base", &Single::base)
        .def("unbase", &Single::unbase)
        .def("hasLink", &Single::hasLink)
        .def("stretch",  [](Single * s) {return to_numpy(s->stretch());}, PYOWN)
        .def("force",  [](Single * s) {return to_numpy(s->force());}, PYOWN)
        .def("stepA", &Single::stepA)
        .def("stepF", &Single::stepF)
        .def("setInteractions", &Single::setInteractions)
        //
        .def("next", [](Single * s, Single * x) {return s->next(x);})
        .def("prev", [](Single * s, Single * x) {return s->prev(x);})
        // Has to be written in full for arcane reasons
        .def("next", [](Single * s) {return s->next();}, PYREF)
        .def("prev", [](Single * s) {return s->prev();}, PYREF)
        //
        .def("tag", &Single::tag)
        .def("property", &Single::property)
        .def("confineSpace", &Single::confineSpace)
        .def("invalid", &Single::invalid);
        
        

    py::class_<SingleProp,Property>(m, "SingleProp")
        .def_readwrite("hand", &SingleProp::hand)
        .def_readwrite("stiffness", &SingleProp::stiffness)
#if NEW_ANCHOR_STIFFNESS
        /// A stiffness to anchor fibers on Solids with angular constraints
        .def_readwrite("anchor_stiff", &SingleProp::anchor_stiff)
#endif      
        .def_readwrite("length", &SingleProp::length)
        .def_readwrite("diffusion", &SingleProp::diffusion)
        .def_readwrite("fast_diffusion", &SingleProp::fast_diffusion)
        .def_readwrite("fast_reservoir", &SingleProp::fast_reservoir)
#if NEW_MOBILE_SINGLE
        /// constant drift
        .def("speed",  [](Single * s) {return to_numpy(s->speed());}, PYOWN)
#endif
        .def_readwrite("confine", &SingleProp::confine)
        .def_readwrite("confine_stiff", &SingleProp::confine_stiff)
        .def_readwrite("confine_spec", &SingleProp::confine_spec)
        .def_readwrite("activity", &SingleProp::activity)
        .def_readwrite("hand_prop", &SingleProp::hand_prop, PYREF)
        .def_readwrite("uni_counts", &SingleProp::uni_counts)
        //
        .def("newSingle", &SingleProp::newSingle, PYREF)
        .def("newWrist", [](SingleProp * p, Mecable const* m, unsigned inx) 
                {return p->newWrist(m, inx);}, PYREF)
        .def("newWrist", [](SingleProp * p, Mecable const* m, unsigned ref, pyarray vec)
                {return p->newWrist(m, ref, to_vector(vec));}, PYREF)
        .def("clear", &SingleProp::clear)        
        .def("read", [](SingleProp * p, std::string & how) {
            Glossary glos = Glossary(how);
            p->read(glos); })
        .def("complete", &SingleProp::complete)        
        .def("clone", &SingleProp::clone, PYREF)
        .def("spaceVolume", &SingleProp::spaceVolume);
    
    py::class_<SingleSet,ObjectSet>(m, "SingleSet")
		.def("__getitem__",[](SingleSet * set, int i) {
				int s = set->size();
                if (i<0) {i+=s;} // Python time negative indexing
				if (i >= s or i<0) {
					 throw py::index_error();
				}
				Single * obj = set->firstID();
				while (i) {
					--i; // Slow because ObjectSet is not a vector
					obj = set->nextID(obj); 
				}
				return obj;
             }, PYREF);
             
    py::class_<Picket,Single>(m, "Picket")
        .def("beforeDetachment", &Picket::beforeDetachment)
        .def("linkStiffness", &Picket::linkStiffness);
	py::class_<PicketLong,Picket>(m, "PicketLong");
    py::class_<Wrist,Single>(m, "Wrist");
    py::class_<WristLong,Wrist>(m, "WristLong");

}

