#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <omp.h>
#include <string.h>

#include "flexfloat.h"

// Grid boundary conditions
// #define RIGHT 1.0
// #define LEFT 1.0
// #define TOP 1.0
// #define BOTTOM 10.0
#include "datasets.h"

// Algorithm settings
#define TOLERANCE 0.0001
#define NPRINT 1000
#define MAX_ITER 100000


int main(int argc, char*argv[]) {

  int k;
  //double tmpnorm,bnorm,norm;
  flexfloat_t tmpnorm,bnorm,norm;
  ff_init(&tmpnorm, (flexfloat_desc_t){EXP_TMPNORM, FRAC_TMPNORM});
  ff_init(&bnorm, (flexfloat_desc_t){EXP_BNORM, FRAC_BNORM});
  ff_init(&norm, (flexfloat_desc_t){EXP_NORM, FRAC_NORM});

  if (argc !=4) {
    printf("usage: $argv[0] GRIDX GRIDY num_threads\n");
      return(1);
  }

  int nx=atoi(argv[1]);
  int ny=atoi(argv[2]);
  int ny2=ny+2;
  int nthds=atoi(argv[3]);

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
    flexfloat_t _tmp01, _tmp02;
    ff_init_double(&_tmp01, TOP, (flexfloat_desc_t){EXP_GRID, FRAC_GRID});
    grid[i]=ff_get_double(&_tmp01);
    ff_init_double(&_tmp02, grid[i], (flexfloat_desc_t){EXP_GRID_NEW, FRAC_GRID_NEW});
    grid_new[i]=ff_get_double(&_tmp02);
    j=(ny+2)*(nx+1)+i;
    //grid_new[j]=grid[j]=BOTTOM;
    flexfloat_t _tmp03, _tmp04;
    ff_init_double(&_tmp03, BOTTOM, (flexfloat_desc_t){EXP_GRID, FRAC_GRID});
    grid[j]=ff_get_double(&_tmp03);
    ff_init_double(&_tmp04, grid[j], (flexfloat_desc_t){EXP_GRID_NEW, FRAC_GRID_NEW});
    grid_new[j]=ff_get_double(&_tmp04);
  }
  for (i=1;i<nx+1;i++) {
    j=(ny+2)*i;
    //grid_new[j]=grid[j]=LEFT;
    flexfloat_t _tmp01, _tmp02;
    ff_init_double(&_tmp01, LEFT, (flexfloat_desc_t){EXP_GRID, FRAC_GRID});
    grid[j]=ff_get_double(&_tmp01);
    ff_init_double(&_tmp02, grid[j], (flexfloat_desc_t){EXP_GRID_NEW, FRAC_GRID_NEW});
    grid_new[j]=ff_get_double(&_tmp02);
    //grid_new[j+ny+1]=grid[j+ny+1]=RIGHT;
    flexfloat_t _tmp03, _tmp04;
    ff_init_double(&_tmp03, RIGHT, (flexfloat_desc_t){EXP_GRID, FRAC_GRID});
    grid[j+ny+1]=ff_get_double(&_tmp03);
    ff_init_double(&_tmp04, grid[j+ny+1], (flexfloat_desc_t){EXP_GRID_NEW, FRAC_GRID_NEW});
    grid_new[j+ny+1]=ff_get_double(&_tmp04);
  }

  // Initialise rest of grid
  for (i=1;i<=nx;i++)
    for (j=1;j<=ny;j++)
    {
      k=(ny+2)*i+j;
      //grid_new[k]=grid[k]=0.0;
      flexfloat_t _tmp01, _tmp02;
      ff_init_double(&_tmp01, 0.0, (flexfloat_desc_t){EXP_GRID, FRAC_GRID});
      grid[k]=ff_get_double(&_tmp01);
      ff_init_double(&_tmp02, grid[k], (flexfloat_desc_t){EXP_GRID_NEW, FRAC_GRID_NEW});
      grid_new[k]=ff_get_double(&_tmp02);
    }

