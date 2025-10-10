#ifndef UTILITIES_H
#define UTILITIES_H
#include <pybind11/pybind11.h>
#include "glossary.h"
#include <pybind11/stl.h>

class Glossary;
#define PYOWN py::return_value_policy::take_ownership
#define PYMOV py::return_value_policy::move
#define PYREF py::return_value_policy::reference

/// A vector of ints
typedef std::vector<int> int_vect;
/// contains adress, sizes, and strides
namespace py = pybind11;
typedef py::array_t<real> pyarray;


/// Get a numpy array from a pointer to real array (raw data)
template <typename CELL>
py::array_t<CELL> * to_numpy_raw(CELL * pointer, int nb_pts, int dim ) {
    // An empty capsule to create numpy array from raw pointers
    constexpr auto cleanup_callback = []() {} ;
    const py::capsule no_delete(cleanup_callback);
    int_vect sizes = {nb_pts, dim};
    int_vect strides = { static_cast<int>(dim*sizeof(CELL)),  static_cast<int>(sizeof(CELL)) };
    py::array_t<CELL> * arr =  new py::array_t<CELL>(sizes, strides, pointer, no_delete);
    return arr;
}

/// Get a numpy array from a pointer to real array (copy)
pyarray * to_numpy(const real * pointer, int nb_pts, int dim )  {
    int_vect sizes = {nb_pts, dim};
    int_vect strides = { static_cast<int>(dim*sizeof(real)),  static_cast<int>(sizeof(real)) };
    pyarray * arr =new pyarray(sizes, strides, pointer);
    return arr;
}

/// Get points for cytosim objects such as fibers or solids
template<typename Obj>
pyarray * get_obj_points(Obj * obj) {
    return to_numpy( obj->addrPoints(), obj->nbPoints(), DIM);
};

/// Get raw data for cytosim mecables
pyarray * get_obj_data(Mecable * obj) {
    return to_numpy_raw( obj->addrPoints(), obj->nbPoints(), DIM);
};

/// Converts a Vector to numpy array (copy)
pyarray * to_numpy(Vector vec) {    
    pyarray * par = new pyarray;
#if ( DIM==1 )
    *par = py::cast(std::vector<real>{vec[0]});
#elif ( DIM==2 )
    *par = py::cast(std::vector<real>{vec[0],vec[1]});
#else
    *par = py::cast(std::vector<real>{vec[0],vec[1],vec[2]});
#endif
    return par;
}

#if ( DIM == 2 )    
pyarray * to_numpy(Torque vec) {    
    pyarray * par = new pyarray;
    *par = py::cast(std::vector<real>{vec});
    return par;
}
#endif

/// Converts a numpy array to a cytosim vector
Vector to_vector(pyarray arr) {
    try {
        py::buffer_info buf1 = arr.request();
        real *ptr1 = (real *) buf1.ptr;
        return Vector(ptr1);
    }
    catch ( Exception & e ) {
            e << "Unable to convert numpy array to Vector" ;
    }
    return Vector(0.0,0.0,0.0);
}

/// Converts a numpy array to a cytosim vector
Vector2 to_vector2(pyarray arr) {
    try {
        py::buffer_info buf1 = arr.request();
        real *ptr1 = (real *) buf1.ptr;
        return Vector2(ptr1);
    }
    catch ( Exception & e ) {
            e << "Unable to convert numpy array to Vector" ;
    }
    return Vector2(0.0,0.0);
}

/// Converts numpy array to cytosim torque (1,2D : real, 3D: vector)
Torque to_torque(pyarray arr) {
    try {
        py::buffer_info buf1 = arr.request();
        real *ptr1 = (real *) buf1.ptr;
#if ( DIM==3 )
        return Torque(ptr1);
#else
        return Torque(*ptr1);
#endif
    }
    catch ( Exception & e ) {
            e << "Unable to convert numpy array to Vector" ;
    }
#if ( DIM==3 )
    return Torque(0.0,0.0,0.0);
#else
    return Torque(0.0);
#endif
}

/// converts a Glossary pair to a python dict
py::dict * pair_to_dict(Glossary::pair_type const & pair) {
    py::dict * dico = new py::dict;
    (*dico)[ py::str(std::get<0>(pair)) ]  = py::cast(std::get<1>(pair)) ;
    return dico;
}

/// converts a Glossary map to a python dict
py::dict * map_to_dict(Glossary::map_type const & mappe) {
    py::dict * dico = new py::dict;
    for (const auto &[name, rec] : mappe) {
            (*dico)[py::str(name)] = py::cast(rec);
        }
    return dico;
}

/// Converts a string to a glossary
Glossary * str_to_glos(std::string str) {
    Glossary * glos = new Glossary(str);
    return glos;
}

#endif
