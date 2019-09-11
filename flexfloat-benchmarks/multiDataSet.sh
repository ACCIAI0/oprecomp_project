#!/bin/bash
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd $DIR
cd $1 #benchmark specific folder
python compile.py ./config_file.txt ./ $4 >/dev/null 2>&1
./$2 $3