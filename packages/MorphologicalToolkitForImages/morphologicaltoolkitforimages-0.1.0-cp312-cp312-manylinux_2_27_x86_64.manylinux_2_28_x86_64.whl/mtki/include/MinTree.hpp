#pragma once

#include "MorphologicalTree.hpp"

class MinTree : public MorphologicalTree {
    public:
        MinTree(py::array image, float adjacencyRadius=1.5);

        ~MinTree();
};
