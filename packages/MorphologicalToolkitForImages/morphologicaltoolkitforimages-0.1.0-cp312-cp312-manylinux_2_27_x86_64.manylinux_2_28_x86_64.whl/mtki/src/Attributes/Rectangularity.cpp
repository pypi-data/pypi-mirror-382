#include "../../include/Attributes/Rectangularity.hpp"

void Rectangularity::postOrder(const Node* node, AttributesWrapper& attributes) const{
    attributes(node->getId(), 4) = attributes(node->getId(), 0) / (attributes(node->getId(), 2) * attributes(node->getId(), 3));
}
