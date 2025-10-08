#include "object.h"
#include <pybind11/pybind11.h>
#include "python_utilities.h"
namespace py = pybind11;

class Object;

/// a utility to enrich the cytosim python module
void load_object_classes(py::module_ &m) {
	py::class_<ObjectSet>(m, "ObjectSet")
		.def("add",  [](ObjectSet * set, Object * obj) {return set->add(obj) ;})
		.def("remove",  [](ObjectSet * set, Object * obj) {return set->remove(obj) ;})
		.def("link",  [](ObjectSet * set, Object * obj) {return set->link(obj) ;})
		.def("unlink",  [](ObjectSet * set, Object * obj) {return set->unlink(obj) ;})
        .def("eraseObject", &ObjectSet::eraseObject)
		.def("erase_all",  [](ObjectSet * set) {return set->erase() ;})
		.def("size",  [](ObjectSet * set) {return set->size() ;})
		.def("__len__",  [](ObjectSet * set) {return set->size() ;})
		.def("first",  [](ObjectSet * set) {return set->first() ;}, PYREF)
		.def("last",  [](ObjectSet * set) {return set->last() ;}, PYREF)
		.def("identifyObject",  [](ObjectSet * set, int n) 
			{return set->identifyObject((ObjectID) n) ;}, PYREF)
		.def("pickObject",  [](ObjectSet * set, Property * p)
			{return set->pickObject(p) ;}, PYREF)
		.def("__getitem__",[](ObjectSet * set, int i) {
				int s = set->size();
                if (i<0) {i+=s;} // Python time negative indexing
				if (i >= s or i<0) {
					 throw py::index_error();
				}
				Object * obj = set->first();
				while (i) {
					--i; 	// This is slow because of objectSet is not a vector
					obj = obj->next();  
				}
				return obj;
             }, PYREF);
     
     /// Python interface to Organizer
    py::class_<Object>(m, "Object")
        .def("reference",  [](Object * obj) {return obj->reference() ;})
        .def("property",  [](Object * obj) {return obj->property() ;}, PYREF)
        .def("position", [](const Object * obj) {return to_numpy(obj->position());}, PYOWN)
        .def("next",  [](Object * obj) {return obj->next() ;}, PYREF)
		.def("__next__",  [](Object * obj) {return obj->next() ;}, PYREF)
        .def("prev",  [](Object * obj) {return obj->prev() ;}, PYREF)
        .def("id",  [](const Object * obj) {return obj->identity();})
        .def("tag",  &Object::tag)
        .def("points", [](const Object * obj) {return pyarray();});
    
    /// Python interface to ObjectList
    py::class_<ObjectList>(m, "ObjectList", "A list-like structure of Cytosim objects")
        .def("__getitem__",[](ObjectList & lis, int i) {
				int s = lis.size();
                if (i<0) {i+=s;} // Python time negative indexing
				if (i >= s or i<0) {
					 throw py::index_error();
				}
				Object * obj = lis[i];
				return obj;
             }, PYREF)
        .def("__len__", [](const ObjectList &v) { return v.size(); });
}
