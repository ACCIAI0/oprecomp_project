# OPRECOMP Project
This project is part of a research project conducted by the University of Bologna about energy efficiency in high precision computing. It's been developed as a master degree thesis project.

##Getting Started
###Prerequisites
* a compatible Linux-based distro (Ubuntu 18.04 has been proven to be compatible)
* Python 3.6 or later, latest version [here](https://www.python.org/downloads/)
* [Cplex](https://www.ibm.com/it-it/products/ilog-cplex-optimization-studio) and [DOcplex](https://developer.ibm.com/docloud/documentation/optimization-modeling/modeling-for-python/) installed

###Python libraries
* numpy
* pandas
* tensorflow
* keras
* sklearn
* scipy
* networkx
* matplotlib
* colorama

All of them can be downloaded and installed using `pip`:
```
pip install <library_name>
```

##Running the project
The main module is `al.py` and it can be launched with the command
```
python3 al.py <arg1> <arg2> ... 
```
There are two mandatory arguments, -bm` and `-exp`, respectively specifying the benchmark and the target error exponent:
```
python3 al.py -bm <benchmark_name> -exp <integer>
```
For a complete list of all parameters names refer to the following list or execute `python3 al.py -help`.

| parameter name | description | mandatory | default |
| ------------- | ----------- | --------- | ------- |
| `-bm` | Specifies the name of the target benchmark. It has to be one present inside the folder `flexfloat-benchmarks` | yes |
| `-exp` | Specifies the target error: `-exp n` is considered as the error ![equation](http://www.sciweavers.org/tex2img.php?eq=10%5E%7B-n%7D&bc=Transparent&fc=Black&im=png&fs=12&ff=arev&edit=0)| yes |
| `-B` | Specifies the maximum number of bits for a variable | | 53 |
| `-b` | Specifies the minimum number of bits for a variable | | 4 |
| `-cfr` | Specifies what type of classifier to use | | DT |
| `-ds` | Specifies the dataset used for training | | 0 |
| `-dump` | Specifies the __directory__ where to dump the result of the computation as a json file | | `None` |
| `-et` | Specifies the threshold over which errors are considered too large | | 0.9 |
| `-limit` | Specifies the orders of magnitude withing which to find the solution, starting from `-exp` | | 0 |
| `-manual` | If specified, it enables step-by-step iterations, forcing the user to press `Enter` between one and the next iteration |
| `-p` | Specifies the probability of changing a single length inside the configuration when generating neighbours | | 0.3 |
| `-pg` | If specified, the program will print the variable graph after the computation | 
| `-reg` | Specifies what type of regressor to use | | NN |
| `-setsize` | Specifies the number fo entries to sample from the real dataset to use as training set and, in part, as test set (see `-setsplit`) | | 1000 |
| `-setsplit` | Specifies the ratio between test set and training set | | 0.1 |
| `-steps` | Specifies how many more steps steps to run after the first non-generated feasible solution has been found | | 5 |

An example of run is the following:
```
python3 al.py -bm convolution -exp 5 -limit 5 -steps 8 -manual -dump ..
```


