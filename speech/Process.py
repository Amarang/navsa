import wave, os, warnings
from tqdm import tqdm
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from Trigger import Trigger
from Fingerprint import Fingerprinter
import Utils as u
import scipy.ndimage as ndimage
from sklearn import linear_model, metrics
from sklearn import cross_validation

class Processor:
    def __init__(self, Ntime=15, Nfreq=15, DO_NUDGE=True,DO_STRETCH=True, alg="logistic"):
        self.Ntime,self.Nfreq = Ntime,Nfreq
        self.YXtot = []
        self.keywordDurations = []
        self.DURATION_SIGMA = 3.0
        self.DO_NUDGE = DO_NUDGE
        self.DO_STRETCH = DO_STRETCH
        self.alg = alg
        self.verbosity = 2
        self.clf = None

    def getFeatures(self, data, framerate, isSignal=0, timestretchFactor=1.0):
        fp = Fingerprinter()
        fp.setData(data, framerate)
        times,freqs,Pxx = fp.getSpectrogram(timestretchFactor)

        ztime = float(self.Ntime) / Pxx.shape[1] if Pxx.shape[1] > self.Ntime else 1
        zfreq = float(self.Nfreq) / Pxx.shape[0] if Pxx.shape[0] > self.Nfreq else 1

        Pxx = ndimage.interpolation.zoom(Pxx,zoom=(zfreq, ztime),order=0)

        nfreq,ntime = Pxx.shape
        freqPad = max(self.Nfreq-nfreq,0) # pad higher frequencies with 0
        timePad = max(self.Ntime-ntime,0) # pad higher times with 0
        Pxx = np.pad(Pxx, [(freqPad,0), (0,timePad)], mode='constant', constant_values=0.0)

        img = Pxx.flatten() # restore freq,time matrix with Pxx.reshape(self.Nfreq,self.Ntime)
        img = np.insert( img, 0, [isSignal] ) # put 0 or 1 at beginning for truth value

        return img

    def getKeywordDurationRange(self):
        mu, sig = self.keywordDurations.mean(), self.keywordDurations.std()
        return [mu - sig*self.DURATION_SIGMA, mu + sig*self.DURATION_SIGMA]

    def processTrainingSet(self, basedir="sounds/train/", signalword="oknavsa", savedir="data/"):

        clips = [clip for clip in os.listdir(basedir) if clip.endswith(".wav")]

        try:
            with open("sounds/train/thresh.dat","r") as fh:
                lines = [line.strip() for line in fh.readlines() if len(line)>1]
                bestThresh = {line.split(",")[0]:int(line.split(",")[1]) for line in lines}
        except:
            bestThresh = {}

        tr = Trigger()

        self.YXtot = []
        self.keywordDurations = []

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore",category=Warning)

            for clip in clips:

                if clip in bestThresh: tr.setParams({"THRESHOLD": bestThresh[clip]})
                else: tr.setParams({"THRESHOLD": 600})

                if clip.lower().startswith(signalword):
                    isSignal = True
                elif clip.lower().startswith("random"):
                    isSignal = False
                else:
                    continue

                tr.readWav(basedir+clip)
                subsamples = tr.getSubsamples()
                framerate = tr.getFramerate()

                if self.verbosity > 1: print "Loading clip %s (isSignal: %i) ==> %i subsamples" % (clip, isSignal, len(subsamples))

                for ss in subsamples:
                    if isSignal:
                        self.keywordDurations.append( self.getSampleDuration(ss, framerate) )

                    self.YXtot.append( self.getFeatures(ss,framerate,isSignal) )
                    if self.DO_STRETCH:
                        self.YXtot.append( self.getFeatures(ss,framerate,isSignal,timestretchFactor=1.20) )
                        self.YXtot.append( self.getFeatures(ss,framerate,isSignal,timestretchFactor=0.80) )

        self.YXtot = np.array(self.YXtot)

        self.keywordDurations = np.array(self.keywordDurations)

        outputname = "%simagedata_%i_%i.npy" % (savedir,self.Nfreq,self.Ntime)
        outputname_meta = "%smetadata_%i_%i.npy" % (savedir,self.Nfreq,self.Ntime)
        np.save(outputname, self.YXtot)
        np.save(outputname_meta, self.keywordDurations)
        if self.verbosity > 1: print "made %s and %s" % (outputname, outputname_meta)

        self.trainAndTest()
        # return score

    def nudge(self, Xtot, Ytot, w=3):
        newXtot = []
        newYtot = np.array([Ytot for _ in range(3)]).ravel(1)
        for x in Xtot:
            xmat = x.reshape(self.Nfreq,self.Ntime)
            left = xmat[:,range(w,self.Ntime)]
            left = np.pad(left, [(0,0), (w,0)], mode='constant', constant_values=0.0)
            right = xmat[:,range(0,self.Ntime-w)]
            right = np.pad(right, [(0,0), (0,w)], mode='constant', constant_values=0.0)
            newXtot.append(xmat.flatten())
            newXtot.append(left.flatten())
            newXtot.append(right.flatten())
        return np.array(newXtot), newYtot

    def getSampleDuration(self, data, framerate):
        return 1.0*len(data)/framerate # seconds

    def loadTrainData(self, datafile):
        metafile = datafile.replace("image","meta")
        self.Nfreq, self.Ntime = map(int,datafile.split(".")[0].split("_")[-2:])
        self.YXtot = np.load(datafile)
        self.keywordDurations = np.load(metafile)

        self.trainAndTest()

    def trainAndTest(self):
        self.clf = None

        Xtot = self.YXtot[:,range(1,len(self.YXtot[0]))]
        Ytot = self.YXtot[:,0]


        if self.verbosity > 1:
            print "Number of signal samples: %i" % int(np.sum(Ytot > 0.5))
            print "Number of background samples: %i" % int(np.sum(Ytot < 0.5))

        X_train, X_test, Y_train, Y_test = cross_validation.train_test_split(Xtot, Ytot, test_size=0.30, random_state=43)

        if self.DO_NUDGE:
            X_train, Y_train = self.nudge(X_train,Y_train, w=3)

        if self.alg == "logistic":
            self.clf = linear_model.LogisticRegression(C=5.0)
        elif self.alg == "svm":
            from sklearn import svm
            self.clf = svm.SVC(probability=True)
        elif self.alg == "perceptron":
            self.clf = linear_model.Perceptron()

        self.clf.fit(X_train, Y_train)

        # from sklearn import cross_validation
        # scores = cross_validation.cross_val_score(self.clf, X_test, Y_test, cv=15)
        # print scores
        # print "score:",scores.mean(), scores.std()

        if self.verbosity > 1:
            print "Results:\n%s\n" % (metrics.classification_report(Y_test,self.clf.predict(X_test)))
            print "Score on training set: %.2f" % self.clf.score(X_train, Y_train)
            print "Score on testing set: %.2f" % self.clf.score(X_test, Y_test)
        
        # return scores.mean(), scores.std()

    def predict(self, features):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore",category=Warning)
            return self.clf.predict_proba(features[1:])[0][1]

    def getKeywordProbability(self, data, framerate):
        features = self.getFeatures(data, framerate)
        return self.predict(features)

if __name__ == '__main__':
    tr = Trigger()
    proc = Processor()
    tr.readWav("sounds/oknavsa4.wav")

    subsamples = tr.getSubsamples()
    framerate = tr.getFramerate()
    for ss in subsamples[:1]:
        img = proc.getFeatures(ss, framerate, 1)
        # print img
        # print img.shape
