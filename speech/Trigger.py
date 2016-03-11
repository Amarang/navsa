from matplotlib.mlab import find
import pyaudio, wave, audioop, io
import sys, time, threading, copy
import matplotlib.pyplot as plt
import numpy as np

class Trigger:
    def __init__(self,DECAYRATE = 1.5, TWINDOW = 0.2, THRESHOLD = 600, FALLING_THRESHOLD_RATIO = 0.8, \
                 PAUSE_THRESHOLD = 0.03, MIN_WORD_TIME = 0.27, MAX_WORD_TIME = 1.2, AMBIENT_MULT = 2.5, KEYWORD_DELAY = 3.5,
                 verbose = False, led=None):

        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 11025
        self.CHUNK = 512 # 256 has better recognition performance?
        self.DTYPE='Int16'

        self.params = {}
        self.params["DECAYRATE"] = DECAYRATE # when computing EMA, how fast to decay weights (lower means RMS persists longer)
        self.params["TWINDOW"] = TWINDOW # when computing EMA, what window size to use in seconds
        self.params["THRESHOLD"] = THRESHOLD # RMS threshold to trigger recording
        self.params["FALLING_THRESHOLD_RATIO"] = FALLING_THRESHOLD_RATIO # putative silence when RMS<THRESHOLD*FALLING_THRESHOLD_RATIO
        self.params["PAUSE_THRESHOLD"] = PAUSE_THRESHOLD # seconds of non-speaking audio before a phrase is considered complete
        self.params["MIN_WORD_TIME"] = MIN_WORD_TIME # recordings shorter than this (in seconds) are clicks or snaps
        self.params["MAX_WORD_TIME"] = MAX_WORD_TIME # recordings longer than this (in seconds) are probably background noise
        self.params["AMBIENT_MULT"] = AMBIENT_MULT # when setting threshold automatically, thresh=AMBIENT_MULT*ambientmean
        self.params["KEYWORD_DELAY"] = KEYWORD_DELAY # how long (in seconds) to consider things said after keyword as commands, after which we must say keyword again

        self.defaultparams = copy.deepcopy(self.params)

        self.saidKeywordHowLongAgo = 30.0
        self.saidKeywordRecently = False

        
        self.stream = None
        self.mic = False
        self.running = False

        self.framerate = None
        self.sampwidth = None
        self.nframes = None
        self.data = None
        self.verbose = verbose
        self.led = led

        self.latestRMS = np.array([])
        self.means = np.array([])
        self.subsamples = []
        self.recording = False

        self.windowsize = None
        self.weight = None

        self.makeWeights()


    def setParams(self, p):
        for key,val in p.items():
            if self.verbose: print "Setting %s to %.2f" % (key, float(val))
            self.params[key] = val
            self.defaultparams[key] = val

    def makeWeights(self):
        self.windowsize = int(1.0*self.RATE/self.CHUNK*self.params["TWINDOW"])
        self.weight = np.arange(0,self.windowsize,1.0)
        self.weight = np.exp(self.params["DECAYRATE"]*self.weight/len(self.weight))
        self.weight /= np.sum(self.weight)

    def reset(self):
        self.mic = False
        self.stream = None
        self.framerate = None
        self.sampwidth = None
        self.nframes = None
        self.data = None

        self.latestRMS = np.array([])
        self.means = np.array([])
        self.subsamples = []
        self.recording = False

        self.makeWeights()

    def readWav(self, fname):
        self.reset()

        self.mic = False
        self.running = True
        self.stream = wave.open(open(fname,"rb"))
        self.framerate = self.stream.getframerate()
        self.sampwidth = self.stream.getsampwidth()
        self.nframes = self.stream.getnframes()

        self.listenLoop()

    def openMic(self, force=False):
        if(self.stream and not force):
            # mic already open
            return

        self.reset()
        self.mic = True
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.FORMAT,channels=self.CHANNELS,rate=self.RATE,input=True,frames_per_buffer=self.CHUNK)
        self.sampwidth = pyaudio.get_sample_size(self.FORMAT)
        self.framerate = self.RATE
        pass

    def readMic(self, callback=None):

        self.openMic()

        self.running = True

        listener_thread = threading.Thread(target=self.listenLoop, kwargs={"callback":callback})
        listener_thread.daemon = True
        listener_thread.start()
        
        def stopper():
            self.running = False
            listener_thread.join()

        return stopper

    def saidKeyword(self): # have said keyword, so now listen for query
        self.saidKeywordHowLongAgo = 0.0
        self.saidKeywordRecently = True
        self.updateParams()

    def hasSaidKeyword(self):
        return self.saidKeywordRecently

    def finishedQuery(self): # made query, so force this to listen for keyword again
        self.saidKeywordHowLongAgo = 30.0
        self.saidKeywordRecently = False

    def updateParams(self):
        if self.saidKeywordHowLongAgo < self.params["KEYWORD_DELAY"]:
            # update params to be looser so that we can capture regular queries now
            self.params["TWINDOW"] = 0.5
            self.params["DECAYRATE"] = 1.0
            self.params["PAUSE_THRESHOLD"] = 0.4
            self.params["FALLING_THRESHOLD_RATIO"] = 0.7
            self.params["MIN_WORD_TIME"] = 0.8
            self.params["MAX_WORD_TIME"] = 12.0
        elif self.saidKeywordRecently:
            self.saidKeywordRecently = False
            if self.led is not None: self.led.stop()
            # back to defaults (listening for WUW)
            self.params = self.defaultparams.copy()


    def getAmbientLevels(self, duration=0.5):
        self.openMic()

        levels = []
        print "Please stfu for %.1f seconds" % duration
        for i in range(int(self.framerate * duration / self.CHUNK)):
            try: data = self.stream.read(self.CHUNK)
            except IOError as ex:
                data = '\x00' * self.CHUNK
            if len(data) == 0: break
            r1 = self.getRMS(data)
            levels.append(r1)

        avg = np.mean(np.array(levels))
        sigma = np.std(np.array(levels))
        print "Ambient RMS is: %.1f" % (avg)
        print "Ambient RMS rms is: %.1f" % (sigma)
        self.params["THRESHOLD"] = avg*self.params["AMBIENT_MULT"]
        self.defaultparams["THRESHOLD"] = avg*self.params["AMBIENT_MULT"]
        # self.params["THRESHOLD"] = avg+sigma*self.params["AMBIENT_MULT"]
        # self.defaultparams["THRESHOLD"] = avg+sigma*self.params["AMBIENT_MULT"]
        print "Setting threshold to %.1f" % (self.params["THRESHOLD"])

    def listenLoop(self, callback=None):

        iloop = 0
        dt = 1.0*self.CHUNK/self.RATE
        timeBelowThresh = 0.0
        trecording = 0.0
        recframes = []
        while self.running:
            iloop += 1


            if self.mic:
                try: data = self.stream.read(self.CHUNK)
                except IOError as ex:
                    data = '\x00' * self.CHUNK
                    self.openMic(force=True) # reset the freaking mic because pyaudio sucks balls on raspberry pi
            else: data = self.stream.readframes(self.CHUNK)
            
            if len(data) == 0: break


            tm = dt*iloop
            self.saidKeywordHowLongAgo += dt

            # self.frames.append(data)
            r1 = self.getRMS(data)

            self.latestRMS = np.append(self.latestRMS, r1)[-self.windowsize:]
            meanRMS = np.dot( self.latestRMS , self.weight[-len(self.latestRMS):] )
            # self.means = np.append(self.means, r1)[-10*self.windowsize:]
            # self.params["THRESHOLD"] = self.params["AMBIENT_MULT"]*np.mean(self.means)

            if self.verbose:
                # rightSide = 5000
                rightSide = self.params["THRESHOLD"]*3
                line = self.drawBar( meanRMS, 0,rightSide, 50, extra="%9.2f %6s [%7.2f] %5s"
                        % (
                          self.params["THRESHOLD"], 
                          "[rec]" if self.recording else "", 
                          self.saidKeywordHowLongAgo,
                          "[trig]" if self.saidKeywordHowLongAgo < self.params["KEYWORD_DELAY"] else ""
                          ) 
                        )
                sys.stdout.write("\r" + line + " ")
                sys.stdout.flush()

            if self.saidKeywordRecently and self.saidKeywordHowLongAgo > self.params["KEYWORD_DELAY"] and not self.recording:
                self.updateParams()

            if self.recording:
                trecording += dt
                recframes.append(data)
                
                if meanRMS < self.params["THRESHOLD"] * self.params["FALLING_THRESHOLD_RATIO"]: timeBelowThresh += dt

                if timeBelowThresh > self.params["PAUSE_THRESHOLD"] or trecording > self.params["MAX_WORD_TIME"]:

                    if trecording > self.params["MIN_WORD_TIME"]:
                        subsample = self.framesToNumpy(recframes[:])
                        subsample_raw = self.betterRawData(b''.join(recframes))
                        self.subsamples.append(subsample)

                        if callback is not None: callback(self,subsample,subsample_raw)

                    # self.recs.append(tm)
                    self.recording = False
                    recframes = []
                    trecording = 0.0

            else:
                if meanRMS > self.params["THRESHOLD"]:
                    self.recording = True
                    timeBelowThresh = 0.0
                    # self.updateParams()
                    # self.recs.append(tm)
                    recframes.append(data)

        self.endLoop()


    def endLoop(self):
        if self.recording:
            self.recording = False
            # if not self.mic: # close up recording interval if end of wav
            #     self.recs.append(1.0 * self.nframes / self.RATE)

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

    def betterRawData(self,data_raw):
        # apparently we have to do this to get voice to work with wit
        with io.BytesIO() as wav_file:
            wav_writer = wave.open(wav_file, "wb")
            wav_writer.setframerate(self.RATE)
            wav_writer.setsampwidth(self.sampwidth)
            wav_writer.setnchannels(self.CHANNELS)
            wav_writer.writeframes(data_raw)
            wav_writer.close()
            wav_data = wav_file.getvalue()
        return wav_data

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

