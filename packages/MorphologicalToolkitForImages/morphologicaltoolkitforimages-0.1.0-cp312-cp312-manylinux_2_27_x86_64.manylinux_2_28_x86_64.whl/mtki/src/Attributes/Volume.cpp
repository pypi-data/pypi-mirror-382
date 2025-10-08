#include "../../include/Attributes/Volume.hpp"

void Volume::preOrder(const Node* node, AttributesWrapper& attributes) const{
    attributes(node->getId(), 1) = attributes(node->getId(), 0) * node->getLevel();
}

void Volume::inOrder(const Node* node, AttributesWrapper& attributes) const{
    attributes(node->getParent()->getId(), 1) += attributes(node->getId(), 1);
}