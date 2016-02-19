import wave, os
from tqdm import tqdm
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import Utils as u

import scipy
import scipy.signal
import scipy.ndimage as ndimage
import scipy.ndimage.filters as filters

class Fingerprinter:
    def __init__(self,NEIGHBORHOOD_SIZE=8, THRESHOLD=0.3, WINDOWSIZE=128, DOFASTSMOOTH=False):

        # self.NWINDOWS = NWINDOWS
        self.WINDOWSIZE = WINDOWSIZE
        self.NEIGHBORHOOD_SIZE = NEIGHBORHOOD_SIZE
        self.THRESHOLD = THRESHOLD
        self.DOFASTSMOOTH = DOFASTSMOOTH

        self.data = None
        self.framerate = None
        self.Pxx = None
        self.freqs = None
        self.times = None

        self.xy = None # xy indices of peaks
        self.tpeaks = None # times of peaks
        self.fpeaks = None # frequencies of peaks

    def setData(self, data, framerate):
        self.data = data
        self.framerate = framerate
        self.Pxx, self.tpeaks, self.fpeaks = None, None, None

    def makeSpectrogram(self):
        # self.Pxx, self.freqs, self.times, _ = plt.specgram(self.data, Fs = self.framerate, NFFT=self.NWINDOWS, noverlap=self.NWINDOWS//2)
        self.freqs, self.times, self.Pxx = scipy.signal.spectrogram(self.data, fs = self.framerate, nperseg=self.WINDOWSIZE)
        self.Pxx = np.log(self.Pxx)

        
        if self.DOFASTSMOOTH:
            self.Pxx = self.Pxx[::2] # every other frequency
            self.freqs = self.freqs[::2]
            self.Pxx = self.Pxx[:,range(0,len(self.Pxx[0]),2)] # every other time
            self.times = self.times[::2]
        else:
            self.Pxx = ndimage.filters.gaussian_filter(self.Pxx, 1, mode='nearest')

        self.Pxx -= self.Pxx.min() # raise lowest to 0
        self.Pxx /= self.Pxx.max() # scale highest to 1

    def getSpectrogram(self):
        if self.Pxx is None:
            self.makeSpectrogram()

        return self.times, self.freqs, self.Pxx

    def findPeaks(self):

        Pxx_max = filters.maximum_filter(self.Pxx, self.NEIGHBORHOOD_SIZE)
        maxima = (self.Pxx == Pxx_max)
        Pxx_min = filters.minimum_filter(self.Pxx, self.NEIGHBORHOOD_SIZE)
        diff = ((Pxx_max - Pxx_min) > self.THRESHOLD)
        maxima[diff == 0] = 0
        labeled, num_objects = ndimage.label(maxima)
        self.xy = np.array(ndimage.center_of_mass(self.Pxx, labeled, range(1, num_objects+1)))
        self.tpeaks, self.fpeaks = self.times[self.xy[:,1].astype('int')], self.freqs[self.xy[:,0].astype('int')]

    def getFingerprint(self):
        if self.Pxx is None:
            self.makeSpectrogram()

        if self.tpeaks is None or self.fpeaks is None:
            self.findPeaks()

        return self.tpeaks, self.fpeaks

    def getFingerprintPoints(self):
        xpts, ypts = self.getFingerprint()
        return np.c_[xpts, ypts]

if __name__=='__main__':
    import Split
    from scikits.talkbox.features import mfcc
    sp = Split.Splitter()
    fp = Fingerprinter()

    fig, axs = plt.subplots(nrows=2, ncols=1) 
    fig.set_size_inches(12.0,10.0)

    sp.doSplit("sounds/train/oknavsa1.wav")
    ss = sp.getSubsamples()[0]

    fp.setData(ss, sp.getFramerate())


    times,freqs, Pxx = fp.getSpectrogram()
    axs[0].pcolormesh(times,freqs,Pxx)

    # ceps = mfcc(ss, fs=sp.getFramerate(), nceps=10)[0]
    # times = np.arange(ceps.shape[0])
    # freqs = np.arange(ceps.shape[1])
    # axs[2].pcolormesh(times,freqs,ceps.T)

    axs[1].plot(np.arange(0.0,len(ss))/sp.getFramerate(), ss, 'b')

    # sp.doSplit("words.wav")
    # axs[1,0].plot(sp.getWaveform(), 'b')
    # axs[1,0].plot(sp.getSmoothWaveform(), 'r')
    # for left,right in sp.getRanges():
    #     axs[1,0].axvspan(left, right, alpha=0.25, color='grey')

    fig.savefig("fp.png", bbox_inches='tight')
    u.web("fp.png")

