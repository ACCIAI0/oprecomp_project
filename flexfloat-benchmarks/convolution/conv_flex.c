#include <stdlib.h>
#include <stdio.h>
#include <math.h>

#include "flexfloat.hpp"

#ifndef FLOAT
#define FLOAT double
#endif

void convolutionRowCPU(
    FLOAT *h_Result,
    FLOAT *h_Data,
    FLOAT *h_Kernel,
    int dataW,
    int dataH,
    int kernelR
)
{
    int x, y, k, d;
    flexfloat<EXP_DATA, FRAC_DATA> ff_data;
    flexfloat<EXP_KERNEL, FRAC_KERNEL> ff_kernel;
    flexfloat<EXP_SUM, FRAC_SUM> ff_sum;
    flexfloat<EXP_TEMP1, FRAC_TEMP1> ff_temp1;

    for(y = 0; y < dataH; y++)
        for(x = 0; x < dataW; x++) {
            ff_sum = 0;
            for(k = -kernelR; k <= kernelR; k++) {
                d = x + k;
                if(d >= 0 && d < dataW) {
                    ff_data = h_Data[y * dataW + d]; // [/SKIP]
                    ff_kernel = h_Kernel[kernelR - k]; // [/SKIP]
                    ff_sum += flexfloat<EXP_SUM, FRAC_SUM>(
                                flexfloat<EXP_TEMP1, FRAC_TEMP1>(ff_data) *
                                flexfloat<EXP_TEMP1, FRAC_TEMP1>(ff_kernel)
                              );
                }
            }
            h_Result[y * dataW + x] = double(flexfloat<EXP_DATA, FRAC_DATA>(ff_sum));  // [/SKIP]
        }
}



void convolutionColumnCPU(
    FLOAT *h_Result,
    FLOAT *h_Data,
    FLOAT *h_Kernel,
    int dataW,
    int dataH,
    int kernelR
){
    int x, y, k, d;
    flexfloat<EXP_DATA, FRAC_DATA> ff_data;
    flexfloat<EXP_KERNEL, FRAC_KERNEL> ff_kernel;
    flexfloat<EXP_SUM, FRAC_SUM> ff_sum;
    flexfloat<EXP_TEMP1, FRAC_TEMP1> ff_temp1;

    for(y = 0; y < dataH; y++)
        for(x = 0; x < dataW; x++) {
            ff_sum = 0;
            for(k = -kernelR; k <= kernelR; k++) {
                d = y + k;
                if(d >= 0 && d < dataH) {
                    ff_data = h_Data[d * dataW + x]; // [/SKIP]
                    ff_kernel = h_Kernel[kernelR - k]; // [/SKIP]
                    ff_sum += flexfloat<EXP_SUM, FRAC_SUM>(
                                flexfloat<EXP_TEMP1, FRAC_TEMP1>(ff_data) *
                                flexfloat<EXP_TEMP1, FRAC_TEMP1>(ff_kernel)
                              );
                }
            }
            h_Result[y * dataW + x] = double(flexfloat<EXP_DATA, FRAC_DATA>(ff_sum)); // [/SKIP]
        }
}


#define     KERNEL_RADIUS 8
#define      KERNEL_W (2 * KERNEL_RADIUS + 1)
#define      DATA_W  256
#define      DATA_H  256
const int   DATA_SIZE = DATA_W * DATA_H * sizeof(FLOAT);
const int KERNEL_SIZE = KERNEL_W * sizeof(FLOAT);

#include "datasets.h"

int main(int argc, char **argv){
    int i;

    FLOAT
        *h_Kernel,
        *h_DataB,
        *h_ResultGPU;

    h_Kernel    = (FLOAT *)malloc(KERNEL_SIZE);
    h_DataB     = (FLOAT *)malloc(DATA_SIZE);

    FLOAT kernelSum = 0;
    for(i = 0; i < KERNEL_W; i++){
        FLOAT dist = (FLOAT)(i - KERNEL_RADIUS) / (FLOAT)KERNEL_RADIUS;
        h_Kernel[i] = expf(- dist * dist / 2);
        kernelSum += h_Kernel[i];
    }
    for(i = 0; i < KERNEL_W; i++)
        h_Kernel[i] /= kernelSum;

    convolutionRowCPU(
        h_DataB,
        data,
        h_Kernel,
        DATA_W,
        DATA_H,
        KERNEL_RADIUS
    );

    convolutionColumnCPU(
        data,
        h_DataB,
        h_Kernel,
        DATA_W,
        DATA_H,
        KERNEL_RADIUS
    );
    for(i = 0; i < DATA_W * DATA_H; i++)
        printf("%.15f,", data[i]);
//print_flexfloat_stats();

    return 0;
}
