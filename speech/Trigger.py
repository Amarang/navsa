from matplotlib.mlab import find
import pyaudio, wave, audioop
import sys, time, threading
import matplotlib.pyplot as plt
import numpy as np
 
# from Process import Processor

class Trigger:
    def __init__(self,training=False):
        self.RECORD_SECONDS = 10
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 11025
        self.CHUNK = 512
        self.DTYPE='Int16'

        self.DECAYRATE = 10.0 # when computing EMA, how fast to decay weights (lower means RMS persists longer)
        self.TWINDOW = 0.2 # when computing EMA, what window size to use in seconds
        self.THRESHOLD = 600 # RMS threshold to trigger recording
        self.FALLING_THRESHOLD_RATIO = 0.9 # exit recording when RMS<THRESHOLD*FALLING_THRESHOLD_RATIO
        self.MIN_WORD_TIME = 0.27 # recordings shorter than this (in seconds) are clicks or snaps
        self.MAX_WORD_TIME = 1.2 # recordings longer than this (in seconds) are probably background noise
        
        self.mic = False

        self.fname = None
        self.framerate = None
        self.sampwidth = None
        self.nframes = None
        self.data = None
        self.verbose = False
        self.training = False

        self.latestRMS = np.array([])
        self.means = []
        self.frames = []
        self.recs = []
        self.recframes = []
        self.subsamples = []
        self.recording = False
        self.trecording = 0.0

        self.windowsize = None
        self.weight = None

        self.makeWeights()

        self.training = training
        if not self.training:
            pass

    def makeWeights(self):
        self.windowsize = int(1.0*self.RATE/self.CHUNK*self.TWINDOW)
        self.weight = np.arange(0,self.windowsize,1.0)
        self.weight = np.exp(self.DECAYRATE*self.weight/len(self.weight))
        self.weight /= np.sum(self.weight)

    def reset(self):
        self.mic = False
        self.stream = None
        self.framerate = None
        self.sampwidth = None
        self.nframes = None
        self.data = None

        self.latestRMS = np.array([])
        self.means = []
        self.frames = []
        self.recs = []
        self.recframes = []
        self.subsamples = []
        self.recording = False
        self.trecording = 0.0

        self.makeWeights()

    def readWav(self, fname,verbose=False):
        self.reset()

        self.mic = False
        self.fname = fname
        self.stream = wave.open(open(fname,"rb"))
        self.framerate = self.stream.getframerate()
        self.sampwidth = self.stream.getsampwidth()
        self.nframes = self.stream.getnframes()
        self.verbose = verbose

        self.listenLoop()

    def readMic(self,verbose=False, duration=10, callback=None):
        self.reset()

        self.mic = True
        self.RECORD_SECONDS = duration
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.FORMAT,channels=self.CHANNELS,rate=self.RATE,input=True,frames_per_buffer=self.CHUNK)
        self.sampwidth = pyaudio.get_sample_size(self.FORMAT)
        self.nframes = self.RECORD_SECONDS * self.RATE
        self.framerate = self.RATE
        self.verbose = verbose

        self.listenLoop(callback=callback)

    def listenLoop(self, callback=None):
        nLoops = int(self.nframes / self.CHUNK)
        for iloop in range(nLoops):

            if self.mic: data = self.stream.read(self.CHUNK)
            else: data = self.stream.readframes(self.CHUNK)

            t = 1.0*iloop*self.CHUNK/self.RATE
            self.frames.append(data)
            r1 = self.getRMS(data)

            self.latestRMS = np.append(self.latestRMS, r1)[-self.windowsize:]
            meanRMS = np.dot( self.latestRMS , self.weight[-len(self.latestRMS):] )
            self.means.append(meanRMS)

            line = self.drawBar( r1, 0,5000, 50, extra="%.2f %s" % (meanRMS, str(self.recording)) )
            if self.verbose:
                sys.stdout.write("\r" + line)
                sys.stdout.flush()

            if self.recording:
                self.trecording += 1.0*self.CHUNK/self.RATE
                self.recframes.append(data)

                if meanRMS < self.THRESHOLD * self.FALLING_THRESHOLD_RATIO or self.trecording > self.MAX_WORD_TIME:

                    if self.trecording > self.MIN_WORD_TIME:
                        subsample = self.framesToNumpy(self.recframes[:])
                        self.subsamples.append(subsample)

                        if callback is not None:
                            callback(subsample,framerate=self.framerate)

                    self.recs.append(t)
                    self.recording = False
                    self.recframes = []
                    self.trecording = 0.0

            else:
                if meanRMS > self.THRESHOLD:
                    self.recording = True
                    self.recs.append(t)
                    self.recframes.append(data)

        self.endLoop()


    def endLoop(self):
        if self.recording:
            self.recording = False
            self.recs.append(1.0 * self.nframes / self.RATE)

        if self.mic:
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()
        else:
            self.stream.close()

    def drawBar(self,val, lower,upper, size=50, extra=""):
        val = 1.0*val
        theval = val
        val = min(val, upper)
        val = max(val, lower)
        frac = 1.0*(val-lower)/(upper-lower)
        fill = int(frac*size)
        strBuff = "%-5i [" % lower
        strBuff += "=" * fill
        strBuff += " " * (size-fill)
        strBuff += "] %5i [%7.1f]" % (upper, theval)
        if len(extra) > 0: strBuff += " ... %s" % extra
        return strBuff

    def framesToNumpy(self, frames):
        frames = ''.join(frames)
        return np.fromstring(frames, self.DTYPE);

    def getRMS(self,signal):
        return audioop.rms(signal,self.sampwidth)

    def getFreq(self,signal):
        return audioop.cross(signal,self.sampwidth)*0.5*self.RATE/self.CHUNK

    def getSubsamples(self):
        return self.subsamples

    def getMainSubsample(self):
        if len(self.subsamples) > 0: return sorted(self.subsamples, key=lambda x: len(x), reverse = True)[0]
        else: return None

    def getFramerate(self):
        return self.framerate


if __name__ == '__main__':
    t = Trigger()
    t.readWav("sounds/oknavsa4.wav", verbose=True)
    print len(t.getSubsamples())

