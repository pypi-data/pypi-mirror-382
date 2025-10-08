#include "../include/Utils.hpp"

torch::Tensor Utils::toTensor(void* data_ptr, uint32_t rows, uint32_t cols, torch::Dtype dtype){
    return torch::from_blob(
        data_ptr,
        {rows, cols},
        dtype
    ).clone();
}