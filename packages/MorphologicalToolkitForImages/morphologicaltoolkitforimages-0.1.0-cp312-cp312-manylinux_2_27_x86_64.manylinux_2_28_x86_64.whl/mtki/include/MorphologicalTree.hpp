#pragma once

#include <pybind11/numpy.h>
#include <torch/torch.h>
// #include <torch/script.h>  // Se for usar TorchScript

#include "../include/PlatformHandler.hpp"
#include "../include/Node.hpp"
#include "../include/UnionFind.hpp"
#include "../include/Pixel.hpp"

#include <iostream>
#include <list>
#include <cstdint>
#include <string>
#include <map>
#include <set>


using namespace std;
namespace py = pybind11;

class MorphologicalTree{
    private:
        /* Attributes */

        Node* root;

        map<uint32_t, Node*> nodes;

        float adjacencyRadius;

        vector<uint32_t> pixelToSmallComponent;

        uint32_t width;

        uint32_t height;


    public:
        /* Constructors */

        MorphologicalTree(py::array image, float adjacencyRadius, function<bool(uint32_t, uint32_t)> pixelSortCompare);

        ~MorphologicalTree();


        /* Aux Methods */

        void computeTree(const uint8_t* image, const vector<uint32_t>& sortedPixels, const vector<uint32_t>& parent);

        torch::Tensor computeCompactJacobian(string_view deviceStr="cuda") const;

        vector<uint32_t> getSubtreeIds(const Node* subtreeRoot) const;

        vector<map<string, InfoValue>> getInfoToDataFrame();


        /* Getters and Setters */

        Node* getRoot() const;

        vector<Node*> getNodes() const;

        const float getAdjacencyRadius() const;

        torch::Tensor getLevels() const;

        torch::Tensor getResidues() const;

        py::array_t<uint8_t> getImage() const;

        vector<uint32_t> getSmallComponents() const;

        uint32_t getWidth() const;

        uint32_t getHeight() const;

        vector<Node*> getNodesById(vector<uint32_t> idList) const;

        void setRoot(Node* root);

        void setAdjacencyRadius(float adjacencyRadius);

};