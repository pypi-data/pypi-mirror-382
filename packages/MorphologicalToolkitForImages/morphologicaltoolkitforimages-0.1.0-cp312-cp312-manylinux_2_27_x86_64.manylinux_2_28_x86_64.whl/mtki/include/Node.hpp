#pragma once

#include "../include/Pixel.hpp"
#include <pybind11/stl.h>

#include <iostream>
#include <vector>
#include <cstdint>
#include <algorithm>
#include <map>
#include <vector>

using namespace std;

using InfoValue = variant<uint32_t, uint8_t, size_t, int8_t, vector<uint32_t>, string>; // TODO: Entender como isso realmente funciona.

class Node {
    private:
        /* Attributes */

        /* const */ uint32_t id;

        uint32_t representant;

        uint8_t level;

        Node* parent;

        vector<Node*> children;

        vector<uint32_t> cnps;

        vector<uint32_t> pixelsOfCC;


        // TODO: Confirmar se a caixa delimitadora deve conter apenas os CNPs ou os pixels de nós descendentes também.
        uint32_t top;

        uint32_t left;

        uint32_t bottom;

        uint32_t right;

    public:
        /* Constructors */

        Node(uint32_t id, uint32_t representant, uint8_t level, Pixel pixel);

        Node(uint32_t id, uint32_t representant, uint8_t level, Pixel pixel, Node* parent);

        ~Node();

        /* Aux Functions */

        bool isRoot();

        map<string, InfoValue> getInfoToDataFrame();

        /* Getters e Setters */

        uint32_t getId() const;

        uint8_t getLevel() const;

        int8_t getResidue() const;

        Node* getParent() const;

        vector<Node*> getChildren() const;

        vector<uint32_t> getCNPs() const;

        vector<uint32_t> getPixelsOfCCs() const;

        uint32_t getTop() const;
        
        uint32_t getLeft() const;
        
        uint32_t getBottom() const;
        
        uint32_t getRight() const;
        
        uint32_t getRepresentant() const;

        void setLevel(uint8_t level);

        void setParent(Node* parent);

        void addChild(Node* child);

        void addCNP(uint32_t pixelIndex, Pixel pixel);

        void setBoundingBox(const Node* node);

        void setTop(uint32_t top);

        void setLeft(uint32_t left);

        void setBottom(uint32_t bottom);

        void setRight(uint32_t right);

        void addCNP(uint32_t);

        void addPixelOfCC(uint32_t);
};
