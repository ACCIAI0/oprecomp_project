import random

array_name = "data"
n_datasets = 30
n_elements = 65536

print("#ifndef DATASET")
print("#define DATASET 0")
print("#endif")

for i in range(n_datasets):
    print("#if DATASET == %d" % (i))
    # Generate a dataset
    print("FLOAT data[]={")
    for i in range(n_elements):
        print(random.uniform(0.0, 1.0), end=",\n")
    print("};")
    print("#endif")
