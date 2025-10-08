#include <pybind11/pybind11.h>
#include "../include/MinTree.hpp"

namespace py = pybind11;

void bind_MinTree(py::module_ &m) {
    py::class_<MinTree, MorphologicalTree>(m, "MinTree")
    .def(py::init<py::array, float>())

    .def_property_readonly(
        "root",
        &MorphologicalTree::getRoot,
        py::return_value_policy::reference,
        "Ponteiro para o nó raiz da árvore."
    )

    .def_property_readonly(
        "nodes",
        &MorphologicalTree::getNodes,
        py::return_value_policy::reference,
        "Lista de ponteiros para os nós da árvore."
    )

    .def_property_readonly(
        "adjacency_radius",
        &MorphologicalTree::getAdjacencyRadius,
        "Raio de vizinhança utilizado na construção da árvore."
    )

    .def_property_readonly(
        "residues",
        &MorphologicalTree::getResidues,
        "Raio de vizinhança utilizado na construção da árvore."
    )

    .def_property_readonly(
        "levels",
        &MorphologicalTree::getLevels,
        "Raio de vizinhança utilizado na construção da árvore."
    )

    .def_property_readonly(
        "small_component",
        &MorphologicalTree::getSmallComponents,
        "Raio de vizinhança utilizado na construção da árvore."
    )

    .def(
        "getNodesById",
        &MorphologicalTree::getNodesById,
        "Lista de ponteiros para os nós da árvore."
    )

    .def(
        "getInfoToDataFrame",
        &MorphologicalTree::getInfoToDataFrame,
        "Lista de ponteiros para os nós da árvore."
    )
    // .def_property_readonly(
    //     "union_find",
    //     &MorphologicalTree::getUnionFind,
    //     "Raio de vizinhança utilizado na construção da árvore."
    // )

    // .def_property_readonly(
    //     "jacobian",
    //     &MorphologicalTree::computeCompactJacobian,
    //     "Jacobiana Compacta"
    // )

    .def(
        "jacobian",
        &MorphologicalTree::computeCompactJacobian,
        "Jacobiana Compacta"
    );
}
