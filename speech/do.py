from tqdm import tqdm
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import matplotlib.pyplot as plt

import Utils as u
from Split import Splitter
from Fingerprint import Fingerprinter
from Process import Processor
from Trigger import Trigger

import time

t0 = time.time()

proc = Processor()

# fname = proc.processTrainingSet(basedir="sounds/train/", signalword="oknavsa", savedir="data/")
# fname = proc.processTrainingSet(basedir="sounds/train/", signalword="navsa", savedir="data/")
proc.loadTrainData("data/imagedata_30_30.npy")

proc.trainAndTest()


tr = Trigger()
for sample in ["oknavsa", "navsa", "random"]:

    tr.readWav("sounds/test_%s.wav" % sample)

    topred = tr.getMainSubsample()
    if topred is None: continue

    topred = proc.getFeatures(topred, tr.getFramerate())

    print sample, round(proc.predict(topred),3)

