#include "fiber.h"
#include "classic_fiber.h"
#include <pybind11/pybind11.h>
#include "python_utilities.h"
#include "dynamic_fiber.h"
#include "growing_fiber_prop.h"
#include "treadmilling_fiber_prop.h"
#include "growing_fiber.h"
#include "treadmilling_fiber.h"

namespace py = pybind11;
class Fiber;
class Object;


/**
 @defgroup PyFiber Fiber
  A group functions to facilitate usage of Fiber in PyCytosim
    * @brief A group functions to facilitate usage of Fiber in PyCytosim
    
    
    @ingroup PyUtilities
*/

/// Converts an object to a Fiber if possible;
/**
 * @brief Converts an object to a Fiber if possible
 
  [python]>>> `fiber = cytosim.Fiber.toFiber(obj)` \n
 * @param obj
 * @return Fiber 

 @ingroup PyFiber
 */
static Fiber* toFiber(Object * obj)
{
    if ( obj  &&  obj->tag() == 'f' )
        return static_cast<Fiber*>(obj);
    return nullptr;
}

/// a utility to enrich the cytosim python module
void load_fiber_classes(py::module_ &m) {
    /// Python interface to Mecable
    py::class_<Chain,Mecable>(m, "Chain")
        .def("nbSegments",  [](Chain * chn) {return chn->nbSegments();})
        .def("lastSegment",  [](Chain * chn) {return chn->lastSegment();})
        .def("setStraight",  [](Chain * chn, pyarray pos, pyarray dir) 
            {   Vector p = to_vector(pos);
                Vector d = to_vector(dir);
                return chn->setStraight(p,d);})
        .def("setStraightLength",  [](Chain * chn, pyarray pos, pyarray dir, real len) 
            {   Vector p = to_vector(pos);
                Vector d = to_vector(dir);
                return chn->setStraight(p,d,len);})
        .def("placeEnd",  [](Chain * chn, int end) {return chn->placeEnd((FiberEnd)end);})
        .def("setEquilibrated",  [](Chain * chn, real len, real persil) {return chn->setEquilibrated(len, persil);})
#if FIBER_HAS_BIRTHTIME
        .def("birthTime",  [](Chain * chn) {return chn->birthTime();})
        .def("age",  [](Chain * chn) {return chn->age();})
#endif
        .def("exactEnd",  [](Chain * chn, int a) {
            return new Mecapoint(chn->exactEnd((FiberEnd)a)); })
        .def("interpolateEndM", [](Chain * chn) {
            return new Interpolation(chn->interpolateEndM());})
        .def("interpolateEndP",  [](Chain * chn) {
            return new Interpolation(chn->interpolateEndP()); })
        .def("interpolateCenter", [](Chain * chn) {
            return new Interpolation(chn->interpolateCenter()); })
        .def("interpolateEnd",  [](Chain * chn, int a)   {
            return new Interpolation(chn->interpolateEnd((FiberEnd)a)); })
        .def("interpolateFrom",  [](Chain * chn, real ab, int a) {
            return new Interpolation(chn->interpolateFrom(ab,(FiberEnd)a)); })
        .def("interpolateAbs",  [](Chain * chn, real ab) {
            return new Interpolation(chn->interpolateAbs(ab)); })
        .def("length",  [](Chain * chn) {return chn->length();})
        .def("length1",  [](Chain * chn) {return chn->length1();})
        .def("contourLength", [](Chain * chn) {return chn->contourLength();})
        .def("betweenMP",  [](Chain * chn, real a) {return chn->betweenMP(a);})
        .def("outsideMP",  [](Chain * chn, real a) {return chn->outsideMP(a);})
        .def("belowP",  [](Chain * chn, real a) {return chn->belowP(a);})
        .def("aboveM",  [](Chain * chn, real a) {return chn->aboveM(a);})
        .def("whichEndDomain",  [](Chain * chn, real a, real b) {return chn->whichEndDomain(a,b);})
        //
        .def("setOrigin",  [](Chain * chn, real a) {return chn->setOrigin(a);})
        .def("abscissaM",  [](Chain * chn) {return chn->abscissaM();})
        .def("abscissaC",  [](Chain * chn) {return chn->abscissaC();})
        .def("abscissaP",  [](Chain * chn) {return chn->abscissaP();})
        .def("abscissaPoint",  [](Chain * chn, real a) {return chn->abscissaPoint(a);})
        .def("abscissaEnd",  [](Chain * chn, int a) {return chn->abscissaPoint((FiberEnd)a);})
        .def("abscissaFrom",  [](Chain * chn, real dis, int a) {return chn->abscissaFrom(dis,(FiberEnd)a);})
        .def("someAbscissa",  [](Chain * chn, real dis, int a, int mod, real alf) {return chn->someAbscissa(dis,(FiberEnd)a, mod, alf);})
        .def("posM",  [](Chain * chn, real a) {return to_numpy(chn->posM(a));}, PYOWN)
        .def("pos",  [](Chain * chn, real a) {return to_numpy(chn->pos(a));}, PYOWN)
        //
        .def("posMiddle",  [](Chain * chn) {return to_numpy(chn->posMiddle());}, PYOWN)
        .def("posEnd",  [](Chain * chn, int end) {return to_numpy(chn->posEnd((FiberEnd)end));}, PYOWN)
        .def("posEndP",  [](Chain * chn) {return to_numpy(chn->posEndP());}, PYOWN)
        .def("posEndM",  [](Chain * chn) {return to_numpy(chn->posEndM());}, PYOWN)
        .def("netForceEndM",  [](Chain * chn) {return to_numpy(chn->netForceEndM());}, PYOWN)
        .def("netForceEndP",  [](Chain * chn) {return to_numpy(chn->netForceEndP());}, PYOWN)
        .def("projectedForceEndM",  [](Chain * chn) {return chn->projectedForceEndM();})
        .def("projectedForceEndP",  [](Chain * chn) {return chn->projectedForceEndP();})
        .def("projectedForceEndM",  [](Chain * chn, int end) {return chn->projectedForceEnd((FiberEnd) end);})
        .def("direction",  [](Chain * chn) {return to_numpy(chn->direction());}, PYOWN)
        .def("segmentation",  [](Chain * chn) {return chn->segmentation();})
        .def("reshape", &Chain::reshape)
        .def("flipChainPolarity",  [](Chain * chn) {return chn->flipChainPolarity();})
        .def("curvature",  [](Chain * chn, unsigned p) {return chn->curvature(p);})
        .def("bendingEnergy0",  [](Chain * chn) {return chn->bendingEnergy0();})
        .def("planarIntersect",  [](Chain * chn, unsigned s, pyarray vec, real a) {return chn->planarIntersect(s, to_vector(vec), a);})
        .def("growM",  [](Chain * chn, real a) {return chn->growM(a);})
        .def("addSegmentM",  [](Chain * chn) {return chn->addSegmentM();})
        .def("cutM",  [](Chain * chn, real a) {return chn->cutM(a);})
        .def("growP",  [](Chain * chn, real a) {return chn->growP(a);})
        .def("addSegmentP",  [](Chain * chn) {return chn->addSegmentP();})
        .def("cutP",  [](Chain * chn, real a) {return chn->cutP(a);})
        .def("grow",  [](Chain * chn, int ref, real a) {return chn->grow((FiberEnd)ref,a);})
        .def("adjustLength",  [](Chain * chn, real a, int ref) {return chn->adjustLength(a,(FiberEnd)ref);})
        .def("truncateM",  [](Chain * chn, unsigned a) {return chn->truncateM(a);})
        .def("truncateP",  [](Chain * chn, unsigned a) {return chn->truncateP(a);});        
    
    py::class_<Mecafil,Chain>(m, "Mecafil")
        .def("tension",  [](Mecafil * mec, unsigned p) {return mec->tension(p);})
        .def("dragCoefficient",  [](Mecafil * mec) {return mec->dragCoefficient();})
        .def("pointMobility",  [](Mecafil * mec) {return mec->pointMobility();})
        .def("leftoverMobility",  [](Mecafil * mec) {return mec->leftoverMobility();});
    
    py::class_<Fiber,Mecafil>(m, "Fiber")
        .def("displayPosM",  [](Fiber * fib, real a) {return to_numpy(fib->displayPosM(a));}, PYOWN)
        .def("setDragCoefficient", &Fiber::setDragCoefficient)
        .def("flipHandsPolarity", &Fiber::flipHandsPolarity)
        .def("flipPolarity", &Fiber::flipPolarity)
        .def("cutM",  [](Fiber * fib, real len) {return fib->cutM(len);})
        .def("cutP",  [](Fiber * fib, real len) {return fib->cutP(len);})
        .def("points",  [](Fiber * fib) {return get_obj_points(fib);}, PYOWN)
        .def("toFiber",  [](Object * obj) {return Fiber::toFiber(obj);},  PYREF)
        .def("nbPoints",  [](Fiber * fib) {return fib->nbPoints();})
        .def("planarCut",  [](Fiber * fib, pyarray n, real a, int p, int m, real min_len) {
            fib->planarCut(to_vector(n), a, static_cast<state_t>(p),static_cast<state_t>(m),min_len);})
        .def("severSoon",  [](Fiber * fib, real a, real w, int m, int p) {
            fib->severSoon(a, w, static_cast<state_t>(m),static_cast<state_t>(p));})
        .def("join",  [](Fiber * fib, Fiber * fob) {return fib->join(fob);})
        .def("updateLength", &Fiber::updateLength)
        .def("updateFiber", &Fiber::updateFiber)
        .def("step", &Fiber::step)
        .def("bendingEnergy", &Fiber::bendingEnergy)
        .def("projectPoint",  [](Fiber * fib, pyarray w) {real dis2 ; return fib->projectPoint(to_vector(w),dis2);})
        .def("endStateM", &Fiber::endStateM)
        .def("endStateP", &Fiber::endStateP)
        .def("endState",  [](Fiber * fib, int end) {return fib->endState(static_cast<FiberEnd>(end));})
        .def("setEndStateM",  [](Fiber * fib, int stat) {return fib->setEndStateM(stat);})
        .def("setEndStateP",  [](Fiber * fib, int stat) {return fib->setEndStateP(stat);})
        .def("setEndState",  [](Fiber * fib, int end, int stat) {return fib->setEndState(static_cast<FiberEnd>(end),stat);})
        .def("addHand", &Fiber::addHand)
        .def("removeHand", &Fiber::removeHand)
        .def("updateHands", &Fiber::updateHands)
        .def("sortHands", &Fiber::sortHands)
        .def("firstHand", &Fiber::firstHand, PYREF)
        .def("freshAssembly",  [](Fiber * fib, int end) {return fib->freshAssembly(static_cast<FiberEnd>(end));})
        .def("nbAttachedHands",  [](Fiber * fib) {return fib->nbAttachedHands();})
        .def("nbHandsInRange",  [](Fiber * fib, real amin, real amax, int end) {return fib->nbHandsInRange(amin, amax, static_cast<FiberEnd>(end));})
        .def("nbHandsNearEnd", &Fiber::nbHandsNearEnd)
        .def("birthTime",  [](Fiber * fib, real t) {return fib->birthTime(t);})
        .def("birthTime",  [](Fiber * fib) {return fib->birthTime();})
        .def("age", &Fiber::age)
#if FIBER_HAS_LATTICE
        .def("lattice",  [](Fiber * fib) {return fib->lattice();}, PYREF)
#endif
        // Here functions about mesh and glue
        .def("next", &Fiber::next, PYREF)
        .def("prev", &Fiber::prev, PYREF)
        .def("activity", &Fiber::activity)
        .def("bad", &Fiber::bad)
        .def("__next__", [](const Fiber * fib) {return fib->next();}, PYREF);
        
        
    /// Python interface to FiberProp
    py::class_<FiberProp,Property>(m, "FiberProp")
        .def_readwrite("segmentation", &FiberProp::segmentation)
        .def_readwrite("rigidity", &FiberProp::rigidity)
        .def_readwrite("min_length", &FiberProp::min_length)
        .def_readwrite("max_length", &FiberProp::max_length)
        .def_readwrite("total_polymer", &FiberProp::total_polymer)
        .def_readwrite("persistent", &FiberProp::persistent)
        .def_readwrite("viscosity", &FiberProp::viscosity)
        .def_readwrite("drag_radius", &FiberProp::drag_radius)
        .def_readwrite("drag_length", &FiberProp::drag_length)
        .def_readwrite("drag_model", &FiberProp::drag_model)
        .def_readwrite("drag_gap", &FiberProp::drag_gap)
        .def_readwrite("binding_key", &FiberProp::binding_key)
        .def_readwrite("lattice", &FiberProp::lattice)
        .def_readwrite("lattice_unit", &FiberProp::lattice_unit)
        .def_readwrite("confine", &FiberProp::confine)
        .def_readwrite("confine_space", &FiberProp::confine_space)
        .def("confine_stiff", [](FiberProp * p) {return to_numpy(p->confine_stiff);}, PYOWN)
        .def_readwrite("steric_key", &FiberProp::steric_key)
        .def_readwrite("steric_radius", &FiberProp::steric_radius)
        .def_readwrite("steric_range", &FiberProp::steric_range)
        .def_readwrite("field", &FiberProp::field)
        .def_readwrite("glue", &FiberProp::glue)
        .def_readwrite("glue_single", &FiberProp::glue_single)
        .def_readwrite("activity", &FiberProp::activity)
        .def_readwrite("display_fresh", &FiberProp::display_fresh)
        .def_readwrite("display", &FiberProp::display);
        
        py::enum_<FiberEnd>(m,"FiberEnd")
            .value("NO_END", NO_END)
            .value("PLUS_END", PLUS_END)
            .value("MINUS_END", MINUS_END)
            .value("BOTH_ENDS", BOTH_ENDS)
            .value("ORIGIN", ORIGIN)
            .value("CENTER", CENTER)
            .export_values();

        py::enum_<AssemblyState>(m,"AssemblyState")
            .value("STATE_WHITE", STATE_WHITE)
            .value("STATE_GREEN", STATE_GREEN)
            .value("STATE_YELLOW", STATE_YELLOW)
            .value("STATE_ORANGE", STATE_ORANGE)
            .value("STATE_RED", STATE_RED)
            .export_values();
    
    py::class_<ClassicFiber,Fiber>(m, "ClassicFiber")
        .def("freshAssemblyM",  [](ClassicFiber * fib) {return fib->freshAssemblyM();})
        .def("freshAssemblyP",  [](ClassicFiber * fib) {return fib->freshAssemblyP();});
		
	py::class_<DynamicFiber,Fiber>(m, "DynamicFiber")
		.def("freshAssemblyM",  [](DynamicFiber * fib) {return fib->freshAssemblyM();})
        .def("freshAssemblyP",  [](DynamicFiber * fib) {return fib->freshAssemblyP();});

    py::class_<ClassicFiberProp,FiberProp>(m, "ClassicFiberProp")
		.def("growing_speed",  [](ClassicFiberProp * prop) {return to_numpy_raw(prop->growing_speed, 1, 2); }, PYOWN)
		.def("growing_off_speed",  [](ClassicFiberProp * prop) {return to_numpy_raw(prop->growing_off_speed, 1, 2);}, PYOWN)
		.def("growing_force",  [](ClassicFiberProp * prop) {return to_numpy_raw(prop->growing_force, 1, 2);}, PYOWN)
		.def("shrinking_speed",  [](ClassicFiberProp * prop) {return to_numpy_raw(prop->shrinking_speed, 1, 2);}, PYOWN)
		.def("catastrophe_rate",  [](ClassicFiberProp * prop) {return to_numpy_raw(prop->catastrophe_rate, 1, 2);}, PYOWN)
		.def("catastrophe_rate_stalled",  [](ClassicFiberProp * prop) {return to_numpy_raw(prop->catastrophe_rate_stalled, 1, 2);}, PYOWN);
	
	py::class_<DynamicFiberProp,FiberProp>(m, "DynamicFiberProp")
		.def("growing_speed",  [](DynamicFiberProp * prop) {return to_numpy_raw(prop->growing_speed, 1, 2); }, PYOWN)
		.def("growing_off_speed",  [](DynamicFiberProp * prop) {return to_numpy_raw(prop->growing_off_speed, 1, 2);}, PYOWN)
		.def("growing_force",  [](DynamicFiberProp * prop) {return to_numpy_raw(prop->growing_force, 1, 2);}, PYOWN)
		.def("shrinking_speed",  [](DynamicFiberProp * prop) {return to_numpy_raw(prop->shrinking_speed, 1, 2);}, PYOWN);
	
	py::class_<GrowingFiber,Fiber>(m, "GrowingFiber");
	py::class_<GrowingFiberProp,FiberProp>(m, "GrowingFiberProp");
	
	py::class_<TreadmillingFiber,Fiber>(m, "TreadmillingFiber");
	py::class_<TreadmillingFiberProp,FiberProp>(m, "TreadmillingFiberProp");
}

