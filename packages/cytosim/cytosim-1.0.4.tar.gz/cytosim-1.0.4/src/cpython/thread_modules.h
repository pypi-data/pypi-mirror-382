#include "sim_thread.h"
#include <pybind11/pybind11.h>
#include "python_utilities.h"
#include "vector3.h"
//#include <pybind11/numpy.h>
//#include <pybind11/stl.h>
namespace py = pybind11;

class SimThread;

/// a utility to enrich the cytosim python module
void load_thread_classes(py::module_ &m) {
    py::class_<SimThread>(m, "SimThread")
        .def("run", &SimThread::run)
        .def("prolong_run", &SimThread::prolong_run)
        .def("hold", &SimThread::hold)
        .def("lock", &SimThread::lock)
        .def("unlock", &SimThread::unlock)
        .def("trylock", &SimThread::trylock)
        .def("cond_wait", &SimThread::cond_wait)
        .def("signal", &SimThread::signal)
        .def("period", &SimThread::period)
        .def("alive", &SimThread::alive)
        .def("start", &SimThread::start)
        .def("prolong", &SimThread::prolong)
        .def("stop", &SimThread::stop)
        .def("cancel", &SimThread::cancel)
        .def("restart", &SimThread::restart)
        .def("eraseSimul", &SimThread::eraseSimul)
        .def("reloadParameters", &SimThread::reloadParameters)
        .def("evaluate", &SimThread::evaluate)
        .def("exportObjects", &SimThread::exportObjects)
        .def("openFile", &SimThread::openFile)
        .def("goodFile", &SimThread::goodFile)
        .def("eof", &SimThread::eof)
        .def("rewindFile", &SimThread::rewindFile)
        .def("loadFrame", &SimThread::loadFrame)
        .def("loadNextFrame", &SimThread::loadNextFrame)
        .def("loadLastFrame", &SimThread::loadLastFrame)
        .def("currentFrame", &SimThread::currentFrame)
        .def("handle", &SimThread::handle)
        .def("createHandle",  [](SimThread * thr, pyarray pos, real range) 
            {   Vector p = to_vector(pos);
#if (DIM==3)
                return thr->createHandle(p,range);})
#else
                Vector3 pp = Vector3(p[0],p[1],0);
                return thr->createHandle(pp,range);})
#endif             
        .def("selectClosestHandle",  [](SimThread * thr, pyarray pos, real range) 
            {   Vector p = to_vector(pos);
#if (DIM==3)
                return thr->selectClosestHandle(p,range);})
#else
                Vector3 pp = Vector3(p[0],p[1],0);
                return thr->selectClosestHandle(pp,range);})
#endif 
        .def("moveHandle",  [](SimThread * thr, pyarray pos) 
            {   Vector p = to_vector(pos);
#if (DIM==3)
                return thr->moveHandle(p);})
#else
                Vector3 pp = Vector3(p[0],p[1],0);
                return thr->moveHandle(pp);})
#endif 
        .def("moveHandles",  [](SimThread * thr, pyarray pos) 
            {   Vector p = to_vector(pos);
#if (DIM==3)
                return thr->moveHandles(p);})
#else
                Vector3 pp = Vector3(p[0],p[1],0);
                return thr->moveHandles(pp);})
#endif 
        .def("detachHandle", &SimThread::detachHandle)
        .def("deleteHandles", &SimThread::deleteHandles)
        .def("releaseHandle", &SimThread::releaseHandle)
        .def("openFile", &SimThread::openFile)
        .def("openFile", &SimThread::openFile)
        .def("openFile", &SimThread::openFile);
        
}
