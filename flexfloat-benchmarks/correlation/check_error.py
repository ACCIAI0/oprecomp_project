import sys
import numpy as np

with open(sys.argv[1], "r") as f1:
    with open(sys.argv[2], "r") as f2:
        line = f1.readline()
        if line[-1] == ',': line = line[:-1]
        res1 = line.split(",")
        res1 = [float(i) for i in res1]
        res1 = np.asarray(res1, dtype=np.float64)
        line = f2.readline()
        if line[-1] == ',': line = line[:-1]
        res2 = line.split(",")
        res2 = [float(i) for i in res2]
        res2 = np.asarray(res2, dtype=np.float64)
        error = np.square(res1 - res2).mean()
        print(error)
