/* Iterative Refinemnet codes
   Authors: JunKyu Lee and Gregory D. Peterson
   Tennessee Advanced Computing Laboratory in University of Tennessee

   Description: This routine provides source code to explore numerical behaviors of iterative refinement for dynamic precision computation.

   Procedure: Modifiy the dimension of matrices and dynamic rountine of MANTISSA (MANT)
*/

#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <string.h>
//#include "mkl.h"

#include "datasets.h"

#define MANT 52 // Set bit-width for mantissa for the computation for Golden result
#define APPROX_MANT 20; //inverse correlation with COND_CONT
#define NDIM 64
#define EPSILON 0.00000000000000011
#define MAXITER 20
#define MANT_STEP3 52  // Should be equal to MANT
#define COND_CONT 0.1  //higher -> lower condition number

/* Function declaration exploiting dynamic precisions */
double my_add(double a, double b, int mant);
double my_sub(double a, double b, int mant);
double my_mult(double a, double b, int mant);
double my_div(double a, double b, int mant);
void GEPP(double **A, double **L, double **U, double **P, int n, int mant); //LU decomposition with Partial Pivoting
void SOL(double **L, double **U, double **P, double *x, double *b, int n, int mant, double *tmp1); //tri-angular solver
void MATVEC(double **A, double *x, double *p, int n, int mant);
double mat_inorm (double **matrix, double *tmp, int n); //infin-norm
int PREC_CONT(double mat_conv, int sol_mant, int n);
double mat_inorm (double **matrix, double *tmp, int n);

double ddnormi(double* dp, int N) {
	int i;
	double temp = 0;
	for (i=0; i<N; i++) {
		if (fabs(dp[i]) > temp) temp = fabs(dp[i]);
	}
	return temp;
	}

