#include "../include/MinTree.hpp"

MinTree::MinTree(py::array image, float adjacencyRadius):
    MorphologicalTree(image, adjacencyRadius, ([](uint8_t a, uint8_t b){ return a < b; }))
{}

MinTree::~MinTree(){}
