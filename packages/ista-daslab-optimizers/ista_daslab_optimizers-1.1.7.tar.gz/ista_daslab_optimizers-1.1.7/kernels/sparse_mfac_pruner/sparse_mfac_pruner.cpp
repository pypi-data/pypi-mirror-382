#include <torch/extension.h>
#include <c10/cuda/CUDAGuard.h>
#include "../utils.h"

// CUDA methods
void compute_row_cuda(
    torch::Tensor V,
    torch::Tensor g,
    torch::Tensor q,
    torch::Tensor out,
    int row,
    int m,
    float damp,
    int N,
    int B,
    int nbits,
);

// C++ methods callable from Python
void compute_row(
    torch::Tensor V,
    torch::Tensor g,
    torch::Tensor q,
    torch::Tensor out,
    int row,
    int m,
    float damp,
    int N,
    int B
) {
	CHECK_INPUT(V);
	CHECK_INPUT(g);
	CHECK_INPUT(q);
	CHECK_INPUT(out);

    int nbits;

    if(IS_BF16(V)) {
        ASSERT_BF16(g);
        ASSERT_BF16(q);
        ASSERT_BF16(out);
        nbits = 16;
    } else if(IS_FLOAT(V)) {
        ASSERT_FLOAT(g);
        ASSERT_FLOAT(q);
        ASSERT_FLOAT(out);
        nbits = 32;
    }

	const at::cuda::OptionalCUDAGuard device_guard(device_of(V));
    compute_row_cuda(V, g, q, out, row, m, damp, N, B, nbits);
}


PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
	m.def("compute_row", &compute_row, "Computes one row of matrix V used for pruning");
}
