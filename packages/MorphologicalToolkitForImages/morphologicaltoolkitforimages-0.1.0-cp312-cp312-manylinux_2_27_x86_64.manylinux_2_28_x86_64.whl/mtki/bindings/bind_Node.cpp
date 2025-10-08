#include <pybind11/pybind11.h>
#include <pybind11/stl.h>


#include "../include/Node.hpp"

namespace py = pybind11;

void bind_Node(py::module_ &m) {
    py::class_<Node>(m, "Node")
        .def(py::init<uint32_t, uint32_t, uint8_t, Pixel>())
        .def(py::init<uint32_t, uint32_t, uint8_t, Pixel, Node*>())
        .def_property_readonly(
            "id",
            &Node::getId
        )

        .def_property(
            "parent",
            &Node::getParent,
            &Node::setParent
        )

        .def_property_readonly(
            "children",
            &Node::getChildren,
            py::return_value_policy::reference,
            "Retorna a lista de ponteiros para os filhos."
        )

        .def_property_readonly(
            "cnps",
            &Node::getCNPs,
            "Retorna a lista de pixels CNPs do nó."
        )

        .def_property_readonly(
            "pixelsOfCC",
            &Node::getPixelsOfCCs,
            py::return_value_policy::reference,
            "Retorna a lista de pixels CNPs do nó."
        )

        .def_property_readonly(
            "level",
            &Node::getLevel,
            "Retorna a lista de pixels CNPs do nó."
        )

        .def_property_readonly(
            "residue",
            &Node::getResidue,
            "Retorna a lista de pixels CNPs do nó."
        )

        .def_property_readonly(
            "representant",
            &Node::getRepresentant,
            "Retorna a lista de pixels CNPs do nó."
        )

        .def_property_readonly(
            "top",
            &Node::getTop,
            "Retorna a lista de pixels CNPs do nó."
        )

        .def_property_readonly(
            "left",
            &Node::getLeft,
            "Retorna a lista de pixels CNPs do nó."
        )

        .def_property_readonly(
            "bottom",
            &Node::getBottom,
            "Retorna a lista de pixels CNPs do nó."
        )

        .def_property_readonly(
            "right",
            &Node::getRight,
            "Retorna a lista de pixels CNPs do nó."
        )
        
        .def(
            "getInfoToDataFrame",
            &Node::getInfoToDataFrame,
            "Lista de ponteiros para os nós da árvore."
        );
}
