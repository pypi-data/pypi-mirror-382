#pragma once

#include "IncrementalAttributesProcessor.hpp"

class Rectangularity : public IncrementalAttributesProcessor{
    public:
        virtual void postOrder(const Node* node, AttributesWrapper& attributes) const override;
};