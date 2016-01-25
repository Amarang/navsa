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
    confidence = round(proc.predict(topred),3)
    print sample, confidence

print "Done testing samples"
print "Now will score realtime audio"

def myCallback(data,framerate):
    confidence = proc.getKeywordProbability(data, framerate)
    if confidence > 0.8: u.play("../sounds/notification.wav")
    print "duration: %.2f s, score: %.2f" % (1.0*len(data)/framerate, confidence)
# thread = threading.Thread(target=tr.readMic, kwargs={"verbose":True, "duration":5, "callback":myCallback})
thread = threading.Thread(target=tr.readMic, kwargs={"duration":8, "callback":myCallback})
thread.start()
print "Done"
# thread.join()
