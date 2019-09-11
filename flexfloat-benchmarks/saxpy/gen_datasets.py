import random

array_name = "data"
n_datasets = 30
n_elements = 10000

print("#define SIZE {}".format(n_elements))
print("#ifndef DATASET")
print("#define DATASET 0")
print("#endif")

for i in range(n_datasets):
    print("#if DATASET == %d" % (i))
    # Generate a dataset
    print("double input[%d]={" % (n_elements))
    for i in range(n_elements):
        print(random.uniform(0.0, 5.0), end=",\n")
    print("};")
    print("#endif")

for i in range(n_datasets):
    print("#if DATASET == %d" % (i))
    # Generate a dataset
    print("double output[%d]={" % (n_elements))
    for i in range(n_elements):
        print(random.uniform(0.0, 5.0), end=",\n")
    print("};")
    print("#endif")
