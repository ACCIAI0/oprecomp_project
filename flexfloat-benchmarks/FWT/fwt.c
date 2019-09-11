#include <stdlib.h>
#include <stdio.h>
#include <math.h>

#ifndef LOG2N
#define LOG2N 16
#endif

#define N     (1 << LOG2N)

#ifndef FLOAT
#define FLOAT double
#endif

#include "datasets.h"

void fwtCPU(FLOAT *h_Output, FLOAT *h_Input)
{

    for(int pos = 0; pos < N; pos++)
        h_Output[pos] = h_Input[pos];

    //Cycle through stages with different butterfly strides
    for(int stride = N / 2; stride >= 1; stride >>= 1){
        //Cycle through subvectors of (2 * stride) elements
        for(int base = 0; base < N; base += 2 * stride)
            //Butterfly index within subvector of (2 * stride) size
            for(int j = 0; j < stride; j++){
                int i0 = base + j +      0;
                int i1 = base + j + stride;

                FLOAT T1 = h_Output[i0];
                FLOAT T2 = h_Output[i1];
                h_Output[i0] = T1 + T2;
                h_Output[i1] = T1 - T2;
            }
    }
}

int main()
{
	int i;
  FLOAT *h_ResultCPU;

	h_ResultCPU = (FLOAT *)malloc(N*sizeof(FLOAT));

	fwtCPU(h_ResultCPU, data);

	for(i=0; i<N; i++)
		printf("%.15f,", h_ResultCPU[i]);

	return 0;
}
