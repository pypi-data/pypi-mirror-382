#pragma once

#include "../Node.hpp"
#include "../AttributesWrapper.hpp"

#include <cstdint>

class IncrementalAttributesProcessor {
    public:
        virtual void preOrder(const Node* node, AttributesWrapper& attributes) const; // = 0; // Esse 0 indica que a classe é puramente virtual e nunca será implementada pela classe base

        virtual void inOrder(const Node* node, AttributesWrapper& attributes) const; // = 0; // Esse 0 indica que a classe é puramente virtual e nunca será implementada pela classe base

        virtual void postOrder(const Node* node, AttributesWrapper& attributes) const; // = 0; // Esse 0 indica que a classe é puramente virtual e nunca será implementada pela classe base

        virtual ~IncrementalAttributesProcessor() = default;
};
