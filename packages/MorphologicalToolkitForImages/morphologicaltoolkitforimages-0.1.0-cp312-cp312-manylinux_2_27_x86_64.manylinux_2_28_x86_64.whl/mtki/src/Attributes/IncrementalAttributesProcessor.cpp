#include "../../include/Attributes/IncrementalAttributesProcessor.hpp"

// TODO: Revisar se essa é uma boa prática, visto que elimmina a obrigatoriedade das subclasses de implementar essas funções

void IncrementalAttributesProcessor::preOrder(const Node* node, AttributesWrapper& attributes) const{}

void IncrementalAttributesProcessor::inOrder(const Node* node, AttributesWrapper& attributes) const{}

void IncrementalAttributesProcessor::postOrder(const Node* node, AttributesWrapper& attributes) const{}