#include <stdio.h>
#include <cuda_fp16.h>

#define SIZE 1000000

#define nTPB 256


#define FLOAT half

__global__ void init(int n, half2 *x, half2 *y)
{
  int idx = threadIdx.x+blockDim.x*blockIdx.x;
  if (idx < n)
  {
    x[idx] = y[idx] =  __float2half2_rn((float)(idx%15));
  }  
}

__global__ void saxpy(int n, float a, half2 *x, half2 *y)
{
  int idx = threadIdx.x+blockDim.x*blockIdx.x;
  if (idx < n)
  {
    half2 a2 = __float2half2_rn(a);
    y[idx] = __hfma2(a2, x[idx], y[idx]);
  }
}

int main(){

  FLOAT *hin, *hout, *din, *dout;
  hin  = (FLOAT *)malloc(SIZE*sizeof(FLOAT));
  hout = (FLOAT *)malloc(SIZE*sizeof(FLOAT));
//  for (int i = 0; i < SIZE; i++) hin[i] = i%15;
//  for (int i = 0; i < SIZE; i++) hout[i] = i%15;
  cudaMalloc(&din,  SIZE*sizeof(FLOAT));
  cudaMalloc(&dout, SIZE*sizeof(FLOAT));

//  cudaMemcpy(din, hin, SIZE*sizeof(FLOAT), cudaMemcpyHostToDevice);
//  cudaMemcpy(dout, hout, SIZE*sizeof(FLOAT), cudaMemcpyHostToDevice);
  init<<<(SIZE/2+nTPB-1)/nTPB,nTPB>>>(SIZE/2, (half2 *)din, (half2 *)dout);

  int k;
  for(k=0; k<5; ++k)
    saxpy<<<(SIZE/2+nTPB-1)/nTPB,nTPB>>>(SIZE/2, 0.5, (half2 *)din, (half2 *)dout);
  cudaMemcpy(hout, dout, SIZE*sizeof(FLOAT), cudaMemcpyDeviceToHost);
//  for (int i = 0; i < DSIZE; i++)
  printf("%f ... %f\n", hout[0], hout[SIZE-1]);
  return 0;
}

