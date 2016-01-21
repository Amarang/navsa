import wave, os
from tqdm import tqdm
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from Fingerprint import Fingerprinter
from Split import Splitter
import Utils as u



sp = Splitter()
# sp.doSplit("navsa.wav")
sp.doSplit("random1.wav")
# sp.doSplit("navsa2.wav")
# sp.doSplit("clicks.wav")
waveform = sp.getWaveform()
smoothwaveform = sp.getSmoothWaveform()
framerate = sp.getFramerate()
ranges = sp.getRanges()
subsamples = sp.getSubsamples()
# print subsamples[0]


fig, axs = plt.subplots(nrows=2, ncols=2) 
fig.set_size_inches(18.0,10.0)

axs[0,0].plot(waveform, 'b')
axs[0,0].plot(smoothwaveform, 'r')
for left,right in ranges:
    axs[0,0].axvspan(left, right, alpha=0.25, color='grey')

fp = Fingerprinter(
        # NWINDOWS=256,
        WINDOWSIZE=128,
        NEIGHBORHOOD_SIZE=15,
        THRESHOLD=3,
        DOFASTSMOOTH=False
        )


iax = 0
for i in range(1):
    iax += 1
    print "here"
    fp.setData(subsamples[i], framerate)
    times,freqs,Pxx = fp.getSpectrogram()
    xpts, ypts = fp.getFingerprint()
    axs[iax//2,iax%2].pcolormesh(times,freqs,Pxx)
    axs[iax//2,iax%2].plot(xpts,ypts,'bo')
    print fp.getFingerprintPoints()

fig.savefig("test.png", bbox_inches='tight')
u.web("test.png")

