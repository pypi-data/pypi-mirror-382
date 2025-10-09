#include "../utils.h"

__device__ void parallel_reduce(float *mem, long T, long logT, long Tid, long offset=0, bool zerorize=false) {
	/*
		Perform parallel reduce in logarithmic time over the vector mem with T threads (mem has T components).
		If zerorize=true, then set the components of mem to zero after accumulation.
		Use offset > 0 to perform the parallel reduction over a different sequence of size T in mem
		Tid is the current thread id and logT is log2(T).
		Return the sum, which will be located at mem[offset]

		Resources:
			https://shreeraman-ak.medium.com/parallel-reduction-with-cuda-d0ae10c1ae2c
	*/
	long mid = T >> 1; // half of number of threads
	long offset_PLUS_Tid = offset + Tid;
	for(long i = 0; i < logT; ++i) { // perform log2(T) rounds of accumulation
		__syncthreads();
		if(Tid < mid) { // left half accumulates, right half sends to left half
			mem[offset_PLUS_Tid] += mem[offset_PLUS_Tid + mid];
			if(zerorize) {
				mem[offset_PLUS_Tid + mid] = 0.;
			}
		}
		mid >>= 1;
	}
}

__device__ inline void copy_global_to_shmem(void *global,
                                            float *shmem,
                                            int global_start,
                                            int global_end,
                                            int nbits) {
    int T = blockDim.x; // number of threads
    int j_global, j_shmem; // used in for-loops to read from global memory to shared memory
    if(nbits == 16) {
        bfloat16 *bf16_global = (bfloat16*) global;
        //  <------------init------------------> <------stop cond------> <-------next steps-------->
        for(j_global = global_start, j_shmem = 0; j_global < global_end; j_global += T, j_shmem += T) { // coalesced memory access to global
            shmem[j_shmem] = __bfloat162float(bf16_global[j_global]);
        }
    } else if(nbits == 32) {
        float *float_global = (float*) global;
        //  <------------init------------------> <------stop cond------> <-------next steps-------->
        for(j_global = global_start, j_shmem = 0; j_global < global_end; j_global += T, j_shmem += T) { // coalesced memory access to global
            shmem[j_shmem] = float_global[j_global];
        }
    }
}

