#include <cuda_runtime.h>

__global__ void badKernel(float *input, float *output) {
    __shared__ float scratch[64];
    int idx = threadIdx.x + blockIdx.x * blockDim.x;

    // No bounds check before indexing
    scratch[idx] = input[idx];

    // Another write without a barrier
    scratch[idx + 1] = scratch[idx] * 2.0f;

    if (threadIdx.x % 2 == 0) {
        output[idx] = scratch[idx + threadIdx.x];
    }
}
