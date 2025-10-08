#include "../../include/Attributes/Dimensions.hpp"

void Dimensions::postOrder(const Node* node, AttributesWrapper& attributes) const{
    // Altura do nó
    attributes(node->getId(), 2) = node->getBottom() - node->getTop() + 1;

    // Largura do nó
    attributes(node->getId(), 3) = node->getRight() - node->getLeft() + 1;
}
