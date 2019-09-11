#!/bin/bash
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
ORIGIN=/home/alberto/oprecomp/oprecomp_thesis/flexfloat-benchmarks/convolution/
#ORIGIN=/2nd_disk/workspace-approx/flexfloat-benchmarks/convolution/
cd $ORIGIN
python compile.py $DIR/config_file.txt $DIR/ >/dev/null 2>&1
cd $DIR
./conv2 $1

