#pragma once

#include <cstdint>

class Pixel{
    private:
        uint32_t row;

        uint32_t col;

    
    public:
        Pixel(uint32_t pixelIndex, uint32_t width, uint32_t height);

        Pixel(uint32_t row, uint32_t col);

        ~Pixel();

        uint32_t getRow() const;

        uint32_t getCol() const;
};
