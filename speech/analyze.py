### current bpython session - file will be reevaluated, ### lines will not be run
import wave
import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack as sfft
SILENCE_TIME = 0.1 # seconds
THRESHOLD = 50


fin = wave.open("test.wav","rb")
# fin = wave.open("test2.wav","rb")
# fin = wave.open("johncena.wav","rb")
data = fin.readframes(fin.getnframes())
# data = fin.readframes(100000)

framerate = fin.getframerate()
print framerate

pdata = np.fromstring(data, dtype='Int16')


def nonZeroRanges(a, threshold=10):
    isntzero = np.concatenate(([0], np.less(a, threshold).view(np.int8), [0]))
    absdiff = np.abs(np.diff(isntzero))
    ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
    print ranges
    return ranges

plt.plot(pdata, 'r')

ranges = nonZeroRanges(pdata, 30)
ranges = np.array([r for r in ranges if r[1]-r[0] > int(SILENCE_TIME*framerate)])

print pdata
print pdata.mean()
print np.abs(pdata).mean()
print pdata.std()
print sfft.fft(pdata)
plt.plot( sfft.irfft(sfft.rfft(pdata)) )

# plt.plot(ranges[:,0], 1+0*ranges[:,0], 'bo')
# plt.plot(ranges[:,1], 1+0*ranges[:,1], 'go')

# plt.plot(ranges)

plt.show()

