import wave, os
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

import scipy.fftpack
import scipy.signal
from scipy.signal import butter, lfilter, freqz, hilbert, savgol_filter, wiener



SILENCE_TIME = 0.015 # seconds
WORD_TIME = 0.1 # seconds
WINDOW_SMOOTH = 0.01 # fraction of nframes
THRESHOLD = 0.8 # n sigma away from 0


def butter_lowpass(lowercut, uppercut, fs, order=5):
    nyq = 0.5 * fs
    uppercut = uppercut / nyq
    lowercut = lowercut / nyq
    b, a = butter(order, [lowercut, uppercut], btype='bandpass', analog=False)
    return b, a

def mafast(v,window):
    s = 0.0
    maf = []
    N = len(v)
    for i in range(N):
        if i < window:
            maf.append(0.0)
            s += v[i]
        elif i==window:
            s += sum(v[i:i+window+1])
            maf.append(s / (2.0*window+1))
        elif window<i<N-window:
            s += v[i+window]
            s -= v[i-window-1]
            maf.append(s/(2.0*window+1))
        elif i>=N-window:
            s -= v[i-window-1]
            maf.append(s/(2.0*window-(i+window-N)))
        else:
            pass
            
    return np.array(maf)

def ma(v,window):
    return np.array([v[max(0,i-window):i+window].mean() for i in range(len(v))])

def butter_lowpass_filter(data, lowercut, uppercut, fs, order=5):
    b, a = butter(order, [lowercut/(0.5*fs), uppercut/(0.5*fs)], btype='bandpass', analog=False)
    return lfilter(b, a, data)

def web(filename,user="namin"):
    os.system("scp %s %s@uaf-8.t2.ucsd.edu:~/public_html/dump/ >& /dev/null" % (filename, user))
    print "Copied to uaf-8.t2.ucsd.edu/~%s/dump/%s" % (user, filename.split("/")[-1])



# fin = wave.open("test.wav","rb")
fin = wave.open("sentence.wav","rb") # knocked sideways, the statue looked as if it would fall
# fin = wave.open("navsa.wav","rb") # navsa navsa navsa navsa
# fin = wave.open("words.wav","rb") # fourier transform sentence
# fin = wave.open("test2.wav","rb")
data = fin.readframes(fin.getnframes())

# fin = wave.open("johncena.wav","rb")
# data = fin.readframes(100000)

framerate = fin.getframerate()
print framerate

pdata = np.fromstring(data, dtype='Int16')

# pdata = butter_lowpass_filter(pdata, 0,5000, framerate, order=3)


def nonZeroRanges(a, threshold=THRESHOLD):
    nranges = 999
    ranges = None
    # threshold = threshold*np.abs(a).max()
    threshold = threshold*np.std(a)
    niters = 0
    while nranges > 50 and niters < 50:
        print "here"
        isntzero = np.concatenate(([0], np.less(a, threshold).view(np.int8), [0]))
        absdiff = np.abs(np.diff(isntzero))
        ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
        ranges = [r for r in ranges if r[1]-r[0]>SILENCE_TIME*framerate]
        nranges = len(ranges)
        threshold *= 0.5
        niters += 1
    # print ranges
    # print niters
    return np.array(ranges)

fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis

# ax.plot(pdata, 'r')

# ranges = nonZeroRanges(pdata, 30)
# ranges = np.array([r for r in ranges if r[1]-r[0] > int(SILENCE_TIME*framerate)])

# print pdata
# print pdata.mean()
# print np.abs(pdata).mean()
# print pdata.std()
# print sfft.fft(pdata)


# cutoffFreq = 100.0 # Hz
# xv = np.linspace(0,30,1000)
# test = butter_lowpass_filter(pdata, 0,500, framerate, order=3)
# ax.plot(test, 'g')

ax.plot(pdata, 'b')


print "here1"
# smooth = wiener(np.abs(pdata),0.01*len(pdata)+1,1)
smooth = mafast(abs(pdata),WINDOW_SMOOTH*len(pdata))
print "here2"
ax.plot(smooth, 'r')

ranges = nonZeroRanges(smooth)

# # ax.plot( sfft.irfft(sfft.rfft(pdata)) )
# print len(ssig.resample(pdata,len(pdata//1000)))
# print len(pdata)
# ax.plot(ssig.resample(pdata,100), 'g')

def invertRanges(ranges, N):
    invRanges = []
    newRight = 0
    for left, right in ranges:
        invRanges.append([newRight,left])
        newRight = right
    return np.array([r for r in invRanges if r[1]-r[0]>WORD_TIME*framerate])


# ax.plot(ranges[:,0], 1+0*ranges[:,0], 'bo')
# ax.plot(ranges[:,1], 1+0*ranges[:,1], 'go')


# for left,right in ranges:
#     ax.axvspan(left, right, alpha=0.25, color='grey')

invRanges = invertRanges(ranges, len(pdata))

for left,right in invRanges:
    ax.axvspan(left, right, alpha=0.25, color='grey')

data = fin.readframes(fin.getnframes())
# data = fin.readframes(100000)

# WRITE IT

print invRanges
for irange,(left,right) in enumerate(invRanges):
    out = wave.open("test/out_%i.wav" % irange, "wb")
    out.setnchannels(fin.getnchannels())
    out.setsampwidth(fin.getsampwidth())
    out.setframerate(fin.getframerate())
    out.setnframes(right-left)
    out.writeframes( pdata[left:right].tostring() )
    out.close()

    # break


# ax.plot(ranges)

fig.savefig("test.png", bbox_inches='tight')
web("test.png")

# plt.show()

