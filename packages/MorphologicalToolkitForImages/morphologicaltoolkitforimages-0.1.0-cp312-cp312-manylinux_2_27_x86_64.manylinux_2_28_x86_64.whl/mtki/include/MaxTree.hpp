#pragma once

#include "MorphologicalTree.hpp"

class MaxTree : public MorphologicalTree {
    public:
        MaxTree(py::array image, float adjacencyRadius=1.5);

        ~MaxTree();
};
