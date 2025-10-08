#pragma once

#include <vector>
#include <stdexcept>
#include <cstdint>

using namespace std;

class AttributesWrapper {
    private:
        vector<double> data;

        uint32_t num_nodes;

        uint32_t num_attrs;

    public:
        AttributesWrapper(uint32_t nodes, uint32_t attrs);

        ~AttributesWrapper();

        double& operator()(uint32_t node, uint32_t attr);

        const double& operator()(uint32_t node, uint32_t attr) const;

        uint32_t getRows() const;

        uint32_t getCols() const;

        double* getRawData();

        const vector<double>& getData() const;
};
