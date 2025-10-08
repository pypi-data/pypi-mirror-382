#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

#include "../include/MorphologicalTree.hpp"

namespace py = pybind11;

void bind_MorphologicalTree(py::module_ &m) {
    py::class_<MorphologicalTree>(m, "MorphologicalTree")
    .def(py::init<py::object, float, function<bool(uint32_t, uint32_t)>>());
}
