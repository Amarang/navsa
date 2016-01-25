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
# sp.doSplit("sounds/oknavsa.wav")

for clip in ["navsa1","navsa2"]:
    sp.doSplit("sounds/train/%s.wav" % clip)
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

    fp = Fingerprinter()


    iax = 0
    for i in range(4):
        iax += 1
        fp.setData(subsamples[i], framerate)
        times,freqs,Pxx = fp.getSpectrogram()
        xpts, ypts = fp.getFingerprint()
        axs[iax//2,iax%2].pcolormesh(times,freqs,Pxx)

    fig.savefig("test_%s.png" % clip)
    u.web("test_%s.png" % clip)

