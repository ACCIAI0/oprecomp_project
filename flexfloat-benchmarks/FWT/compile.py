import sys
import csv
import subprocess

# Pulp with SmallFloat extensions
def set_coefficient_bits(prec):
    if(prec <= 3):                   # float8
        return 5
    elif(prec > 3 and prec <= 8):    # float16ext
        return 8
    elif(prec > 8 and prec <= 11):   # float16
        return 5
    elif(prec > 11 and prec <= 24):  # float32
        return 8
    elif(prec > 24 and prec <= 53):  # float64
        return 11

def init_params(config_vals):
    result = []

    result.append(" -DFRAC_INPUT=%d" % (config_vals[0] - 1))
    result.append(" -DFRAC_OUTPUT=%d" % (config_vals[1] - 1))

    result.append(" -DEXP_INPUT=%d" % set_coefficient_bits(config_vals[0]))
    result.append(" -DEXP_OUTPUT=%d" % set_coefficient_bits(config_vals[1]))


    return "".join(result)

with open(sys.argv[1], 'r') as config_file:
    reader = csv.reader(config_file)
    row = next(reader)
    if row[-1] == '':
        del row[-1]
    config_vals = [int(x) for x in row]
    ext_cflags = init_params(config_vals)
    make_process = subprocess.Popen(
            "make clean all -f Makefile_flex CONF_MODE=file EXT_CFLAGS=\""
            + ext_cflags + "\" OUTPUT_DIR=\"" + sys.argv[2] + "\" DATASET=" + 
            sys.argv[3], shell=True, stderr=subprocess.STDOUT)
    make_process.wait()
