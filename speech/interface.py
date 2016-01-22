import wave, os
from tqdm import tqdm
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from Fingerprint import Fingerprinter
from Split import Splitter
import Utils as u


import scipy.ndimage as ndimage

sp = Splitter()
sp.doSplit("sounds/oknavsa.wav")
# sp.doSplit("sounds/oknavsa3.wav")
# sp.doSplit("sounds/oknavsaoffice2.wav")
# sp.doSplit("sounds/random4.wav")
# sp.doSplit("navsa2.wav")
waveform = sp.getWaveform()
smoothwaveform = sp.getSmoothWaveform()
framerate = sp.getFramerate()
ranges = sp.getRanges()
subsamples = sp.getSubsamples()
print len(subsamples)


fig, axs = plt.subplots(nrows=3, ncols=2) 
fig.set_size_inches(18.0,10.0)

axs[0,0].plot(waveform, 'b')
axs[0,0].plot(smoothwaveform, 'r')
for left,right in ranges:
    axs[0,0].axvspan(left, right, alpha=0.25, color='grey')

fp = Fingerprinter(
        # NWINDOWS=256,
        WINDOWSIZE=128,
        NEIGHBORHOOD_SIZE=8,
        THRESHOLD=0.3,
        DOFASTSMOOTH=False
        )


iax = 0
for i in range(1):
    iax += 1
    print "here"
    fp.setData(subsamples[i], framerate)
    times,freqs,Pxx = fp.getSpectrogram()


    zx, zy = 1, 1
    if Pxx.shape[1] > 50:
        zx = 50.0 / Pxx.shape[1]
    if Pxx.shape[0] > 50:
        zy = 50.0 / Pxx.shape[0]

    Pxx = ndimage.interpolation.zoom(Pxx,zoom=(zy, zx),order=0)
    print Pxx.shape
    freqs = freqs[:Pxx.shape[0]]
    times = times[:Pxx.shape[1]]

    xpts, ypts = fp.getFingerprint()
    # print Pxx
    # thresh = 0.5
    # Pxx[Pxx > thresh] = 1
    # Pxx[Pxx < thresh] = 0
    axs[iax//2,iax%2].pcolormesh(times,freqs,Pxx)
    axs[iax//2,iax%2].plot(xpts,ypts,'bo')
    # print fp.getFingerprintPoints()

fig.savefig("test.png", bbox_inches='tight')
u.web("test.png")

