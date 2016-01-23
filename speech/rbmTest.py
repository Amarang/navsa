from tqdm import tqdm
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import Utils as u

from sklearn import linear_model, metrics
from sklearn.cross_validation import train_test_split


def nudge(Xtot, Ytot, Nfreq, Ntime, w=5):
    newXtot = []
    newYtot = np.array([Ytot for _ in range(3)]).ravel(1)
    for x in Xtot:
        xmat = x.reshape(Nfreq,Ntime)
        left = xmat[:,range(w,Ntime)]
        left = np.pad(left, [(0,0), (w,0)], mode='constant', constant_values=0.0)
        right = xmat[:,range(0,Ntime-w)]
        right = np.pad(right, [(0,0), (0,w)], mode='constant', constant_values=0.0)
        newXtot.append(xmat.flatten())
        newXtot.append(left.flatten())
        newXtot.append(right.flatten())
    return np.array(newXtot), newYtot


datafile = "data/imagedata_25_25.npy"
Nfreq, Ntime = map(int,datafile.split(".")[0].split("_")[-2:])

YXtot = np.load(datafile)
Xtot = YXtot[:,range(1,len(YXtot[0]))]
Ytot = YXtot[:,0]

Xtot, Ytot = nudge(Xtot,Ytot,Nfreq,Ntime)
print Xtot.shape, Ytot.shape

X_train, X_test, Y_train, Y_test = train_test_split(Xtot, Ytot, test_size=0.75, random_state=42)


logistic_classifier = linear_model.LogisticRegression(C=100.0)
logistic_classifier.fit(X_train, Y_train)

print "Logistic regression using raw pixel features:\n%s\n" % (metrics.classification_report(Y_test,logistic_classifier.predict(X_test)))

print logistic_classifier.score(X_train, Y_train)
print logistic_classifier.score(X_test, Y_test)

