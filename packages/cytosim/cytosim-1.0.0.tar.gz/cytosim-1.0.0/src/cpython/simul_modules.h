#include "fiber_prop.h"
#include "simul_prop.h"
#include "python_utilities.h"
#include <pybind11/pybind11.h>
namespace py = pybind11;
class Property;

/// a utility to enrich the cytosim python module
auto load_simul_classes(py::module_ &m) {
    /// Python interface to Vector
    auto pyVector = py::class_<Vector>(m, "Vector", py::buffer_protocol())
        .def_buffer([](Vector &vec) -> py::buffer_info {
            void * data = vec.data();
            //int_vect sizes =  {1, DIM};
            int_vect sizes =  {DIM};
            //int_vect strides =  {DIM*sizeof(real), sizeof(real)};
            int_vect strides =  {sizeof(real)};
            return py::buffer_info(
                   data,                               /* Pointer to buffer */
                   sizeof(real),                          /* Size of one scalar */
                   py::format_descriptor<real>::format(), /* Python struct-style format descriptor */
                   1,                                      /* Number of dimensions */
                   sizes,                 /* Buffer dimensions */
                   strides             /* Strides (in bytes) for each index */
                );
    });
    
#if (DIM !=3)    
    /// Python interface to Vector
    py::class_<Vector3>(m, "Vector3", py::buffer_protocol())
    .def_buffer([](Vector3 &vec) -> py::buffer_info {
        void * data = vec.data();
        int_vect sizes =  {3};
        int_vect strides =  {sizeof(real)};
        return py::buffer_info(
               data,                               /* Pointer to buffer */
               sizeof(real),                          /* Size of one scalar */
               py::format_descriptor<real>::format(), /* Python struct-style format descriptor */
               1,                                      /* Number of dimensions */
               sizes,                 /* Buffer dimensions */
               strides             /* Strides (in bytes) for each index */
               );
    });
#else
    m.attr("Vector3") = pyVector;
#endif
    
    /// Python interface to default property
    py::class_<Property>(m, "Prop")
        .def("name", &Property::name)
        .def("change", [](Property * prop, std::string winds, Simul * sim) {
            Glossary of_change = Glossary(winds);
            prop->read(of_change);
            prop->complete(*sim);
        })
        .def("read", [](Property * prop, std::string winds) {
            Glossary of_change = Glossary(winds);
            prop->read(of_change);
        })
        .def("change_glos", [](Property * prop, Glossary & winds, Simul * sim) {
            prop->read(winds);
            prop->complete(*sim);
        })
        .def("read_glos", [](Property * prop, Glossary & winds) {
            prop->read(winds);
        })
        .def("complete",  [](Property * prop, Simul * sim) {return prop->complete(*sim);})
        .def("rename", &Property::rename)
        .def("is_named", &Property::is_named)
        .def("number", &Property::number)
        .def("renumber", &Property::renumber)
        .def("clear", &Property::clear)
        .def("clone", &Property::clone, PYREF);
        
        
    
    py::class_<SpaceSet,ObjectSet>(m, "SpaceSet");
	py::class_<FiberSet,ObjectSet>(m, "FiberSet");
	py::class_<FieldSet,ObjectSet>(m, "FieldSet");
	py::class_<SphereSet,ObjectSet>(m, "SphereSet");
	py::class_<BeadSet,ObjectSet>(m, "BeadSet");
	py::class_<SolidSet,ObjectSet>(m, "SolidSet");
	py::class_<OrganizerSet,ObjectSet>(m, "OrganizerSet");
	
    
    auto pysim = py::class_<Simul>(m, "Simul")
        .def("frame",  [](Simul * sim) {return Frame(sim);}, py::return_value_policy::move)
        .def_readwrite("prop",   &Simul::prop , PYREF)
        .def_readonly("sMeca",   &Simul::sMeca , PYREF)
        .def_readwrite("properties",   &Simul::properties , PYREF)
        .def_readonly("spaces",   &Simul::spaces , PYREF)
        .def_readonly("fields",   &Simul::fields , PYREF)
        .def_readonly("fibers",   &Simul::fibers , PYREF)
        .def_readonly("spheres",   &Simul::spheres , PYREF)
        .def_readonly("beads",   &Simul::beads , PYREF)
        .def_readonly("solids",   &Simul::solids , PYREF)
        .def_readonly("couples",   &Simul::couples , PYREF)
        .def_readonly("singles",   &Simul::singles , PYREF)
        .def_readonly("organizers",   &Simul::organizers , PYREF)
        .def("remove",  [](Simul * sim, Object* obj) {return sim->remove(obj);})
        .def("eraseObject", &Simul::eraseObject)
        .def("eraseObjects", [](Simul *sim, ObjectList const& liste) {return sim->eraseObjects(liste);})
        .def("eraseObjects", [](Simul *sim, py::list const& liste) {
            std::vector<Object*> vec = liste.cast<std::vector<Object*>>();
            for ( Object * obj : vec ) {
                sim->eraseObject(obj);
                } })
        .def("time",  [](Simul * sim) {return sim->time();})
        .def("time_step",  [](Simul * sim) {return sim->time_step();})
        .def("steps",  &Simul::steps)
        .def("computeForces",  &Simul::computeForces)
        .def("prepared_solve",  &Simul::prepared_solve)
        .def("prepare_meca",  &Simul::prepare_meca)
        .def("initCytosim",  &Simul::initCytosim )   
        .def("prepare",  &Simul::prepare )   
        .def("solve_meca",  &Simul::solve_meca)
        .def("solve_force", &Simul::solve_force)
        .def("solve_auto",  [](Simul * sim) {return sim->solve_auto();})
        .def("parser",  [](Simul * sim)  {return sim->parser() ;}, PYREF)
        .def("parser",  [](Simul * sim, Parser * p)  {return sim->parser(p) ;}, PYREF)
          
        .def("toMecable",  [](Simul * sim, Object* o) {return sim->toMecable(o);} , PYREF)
        .def("findMecable",  [](Simul * sim, std::string s) {return sim->pickMecable(s);} , PYREF)
        .def("findSpace",  [](Simul * sim, std::string s) {return sim->findSpace(s);} , PYREF)
        .def("rename",  [](Simul * sim, std::string s) {return sim->rename(s);} , PYREF)
        .def("isCategory",  [](Simul * sim, std::string s) {return sim->isCategory(s);} , PYREF)
        .def("findProperty",  [](Simul * sim, std::string s) {return sim->findProperty(s);} , PYREF)
        .def("writeProperties",  [](Simul * sim) {return sim->writeProperties(1);} )
        .def("writePropertiesToNoPrune",  [](Simul * sim) {return sim->writeProperties(0);} );
        
        
    
    /// Python interface to simulProp
    py::class_<SimulProp,Property>(m, "SimulProp")
        .def_readwrite("time", &SimulProp::time)
        .def_readwrite("time_step", &SimulProp::time_step)
        .def_readwrite("viscosity", &SimulProp::viscosity)
        .def_readwrite("kT", &SimulProp::kT)
        .def_readwrite("tolerance", &SimulProp::tolerance)
        .def_readwrite("acceptable_prop", &SimulProp::acceptable_prob)
        .def_readwrite("precondition", &SimulProp::precondition)
        .def_readwrite("steric_mode", &SimulProp::steric_mode)
        //
        .def_readwrite("steric_max_range", &SimulProp::steric_max_range)
        .def_readwrite("binding_grid_step", &SimulProp::binding_grid_step)
        .def_readwrite("verbose", &SimulProp::verbose)
        .def_readwrite("config_file", &SimulProp::config_file)
        .def_readwrite("property_file", &SimulProp::property_file)
        .def_readwrite("system_file", &SimulProp::system_file)
        .def_readwrite("skip_free_couple", &SimulProp::skip_free_couple)
        .def_readwrite("display_fresh", &SimulProp::display_fresh)
        .def_readwrite("display", &SimulProp::display)
        .def("read",  [](SimulProp * prop, Glossary & glos) {return prop->read(glos);})
        .def("read_str",  [](SimulProp * prop, std::string const& str) 
                {Glossary * glos = str_to_glos(str) ; return prop->read(*glos);})
        .def("clone",  [](SimulProp * prop) {return prop->clone();});
        

    return pysim;
}

