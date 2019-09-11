#!/bin/bash
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
#ORIGIN=/home/giuseppe/workspace-OPRECOMP/TEMP/flexfloat-benchmarks/dwt/
ORIGIN=/home/alberto/oprecomp/oprecomp_thesis/flexfloat-benchmarks/dwt/
cd $ORIGIN
python compile.py $DIR/config_file.txt $DIR/ >/dev/null 2>&1
cd $DIR
./dwt2 $1