/*  for (i=0;i<=nx+1;i++) {
    for (j=0;j<=ny+1;j++){
      printf("->%lf ",grid[j+i*(ny+2)]);
    }
    printf("\n");
  }
*/

  //tmpnorm=0.0;
  flexfloat_t _tmp01;
  ff_init_double(&_tmp01, 0.0, (flexfloat_desc_t){EXP_TMPNORM, FRAC_TMPNORM});
  tmpnorm = _tmp01;
  for (i=1;i<=nx;i++) {
    for (j=1;j<=ny;j++) {
      k=(ny+2)*i+j;
      //tmpnorm=tmpnorm+pow(grid[k]*4-grid[k-1]-grid[k+1] - grid[k-(ny+2)] - grid[k+(ny+2)], 2);
      flexfloat_t _tmp01, _tmp02, _tmp03, _tmp04, _tmp05, _tmp06, _tmp07, _tmp08, _tmp09, _tmp10;
      flexfloat_t _tmp11, _tmp12, _tmp13, _tmp14, _tmp15, _tmp16, _tmp17, _tmp18, _tmp19, _tmp20;
      flexfloat_t _tmp21, _tmp22, _tmp23, _tmp24, _tmp25;
      ff_init_double(&_tmp01, grid[k+(ny+2)], (flexfloat_desc_t){EXP_GRID, FRAC_GRID});
      ff_init_double(&_tmp02, grid[k-(ny+2)], (flexfloat_desc_t){EXP_GRID, FRAC_GRID});
      ff_init_double(&_tmp03, grid[k+1], (flexfloat_desc_t){EXP_GRID, FRAC_GRID});
      ff_init_double(&_tmp04, grid[k-1], (flexfloat_desc_t){EXP_GRID, FRAC_GRID});
      ff_init_double(&_tmp05, grid[k], (flexfloat_desc_t){EXP_GRID, FRAC_GRID});
      ff_init_double(&_tmp06, 4, (flexfloat_desc_t){EXP_CONST1, FRAC_CONST1});
      ff_init_ff(&_tmp07, &_tmp05, (flexfloat_desc_t){EXP_TEMP1, FRAC_TEMP1});
      ff_init_ff(&_tmp08, &_tmp06, (flexfloat_desc_t){EXP_TEMP1, FRAC_TEMP1});
      ff_init(&_tmp09, (flexfloat_desc_t){EXP_TEMP1, FRAC_TEMP1});
      ff_mul(&_tmp09, &_tmp07, &_tmp08);
      ff_init_ff(&_tmp10, &_tmp09, (flexfloat_desc_t){EXP_TEMP2, FRAC_TEMP2});
      ff_init_ff(&_tmp11, &_tmp04, (flexfloat_desc_t){EXP_TEMP2, FRAC_TEMP2});
      ff_init(&_tmp12, (flexfloat_desc_t){EXP_TEMP2, FRAC_TEMP2});
      ff_sub(&_tmp12, &_tmp10, &_tmp11);
      ff_init_ff(&_tmp13, &_tmp12, (flexfloat_desc_t){EXP_TEMP3, FRAC_TEMP3});
      ff_init_ff(&_tmp14, &_tmp03, (flexfloat_desc_t){EXP_TEMP3, FRAC_TEMP3});
      ff_init(&_tmp15, (flexfloat_desc_t){EXP_TEMP3, FRAC_TEMP3});
      ff_sub(&_tmp15, &_tmp13, &_tmp14);
      ff_init_ff(&_tmp16, &_tmp15, (flexfloat_desc_t){EXP_TEMP4, FRAC_TEMP4});
      ff_init_ff(&_tmp17, &_tmp02, (flexfloat_desc_t){EXP_TEMP4, FRAC_TEMP4});
      ff_init(&_tmp18, (flexfloat_desc_t){EXP_TEMP4, FRAC_TEMP4});
      ff_sub(&_tmp18, &_tmp16, &_tmp17);
      ff_init_ff(&_tmp19, &_tmp18, (flexfloat_desc_t){EXP_TEMP5, FRAC_TEMP5});
      ff_init_ff(&_tmp20, &_tmp01, (flexfloat_desc_t){EXP_TEMP5, FRAC_TEMP5});
      ff_init(&_tmp21, (flexfloat_desc_t){EXP_TEMP5, FRAC_TEMP5});
      ff_sub(&_tmp21, &_tmp19, &_tmp20);
      ff_init_double(&_tmp22, pow(ff_get_double(&_tmp21), 2), (flexfloat_desc_t){EXP_TEMP6, FRAC_TEMP6});
      ff_init_ff(&_tmp23, &tmpnorm, (flexfloat_desc_t){EXP_TEMP6, FRAC_TEMP6});
      ff_init(&_tmp24, (flexfloat_desc_t){EXP_TEMP6, FRAC_TEMP6});
      ff_add(&_tmp24, &_tmp23, &_tmp22);
      ff_init_ff(&_tmp25, &_tmp24, (flexfloat_desc_t){EXP_TMPNORM, FRAC_TMPNORM});
      tmpnorm=_tmp25;
    }
  }
  //bnorm=sqrt(tmpnorm);
  flexfloat_t _tmp02;
  ff_init_double(&_tmp02, sqrt(ff_get_double(&tmpnorm)), (flexfloat_desc_t){EXP_BNORM, FRAC_BNORM});
  bnorm = _tmp02;

