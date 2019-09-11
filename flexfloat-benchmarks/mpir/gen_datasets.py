import random

array_name = "data"
n_datasets = 30
n_elements_x = 64
n_elements_y = 64


print("#ifndef DATASET")
print("#define DATASET 0")
print("#endif")

for i in range(n_datasets):
    print("#if DATASET == %d" % (i))
    # Generate a dataset
    print("double data[][64]={")
    for i in range(n_elements_x):
        print("{", end="")
        for j in range(n_elements_y):
            print(random.uniform(0, 1.0), end=", ")
        print("},")
    print("};")
    print("double coeffs[64]={")
    for i in range(n_elements_x):
        print(random.uniform(0, 1.0), end=", ")
    print("};")
    print("#endif")
