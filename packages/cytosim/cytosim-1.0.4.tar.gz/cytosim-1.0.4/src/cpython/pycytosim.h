#ifndef REPORT_PYTHON_H
#define REPORT_PYTHON_H

//#include "simul.h"
#include "sim_thread.h"
#include "messages.h"
#include "glossary.h"
#include "exceptions.h"
#include "print_color.h"
#include "filepath.h"
#include "splash.h"
#include <csignal>
#include "unistd.h"
#include "python_frame.h"
#include "simul_modules.h"
#include "interface_modules.h"
#include "fiber_modules.h"
#include "solid_modules.h"
#include "space_modules.h"
#include "point_modules.h"
#include "thread_modules.h"
#include "single_modules.h"
#include "lattice_modules.h"
#include "meca_modules.h"
#include "couple_modules.h"
#include "organizer_modules.h"
#include "object_modules.h"
#include "hand_modules.h"
#include "glossary_modules.h"
#include <functional>

namespace py = pybind11;

void bar(void);
class SimThread;

void prepare_module(py::module_ m) {
/// Loading properties into the module
    load_thread_classes(m);
    load_interface_classes(m);
    load_object_classes(m);
    load_meca_classes(m);
    load_point_classes(m);
    auto pysim = load_simul_classes(m);
    load_glossary_classes(m);
    load_solid_classes(m);
    load_fiber_classes(m);
    load_hand_classes(m);
    load_space_classes(m);
    load_single_classes(m);
    load_couple_classes(m);
    load_organizer_classes(m);
    
    declare_lattice(m, (uint8_t)1, "Lattice_uint8");
    declare_lattice(m, (uint16_t)1, "Lattice_uint16");
    declare_lattice(m, (uint64_t)1, "Lattice_uint64");
    declare_lattice(m, (uint32_t)1, "Lattice_uint32");
    declare_lattice(m, (real)1.0, "Lattice_real");
    
    /// We declare object groups
    // We can later add additional def to any of these groups
    //auto fibs = declare_group(m, ObjGroup<Fiber,FiberProp>(), ObjVec<Fiber>(), "Fiber");
    auto fibs = declare_group(m, ObjGroup<Fiber,FiberProp>(), "FiberGroup");
    auto sols = declare_group(m, ObjGroup<Solid,SolidProp>(), "SolidGroup");
    auto spas = declare_group(m, ObjGroup<Space,SpaceProp>(), "SpaceGroup");
    auto beds = declare_group(m, ObjGroup<Bead,BeadProp>(), "BeadGroup");
    auto sfrs = declare_group(m, ObjGroup<Sphere,SphereProp>(), "SphereGroup");
    auto orgs = declare_group(m, ObjGroup<Organizer,Property>(), "OrganizerGroup");
    auto sins = declare_group(m, ObjGroup<Single,SingleProp>(), "SingleGroup");
    auto cous = declare_group(m, ObjGroup<Couple,CoupleProp>(), "CoupleGroup");
}

#endif
