#include <cuda_runtime.h>

__global__ void goodKernel(const float *input, float *output, int n) {
    __shared__ float scratch[64];
    int idx = threadIdx.x + blockIdx.x * blockDim.x;
    if (idx >= n) {
        return;
    }

    scratch[threadIdx.x] = input[idx];
    __syncthreads();

    output[idx] = scratch[threadIdx.x] * 0.5f;
}