__global__ void compute_row_kernel(void *global_V,
                                   void *global_g,
                                   void *global_q,
                                   void *global_out,
                                   int row, /* current row in V to be computed */
                                   int m, /* index of the row to compute now using all previous row-1 rows */
                                   float damp,
                                   int N, /* number of Fisher blocks*/
                                   int B, /* size of Fisher Block*/
                                   int nbits) {
    /*
        Computes one row of matrix V from the M-FAC pruner.
        Parameters:
            - global_V: matrix of size m x N x B
            - global_g: matrix of size N x B
            - global_q: matrix of size m x N
            - global_out: matrix of size N x B
            - row: compute global_V[j, :, :] given the previous row-1 rows
            - m: total number of gradients (useful to compute q)
            - N: number of Fisher blocks
            - B: size of a Fisher block

        This kernel loops through the first dimension of V (from 0 to m-1).
        Each CUDA thread block processes row Bid from global_V[i] and global_g (e.g. global_V[i, Bid, :] and global_g[Bid, :], equivalent to one Fisher block)
        Processing these rows can be done in parallel by multiple thread blocks without interfering with each other
        To be efficient with the memory, we use shared memory in the following way:
        - V stores the current row global_V[i, Bid, :] (global_V is read only once)
        - g stores the current row global_g[Bid, :] (global_g is read only once)
        - prods stores the element-wise products V_j * g_j
        - Vout accumulates the row Bid of global_out, which is written only once

                B
            |----------|
          N |     |----------|
            |     |     |----------|
            |-----|     |          |
                  |-----|          |
                        |----------|
    */

	const int Bid = blockIdx.x; // block id
	const int T = blockDim.x; // number of threads
	const int Tid = threadIdx.x; // thread id
	int logT = log_threads(T);

    extern __shared__ float mem[];
    float *V = mem; // size B, stores one row of V
    float *g = mem + B; // size B, stores one row of g
    float *prods = mem + 2 * B; // size B, stores products V*g before summing up.
    float *Vout = mem + 3 * B; // size B, accumulates dot * V

    // predefined constants to avoid computing the same quantities multiple times
    int N_B = N * B;
    int Bid_B = Bid * B;

    // variables
    int i; // iterates through the first dimension of V, from 0 to m-1
    int j, j_global; // universal index variables
    int global_V_dim0_i_block_Bid_start, global_V_dim0_i_block_Bid_end; // start/end indices for V[i, Bid, :]
    int global_g_block_Bid_start = Bid_B, global_g_block_Bid_end = Bid_B + B; // start/end indices for g[Bid, :]
    int global_out_block_Bid_start = Bid_B, global_out_block_Bid_end = Bid_B + B;
    float dot; // stores the dot product between V and g, which are V[i, Bid, :] and g[Bid, :] (e.g. dots[:, Bid])
    float q; // stores the value q[i, Bid]
    float m_float = (float) m;

    // read g[Bid, :] from global memory to shared memory only once
    copy_global_to_shmem(global_g, g, global_g_block_Bid_start, global_g_block_Bid_end, nbits);
    __syncthreads();

    // initialize Vout with damp * g:
    for(j = 0; j < B; j += T) {
        Vout[j] = damp * g[j];
    }
    __syncthreads();

    // compute scalar products, stored in dots
    for(i = 0; i < row; ++i) { // iterate through the first dimension of V

        // read q[i, Bid] only in thread 0
        if(Tid == 0) { // read q only on the first thread and save it in prods[0] (prods will be overwritten with V * g after that)
            if(nbits == 16) {
                bfloat16 *bf16_global_q = (bfloat16*) global_q;
                prods[0] = __bfloat162float(bf16_global_q[i * N + Bid]);
            } else if (nbits == 32) {
                float *float_global_q = (float*) global_q;
                prods[0] = float_global_q[i * N + Bid];
            }
        }
        __syncthreads();

        q = prods[0]; // this will be run on all threads (send q to all threads via prods[0])

        __syncthreads();

        // read V[i, Bid, :] from global memory to shared memory only once
        global_V_dim0_i_block_Bid_start = i * N_B + // go to the beginning of row i
                                         Bid_B; // go to the beginning of block Bid on row i
        global_V_dim0_i_block_Bid_end = global_V_dim0_i_block_Bid_start + B;
        copy_global_to_shmem(global_V, V, global_V_dim0_i_block_Bid_start, global_V_dim0_i_block_Bid_end, nbits);
        __syncthreads();

        // compute dot product between V and g (e.g. element-wise multiplication)
        for(j = 0; j < B; j += T) {
            prods[j] = V[j] * g[j];
        }
        __syncthreads();

        // TODO: how to compute q[row] directly here?

        // compute the sum of all elements in prods (result will be stored at prods[0])
        parallel_reduce(prods, T, logT, Tid, 0, false);
        dot = prods[0]; // all threads will have the dot product in this variable

        // write m + dot in global_q[i, Bid] only if row < m
        if(Tid == 0) {
            if(row < m) { // computing rows of V is not finished
                if(nbits == 16) {
                    bfloat16 *bf16_global_q = (bfloat16*) global_q;
                    bf16_global_q[row * N + Bid] = __float2bfloat16(m_float + dot);
                } else if(nbits == 32) {
                    float *float_global_q = (float*) global_q;
                    float_global_q[row * N + Bid] = m_float + dot;
                }
            }
        }
        __syncthreads();

        // store (dot/q) * V to Vout
        for(j = 0; j < B; j += T) {
            Vout[j] -= (dot / q) * V[j];
        }
        __syncthreads();
    }

    // write to out
    if(nbits == 16) {
        bfloat16 *bf16_global_out = (bfloat16*) global_out;
        //  <---------------init-----------------------> <------------stop cond-------------> <---next steps----->
        for(j_global = global_out_block_Bid_start, j = 0; j_global < global_out_block_Bid_end; j_global+=T, j += T) {
            bf16_global_out[j_global] = __float2bfloat16(Vout[j]);
        }
    } else if (nbits == 32) {
        float *float_global_out = (bfloat16*) global_out;
        //  <---------------init-----------------------> <------------stop cond-------------> <---next steps----->
        for(j_global = global_out_block_Bid_start, j = 0; j_global < global_out_block_Bid_end; j_global+=T, j += T) {
            float_global_out[j_global] = Vout[j];
        }
    }
}

void compute_row_cuda(torch::Tensor V,
                      torch::Tensor g,
                      torch::Tensor q,
                      torch::Tensor out,
                      int row,
                      int m,
                      float damp,
                      int N,
                      int B,
                      int nbits) {

    dim3 blocks(N, 1, 1);
    dim3 threads(1024, 1, 1);
    int shared_mem_size_bytes = (4 * B) * sizeof(float);

    if(shared_mem_size_bytes > 48 * 1024) {
        //// if we want to allocate more than 48KB, then we have to call this method
        cudaFuncSetAttribute(compute_row_kernel, cudaFuncAttributeMaxDynamicSharedMemorySize, shared_mem_size_bytes);
    }

    compute_row_kernel<<<blocks, threads, shared_mem_size_bytes>>>(
        (void*) V.data_ptr(),
        (void*) g.data_ptr(),
        (void*) q.data_ptr(),
        (void*) out.data_ptr(),
        row,
        m,
        damp,
        N,
        B,
        nbits);

	GPU_ERROR_CHECK(cudaGetLastError());
	GPU_ERROR_CHECK(cudaPeekAtLastError());
	GPU_ERROR_CHECK(cudaDeviceSynchronize());
}