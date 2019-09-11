#include <stdlib.h>
#include <stdio.h>
#include <math.h>

#ifndef LOG2N
#define LOG2N 16
#endif

#define N     (1 << LOG2N)

#define LOG2K  7
#define K     (1<<7)


#ifndef FLOAT
#define FLOAT double
#endif



#define ELEMENTARY_LOG2SIZE 11

__global__ void fwtBatch1Kernel(FLOAT *d_Output, FLOAT *d_Input, int log2N){

    const int    n = 1 << log2N;
    int     stride = n;
    const int base = blockIdx.x << log2N;

    //(2 ** 11) * 4 bytes == 8KB -- maximum s_data[] size for G80
    extern __shared__ FLOAT s_data[];
    FLOAT *d_Src = d_Input  + base;
    FLOAT *d_Dst = d_Output + base;

    for(int pos = threadIdx.x; pos < n; pos += blockDim.x)
        s_data[pos] = d_Src[pos];


    //Do single radix-2 stage if for odd power
    if(log2N & 1){
        __syncthreads();
        stride >>= 1;
        for(int pos = threadIdx.x; pos < n / 2; pos += blockDim.x){
            int lo = pos & (stride - 1);
            int i0 = ((pos - lo) << 1) + lo;
            int i1 = i0 + stride;

            FLOAT t0 = s_data[i0];
            FLOAT t1 = s_data[i1];
            s_data[i0] = t0 + t1;
            s_data[i1] = t0 - t1;
        }
    }

    //Main radix4 stages
    stride >>= 2;
    int pos = threadIdx.x;
    for(; stride >= 1; stride >>= 2){
        __syncthreads();
        int lo = pos & (stride - 1);
        int i0 = ((pos - lo) << 2) + lo;
        int i1 = i0 + stride;
        int i2 = i1 + stride;
        int i3 = i2 + stride;

        FLOAT d0 = s_data[i0];
        FLOAT d1 = s_data[i1];
        FLOAT d2 = s_data[i2];
        FLOAT d3 = s_data[i3];

        FLOAT t;
        t = d0; d0         = d0 + d2; d2         = t - d2;
        t = d1; d1         = d1 + d3; d3         = t - d3;
        t = d0; s_data[i0] = d0 + d1; s_data[i1] = t - d1;
        t = d2; s_data[i2] = d2 + d3; s_data[i3] = t - d3;
    }

    __syncthreads();
    for(int pos = threadIdx.x; pos < n; pos += blockDim.x)
        d_Dst[pos] = s_data[pos];
}

////////////////////////////////////////////////////////////////////////////////
// Single in-global memory radix-4 Fast Walsh Transform pass
// (for strides exceeding elementary vector size)
////////////////////////////////////////////////////////////////////////////////
__global__ void fwtBatch2Kernel(
    FLOAT *d_Output,
    FLOAT *d_Input,
    int stride
){
    const int pos = blockIdx.x * blockDim.x + threadIdx.x;
    const int   n = blockDim.x *  gridDim.x * 4;

    FLOAT *d_Src = d_Input  + blockIdx.y * n;
    FLOAT *d_Dst = d_Output + blockIdx.y * n;

    int lo = pos & (stride - 1);
    int i0 = ((pos - lo) << 2) + lo;
    int i1 = i0 + stride;
    int i2 = i1 + stride;
    int i3 = i2 + stride;

    FLOAT d0 = d_Src[i0];
    FLOAT d1 = d_Src[i1];
    FLOAT d2 = d_Src[i2];
    FLOAT d3 = d_Src[i3];

    FLOAT t;
    t = d0; d0        = d0 + d2; d2        = t - d2;
    t = d1; d1        = d1 + d3; d3        = t - d3;
    t = d0; d_Dst[i0] = d0 + d1; d_Dst[i1] = t - d1;
    t = d2; d_Dst[i2] = d2 + d3; d_Dst[i3] = t - d3;
}

////////////////////////////////////////////////////////////////////////////////
// Put everything together: batched Fast Walsh Transform CPU front-end
////////////////////////////////////////////////////////////////////////////////
void fwtBatchGPU(FLOAT *d_Data, int M, int log2N){
    int n = 1 << log2N;
    dim3 grid((1 << log2N) / 1024, M, 1);
    for(; log2N > ELEMENTARY_LOG2SIZE; log2N -= 2, n >>= 2, M <<= 2){
        fwtBatch2Kernel<<<grid, 256>>>(d_Data, d_Data, n / 4);
    }

    fwtBatch1Kernel<<<M, n / 4, n * sizeof(FLOAT)>>>(
        d_Data,
        d_Data,
        log2N
    );
}



////////////////////////////////////////////////////////////////////////////////
// Modulate two arrays
////////////////////////////////////////////////////////////////////////////////
__global__ void modulateKernel(FLOAT *d_A, FLOAT *d_B, int n){
    int        tid = blockIdx.x * blockDim.x + threadIdx.x;
    int numThreads = blockDim.x * gridDim.x;
    FLOAT     rcpN = 1.0f / (FLOAT)n;

    for(int pos = tid; pos < n; pos += numThreads)
        d_A[pos] *= d_B[pos] * rcpN;
}

//Interface to modulateKernel()
void modulateGPU(FLOAT *d_A, FLOAT *d_B, int n){
    modulateKernel<<<128, 256>>>(d_A, d_B, n);
}


int main()
{
	int i;


    FLOAT
        *h_Data,
        *h_Kernel,
        *h_ResultGPU;

    FLOAT
        *d_Data,
        *d_Kernel;

	h_Data      = (FLOAT *)malloc(N*sizeof(FLOAT));
    h_Kernel    = (FLOAT *)malloc(K*sizeof(FLOAT));
	h_ResultGPU = (FLOAT *)malloc(N*sizeof(FLOAT));

    cudaMalloc((void **)&d_Kernel, N*sizeof(FLOAT));
    cudaMalloc((void **)&d_Data,   N*sizeof(FLOAT)); 

    for (i = 0; i < N; i++)
        h_Data[i] = (FLOAT)rand() / (FLOAT)RAND_MAX;
    for (i = 0; i < K; i++)
        h_Kernel[i] = (FLOAT)rand() / (FLOAT)RAND_MAX;    

    cudaMemset(d_Kernel, 0, N*sizeof(FLOAT));
    cudaMemcpy(d_Kernel, h_Kernel, K*sizeof(FLOAT), cudaMemcpyHostToDevice);
    cudaMemcpy(d_Data,   h_Data,   N*sizeof(FLOAT), cudaMemcpyHostToDevice);

    fwtBatchGPU(d_Data, 1, LOG2N);
    fwtBatchGPU(d_Kernel, 1, LOG2N);
    modulateGPU(d_Data, d_Kernel, N);
    fwtBatchGPU(d_Data, 1, LOG2N);

    cudaMemcpy(h_ResultGPU, d_Data, N*sizeof(FLOAT), cudaMemcpyDeviceToHost);

	for(i=0; i<N; i++)
		printf("%.15f,", h_ResultGPU[i]);

	return 0;
}