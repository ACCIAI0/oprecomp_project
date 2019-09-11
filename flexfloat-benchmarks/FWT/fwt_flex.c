#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include "flexfloat.hpp"

#ifndef LOG2N
#define LOG2N 16
#endif

#define N     (1 << LOG2N)

#ifndef FLOAT
#define FLOAT float
#endif

#include "datasets.h"

void fwtCPU(FLOAT *h_Output, FLOAT *h_Input)
{
    flexfloat<EXP_INPUT, FRAC_INPUT> ff_input;
    flexfloat<EXP_OUTPUT, FRAC_OUTPUT> ff_output;

    for(int pos = 0; pos < N; pos++) {
        ff_input = h_Input[pos]; // [/SKIP]
        ff_output = flexfloat<EXP_OUTPUT, FRAC_OUTPUT>(ff_input);
        h_Output[pos] =   double(ff_input); // [/SKIP]
      }

    //Cycle through stages with different butterfly strides
    for(int stride = N / 2; stride >= 1; stride >>= 1){
        //Cycle through subvectors of (2 * stride) elements
        for(int base = 0; base < N; base += 2 * stride)
            //Butterfly index within subvector of (2 * stride) size
            for(int j = 0; j < stride; j++){
                int i0 = base + j +      0;
                int i1 = base + j + stride;

                flexfloat<EXP_OUTPUT, FRAC_OUTPUT> T1;
                T1 = h_Output[i0];
                flexfloat<EXP_OUTPUT, FRAC_OUTPUT> T2;
                T2 = h_Output[i1];
                flexfloat<EXP_OUTPUT, FRAC_OUTPUT> Temp;
                Temp = T1 + T2;
                h_Output[i0] = double(Temp); // [/SKIP]
                Temp = T1 - T2;
                h_Output[i1] = double(Temp); // [/SKIP]
            }
    }
}

int main()
{
	int i;
  FLOAT  *h_ResultCPU;

	h_ResultCPU = (FLOAT *)malloc(N*sizeof(FLOAT));

	fwtCPU(h_ResultCPU, data);

	for(i=0; i<N; i++)
		printf("%.15f,", h_ResultCPU[i]);

	return 0;
}

