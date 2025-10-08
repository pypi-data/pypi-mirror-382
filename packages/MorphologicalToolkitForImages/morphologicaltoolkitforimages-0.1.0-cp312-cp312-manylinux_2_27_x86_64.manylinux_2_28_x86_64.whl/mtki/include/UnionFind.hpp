#pragma once

#include <pybind11/numpy.h>

#include <vector>
#include <cstdint>
#include <numeric>
#include <algorithm>
#include <cmath>
#include <iostream>
#include <cstdlib>
#include <optional>

#include <unistd.h> // sleep

using namespace std;
namespace py = pybind11;

class UnionFind {

    private:
        vector<uint32_t> parent;

        function<bool(uint8_t, uint8_t)> pixelSortCompare;

        vector<uint32_t> sortedPixels;


    public:
        UnionFind(const uint8_t* image, const float& adjacencyRadius, uint32_t width, uint32_t height, uint32_t size, function<bool(uint8_t, uint8_t)> pixelSortCompare);

        ~UnionFind();

        vector<uint32_t> sortPixels(const uint8_t* image, const uint32_t& size);

        vector<int32_t> computeOffsets(const float& adjacencyRadius, uint32_t width);

        void unionSets(uint32_t p, int32_t q, vector<optional<uint32_t>>& zpar);
        
        uint32_t findRoot(uint32_t q, vector<optional<uint32_t>>& zpar);

        void canonize(const uint8_t* image, const vector<uint32_t>& sortedPixels);

        vector<uint32_t> getParents() const;

        vector<uint32_t> getSortedPixels() const;


};
