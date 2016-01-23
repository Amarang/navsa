from tqdm import tqdm
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import matplotlib.pyplot as plt

import Utils as u
from Split import Splitter
from Fingerprint import Fingerprinter
from Process import Processor

import time

t0 = time.time()

proc = Processor()
# fname = proc.processTrainingSet(basedir="sounds/train/", signalword="oknavsa", savedir="data/")
proc.loadTrainData("data/imagedata_30_30.npy")

print "%.2f" % (time.time()-t0)


for i in range(10):
    t0 = time.time()
    proc.trainAndTest()
    print "%.2f" % (time.time()-t0)