int main()
{

	int *iwork, *ipiv, *info;
	double **matrix, **L, **U, **P;
	double *x, *gx, *z, *b, *tmp1, *p, *resid, *rcond, *A, *work;
	int i, j, samp, up_mant, resid_mant, sol_mant, n_iter, max_iter, isample, ndim; //gen;
	double xdif_nrm, anorm, gnrm, r_nrm, x_nrm, pre_r_nrm, b_nrm, mat_infnorm;
	int num_cancel, success;

	double *cond;
	double *conv;


	up_mant = MANT_STEP3;	//precision for solution update process
	max_iter = MAXITER;	//iteration threshold
	samp = 1;	//number of test matrices
	success = 0;

	L = malloc(NDIM*sizeof(double *));
	U = malloc(NDIM*sizeof(double *));
	matrix = malloc(NDIM*sizeof(double *));
	P = malloc(NDIM*sizeof(double *));
	cond = malloc(NDIM*sizeof(double *));
	conv = malloc(NDIM*sizeof(double *));

	for (i=0;i<NDIM;i++)
	{
		L[i]=malloc(NDIM*sizeof(double));
		U[i]=malloc(NDIM*sizeof(double));
		matrix[i]=malloc(NDIM*sizeof(double));
		P[i]=malloc(NDIM*sizeof(double));
	}

	x = malloc(NDIM*sizeof(double));
	b = malloc(NDIM*sizeof(double));
	tmp1 = malloc(NDIM*sizeof(double));
	p = malloc(NDIM*sizeof(double));
	resid = malloc(NDIM*sizeof(double));
	z = malloc(NDIM*sizeof(double));
	gx = malloc(NDIM*sizeof(double));
	iwork = malloc((NDIM+1)*sizeof(int));
	work = malloc(NDIM*sizeof(double));
	A = malloc(NDIM*NDIM*sizeof(double));
	ipiv = malloc(NDIM*sizeof(int));
	info = malloc(sizeof(int));
	rcond = malloc((4*NDIM+1)*sizeof(double));

	//FILE *fp1, *fp2;
	//char buffer[30];
	//double data;
	isample = 0;
	ndim = NDIM;

	//for (ni=0; ni<4; ni++)
	//{
	for (isample=0;isample<samp;isample++) {

   		// matrix initialization
		for (i=0;i<ndim;i++)
		{
			for (j=0;j<ndim;j++) {matrix[i][j] = data[i][j];}
			matrix[i][i] += COND_CONT;
		 }

		mat_infnorm = mat_inorm (matrix, tmp1, ndim);
		printf("matrix norm : %f\n", mat_infnorm);

		for(i=0;i<ndim;i++) b[i] = coeffs[i];
		b_nrm = ddnormi(b, ndim);

		for (i=0;i<ndim;i++)
		{
		for (j=0;j<ndim;j++)
			{
			A[ndim*i+j] = matrix[i][j]; //A is recalculated here after calculating a condition number
			L[i][j] = 0.0;
			U[i][j] = 0.0;
			}
		}

		/********************************/
		/* Iterative Refinement Routine */
		/********************************/

		// START with 20/50bit width for precision for solving
		sol_mant =APPROX_MANT;

		// Solve Ax = b one time using GEPP
		GEPP(matrix, L, U, P, ndim, sol_mant);
		SOL(L, U, P, x, b, ndim, sol_mant, tmp1);

		pre_r_nrm = ddnormi(resid, ndim); //initial residual size



		resid_mant = (int)((double)(sol_mant)*2.0);

		for(n_iter=1; n_iter<(max_iter+1); n_iter++)
		{
			// residual calculation
			MATVEC(matrix, x, p, ndim, resid_mant);
			for(i=0; i<ndim; i++)
			resid[i] = my_sub(b[i],p[i],resid_mant);

			r_nrm = ddnormi(resid, ndim); //detect infinity norm of residual (i.e., residual size)
			x_nrm = ddnormi(x, ndim);
      printf("ACCURACY: %.15f\n", sqrt(ndim)*EPSILON);
			if (r_nrm/(mat_infnorm*x_nrm) < sqrt(ndim)*EPSILON) //double precision accuiracy for backward error --> terminiate loop
			{ printf("backward success.\n"); success = 1;
			break;}

			//1st iteration
			SOL(L, U, P, z, resid, ndim, sol_mant, tmp1);

			// MONOTONOUS INCREASING/DECREASING PRECISON

			if (r_nrm/pre_r_nrm < 0.5) // if convergence happens
			{resid_mant = sol_mant + (int) ( log2(b_nrm/r_nrm) + log2(pre_r_nrm/r_nrm) + 1.0); }//detect the number of cancellations
			else //if convergence not happen,
			{resid_mant += 1; }

			if (resid_mant>52) {resid_mant = 52;}

			pre_r_nrm = r_nrm; //store for the current residual as previous residual
			printf("resid_mant: %d at %ith iteration accuracy %g \n", resid_mant, n_iter, r_nrm/(mat_infnorm*x_nrm) );

			//1st update
			for(i=0; i<ndim; i++)
			x[i] = my_add(x[i],z[i],up_mant);


		}
	if(!success) printf("failure backward convergence at %ith sample\n", isample);

    success = 0;
	}

return 0;
// End of Main Function
}





// Start of User Functions
double my_add(double a, double b, int mant)
{
	unsigned long long int * a_copy;
	unsigned long long int * b_copy;

	unsigned long long int a1;
	unsigned long long int b1;

	double *ad;
	double *bd;

	double ad1;
	double bd1;


	double c;
	double d;
	double *result;
	unsigned long long int * raw;
	unsigned long long int man_mask;
	unsigned long long int raw_result;

	int j;

	man_mask = 0x8000000000000000;

	for (j=0;j<(mant-1);j++)
	{man_mask = man_mask>>1;
	man_mask = man_mask + 0x8000000000000000;}

	man_mask = man_mask>>12; //rearange to take mantissa part

	man_mask = 0xfff0000000000000 | man_mask;

	a_copy = &a;
	b_copy = &b;

	a1 = *a_copy;
	b1 = *b_copy;

	a1 = a1 & man_mask;
	b1 = b1 & man_mask;

	ad = &a1;
	bd = &b1;

	ad1 = *ad;
	bd1 = *bd;

	c = ad1 + bd1;

	raw = &c;
	raw_result = *raw;
	raw_result = man_mask&raw_result;
	result = &raw_result;
	d = *result;

	return (d);
}

