#include "../include/AttributesWrapper.hpp"

// TODO: Revisar essa classe inteira ()

AttributesWrapper::AttributesWrapper(uint32_t nodes, uint32_t attrs):
    data(nodes * attrs, 0.0),
    num_nodes(nodes),
    num_attrs(attrs)
{}

AttributesWrapper::~AttributesWrapper(){}


double& AttributesWrapper::operator()(uint32_t node, uint32_t attr){
    if(node >= num_nodes || attr >= num_attrs){
        throw std::out_of_range("AttributeMatrix access out of range");
    }

    return data[node * num_attrs + attr];
}

const double& AttributesWrapper::operator()(uint32_t node, uint32_t attr) const{
    if(node >= num_nodes || attr >= num_attrs){
        throw std::out_of_range("AttributeMatrix access out of range");
    }

    return data[node * num_attrs + attr];
}

uint32_t AttributesWrapper::getRows() const{
    return this->num_nodes;
}

uint32_t AttributesWrapper::getCols() const{
    return this->num_attrs;
}

double* AttributesWrapper::getRawData(){
    return this->data.data();
}

const vector<double>& AttributesWrapper::getData() const {
    return data;
}