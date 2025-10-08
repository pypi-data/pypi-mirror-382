#include "../include/Pixel.hpp"

Pixel::Pixel(uint32_t pixelIndex, uint32_t width, uint32_t height):
    row(pixelIndex / width),
    col(pixelIndex % width)
{
    // TODO: Implementar uma validação para ver se não está ultrapassando os limites do dominio
}

Pixel::Pixel(uint32_t row, uint32_t col):
    row(row),
    col(col)
{}

Pixel::~Pixel(){}

uint32_t Pixel::getRow() const{
    return this->row;
}

uint32_t Pixel::getCol() const{
    return this->col;
}
