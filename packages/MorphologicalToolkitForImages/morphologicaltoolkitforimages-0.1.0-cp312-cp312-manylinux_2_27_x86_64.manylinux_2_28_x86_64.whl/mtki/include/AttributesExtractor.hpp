#pragma once

#include <torch/torch.h>

#include "MorphologicalTree.hpp"
// #include "Attributes/IncrementalAttributesProcessor.hpp"
#include "AttributesWrapper.hpp"
#include "Attributes/Area.hpp"
#include "Attributes/Volume.hpp"
#include "Attributes/Dimensions.hpp"
#include "Attributes/Rectangularity.hpp"
#include "Utils.hpp"

#include <iostream>

using namespace std;

class AttributesExtractor {
    private: 
        static vector<unique_ptr<IncrementalAttributesProcessor>> processors;

    public:
        static const vector<unique_ptr<IncrementalAttributesProcessor>>& getProcessors();

        static torch::Tensor computeAttributes(const MorphologicalTree& tree);

        static void computeIncrementalAttributes(const Node* node, AttributesWrapper& attributes);

        static void preOrderProcess(const Node* node, AttributesWrapper& attributes);

        static void inOrderProcess(const Node* node, AttributesWrapper& attributes);

        static void postOrderProcess(const Node* node, AttributesWrapper& attributes);
};
