#pragma once

#include "IncrementalAttributesProcessor.hpp"

class Dimensions : public IncrementalAttributesProcessor{
    public:
        virtual void postOrder(const Node* node, AttributesWrapper& attributes) const override;
};