import sys, os, time
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *
from collections import deque
import pyaudio
import audioop
import math
import wave

import Utils as u

class Listener:
    def __init__(self, hmm_type=1, vad_threshold=3.5, pl_window=10, wip=1e-4, silprob=0.3, bestpath=True):
        self.CHUNK = 1024
        self.RATE = 16000
        self.FORMAT = pyaudio.paInt16

        self.RUN_SECONDS = 1000

        self.sampwidth = pyaudio.get_sample_size(self.FORMAT)

        # Create a decoder with certain model
        self.config = Decoder.default_config()

        if hmm_type == 0:
            self.config.set_string('-hmm', '/usr/local/share/pocketsphinx/model/en-us/en-us')
        elif hmm_type == 1:
            self.config.set_string('-hmm', 'test/cmusphinx-en-us-5.2')

        self.config.set_string('-dict', 'test/7705.dic')
        self.config.set_string('-lm', 'test/7705.lm')

        self.config.set_string('-logfn', '/dev/null')
        self.config.set_string('-debug', '1')

        # http://cmusphinx.sourceforge.net/wiki/pocketsphinxhandhelds
        self.config.set_boolean('-bestpath', bestpath) # default is true
        self.config.set_float('-vad_threshold', vad_threshold) # default is 2
        self.config.set_float("-pl_window", pl_window) # default is 5, range is 0 to 10
        self.config.set_float('-wip', wip) #  0.005           Silence word transition probability
        self.config.set_float('-silprob', silprob) # 0.65            Word insertion penalty

        self.t0_d = time.time()
        self.decoder = Decoder(self.config)
        self.t1_d = time.time()

        self.deque_time = deque(maxlen=50)
        self.deque_mean = deque(maxlen=5)

        self.mic = False
        self.wf = None

    def reset(self):
        self.decoder = Decoder(self.config)

    def is_keyword(self, hyp, seg=None):
        if "navsa" in hyp.lower(): return True

        return False
        
    def handle_audio(self, buf, frame_count, time_info, status):
        if not self.mic: buf = self.wf.readframes(frame_count)

        if not buf: return

        self.decoder.process_raw(buf, False, False)

        mean_rms = audioop.rms(buf,self.sampwidth) 
        self.deque_mean.append(mean_rms)
        self.deque_time.append(time.time())

        if self.decoder.hyp() != None:
            hypstr = str(self.decoder.hyp().hypstr)
            print hypstr
            self.decoder.end_utt()
            self.decoder.start_utt()
            
            if self.mic:
                if self.is_keyword(hypstr):
                    u.beep()

        meas_chunk_time = max((self.deque_time[-1] - self.deque_time[0]) / max(len(self.deque_time)-1,1), 0.001)
        pred_chunk_time = 1.0*self.CHUNK/self.RATE
        perfpct = 100.0*pred_chunk_time/meas_chunk_time # < 100%, we're computing slowly, >100% we're time-traveling (good?). ~100% we're good
        meanRMS = 1.0*sum(self.deque_mean)/max(len(self.deque_mean),1)
        line = self.drawBar( meanRMS, 0,1250, 30, extra="[%3.0f%% speed] [%i]" % (perfpct, self.decoder.get_in_speech()) )
        sys.stdout.write("\r" + line + " ")
        sys.stdout.flush()

        return (buf, pyaudio.paContinue)

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

    def listen_mic(self):
        self.mic = True

        p = pyaudio.PyAudio()

        self.decoder.start_utt()
        stream = p.open(format = self.FORMAT, channels=1, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK, stream_callback = self.handle_audio)
        print "starting"
        stream.start_stream()
        try:
            for i in xrange(10*self.RUN_SECONDS):
                time.sleep(0.1)


        except KeyboardInterrupt:
            print "Terminated"

        stream.stop_stream()
        stream.close()
        p.terminate()
        
    def listen_file_realtime(self, fname):
        self.mic = False

        self.wf = wave.open(fname, "rb")
        p = pyaudio.PyAudio()

        self.decoder.start_utt()
        print self.wf.getframerate()
        stream = p.open(format=p.get_format_from_width(self.wf.getsampwidth()), channels=self.wf.getnchannels(), frames_per_buffer=self.CHUNK,rate=self.wf.getframerate(), input=True, stream_callback=self.handle_audio)
        print "starting"
        stream.start_stream()

        try:
            while stream.is_active():
                time.sleep(1.0)
        except KeyboardInterrupt:
            print "Terminated"


        stream.stop_stream()
        stream.close()
        self.wf.close()
        p.terminate()


    def listen_file(self, fname, shutup=False):
        self.mic = False

        # stream = open("psr_bg_laptop_16000_240.wav", "rb")
        stream = open(fname, "rb")
        self.decoder.start_utt()

        t0 = time.time()
        nwords = 0
        nkeywords = 0
        while True:
            buf = stream.read(self.CHUNK)
            if buf: self.decoder.process_raw(buf, False, False)
            else: break
            hypothesis = self.decoder.hyp()
            if hypothesis != None:
                # print [(seg.word, seg.prob, seg.start_frame, seg.end_frame) for seg in self.decoder.seg()]
                # print dir(list(self.decoder.seg())[0])
                # print [(seg.word, math.exp(seg.prob), seg.lscore, seg.ascore, round(1.0*(seg.end_frame-seg.start_frame),2)) for seg in self.decoder.seg()]
                hypstr = str(self.decoder.hyp().hypstr)
                if not shutup:
                    print hypstr

                nwords += 1
                if self.is_keyword(hypstr):
                    nkeywords += 1

                self.decoder.end_utt()
                self.decoder.start_utt()

        self.decoder.end_utt()

        t1 = time.time()


        # time to make decoder
        tdec = self.t1_d - self.t0_d
        
        # time to run through audio file
        trun = t1 - t0

        return {'fname': fname, 'tdec': tdec, 'trun': trun, 'nwords': nwords, 'nkeywords': nkeywords}


