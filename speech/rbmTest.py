from tqdm import tqdm
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import Utils as u

from sklearn import linear_model, datasets, metrics
from sklearn.cross_validation import train_test_split
from sklearn.neural_network import BernoulliRBM
from sklearn.pipeline import Pipeline

def nudge(Xtot, Ytot, Nfreq, Ntime, w=2):
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


datafile = "data/imagedata_30_40.npy"
Nfreq, Ntime = map(int,datafile.split(".")[0].split("_")[-2:])

YXtot = np.load(datafile)
Xtot = YXtot[:,range(1,len(YXtot[0]))]
Ytot = YXtot[:,0]

print Xtot.shape, Ytot.shape

Xtot, Ytot = nudge(Xtot,Ytot,Nfreq,Ntime)
# print Xtot, Ytot
print Xtot.shape, Ytot.shape

X_train, X_test, Y_train, Y_test = train_test_split(Xtot, Ytot,
                                                    test_size=0.2,
                                                    random_state=42)

# Models we will use
logistic = linear_model.LogisticRegression()
rbm = BernoulliRBM(random_state=0, verbose=True)

classifier = Pipeline(steps=[('rbm', rbm), ('logistic', logistic)])

###############################################################################
# Training

# Hyper-parameters. These were set by cross-validation,
# using a GridSearchCV. Here we are not performing cross-validation to
# save time.
rbm.learning_rate = 0.06
rbm.n_iter = 20
# More components tend to give better prediction performance, but larger
# fitting time
rbm.n_components = 50
logistic.C = 6000.0

# Training RBM-Logistic Pipeline
classifier.fit(X_train, Y_train)

# Training Logistic regression
logistic_classifier = linear_model.LogisticRegression(C=100.0)
logistic_classifier.fit(X_train, Y_train)

###############################################################################
# Evaluation

print()
print("Logistic regression using RBM features:\n%s\n" % (
    metrics.classification_report(
        Y_test,
        classifier.predict(X_test))))

print("Logistic regression using raw pixel features:\n%s\n" % (
    metrics.classification_report(
        Y_test,
        logistic_classifier.predict(X_test))))


print logistic_classifier.predict(X_test)
print Y_test
