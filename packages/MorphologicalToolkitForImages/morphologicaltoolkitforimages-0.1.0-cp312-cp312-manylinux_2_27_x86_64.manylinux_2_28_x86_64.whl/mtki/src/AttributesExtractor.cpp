#include "../include/AttributesExtractor.hpp"

torch::Tensor AttributesExtractor::computeAttributes(const MorphologicalTree& tree){
    AttributesWrapper attributes(tree.getNodes().size(), 5);

    computeIncrementalAttributes(tree.getRoot(), attributes);

    return Utils::toTensor(attributes.getRawData(), attributes.getRows(), attributes.getCols(), torch::kFloat64);
}

void AttributesExtractor::computeIncrementalAttributes(const Node* node, AttributesWrapper& attributes){
    preOrderProcess(node, attributes);

    for(const Node* child : node->getChildren()){
        computeIncrementalAttributes(child, attributes);

        inOrderProcess(child, attributes);
    }

    postOrderProcess(node, attributes);
}

void AttributesExtractor::preOrderProcess(const Node* node, AttributesWrapper& attributes){
    for(const auto& processor : getProcessors()){
        processor->preOrder(node, attributes);
    }
}

void AttributesExtractor::inOrderProcess(const Node* node, AttributesWrapper& attributes){
    // Cenário onde o node é a raiz
    if(node->getParent() == nullptr){
        return;
    }

    // Ajusta a caixa delimitadora para levar em conta os nós descendentes
    node->getParent()->setBoundingBox(node);

    for(const auto& processor : getProcessors()){
        processor->inOrder(node, attributes);
    }
}

void AttributesExtractor::postOrderProcess(const Node* node, AttributesWrapper& attributes){
    for(const auto& processor : getProcessors()){
        processor->postOrder(node, attributes);
    }
}


vector<unique_ptr<IncrementalAttributesProcessor>> AttributesExtractor::processors;

const vector<unique_ptr<IncrementalAttributesProcessor>>& AttributesExtractor::getProcessors(){
    if (processors.empty()){
        processors.emplace_back(std::make_unique<Area>());              // 0
        processors.emplace_back(std::make_unique<Volume>());            // 1
        processors.emplace_back(std::make_unique<Dimensions>());        // 2, 3
        processors.emplace_back(std::make_unique<Rectangularity>());    // 4
    }

    return processors;
}