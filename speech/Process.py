import wave, os, warnings
from tqdm import tqdm
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from Split import Splitter
from Trigger import Trigger
from Fingerprint import Fingerprinter
import Utils as u
import scipy.ndimage as ndimage
from sklearn import linear_model, metrics
from sklearn.cross_validation import train_test_split



class Processor:
    def __init__(self, Ntime=30, Nfreq=30):
        self.Ntime,self.Nfreq = 30,30
        self.YXtot = []
        self.keywordDurations = []
        self.DURATION_SIGMA = 3.0
        self.clf = None



    def getFeatures(self, data, framerate, isSignal=0):
        fp = Fingerprinter()
        fp.setData(data, framerate)
        times,freqs,Pxx = fp.getSpectrogram()

        ztime = float(self.Ntime) / Pxx.shape[1] if Pxx.shape[1] > self.Ntime else 1
        zfreq = float(self.Nfreq) / Pxx.shape[0] if Pxx.shape[0] > self.Nfreq else 1

        # print zfreq,ztime
        Pxx = ndimage.interpolation.zoom(Pxx,zoom=(zfreq, ztime),order=0)


        nfreq,ntime = Pxx.shape
        freqPad = self.Nfreq-nfreq # pad higher frequencies with 0
        timePad = self.Ntime-ntime # pad higher times with 0
        Pxx = np.pad(Pxx, [(freqPad,0), (0,timePad)], mode='constant', constant_values=0.0)

        img = Pxx.flatten() # restore freq,time matrix with Pxx.reshape(self.Nfreq,self.Ntime)
        img = np.insert( img, 0, [isSignal] ) # put 0 or 1 at beginning for truth value

        return img

    def getKeywordDurationRange(self):
        mu, sig = self.keywordDurations.mean(), self.keywordDurations.std()
        return [mu - sig*self.DURATION_SIGMA, mu + sig*self.DURATION_SIGMA]

    def processTrainingSet(self, basedir="sounds/train/", signalword="oknavsa", savedir="data/"):

        clips = os.listdir(basedir)

        # sp = Splitter()
        tr = Trigger(training=True)

        self.YXtot = []
        self.keywordDurations = []

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore",category=Warning)

            for clip in clips:

                if clip.lower().startswith(signalword):
                    isSignal = True
                elif clip.lower().startswith("random"):
                    isSignal = False
                else:
                    continue


                tr.readWav(basedir+clip)
                subsamples = tr.getSubsamples()
                framerate = tr.getFramerate()

                print "Loading clip %s (isSignal: %i) ==> %i subsamples" % (clip, isSignal, len(subsamples))


                for ss in subsamples:
                    if isSignal:
                        self.keywordDurations.append( self.getSampleDuration(ss, framerate) )
                    img = self.getFeatures(ss, framerate, isSignal)
                    self.YXtot.append(img)

        self.YXtot = np.array(self.YXtot)

        self.keywordDurations = np.array(self.keywordDurations)

        outputname = "%simagedata_%i_%i.npy" % (savedir,self.Nfreq,self.Ntime)
        np.save(outputname, self.YXtot)
        print "made %s" % outputname
        return outputname


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
        self.Nfreq, self.Ntime = map(int,datafile.split(".")[0].split("_")[-2:])
        self.YXtot = np.load(datafile)


    def trainAndTest(self):
        self.clf = None

        Xtot = self.YXtot[:,range(1,len(self.YXtot[0]))]
        Ytot = self.YXtot[:,0]


        # Xtot, Ytot = self.nudge(Xtot,Ytot, w=3)

        X_train, X_test, Y_train, Y_test = train_test_split(Xtot, Ytot, test_size=0.15, random_state=42)

        logistic_classifier = linear_model.LogisticRegression(C=2.0)
        logistic_classifier.fit(X_train, Y_train)

        self.clf = logistic_classifier

        # print "Logistic regression using raw pixel features:\n%s\n" % (metrics.classification_report(Y_test,logistic_classifier.predict(X_test)))

        # print "Score on training set: %.2f" % logistic_classifier.score(X_train, Y_train)
        # print "Score on testing set: %.2f" % logistic_classifier.score(X_test, Y_test)

    def predict(self, features):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore",category=Warning)
            return self.clf.predict_proba(features[1:])[0][1]

    def getKeywordProbability(self, data, framerate):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore",category=Warning)
            features = self.getFeatures(data, framerate)
            return self.clf.predict_proba(features[1:])[0][1]

