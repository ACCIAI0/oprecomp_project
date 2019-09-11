
#include <stdlib.h>
#include <stdio.h>
#include <time.h>

int main(int argc, char *argv[])
{
  int i;
  int SIZE = atoi(argv[1]);
  srand((unsigned int)time(NULL));
  float a = 5.0;
  for(i=0; i<SIZE; ++i)
  {
    double x = (double)rand()/(double)(RAND_MAX/a);
    printf("%.15f,", x);
  }
  return 0;
}
