#!/bin/bash
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
#ORIGIN=/home/giuseppe/workspace-OPRECOMP/TEMP/flexfloat-benchmarks/FWT/
ORIGIN=/home/alberto/oprecomp/oprecomp_thesis/flexfloat-benchmarks/FWT/
cd $ORIGIN
python compile.py $DIR/config_file.txt $DIR/ >/dev/null 2>&1
cd $DIR
./fwt2 $1

