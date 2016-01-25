from tqdm import tqdm
import threading
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import matplotlib.pyplot as plt

import Utils as u
from Split import Splitter
from Fingerprint import Fingerprinter
from Process import Processor
from Trigger import Trigger

proc = Processor()
tr = Trigger()

fname = proc.processTrainingSet(basedir="sounds/train/", signalword="oknavsa", savedir="data/")
# fname = proc.processTrainingSet(basedir="sounds/train/", signalword="navsa", savedir="data/")
# proc.loadTrainData("data/imagedata_30_30.npy")
proc.trainAndTest()

#if not in this range, we want to not fingerprint it to save time and trouble
lower,upper = proc.getKeywordDurationRange()
print lower,upper
# tr.MIN_WORD_TIME = lower
# tr.MAX_WORD_TIME = upper

for sample in ["oknavsa", "navsa", "random"]:
    tr.readWav("sounds/test_%s.wav" % sample)
    topred = tr.getMainSubsample()
    if topred is None: continue
    topred = proc.getFeatures(topred, tr.getFramerate())
    print sample, round(proc.predict(topred),3)

print "Done testing samples"
print "Now will score realtime audio"

# def myCallback(data,framerate):
#     print "duration: %.2f s, score: %.2f" % (1.0*len(data)/framerate, proc.getKeywordProbability(data, framerate))

# # thread = threading.Thread(target=tr.readMic, kwargs={"verbose":True, "duration":5, "callback":myCallback})
# thread = threading.Thread(target=tr.readMic, kwargs={"duration":15, "callback":myCallback})
# thread.start()

# print "Done"

# # thread.join()