if __name__ == '__main__':

    # lst = Listener(hmm_type=0)
    lst = Listener()

    # results_sig = lst.listen_file('office_bg_mac_16000_360.wav', shutup=True); print results_sig
    # lst.reset()
    # results_sig = lst.listen_file('home_navsa_pi_16000_120.wav', shutup=True); print results_sig
    # lst.reset()
    # results_sig = lst.listen_file('psr_bg_laptop_16000_240.wav', shutup=True); print results_sig

    lst.listen_file_realtime('home_navsa_pi_16000_120.wav')

    # lst.listen_mic()

    # import itertools, random
    # p = list(itertools.product(
    #    *([2.0, 2.3, 2.6, 2.9, 3.2, 3.5, 3.8, 4.1, 4.4],
    #      [0, 2, 5, 7, 10],
    #      [0.1, 0.01, 0.001, 1e-4],
    #      [0.1, 0.3, 0.5, 0.7, 0.9]) ))
    # for i in range(300):
    #     vad_threshold, pl_window, wip, silprob = random.choice(p)
    #     for hmm_type in [0,1]:
    #         for bestpath in [True, False]:

    #             params = { "hmm_type":hmm_type, "vad_threshold":vad_threshold, "pl_window":pl_window, "wip":wip, "silprob":silprob, "bestpath":bestpath }
    #             print "using params:", params
    #             lst = Listener(**params)

    #             results_sig = lst.listen_file('home_navsa_pi_16000_120.wav')
    #             results_bg = lst.listen_file('psr_bg_laptop_16000_240.wav')
    #             print "results:", results_bg, results_sig

    #             obj_to_save = params
    #             for key in results_bg: obj_to_save[key+"_bg"] = results_bg[key]
    #             for key in results_sig: obj_to_save[key+"_sig"] = results_sig[key]

    #             print "obj:",obj_to_save
    #             sys.stdout.flush()

