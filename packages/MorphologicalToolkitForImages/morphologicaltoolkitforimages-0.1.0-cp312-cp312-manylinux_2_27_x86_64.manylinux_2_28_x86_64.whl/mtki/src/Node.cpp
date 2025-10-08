#include "../include/Node.hpp"


/* Constructors */

Node::Node(uint32_t id, uint32_t representant, uint8_t level, Pixel pixel):
    id(id),
    representant(representant),
    level(level),
    parent(nullptr),
    top(pixel.getRow()),
    left(pixel.getCol()),
    bottom(pixel.getRow()),
    right(pixel.getCol())
{}

Node::Node(uint32_t id, uint32_t representant, uint8_t level, Pixel pixel, Node* parent):
    id(id),
    representant(representant),
    level(level),
    parent(parent),
    top(pixel.getRow()),
    left(pixel.getCol()),
    bottom(pixel.getRow()),
    right(pixel.getCol())
{
    this->parent->addChild(this);
}

Node::~Node(){
    for(Node* child : this->children){
        delete child;
    }
}

/* Aux Functions */

map<string, InfoValue> Node::getInfoToDataFrame(){
    map<string, InfoValue> infoMap;

    // TODO: Criar função dedicada a retornar Id dos filhos
    vector<uint32_t> childrenIds(this->children.size());
    for(const auto& child : this->children) {
        childrenIds.push_back(child->getId());
    }

    infoMap["Id"] = this->id;
    infoMap["Level"] = this->level;    
    infoMap["Residue"] = this->getResidue();    
    infoMap["ParentId"] = this->parent != nullptr ? this->parent->getId() : 0;    
    infoMap["Children"] = childrenIds;    
    infoMap["PixelsOfCC"] = this->pixelsOfCC;    
    infoMap["CNPs"] = this->cnps;    
    infoMap["Area"] = this->pixelsOfCC.size();

    return infoMap;
}

/* Getters and Setters */

uint32_t Node::getId() const{
    // TODO: validar para raiz
    return this->id;
}

uint8_t Node::getLevel() const{
    return this->level;
}

int8_t Node::getResidue() const{
    return this->parent == nullptr ? this->level : this->level - this->parent->level;
}

Node* Node::getParent() const{
    return this->parent;
}

vector<Node*> Node::getChildren() const{
    return this->children;
}

vector<uint32_t> Node::getCNPs() const{
    return this->cnps;
}

vector<uint32_t> Node::getPixelsOfCCs() const{
    return this->pixelsOfCC;
}

uint32_t Node::getTop() const{
    return this->top;
}

uint32_t Node::getLeft() const{
    return this->left;
}

uint32_t Node::getBottom() const{
    return this->bottom;
}

uint32_t Node::getRight() const{
    return this->right;
}

uint32_t Node::getRepresentant() const{
    return this->representant;
}

void Node::setLevel(uint8_t level){
    this->level = level;
}

void Node::setParent(Node* parent){
    this->parent = parent;
}

void Node::addChild(Node* child){
    this->children.push_back(child);
}

void Node::addCNP(uint32_t pixelIndex, Pixel pixel){
    this->cnps.push_back(pixelIndex);

    this->setTop(pixel.getRow());
    this->setLeft(pixel.getCol());
    this->setBottom(pixel.getRow());
    this->setRight(pixel.getCol());
}

void Node::setBoundingBox(const Node* node){
    this->setTop(node->getTop());
    this->setLeft(node->getLeft());
    this->setBottom(node->getBottom());
    this->setRight(node->getRight());
}

void Node::setTop(uint32_t top){
    // this->top = this->top < top ? this->top : top;
    this->top = min(this->top, top);
}

void Node::setLeft(uint32_t left){
    // this->left = this->left < left ? this->left : left;
    this->left = min(this->left, left);
}

void Node::setBottom(uint32_t bottom){
    // this->bottom = this->bottom > bottom ? this->bottom : bottom;
    this->bottom = max(this->bottom, bottom);
}

void Node::setRight(uint32_t right){
    // this->right = this->right > right ? this->right : right;
    this->right = max(this->right, right);
}

void Node::addCNP(uint32_t pixel){
    this->cnps.push_back(pixel);
    this->pixelsOfCC.push_back(pixel);

    if(this->parent != nullptr){
        this->parent->addPixelOfCC(pixel);
    }
}

void Node::addPixelOfCC(uint32_t pixel){
    this->pixelsOfCC.push_back(pixel);

    if(this->parent != nullptr){
        this->parent->addPixelOfCC(pixel);
    }
}

