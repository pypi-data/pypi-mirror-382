#include "../../include/Attributes/Area.hpp"

void Area::preOrder(const Node* node, AttributesWrapper& attributes) const{
    attributes(node->getId(), 0) = static_cast<double>(node->getCNPs().size());
}

void Area::inOrder(const Node* node, AttributesWrapper& attributes) const{
    attributes(node->getParent()->getId(), 0) += attributes(node->getId(), 0);
}