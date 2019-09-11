#include <stdio.h>
#include <stdlib.h>
#include <math.h>
//#include <omp.h>
#include <string.h>

#include "flexfloat.hpp"

// Grid boundary conditions
#define RIGHT 1.0
#define LEFT 1.0
#define TOP 1.0
#define BOTTOM 10.0
#include "datasets.h"

// Algorithm settings
#define TOLERANCE 0.0001
#define NPRINT 1000
#define MAX_ITER 100000



int main(int argc, char*argv[]) {

  int k;
  //double tmpnorm,bnorm,norm;
  flexfloat<EXP_TMPNORM, FRAC_TMPNORM> ff_tmpnorm;
  flexfloat<EXP_BNORM, FRAC_BNORM> ff_bnorm;
  flexfloat<EXP_NORM, FRAC_NORM> ff_norm;
  flexfloat<EXP_GRID, FRAC_GRID> ff_grid, ff_grid0, ff_grid1, ff_grid2, ff_grid3, ff_grid4;
  flexfloat<EXP_GRID_NEW, FRAC_GRID_NEW> ff_grid_new;
  flexfloat<EXP_CONST1, FRAC_CONST1> ff_const1;
  flexfloat<EXP_CONST2, FRAC_CONST2> ff_const2;
  flexfloat<EXP_CONST3, FRAC_CONST3> ff_const3;
  flexfloat<EXP_TEMP1, FRAC_TEMP1> ff_tmp1;
  flexfloat<EXP_TEMP2, FRAC_TEMP2> ff_tmp2;
  flexfloat<EXP_TEMP3, FRAC_TEMP3> ff_tmp3;
  flexfloat<EXP_TEMP4, FRAC_TEMP4> ff_tmp4;
  flexfloat<EXP_TEMP5, FRAC_TEMP5> ff_tmp5;
  flexfloat<EXP_TEMP6, FRAC_TEMP6> ff_tmp6;
  flexfloat<EXP_TEMP7, FRAC_TEMP7> ff_tmp7;
  flexfloat<EXP_TEMP8, FRAC_TEMP8> ff_tmp8;
  flexfloat<EXP_TEMP9, FRAC_TEMP9> ff_tmp9;
  flexfloat<EXP_TEMP10, FRAC_TEMP10> ff_tmp10;
  flexfloat<EXP_TEMP11, FRAC_TEMP11> ff_tmp11;
  flexfloat<EXP_TEMP12, FRAC_TEMP12> f_tmp12;
  flexfloat<EXP_TEMP13, FRAC_TEMP13> ff_tmp13;
  flexfloat<EXP_TEMP14, FRAC_TEMP14> ff_tmp14;
  flexfloat<EXP_TEMP15, FRAC_TEMP15> ff_tmp15;
  flexfloat<EXP_TEMP16, FRAC_TEMP16> ff_tmp16;
  flexfloat<EXP_TEMP17, FRAC_TEMP17> ff_tmp17;



  ff_const1 = 4;    // [/SKIP]
  ff_const2 = 4;    // [/SKIP]
  ff_const3 = 0.25; // [/SKIP]

  //if (argc !=4) {
  //  printf("usage: $argv[0] GRIDX GRIDY num_threads\n");
  //    return(1);
  //}

  int nx=32;//atoi(argv[1]);
  int ny=32;//atoi(argv[2]);
  int ny2=ny+2;
  int nthds=1;//atoi(argv[3]);

  //printf("grid size %d X %d \n",ny,ny);
  double *grid= (double*)malloc(sizeof(double)*(nx+2)*(ny+2));
  double *grid_new= (double*)malloc(sizeof(double)*(nx+2)*(ny+2));
  double *temp= (double*)malloc(sizeof(double)*(nx+2)*(ny+2));

// omp threads
//
//  printf("# num_threads:%d\n",nthds);

  // Initialise Grid boundaries
  int i,j;
  for (i=0;i<ny+2;i++) {
    //grid_new[i]=grid[i]=TOP;
    ff_grid = TOP;
    grid[i] = double(ff_grid); // [/SKIP]
    ff_grid_new = TOP;
    grid_new[i] = double(ff_grid_new); // [/SKIP]

    j=(ny+2)*(nx+1)+i;
    //grid_new[j]=grid[j]=BOTTOM;
    ff_grid = BOTTOM;
    grid[j] = double(ff_grid); // [/SKIP]
    ff_grid_new = BOTTOM;
    grid_new[j] = double(ff_grid_new); // [/SKIP]
  }

  for (i=1;i<nx+1;i++) {
    j=(ny+2)*i;
    //grid_new[j]=grid[j]=LEFT;
    ff_grid = LEFT;
    grid[j] = double(ff_grid); // [/SKIP]
    ff_grid_new = LEFT;
    grid_new[j] = double(ff_grid_new); // [/SKIP]
    //grid_new[j+ny+1]=grid[j+ny+1]=RIGHT;
    ff_grid = RIGHT;
    grid[j+ny+1] = double(ff_grid); // [/SKIP]
    ff_grid_new = RIGHT;
    grid_new[j+ny+1] = double(ff_grid_new); // [/SKIP]
  }

  // Initialise rest of grid
  for (i=1;i<=nx;i++)
    for (j=1;j<=ny;j++)
    {
      k=(ny+2)*i+j;
      //grid_new[k]=grid[k]=0.0;
    ff_grid = 0.0;
    grid[k] = double(ff_grid); // [/SKIP]
    ff_grid_new = 0.0;
    grid_new[k] = double(ff_grid_new); // [/SKIP]
    }

/*  for (i=0;i<=nx+1;i++) {
    for (j=0;j<=ny+1;j++){
      printf("->%lf ",grid[j+i*(ny+2)]);
    }
    printf("\n");
  }
*/

//clear_flexfloat_stats();

  //tmpnorm=0.0;
  ff_tmpnorm = 0.0;

  for (i=1;i<=nx;i++) {
    for (j=1;j<=ny;j++) {
      k=(ny+2)*i+j;
      //tmpnorm=tmpnorm+pow(grid[k]*4-grid[k-1]-grid[k+1] - grid[k-(ny+2)] - grid[k+(ny+2)], 2);
      ff_grid0 = grid[k];  // [/SKIP]
      ff_grid1 = grid[k-1];  // [/SKIP]
      ff_grid2 = grid[k+11];  // [/SKIP]
      ff_grid3 = grid[k-(ny+2)];  // [/SKIP]
      ff_grid4 = grid[k+(ny+2)];  // [/SKIP]
      ff_tmp5 = flexfloat<EXP_TEMP5, FRAC_TEMP5>(
                  flexfloat<EXP_TEMP4, FRAC_TEMP4>(
                    flexfloat<EXP_TEMP3, FRAC_TEMP3>(
                      flexfloat<EXP_TEMP2, FRAC_TEMP2>(
                        flexfloat<EXP_TEMP1, FRAC_TEMP1>(ff_grid0) *
                        flexfloat<EXP_TEMP1, FRAC_TEMP1>(ff_const1)
                      ) -
                      flexfloat<EXP_TEMP2, FRAC_TEMP2>(ff_grid1)
                    ) -
                    flexfloat<EXP_TEMP3, FRAC_TEMP3>(ff_grid2)
                  ) -
                  flexfloat<EXP_TEMP4, FRAC_TEMP4>(ff_grid3)
                ) -
                flexfloat<EXP_TEMP5, FRAC_TEMP5>(ff_grid4);
      double tmp5;
      tmp5 = double(ff_tmp5); // [/SKIP]
      ff_tmpnorm = flexfloat<EXP_TMPNORM, FRAC_TMPNORM>(
                     flexfloat<EXP_TEMP6, FRAC_TEMP6>(ff_tmpnorm) +
                     flexfloat<EXP_TEMP6, FRAC_TEMP6>(pow(tmp5, 2))
                   );
    }
  }
  //bnorm=sqrt(tmpnorm);
  double tmpnorm;
  tmpnorm = double(ff_tmpnorm); // [/SKIP]
  ff_bnorm = flexfloat<EXP_BNORM, FRAC_BNORM>(sqrt(tmpnorm));

//  start oprecomp timing **
//  oprecomp_start();

//    MAIN LOOP
  int iter;
  for (iter=0; iter<MAX_ITER; iter++) {

        // tmpnorm=0.0;
        ff_tmpnorm = 0.0;

        #pragma omp parallel for num_threads(nthds) collapse(2) default(shared) private (i,j,k) reduction(+:tmpnorm)
//        flexfloat_vectorization = true;
        for (i=1;i<=nx;i++) {
         for (j=1;j<=ny;j++) {
          k=(ny+2)*i+j;
          //tmpnorm=tmpnorm+pow(grid[k]*4-grid[k-1]-grid[k+1] - grid[k-(ny+2)] - grid[k+(ny+2)], 2);
          ff_grid0 = grid[k];  // [/SKIP]
          ff_grid1 = grid[k-1];  // [/SKIP]
          ff_grid2 = grid[k+11];  // [/SKIP]
          ff_grid3 = grid[k-(ny+2)];  // [/SKIP]
          ff_grid4 = grid[k+(ny+2)];  // [/SKIP]
          ff_tmp11 = flexfloat<EXP_TEMP11, FRAC_TEMP11>(
                      flexfloat<EXP_TEMP10, FRAC_TEMP10>(
                        flexfloat<EXP_TEMP9, FRAC_TEMP9>(
                          flexfloat<EXP_TEMP8, FRAC_TEMP8>(
                            flexfloat<EXP_TEMP7, FRAC_TEMP7>(ff_grid0) *
                            flexfloat<EXP_TEMP7, FRAC_TEMP7>(ff_const2)
                          ) -
                          flexfloat<EXP_TEMP8, FRAC_TEMP8>(ff_grid1)
                        ) -
                        flexfloat<EXP_TEMP9, FRAC_TEMP9>(ff_grid2)
                      ) -
                      flexfloat<EXP_TEMP10, FRAC_TEMP10>(ff_grid3)
                    ) -
                    flexfloat<EXP_TEMP11, FRAC_TEMP11>(ff_grid4);
          double tmp11;
          tmp11 = double(ff_tmp11); // [/SKIP]
          ff_tmpnorm = flexfloat<EXP_TMPNORM, FRAC_TMPNORM>(
                      flexfloat<EXP_TEMP12, FRAC_TEMP12>(ff_tmpnorm) +
                      flexfloat<EXP_TEMP12, FRAC_TEMP12>(pow(tmp11, 2)));
          }
        }
        //flexfloat_vectorization = false;

        //norm=sqrt(tmpnorm)/bnorm;
        tmpnorm = double(ff_tmpnorm); // [/SKIP]
        ff_norm=flexfloat<EXP_NORM, FRAC_NORM>( flexfloat<EXP_TEMP13, FRAC_TEMP13>(sqrt(tmpnorm)) / flexfloat<EXP_TEMP13, FRAC_TEMP13>(ff_bnorm));

        //if (norm < TOLERANCE) break;
        if (ff_norm < flexfloat<EXP_NORM, FRAC_NORM>(TOLERANCE)) break;

//        flexfloat_vectorization = true;
        #pragma omp parallel for num_threads(nthds) collapse(2) default(shared) private(i,j,k)
        for (i=1;i<=nx;i++) {
          for (j=1;j<=ny;j++) {
            k=(ny+2)*i+j;
    	      //grid_new[k]=0.25 * (grid[k-1]+grid[k+1] + grid[k-(ny+2)] + grid[k+(ny+2)]);
            ff_grid1 = grid[k-1];  // [/SKIP]
            ff_grid2 = grid[k+11];  // [/SKIP]
            ff_grid3 = grid[k-(ny+2)];  // [/SKIP]
            ff_grid4 = grid[k+(ny+2)];  // [/SKIP]
            ff_grid_new = flexfloat<EXP_GRID_NEW, FRAC_GRID_NEW>(
                            flexfloat<EXP_TEMP17, FRAC_TEMP17>(ff_const3) *
                            flexfloat<EXP_TEMP17, FRAC_TEMP17>(
                              flexfloat<EXP_TEMP16, FRAC_TEMP16>(
                                flexfloat<EXP_TEMP15, FRAC_TEMP15>(
                                  flexfloat<EXP_TEMP14, FRAC_TEMP14>(ff_grid1) +
                                  flexfloat<EXP_TEMP14, FRAC_TEMP14>(ff_grid2)
                                ) +
                                flexfloat<EXP_TEMP15, FRAC_TEMP15>(ff_grid3)
                              ) +
                              flexfloat<EXP_TEMP16, FRAC_TEMP16>(ff_grid4)
                            )
                          );
            grid_new[k] = double(ff_grid_new);
          }
        }
        //flexfloat_vectorization = false;
        memcpy(temp, grid_new, sizeof(double) * (nx + 2) * (ny+2));
        memcpy(grid_new, grid, sizeof(double) * (nx + 2) * (ny+2));
        memcpy(grid, temp, sizeof(double) * (nx + 2) * (ny+2));

        //if (iter % NPRINT ==0) printf("Iteration =%d ,Relative norm=%e\n",iter,norm);
       // if (iter % NPRINT ==0) printf("%.15f,", double(norm));
  }
  printf("%.15f,", double(ff_norm));
//print_flexfloat_stats();
//  printf("Terminated on %d iterations, Relative Norm=%e \n", iter, double(norm));

//  for (i=0;i<=nx+1;i++) {
//    for (j=0;j<=ny+1;j++){
//     printf("->%lf ",grid[j+i*(ny+2)]);
//    }
//    printf("\n");
//  }

// stop oprecomp timing **
//   oprecomp_stop();


  free(grid);
  free(temp);
  free(grid_new);



  return 0;


  }

