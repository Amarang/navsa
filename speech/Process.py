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
from sklearn import ensemble
from sklearn import svm
from sklearn import naive_bayes

class Processor:
    def __init__(self, Ntime=15, Nfreq=15, TRAIN_FRAC=0.90, NUDGE_FRAC=0.0,alg="logistic",verbosity=2):
        self.Ntime,self.Nfreq = Ntime,Nfreq
        self.YXtot = []
        self.keywordDurations = []
        self.DURATION_SIGMA = 1.7
        self.TRAIN_FRAC = TRAIN_FRAC
        self.NUDGE_FRAC = NUDGE_FRAC
        self.alg = alg
        self.verbosity = verbosity
        self.clf = None

    def getFeatures(self, data, framerate, isSignal=0):
        fp = Fingerprinter()
        fp.setData(data, framerate)
        times,freqs,Pxx = fp.getSpectrogram()

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
        fnames = []
        durations = []
        self.keywordDurations = []

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore",category=Warning)

            for clip in clips:

                if clip in bestThresh: tr.setParams({"THRESHOLD": bestThresh[clip]})
                else: tr.setParams({"THRESHOLD": 600})

                if clip.lower().startswith(signalword): isSignal = True
                elif clip.lower().startswith("random"): isSignal = False
                elif clip.lower().startswith("background"): isSignal = False
                else: continue

                tr.readWav(basedir+clip)
                subsamples = tr.getSubsamples()
                framerate = tr.getFramerate()

                if self.verbosity > 1: print "Loading clip %s (isSignal: %i) ==> %i subsamples" % (clip, isSignal, len(subsamples))

                for ss in subsamples:
                    duration = self.getSampleDuration(ss, framerate) 
                    if isSignal: self.keywordDurations.append(duration)

                    self.YXtot.append( self.getFeatures(ss,framerate,isSignal) )
                    fnames.append(clip)
                    durations.append(duration)

        self.YXtot = np.array(self.YXtot)

        self.keywordDurations = np.array(self.keywordDurations)

        outputname = "%simagedata_%i_%i.npy" % (savedir,self.Nfreq,self.Ntime)
        outputname_meta = "%smetadata_%i_%i.npy" % (savedir,self.Nfreq,self.Ntime)
        np.save(outputname, self.YXtot)
        np.save(outputname_meta, self.keywordDurations)
        if self.verbosity > 1: print "made %s and %s" % (outputname, outputname_meta)

        idx_test, YXtest = self.trainAndTest()

        return np.array(fnames)[idx_test], np.array(durations)[idx_test], YXtest
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

        Xtot = self.YXtot[:,1:]
        Ytot = self.YXtot[:,0]
        idx = np.arange(Xtot.shape[0])

        if self.verbosity > 1:
            print "Number of signal samples: %i" % int(np.sum(Ytot > 0.5))
            print "Number of background samples: %i" % int(np.sum(Ytot < 0.5))

        X_train, X_test, Y_train, Y_test, idx_train, idx_test = cross_validation.train_test_split(Xtot, Ytot, idx, test_size=1.0-self.TRAIN_FRAC, random_state=42)

        if self.NUDGE_FRAC > 0.01:
            X_train, Y_train = self.nudge(X_train,Y_train, w=int(self.NUDGE_FRAC*self.Ntime + 1))

        if self.alg == "logistic": self.clf = linear_model.LogisticRegression(C=4.0)
        elif self.alg == "svm": self.clf = svm.SVC(probability=True)
        elif self.alg == "adaboost": self.clf = ensemble.AdaBoostClassifier()
        elif self.alg == "randforest": self.clf = ensemble.RandomForestClassifier()
        elif self.alg == "bagging": self.clf = ensemble.BaggingClassifier()
        elif self.alg == "gaussiannb": self.clf = naive_bayes.GaussianNB()
        elif self.alg == "perceptron": self.clf = linear_model.Perceptron()
        elif self.alg == "voting":
            self.clf = ensemble.VotingClassifier(
                    estimators=[
                            ('lr',linear_model.LogisticRegression(C=4.0)),
                            ('ada',ensemble.AdaBoostClassifier()),
                            ('rf',ensemble.RandomForestClassifier()),
                            ('bag',ensemble.BaggingClassifier()),
                            ('gnb',naive_bayes.GaussianNB()),
                            ('svm',svm.SVC(probability=True))
                        ],
                    voting='soft'
                    )

        self.clf.fit(X_train, Y_train)

        # scores = cross_validation.cross_val_score(self.clf, X_test, Y_test, cv=15)
        # print scores
        # print "score:",scores.mean(), scores.std()

        if self.verbosity > 1:
            print "Results:\n%s\n" % (metrics.classification_report(Y_test,self.clf.predict(X_test)))
            print "Score on training set: %.2f" % self.clf.score(X_train, Y_train)
            print "Score on testing set: %.2f" % self.clf.score(X_test, Y_test)
        
        # return scores.mean(), scores.std()
        return idx_test, np.c_[Y_test, X_test]

    def predict(self, features):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore",category=Warning)
            return self.clf.predict_proba(features[1:])[0][1]
            # print self.clf.decision_function(features[1:])
            # return self.clf.decision_function(features[1:])

    def getKeywordProbability(self, data, framerate):
        features = self.getFeatures(data, framerate)
        return self.predict(features)

