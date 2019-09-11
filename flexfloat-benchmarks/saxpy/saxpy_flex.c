
#include <stdio.h>

#include "data.h"

#include "flexfloat.hpp"

void saxpy(int n, double a, double * __restrict x, double * __restrict y)
{
  for (int i = 0; i < n; ++i)
      y[i] = (double) (flexfloat<EXP_Y, FRAC_Y>(flexfloat<EXP_A, FRAC_A>(a))*flexfloat<EXP_Y, FRAC_Y>(flexfloat<EXP_X, FRAC_X>(x[i])) + flexfloat<EXP_Y, FRAC_Y>(y[i]));
}

int main()
{
  saxpy(SIZE, 2.0, input, output);  
  int i;
  for(i=0; i<SIZE; ++i)
    printf("%.15f,", output[i]);
  //print_flexfloat_stats();
  return 0;
}
