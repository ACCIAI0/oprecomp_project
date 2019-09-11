#!/bin/bash
counter=0
while [ $counter -lt 30 ]; do
        {
	make clean all DATASET=$counter -f Makefile_flex && ./corr2 > out-ref.txt
	python3 compile.py config.txt ./ $counter && ./corr2 > out.txt
        } > /dev/null
	python3 check_error.py out-ref.txt out.txt
        let counter=counter+1
done
