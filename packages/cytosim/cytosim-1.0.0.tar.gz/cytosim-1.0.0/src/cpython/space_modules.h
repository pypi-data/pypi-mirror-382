#include "space.h"
#include "space_dynamic_ellipse.h"
#include "space_dynamic_disc.h"
#include "space_dynamic_sphere.h"
#include <pybind11/pybind11.h>
#include "python_utilities.h"
//#include <pybind11/numpy.h>
//#include <pybind11/stl.h>
namespace py = pybind11;

class Space;
class Object;


/**
 @defgroup PySpace Space
  * @brief A group functions to facilitate usage of Space in PyCytosim
    
    A space behaves like a cytosim space.
     
    @ingroup PyUtilities
 */

/// Converts an object to a Space if possible;
/**
 * @brief Converts an object to a Space if possible
 
  [python]>>> `space = cytosim.Space.toSpace(obj) ` \n
 * @param obj
 * @return Space 

 
 @ingroup PySpace
 */
static Space* toSpace(Object * obj)
{
    if ( obj  &&  obj->tag() == 'e' )
        return static_cast<Space*>(obj);
    return nullptr;
}

/// a utility to enrich the cytosim python module
void load_space_classes(py::module_ &m) {
     /// Python interface to space
    py::class_<Space,Object>(m, "Space")
        .def("toSpace",  [](Object * s) {return toSpace(s);}, PYREF)
        .def("resize",  [](Space * sp, std::string sizes) {
            Glossary glos = Glossary(sizes); sp->resize(glos) ;})
        .def("getModulo", &Space::getModulo)
        .def("thickness", &Space::thickness)
        .def("volume", &Space::volume)
        .def("surface", &Space::surface)
        .def("boundaries",  [](const Space * sp)
            {Vector V,W; 
            sp->boundaries(V,W);
                return std::vector<pyarray>{to_numpy(V),to_numpy(W)};
                }, PYOWN)
        .def("inside", [](const Space * sp, pyarray pos) {return sp->inside(to_vector(pos));})
        .def("project", [](const Space * sp, pyarray pos) {return to_numpy(sp->project(to_vector(pos)));}, PYOWN)
        .def("setConfinement", [](const Space * sp, pyarray pos, Mecapoint pt, Meca & mec, real stiff)
            {return sp->setConfinement(to_vector(pos), pt, mec, stiff);})
            .def("setConfinement", [](const Space * sp, pyarray pos, Mecapoint pt, real rad, Meca & mec, real stiff)
            {return sp->setConfinement(to_vector(pos), pt, rad, mec, stiff);})
        .def("allInside", [](const Space * sp, pyarray pos, real rad) {return sp->allInside(to_vector(pos),rad);})
        .def("allOutside", [](const Space * sp, pyarray pos, real rad) {return sp->allOutside(to_vector(pos),rad);})
        .def("maxExtension", &Space::maxExtension)
        .def("outside", [](const Space * sp, pyarray pos) {return sp->outside(to_vector(pos));})
        .def("projectDeflated", [](const Space * sp, pyarray pos, real rad) 
            {return to_numpy(sp->projectDeflated(to_vector(pos),rad));}, PYOWN)
        .def("estimateVolume", &Space::estimateVolume)
        .def("bounceOnEdges", [](const Space * sp, pyarray pos) {return to_numpy(sp->bounceOnEdges(to_vector(pos)));}, PYOWN)
        .def("bounce", [](const Space * sp, pyarray pos) {return to_numpy(sp->bounce(to_vector(pos)));}, PYOWN)
        .def("distanceToEdgeSqr", [](const Space * sp, pyarray pos) {return sp->distanceToEdgeSqr(to_vector(pos));})
        .def("distanceToEdge", [](const Space * sp, pyarray pos) {return sp->distanceToEdge(to_vector(pos));})
        .def("signedDistanceToEdge", [](const Space * sp, pyarray pos) {return sp->signedDistanceToEdge(to_vector(pos));})
        .def("placeNearEdge", [](const Space * sp, real rad, int tries) {return to_numpy(sp->placeNearEdge(rad,tries));}, PYOWN)
        .def("onSurface", [](const Space * sp, real rad, int tries) {return to_numpy(sp->onSurface(rad,tries));}, PYOWN)
        
        .def("place", [](const Space * sp) {return to_numpy(sp->place());}, PYOWN)
        .def("normalToEdge", [](const Space * sp, pyarray pos) {return to_numpy(sp->normalToEdge(to_vector(pos)));}, PYOWN)
        .def("placeNearEdge", [](const Space * sp, real rad) {return to_numpy(sp->placeNearEdge(rad));}, PYOWN)
        .def("placeOnEdge", [](const Space * sp, real rad) {return to_numpy(sp->placeOnEdge(rad));}, PYOWN);
        
        
        
    
    py::class_<SpaceProp,Property>(m, "SpaceProp");
            
    py::enum_<Confinement>(m,"Confinement")
        .value("CONFINE_OFF", CONFINE_OFF)
        .value("CONFINE_INSIDE", CONFINE_INSIDE)
        .value("CONFINE_OUTSIDE", CONFINE_OUTSIDE)
        .value("CONFINE_ON", CONFINE_ON)
        .value("CONFINE_ALL_INSIDE", CONFINE_ALL_INSIDE)
        .value("CONFINE_ALL_OUTSIDE", CONFINE_ALL_OUTSIDE)
        .value("CONFINE_PLUS_END", CONFINE_PLUS_END)
        .value("CONFINE_MINUS_END", CONFINE_MINUS_END)
        .value("CONFINE_BOTH_ENDS", CONFINE_BOTH_ENDS)
        .value("CONFINE_PLUS_OUT", CONFINE_PLUS_OUT)
        .value("CONFINE_POINT", CONFINE_POINT)
        .value("CONFINE_RANGE", CONFINE_RANGE)
        .export_values();
    
    py::class_<SpaceDynamicProp,SpaceProp>(m, "SpaceDynamicProp")
        .def_readwrite("viscosity", &SpaceDynamicProp::viscosity)
        .def_readwrite("viscosity_rot", &SpaceDynamicProp::viscosity_rot)
        .def_readwrite("tension", &SpaceDynamicProp::tension)
        .def_readwrite("volume", &SpaceDynamicProp::volume)
        .def_readwrite("mobility_dt", &SpaceDynamicProp::mobility_dt)
        .def_readwrite("mobility_rot_dt", &SpaceDynamicProp::mobility_rot_dt)
        ;
    
    py::class_<SpaceEllipse,Space>(m, "SpaceEllipse")
        .def("radius",  [](SpaceEllipse * sp) {return to_numpy(sp->radius());}, PYOWN)
        ;
        
    py::class_<SpaceDynamicEllipse,SpaceEllipse>(m, "SpaceDynamicEllipse")
        .def("director",  [](SpaceDynamicEllipse * sp, int i) {return to_numpy(sp->director(i));}, PYOWN)
        .def("get_pressure", &SpaceDynamicEllipse::get_pressure)
        .def("get_rad_forces",  [](SpaceDynamicEllipse * sp) {return to_numpy(sp->get_rad_forces());}, PYOWN)
        .def("get_Rforces",  [](SpaceDynamicEllipse * sp) {return to_numpy(sp->get_Rforces());}, PYOWN)
        .def("get_Torques",  [](SpaceDynamicEllipse * sp) {return to_numpy(sp->get_Torques());}, PYOWN)
        ;
        
     py::class_<SpaceDynamicDisc,Space>(m, "SpaceDynamicDisc")
        .def("radius", &SpaceDynamicDisc::radius)
        .def("force", &SpaceDynamicDisc::force)
        ;
        
     py::class_<SpaceSphere,Space>(m, "SpaceSphere")
        .def("radius", &SpaceSphere::radius)
        ;
        
    py::class_<SpaceDynamicSphere,SpaceSphere>(m, "SpaceDynamicSphere")
        .def("force", &SpaceDynamicSphere::force)
        ;
}

