### current bpython session - file will be reevaluated, ### lines will not be run
import wave
import numpy as np
import matplotlib.pyplot as plt
SILENCE_TIME = 0.1 # seconds
THRESHOLD = 30


wave.open("test.wav","rb")
fin = wave.open("test.wav","rb")
data = fin.readframes(fin.getnframes())

framerate = fin.getframerate()

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
# xs = ranges[:,0]
# ys = 1 + 0*ranges[:,0]
plt.plot(ranges[:,0], 1+0*ranges[:,0], 'bo')
plt.plot(ranges[:,1], 1+0*ranges[:,1], 'go')
# plt.plot(ranges)
plt.show()
# ranges = [r for r in ranges if r[1]-r[0] > int(SILENCE_TIME*framerate)]
# print np.array(ranges)

# pdata2 = np.copy(pdata)
# pdata2[np.abs(pdata2) < 10] = 0
# plt.plot(pdata2, 'b')
# plt.show()
# def consecutiveZero(data, stepsize=0):
#     return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)

