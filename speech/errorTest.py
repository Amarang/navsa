import wave, os
from tqdm import tqdm
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from Split import Splitter
import Utils as u
import random



clips = [
    ["navsa",10],
    ["oknavsa",9],
    ["navsa2",9],
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

# params = np.arange(0.1,0.9,0.01) 
# p1s = np.arange(0.005,0.02,0.005)
# p2s = np.arange(0.1,0.3,0.01)
# p3s = np.arange(0.004,0.01,0.001)
# p4s = np.arange(0.2,0.8,0.1)


# ncombos = len(p1s)*len(p2s)*len(p3s)*len(p4s)
# print ncombos


# ps = []
# minabserr = 100

# for i in range(100):
for param in [1]:


    # p1 = random.choice(p1s)
    # p2 = random.choice(p2s)
    # p3 = random.choice(p3s)
    # p4 = random.choice(p4s)
    # sp = Splitter(
    #         SILENCE_TIME=p1,
    #         WORD_TIME=p2,
    #         WINDOW_SMOOTH=p3,
    #         THRESHOLD=p4
    #         )

    sp = Splitter(
            SILENCE_TIME=0.015,
            WORD_TIME=0.22,
            WINDOW_SMOOTH=0.006,
            THRESHOLD=0.5
            )

    abserr = 0
    for clip,nwords in clips:
        sp.doSplit( "sounds/%s.wav" % clip )
        nsubsamples = len(sp.getSubsamples())
        print clip,nwords,nsubsamples
        abserr += abs(nwords - nsubsamples)


    # if abserr < minabserr:
    #     ps = [p1,p2,p3,p4]
    #     minabserr = abserr

    totwords = sum([c[1] for c in clips])
    print "[%.4f] %i/%i=%.2f" % (param,abserr,totwords, 1.0*abserr/totwords)
    # print "[%.5f %.5f %.5f %.5f] %i/%i=%.2f" % (p1,p2,p3,p4,abserr,totwords, 1.0*abserr/totwords)


# print minabserr
# print ps

