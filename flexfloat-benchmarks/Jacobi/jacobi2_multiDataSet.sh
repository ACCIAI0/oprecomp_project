#!/bin/bash
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
#ORIGIN=/2nd_disk/workspace-approx/flexfloat-benchmarks/Jacobi/
ORIGIN=/home/alberto/oprecomp/oprecomp_thesis/flexfloat-benchmarks/Jacobi/
cd $ORIGIN
python compile.py $DIR/config_file.txt $DIR/ $2 >/dev/null 2>&1
cd $DIR
./jacobi2 $1

