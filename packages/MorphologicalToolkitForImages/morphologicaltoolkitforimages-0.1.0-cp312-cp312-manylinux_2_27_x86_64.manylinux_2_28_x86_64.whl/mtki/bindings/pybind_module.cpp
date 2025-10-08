#include <pybind11/pybind11.h>

namespace py = pybind11;

// Declarar o protótipo
void bind_Node(py::module_ &);
void bind_MorphologicalTree(py::module_ &);
void bind_MaxTree(py::module_ &);
void bind_MinTree(py::module_ &);
// void bind_UnionFind(py::module_ &);
void bind_AttributesExtractor(py::module_ &);


PYBIND11_MODULE(mtki, m) {
    m.doc() = "Biblioteca para geração de árvores morfológicas, extração de atributos e aplicação de filtros em imagens.";

    bind_Node(m);
    bind_MorphologicalTree(m);
    bind_MaxTree(m);
    bind_MinTree(m);
    // bind_UnionFind(m);
    bind_AttributesExtractor(m);

}
