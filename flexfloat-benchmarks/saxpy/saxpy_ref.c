
#include <stdio.h>

#include "data.h"


void saxpy(int n, double a, double * __restrict x, double * __restrict y)
{
  for (int i = 0; i < n; ++i)
      y[i] = a*x[i] + y[i];
}

int main()
{
  saxpy(SIZE, 2.0, input, output);  
  int i;
  for(i=0; i<SIZE; ++i)
    printf("%.15f,", output[i]);
  return 0;
}
