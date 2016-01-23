import wave, os
from tqdm import tqdm
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from Split import Splitter
from Fingerprint import Fingerprinter
import Utils as u
import random

import scipy.ndimage as ndimage

def getFeatures(data, framerate):
    fp = Fingerprinter()
    fp.setData(ss, framerate)
    times,freqs,Pxx = fp.getSpectrogram()

    ztime = float(Ntime) / Pxx.shape[1] if Pxx.shape[1] > Ntime else 1
    zfreq = float(Nfreq) / Pxx.shape[0] if Pxx.shape[0] > Nfreq else 1

    Pxx = ndimage.interpolation.zoom(Pxx,zoom=(zfreq, ztime),order=0)

    nfreq,ntime = Pxx.shape
    freqPad = Nfreq-nfreq # pad higher frequencies with 0
    timePad = Ntime-ntime # pad higher times with 0
    Pxx = np.pad(Pxx, [(freqPad,0), (0,timePad)], mode='constant', constant_values=0.0)

    img = Pxx.flatten() # restore freq,time matrix with Pxx.reshape(Nfreq,Ntime)
    img = np.insert( img, 0, [isSignal] ) # put 0 or 1 at beginning for truth value

    return img



import time

basedir = "sounds/train/"
clips = os.listdir(basedir)

sp = Splitter()

Ntime,Nfreq = 30,30

YXtot = []

avgTimes = []
for clip in clips:

    sp.doSplit(basedir+clip)
    subsamples = sp.getSubsamples()
    framerate = sp.getFramerate()

    isSignal = int("oknavsa" in clip.lower())

    for ss in subsamples:
        t0 = time.time()

        img = getFeatures(ss, framerate)

        YXtot.append(img)

        avgTimes.append((time.time()-t0)*1000.0)

avgTimes = np.array(avgTimes)
print avgTimes.mean()
print avgTimes.std()

YXtot = np.array(YXtot)

np.save("data/imagedata_%i_%i.npy" % (Nfreq,Ntime), YXtot)
print "made data/imagedata_%i_%i.npy" % (Nfreq,Ntime)

