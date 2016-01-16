import wave, os
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import Utils as u


class Splitter:
    def __init__(self,SILENCE_TIME=0.015, WORD_TIME=0.1, WINDOW_SMOOTH=0.01, THRESHOLD=0.8):

        self.SILENCE_TIME = SILENCE_TIME # seconds
        self.WORD_TIME = WORD_TIME # seconds
        self.WINDOW_SMOOTH = WINDOW_SMOOTH # fraction of nframes
        self.THRESHOLD = THRESHOLD # n sigma away from 0
        self.DTYPE='Int16'

        self.fname = None
        self.framerate = None
        self.nchannels = None
        self.sampwidth = None
        self.nframes = None
        self.data = None
        self.smooth = None
        self.ranges = None
        self.subsamples = []

    def readWav(self, fname):
        self.fname = fname
        fin = wave.open(fname,"rb")
        data = fin.readframes(fin.getnframes())

        self.framerate = fin.getframerate()
        self.data = np.fromstring(data, dtype=self.DTYPE)
        self.nchannels = fin.getnchannels()
        self.sampwidth = fin.getsampwidth()
        self.nframes = fin.getnframes()


    def movingAverage(self, v, window):
        s = 0.0
        maf = []
        v = np.array(v, dtype="int32")
        N = len(v)
        for i in range(N):
            if i < window:
                maf.append(0.0)
                s += v[i]
            elif i==window:
                s += sum(v[i:i+window+1])
                maf.append(s / (2.0*window+1))
            elif window<i<N-window:
                s += v[i+window] - v[i-window-1]
                maf.append(s/(2.0*window+1))
            elif i>=N-window:
                s -= v[i-window-1]
                maf.append(s/(2.0*window-(i+window-N)))
            else: pass
        return np.array(maf)

    def invertRanges(self, ranges, N):
        invRanges = []
        newRight = 0
        for left, right in ranges:
            invRanges.append([newRight,left])
            newRight = right
        return np.array([r for r in invRanges if r[1]-r[0]>self.WORD_TIME*self.framerate])

    def speakingRanges(self, a, threshold):
        nranges = 999
        ranges = None
        threshold = threshold*np.std(a)
        niters = 0
        while nranges > 50 and niters < 10:
            isntzero = np.concatenate(([0], np.less(a, threshold).view(np.int8), [0]))
            absdiff = np.abs(np.diff(isntzero))
            ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
            ranges = [r for r in ranges if r[1]-r[0]>self.SILENCE_TIME*self.framerate]
            nranges = len(ranges)
            threshold *= 0.5
            niters += 1
        return self.invertRanges(ranges,len(self.data))

    def makeRanges(self):
        self.smooth = self.movingAverage(np.abs(self.data), self.WINDOW_SMOOTH*len(self.data))
        self.ranges = self.speakingRanges(self.smooth, self.THRESHOLD)
        # print smooth
        # print self.ranges

    def makeSubsamples(self):
        for irange,(left,right) in enumerate(self.ranges):
            self.subsamples.append( self.data[left:right] )

    def doSplit(self, fname):
        self.readWav(fname)
        self.makeRanges()
        self.makeSubsamples()

    def saveSubsamples(self, directory="test/"):
        prefix = directory + "/" + self.fname.split(".")[0]
        for irange,(left,right) in enumerate(self.ranges):
            filename = "%s_%i.wav" % (prefix, irange)
            out = wave.open(filename, "wb")
            out.setnchannels(self.nchannels)
            out.setsampwidth(self.sampwidth)
            out.setframerate(self.framerate)
            out.setnframes(right-left)
            out.writeframes( self.data[left:right].tostring() )
            out.close()
            print "[Split] saved %s" % filename

    def getWaveform(self):
        return self.data

    def getSmoothWaveform(self):
        return self.smooth

    def getRanges(self):
        return self.ranges

if __name__=='__main__':
    sp = Splitter()
    fig, axs = plt.subplots(nrows=2, ncols=2) 
    fig.set_size_inches(18.0,10.0)

    sp.doSplit("navsa.wav")
    sp.saveSubsamples("test/")
    axs[0,0].plot(sp.getWaveform(), 'b')
    axs[0,0].plot(sp.getSmoothWaveform(), 'r')
    for left,right in sp.getRanges():
        axs[0,0].axvspan(left, right, alpha=0.25, color='grey')

    sp.doSplit("sentence.wav")
    axs[0,1].plot(sp.getWaveform(), 'b')
    axs[0,1].plot(sp.getSmoothWaveform(), 'r')
    for left,right in sp.getRanges():
        axs[0,1].axvspan(left, right, alpha=0.25, color='grey')

    sp.doSplit("words.wav")
    axs[1,0].plot(sp.getWaveform(), 'b')
    axs[1,0].plot(sp.getSmoothWaveform(), 'r')
    for left,right in sp.getRanges():
        axs[1,0].axvspan(left, right, alpha=0.25, color='grey')

    fig.savefig("test.png", bbox_inches='tight')
    u.web("test.png")


# WRITE IT

# print invRanges
# for irange,(left,right) in enumerate(invRanges):
#     out = wave.open("test/out_%i.wav" % irange, "wb")
#     out.setnchannels(fin.getnchannels())
#     out.setsampwidth(fin.getsampwidth())
#     out.setframerate(fin.getframerate())
#     out.setnframes(right-left)
#     out.writeframes( pdata[left:right].tostring() )
#     out.close()

    # break
