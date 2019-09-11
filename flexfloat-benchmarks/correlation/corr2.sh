#!/bin/bash
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
ORIGIN=/home/alberto/oprecomp/oprecomp_thesis/flexfloat-benchmarks/correlation/
#ORIGIN=/2nd_disk/workspace-approx/flexfloat-benchmarks/correlation/
cd $ORIGIN
python compile.py $DIR/config_file.txt $DIR/ >/dev/null 2>&1
cd $DIR
./corr2 $1