double my_sub(double a, double b, int mant)
{
	unsigned long long int * a_copy;
	unsigned long long int * b_copy;

	unsigned long long int a1;
	unsigned long long int b1;

	double *ad;
	double *bd;

	double ad1;
	double bd1;


	double c;
	double d;
	double *result;
	unsigned long long int * raw;
	unsigned long long int man_mask;
	unsigned long long int raw_result;

	int j;

	man_mask = 0x8000000000000000;

	for (j=0;j<(mant-1);j++)
	{man_mask = man_mask>>1;
	man_mask = man_mask + 0x8000000000000000;}

	man_mask = man_mask>>12; //rearange to take mantissa part

	man_mask = 0xfff0000000000000 | man_mask;

	a_copy = &a;
	b_copy = &b;

	a1 = *a_copy;
	b1 = *b_copy;

	a1 = a1 & man_mask;
	b1 = b1 & man_mask;

	ad = &a1;
	bd = &b1;

	ad1 = *ad;
	bd1 = *bd;

	c = ad1 - bd1;

	raw = &c;
	raw_result = *raw;
	raw_result = man_mask&raw_result;
	result = &raw_result;
	d = *result;

	return (d);
}

double my_mult(double a, double b, int mant)
{
	unsigned long long int * a_copy;
	unsigned long long int * b_copy;

	unsigned long long int a1;
	unsigned long long int b1;

	double *ad;
	double *bd;

	double ad1;
	double bd1;


	double c;
	double d;
	double *result;
	unsigned long long int * raw;
	unsigned long long int man_mask;
	unsigned long long int raw_result;

	int j;

	man_mask = 0x8000000000000000;

	for (j=0;j<(mant-1);j++)
	{man_mask = man_mask>>1;
	man_mask = man_mask + 0x8000000000000000;}

	man_mask = man_mask>>12; //rearange to take mantissa part

	man_mask = 0xfff0000000000000 | man_mask;

	a_copy = &a;
	b_copy = &b;

	a1 = *a_copy;
	b1 = *b_copy;

	a1 = a1 & man_mask;
	b1 = b1 & man_mask;

	ad = &a1;
	bd = &b1;

	ad1 = *ad;
	bd1 = *bd;

	c = ad1 * bd1;

	raw = &c;
	raw_result = *raw;
	raw_result = man_mask&raw_result;
	result = &raw_result;
	d = *result;

	return (d);
}

double my_div(double a, double b, int mant)
{
	unsigned long long int * a_copy;
	unsigned long long int * b_copy;

	unsigned long long int a1;
	unsigned long long int b1;

	double *ad;
	double *bd;

	double ad1;
	double bd1;


	double c;
	double d;
	double *result;
	unsigned long long int * raw;
	unsigned long long int man_mask;
	unsigned long long int raw_result;

	int j;

	man_mask = 0x8000000000000000;

	for (j=0;j<(mant-1);j++)
	{man_mask = man_mask>>1;
	man_mask = man_mask + 0x8000000000000000;}

	man_mask = man_mask>>12; //rearange to take mantissa part

	man_mask = 0xfff0000000000000 | man_mask;

	a_copy = &a;
	b_copy = &b;

	a1 = *a_copy;
	b1 = *b_copy;

	a1 = a1 & man_mask;
	b1 = b1 & man_mask;

	ad = &a1;
	bd = &b1;

	ad1 = *ad;
	bd1 = *bd;

	c = ad1 / bd1;

	raw = &c;
	raw_result = *raw;
	raw_result = man_mask&raw_result;
	result = &raw_result;
	d = *result;

	return (d);
}


