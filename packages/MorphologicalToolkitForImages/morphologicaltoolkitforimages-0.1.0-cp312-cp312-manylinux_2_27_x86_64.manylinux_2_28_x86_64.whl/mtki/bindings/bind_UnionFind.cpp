#include <pybind11/pybind11.h>
#include "../include/UnionFind.hpp"

namespace py = pybind11;

void bind_UnionFind(py::module_ &m) {
    py::class_<UnionFind>(m, "UnionFind")
        .def(py::init<uint8_t*, const float&, uint32_t, uint32_t, uint32_t, function<bool(uint32_t, uint32_t)>>());

        // .def_property_readonly(
        //     "parent",
        //     &UnionFind::getParent
        // );
}
