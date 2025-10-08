#pragma once

#include <torch/torch.h>

class Utils {
    public:

        static torch::Tensor toTensor(void* data_ptr, uint32_t rows, uint32_t cols, torch::Dtype dtype);

};
