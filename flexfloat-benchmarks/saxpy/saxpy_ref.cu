#include <stdio.h>
#include <cuda_fp16.h>

#define SIZE 1000000

#define nTPB 256

#ifndef FLOAT
#define FLOAT double
#endif

__global__ void saxpy(int n, FLOAT a, FLOAT *x, FLOAT *y)
{
  int idx = threadIdx.x+blockDim.x*blockIdx.x;
  if (idx < n)
  {
    y[idx] = a * x[idx] + y[idx];
  }
}

int main()
{

  FLOAT *hin, *hout, *din, *dout;
  hin  = (FLOAT *)malloc(SIZE*sizeof(FLOAT));
  hout = (FLOAT *)malloc(SIZE*sizeof(FLOAT));
  for (int i = 0; i < SIZE; i++) hin[i] = i%15;
  for (int i = 0; i < SIZE; i++) hout[i] = i%15;
  cudaMalloc(&din,  SIZE*sizeof(FLOAT));
  cudaMalloc(&dout, SIZE*sizeof(FLOAT));
  cudaMemcpy(din, hin, SIZE*sizeof(FLOAT), cudaMemcpyHostToDevice);
  cudaMemcpy(dout, hout, SIZE*sizeof(FLOAT), cudaMemcpyHostToDevice);

  int k;
  for(k=0; k<5; ++k)
    saxpy<<<(SIZE+nTPB-1)/nTPB,nTPB>>>(SIZE, 0.5124353, din, dout);
  cudaMemcpy(hout, dout, SIZE*sizeof(FLOAT), cudaMemcpyDeviceToHost);
  for (int i = 0; i < SIZE; i++)
    printf("%f,", hout[i]);
  return 0;
}

