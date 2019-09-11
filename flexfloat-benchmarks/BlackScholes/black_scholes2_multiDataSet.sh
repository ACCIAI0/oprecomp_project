#!/bin/bash
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
ORIGIN=/home/alberto/oprecomp/oprecomp_thesis/flexfloat-benchmarks/BlackScholes/
cd $ORIGIN
python compile.py $DIR/config_file.txt $DIR/ $2 >/dev/null 2>&1
cd $DIR
./black_scholes2 $1