//  start oprecomp timing **
//  oprecomp_start();

//    MAIN LOOP
  int iter;
  for (iter=0; iter<MAX_ITER; iter++) {

       // tmpnorm=0.0;
       tmpnorm = _tmp01;

       #pragma omp parallel for num_threads(nthds) collapse(2) default(shared) private (i,j,k) reduction(+:tmpnorm)
        for (i=1;i<=nx;i++) {
         for (j=1;j<=ny;j++) {
          k=(ny+2)*i+j;
          //tmpnorm=tmpnorm+pow(grid[k]*4-grid[k-1]-grid[k+1] - grid[k-(ny+2)] - grid[k+(ny+2)], 2);
          flexfloat_t _tmp01, _tmp02, _tmp03, _tmp04, _tmp05, _tmp06, _tmp07, _tmp08, _tmp09, _tmp10;
          flexfloat_t _tmp11, _tmp12, _tmp13, _tmp14, _tmp15, _tmp16, _tmp17, _tmp18, _tmp19, _tmp20;
          flexfloat_t _tmp21, _tmp22, _tmp23, _tmp24, _tmp25;
          ff_init_double(&_tmp01, grid[k+(ny+2)], (flexfloat_desc_t){EXP_GRID, FRAC_GRID});
          ff_init_double(&_tmp02, grid[k-(ny+2)], (flexfloat_desc_t){EXP_GRID, FRAC_GRID});
          ff_init_double(&_tmp03, grid[k+1], (flexfloat_desc_t){EXP_GRID, FRAC_GRID});
          ff_init_double(&_tmp04, grid[k-1], (flexfloat_desc_t){EXP_GRID, FRAC_GRID});
          ff_init_double(&_tmp05, grid[k], (flexfloat_desc_t){EXP_GRID, FRAC_GRID});
          ff_init_double(&_tmp06, 4, (flexfloat_desc_t){EXP_CONST2, FRAC_CONST2});
          ff_init_ff(&_tmp07, &_tmp05, (flexfloat_desc_t){EXP_TEMP7, FRAC_TEMP7});
          ff_init_ff(&_tmp08, &_tmp06, (flexfloat_desc_t){EXP_TEMP7, FRAC_TEMP7});
          ff_init(&_tmp09, (flexfloat_desc_t){EXP_TEMP7, FRAC_TEMP7});
          ff_mul(&_tmp09, &_tmp07, &_tmp08);
          ff_init_ff(&_tmp10, &_tmp09, (flexfloat_desc_t){EXP_TEMP8, FRAC_TEMP8});
          ff_init_ff(&_tmp11, &_tmp04, (flexfloat_desc_t){EXP_TEMP8, FRAC_TEMP8});
          ff_init(&_tmp12, (flexfloat_desc_t){EXP_TEMP8, FRAC_TEMP8});
          ff_sub(&_tmp12, &_tmp10, &_tmp11);
          ff_init_ff(&_tmp13, &_tmp12, (flexfloat_desc_t){EXP_TEMP9, FRAC_TEMP9});
          ff_init_ff(&_tmp14, &_tmp03, (flexfloat_desc_t){EXP_TEMP9, FRAC_TEMP9});
          ff_init(&_tmp15, (flexfloat_desc_t){EXP_TEMP9, FRAC_TEMP9});
          ff_sub(&_tmp15, &_tmp13, &_tmp14);
          ff_init_ff(&_tmp16, &_tmp15, (flexfloat_desc_t){EXP_TEMP10, FRAC_TEMP10});
          ff_init_ff(&_tmp17, &_tmp02, (flexfloat_desc_t){EXP_TEMP10, FRAC_TEMP10});
          ff_init(&_tmp18, (flexfloat_desc_t){EXP_TEMP10, FRAC_TEMP10});
          ff_sub(&_tmp18, &_tmp16, &_tmp17);
          ff_init_ff(&_tmp19, &_tmp18, (flexfloat_desc_t){EXP_TEMP11, FRAC_TEMP11});
          ff_init_ff(&_tmp20, &_tmp01, (flexfloat_desc_t){EXP_TEMP11, FRAC_TEMP11});
          ff_init(&_tmp21, (flexfloat_desc_t){EXP_TEMP11, FRAC_TEMP11});
          ff_sub(&_tmp21, &_tmp19, &_tmp20);
          ff_init_double(&_tmp22, pow(ff_get_double(&_tmp21), 2), (flexfloat_desc_t){EXP_TEMP12, FRAC_TEMP12});
          ff_init_ff(&_tmp23, &tmpnorm, (flexfloat_desc_t){EXP_TEMP12, FRAC_TEMP12});
          ff_init(&_tmp24, (flexfloat_desc_t){EXP_TEMP12, FRAC_TEMP12});
          ff_add(&_tmp24, &_tmp23, &_tmp22);
          ff_init_ff(&_tmp25, &_tmp24, (flexfloat_desc_t){EXP_TMPNORM, FRAC_TMPNORM});
          tmpnorm=_tmp25;
        }
      }

        //norm=sqrt(tmpnorm)/bnorm;
        flexfloat_t _tmp03, _tmp04, _tmp05, _tmp06;
        ff_init_double(&_tmp03, sqrt(ff_get_double(&tmpnorm)), (flexfloat_desc_t){EXP_TEMP13, FRAC_TEMP13});
        ff_init_ff(&_tmp04, &bnorm, (flexfloat_desc_t){EXP_TEMP13, FRAC_TEMP13});
        ff_init(&_tmp05, (flexfloat_desc_t){EXP_TEMP13, FRAC_TEMP13});
        ff_div(&_tmp05, &_tmp03, &_tmp04);
        ff_init_ff(&_tmp06, &_tmp05, (flexfloat_desc_t){EXP_NORM, FRAC_NORM});
        norm=_tmp06;

        //if (norm < TOLERANCE) break;
        flexfloat_t _tmp07;
        ff_init_double(&_tmp07, TOLERANCE, (flexfloat_desc_t){EXP_NORM, FRAC_NORM});
        if (ff_lt(&norm, &_tmp07)) break;

        #pragma omp parallel for num_threads(nthds) collapse(2) default(shared) private(i,j,k)
        for (i=1;i<=nx;i++) {
          for (j=1;j<=ny;j++) {
            k=(ny+2)*i+j;
    	      //grid_new[k]=0.25 * (grid[k-1]+grid[k+1] + grid[k-(ny+2)] + grid[k+(ny+2)]);
            flexfloat_t _tmp01, _tmp02, _tmp03, _tmp04, _tmp05, _tmp06, _tmp07, _tmp08, _tmp09, _tmp10;
            flexfloat_t _tmp11, _tmp12, _tmp13, _tmp14, _tmp15, _tmp16, _tmp17, _tmp18;
            ff_init_double(&_tmp01, grid[k+(ny+2)], (flexfloat_desc_t){EXP_GRID, FRAC_GRID});
            ff_init_double(&_tmp02, grid[k-(ny+2)], (flexfloat_desc_t){EXP_GRID, FRAC_GRID});
            ff_init_double(&_tmp03, grid[k+1], (flexfloat_desc_t){EXP_GRID, FRAC_GRID});
            ff_init_double(&_tmp04, grid[k-1], (flexfloat_desc_t){EXP_GRID, FRAC_GRID});
            ff_init_double(&_tmp05, 0.25, (flexfloat_desc_t){EXP_CONST3, FRAC_CONST3});
            ff_init_ff(&_tmp06, &_tmp04, (flexfloat_desc_t){EXP_TEMP14, FRAC_TEMP14});
            ff_init_ff(&_tmp07, &_tmp03, (flexfloat_desc_t){EXP_TEMP14, FRAC_TEMP14});
            ff_init(&_tmp08, (flexfloat_desc_t){EXP_TEMP14, FRAC_TEMP14});
            ff_add(&_tmp08, &_tmp06, &_tmp07);
            ff_init_ff(&_tmp09, &_tmp08, (flexfloat_desc_t){EXP_TEMP15, FRAC_TEMP15});
            ff_init_ff(&_tmp10, &_tmp02, (flexfloat_desc_t){EXP_TEMP15, FRAC_TEMP15});
            ff_init(&_tmp11, (flexfloat_desc_t){EXP_TEMP15, FRAC_TEMP15});
            ff_add(&_tmp11, &_tmp09, &_tmp10);
            ff_init_ff(&_tmp12, &_tmp11, (flexfloat_desc_t){EXP_TEMP16, FRAC_TEMP16});
            ff_init_ff(&_tmp13, &_tmp01, (flexfloat_desc_t){EXP_TEMP16, FRAC_TEMP16});
            ff_init(&_tmp14, (flexfloat_desc_t){EXP_TEMP16, FRAC_TEMP16});
            ff_add(&_tmp14, &_tmp12, &_tmp13);
            ff_init_ff(&_tmp15, &_tmp05, (flexfloat_desc_t){EXP_TEMP17, FRAC_TEMP17});
            ff_init_ff(&_tmp16, &_tmp14, (flexfloat_desc_t){EXP_TEMP17, FRAC_TEMP17});
            ff_init(&_tmp17, (flexfloat_desc_t){EXP_TEMP17, FRAC_TEMP17});
            ff_mul(&_tmp17, &_tmp15, &_tmp16);
            ff_init_ff(&_tmp18, &_tmp17, (flexfloat_desc_t){EXP_GRID_NEW, FRAC_GRID_NEW});
            grid_new[k]=ff_get_double(&_tmp18);
          }
        }
        memcpy(temp, grid_new, sizeof(double) * (nx + 2) * (ny+2));
        memcpy(grid_new, grid, sizeof(double) * (nx + 2) * (ny+2));
        memcpy(grid, temp, sizeof(double) * (nx + 2) * (ny+2));

        //if (iter % NPRINT ==0) printf("Iteration =%d ,Relative norm=%e\n",iter,norm);
        if (iter % NPRINT ==0) printf("%.15f,",ff_get_double(&norm));
  }

  printf("Terminated on %d iterations, Relative Norm=%e \n", iter, ff_get_double(&norm));

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