if __name__ == '__main__':
    tr = Trigger()

    proc = Processor(Nfreq=15, Ntime=15, TRAIN_FRAC=0.50, NUDGE_FRAC=0.0, alg="logistic", verbosity=2)
    # proc = Processor(Nfreq=25, Ntime=25, TRAIN_FRAC=0.70, DO_NUDGE=True, alg="voting", verbosity=2)
    # proc = Processor(DO_NUDGE=True, alg="voting", verbosity=2)
    fnames, durations, YXtot = proc.processTrainingSet(basedir="sounds/train/", signalword="oknavsa", savedir="data/")
    fnames_new = []
    for fname in fnames:
        if fname.startswith("background_psr"): fname_new = "PSR"
        if fname.startswith("background_typing"): fname_new = "BG typing"
        elif fname.startswith("background"): fname_new = "BG"
        elif fname.startswith("oknavsa_bg"): fname_new = "Navsa with BG"
        elif fname.startswith("oknavsa_bmic"): fname_new = "Navsa with bad mic"
        elif fname.startswith("oknavsa"): fname_new = "Navsa"
        elif fname.startswith("random"): fname_new = "BG words"
        else: fname_new = "unknown"
        fnames_new.append(fname_new)
    fnames = np.array(fnames_new)
    scores = np.apply_along_axis(proc.predict, 1, YXtot)

    fig, axs = plt.subplots(nrows=1, ncols=2) 
    fig.set_size_inches(18.0,9.0)

    names = ['BG','BG typing','BG words','PSR','Navsa with BG','Navsa with bad mic','Navsa']
    colors = ["red", "orangered", "firebrick", "lightcoral", "teal", "skyblue", "dodgerblue"]

    scores_names = []
    durations_names = []
    for name in names:
        scores_names.append( scores[fnames==name] )
        durations_names.append( durations[fnames==name] )

    axs[0].hist(scores_names, 20,    range=(-0.05, 1.05), stacked=True, color=colors, histtype='stepfilled', label=names)
    axs[1].hist(durations_names, 20,  range=(0.23, 1.25), stacked=True, color=colors, histtype='stepfilled', label=names)

    axs[0].set_title("Signal probability")
    axs[0].legend(prop={'size': 10})

    axs[1].set_title("Phrase duration")
    axs[1].legend(prop={'size': 10})

    fig.savefig("alg.png", bbox_inches='tight')
    u.web("alg.png")
