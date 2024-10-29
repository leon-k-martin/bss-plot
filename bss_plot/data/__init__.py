from os.path import abspath, dirname, join
import numpy as np

ROOT = dirname(abspath(__file__))

hcp_sc = np.loadtxt(join(ROOT, "HCP_avg-SC.txt"))
