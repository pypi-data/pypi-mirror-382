#pragma once

#include "IncrementalAttributesProcessor.hpp"

class Volume : public IncrementalAttributesProcessor{
    public:
        virtual void preOrder(const Node* node, AttributesWrapper& attributes) const override;

        virtual void inOrder(const Node* node, AttributesWrapper& attributes) const override;
};