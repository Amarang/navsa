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


clips = [
    # ["navsa",10],
    ["oknavsa",9],
    # ["navsa2",9],
    ["oknavsa2",8],
    ["oknavsaoffice",12],
    ["oknavsaoffice2",39],
    ["random1",11],
    ["random2",12],
    ["random3",55],
    ["random4",56],
    ["random5",62],
    ["oknavsa3",51],
    ["oknavsa4",48]
]

sp = Splitter()
fp = Fingerprinter()

# Ntime,Nfreq = 6,5
Ntime,Nfreq = 40,30

YXtot = []

# for clip,nwords in clips[:1]:
for clip,nwords in tqdm(clips):

    sp.doSplit( "sounds/%s.wav" % clip )
    subsamples = sp.getSubsamples()
    framerate = sp.getFramerate()

    isSignal = int("oknavsa" in clip.lower())

    # for ss in subsamples[:2]:
    for ss in subsamples:

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

        # print img
        YXtot.append(img)

YXtot = np.array(YXtot)

np.save("data/imagedata_%i_%i.npy" % (Nfreq,Ntime), YXtot)