void GEPP(double **A, double **L, double **U, double **P, int n, int mant)
{
	double temp;
	int i, j, k;

	for(i=0;i<n;i++)
	{
		for(j=0;j<n;j++)
	{L[i][j]=0.0; P[i][j]=0.0;	}}

	for(i=0;i<n;i++)
	{P[i][i] = 1.0;}

	for(i=0;i<n;i++)
	{for(j=0;j<n;j++)
	{U[i][j] = A[i][j];}}

	for(i=0;i<n;i++)
	{
	for(j=i+1;j<n;j++)
	{
		if(abs(U[i][i]) < abs(U[j][i]))
        { for(k=0; k<n; k++)
        { temp = U[j][k];
          U[j][k] = U[i][k];
          U[i][k] = temp;
		  temp = P[j][k];
          P[j][k] = P[i][k];
          P[i][k] = temp;	}}}}


	for(i=0;i<n;i++)
	{
		for(j=i+1;j<n;j++)
		{L[j][i] = my_div(U[j][i],U[i][i],mant); //Lower Triangular matrix formation

			for(k=0;k<n;k++)
			{
	 		 U[j][k] = my_sub(U[j][k],my_mult(U[i][k],L[j][i],mant),mant);}
	 		 }
 	}

 	for(i=0;i<n;i++)
	L[i][i] = 1.0;

	}


/* Solver */

void SOL(double **L, double **U, double **P, double *x, double *b, int n, int mant, double *tmp1)
{
	int i, j;
	double temp;

	for (i=0;i<n;i++)
	{ x[i] = 0.0; // x will be used for P*b represetation for GEPP solver
	  tmp1[i] = 0.0;}

	for(i=0;i<n;i++)
	{
		for(j=0;j<n;j++)
		{
			x[i] = my_add(my_mult(P[i][j],b[j],mant),x[i],mant);
		}}

		// Solve triangular system
			tmp1[0] = x[0];
		for(i=1;i<n;i++)
		{ temp = 0;
			for(j=0;j<i;j++)
			{temp = my_add(temp,my_mult(L[i][j],tmp1[j],mant),mant);}
			 tmp1[i] = my_sub(x[i],temp,mant);
		}

	// x will be updated again to a solution
	    x[n-1] = my_div(tmp1[n-1],U[n-1][n-1],mant);
		for(i=n-2;i>(-1);i--)
		{ temp = 0;
			for(j=i+1;j<n;j++)
			{temp = my_add(temp,my_mult(U[i][j],x[j],mant),mant);}
			x[i] = my_div(my_sub(tmp1[i],temp,mant),U[i][i],mant);
		}
	}


void MATVEC (double **A, double *x, double *p, int n, int mant)
{
	int i,j;

	for(i=0;i<n;i++)
	{ p[i] = 0.0; }

	for (i=0;i<n;i++)
	{
		for(j=0;j<n;j++)
		{ p[i] = my_add(p[i],my_mult(A[i][j],x[j],mant),mant);}
	}
}

double mat_inorm (double **matrix, double *tmp, int n)
{
	int i, j;
	double temp;

	for(i=0;i<n;i++)
	tmp[i] = 0.0;

	for(i=0;i<n;i++)
	{
		for(j=0;j<n;j++)
		{
		tmp[i] = tmp[i] + fabs(matrix[i][j]);

		}
	}

	temp = tmp[0];
	for(i=0;i<(n-1);i++)
	{
		if (tmp[i+1]>tmp[i])
		{temp = tmp[i+1];}
    }

    return temp;
}
/*
int PREC_CONT(int num_cancel, int sol_mant, int n)
{
	int dprec;

	 if (mat_conv > 17000 || mat_conv < 60000)
	 {dprec = sol_mant + 5;}
	 else if (mat_conv < 17000)
	 {dprec = sol_mant + 5;}

	 return dprec;
 }
*/
