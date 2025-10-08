#include <pybind11/pybind11.h>
#include "../include/AttributesExtractor.hpp"

namespace py = pybind11;

void bind_AttributesExtractor(py::module_ &m) {
    m.def(
        "Attributes",
        &AttributesExtractor::computeAttributes,
        py::arg("tree"),
        "Extrai os atributos da árvore morfológica e retorna um tensor"
    );
}
