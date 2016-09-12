import sys, os, time
import numpy as np
# from pocketsphinx.pocketsphinx import *
# from sphinxbase.sphinxbase import *
from collections import deque
import pyaudio
import audioop
import math
import wave
import io

import matplotlib.pyplot as plt

from scipy import signal

RPI = True
try:
    from RGB import Lights
except:
    RPI = False
    pass

import Utils as u

class Listener:
    def __init__(self):

        self.CHUNK = 1024
        self.RATE = 16000
        self.FORMAT = pyaudio.paInt16
        self.DTYPE='Int16'
        self.CHANNELS = 1

        self.RUN_SECONDS = 1000

        self.sampwidth = pyaudio.get_sample_size(self.FORMAT)

        self.mic = False
        self.wf = None

        self.deque_time = deque(maxlen=20)
        self.deque_mean = deque(maxlen=3)
        self.deque_freq = deque(maxlen=3)

        self.posneg_frequencies = np.fft.fftfreq(self.CHUNK, 1.0/self.RATE) 
        self.freqs_indices = np.where(self.posneg_frequencies >= 0)
        self.freqs = self.posneg_frequencies[np.where(self.posneg_frequencies >= 0)]

        self.t0 = time.time()
        self.ichunk = 0

        # plt.ion()
        # plt.axis([0,100,0,800])
        # fig=plt.figure()

        if RPI:
            self.led = Lights()
            self.led.start()



    def framesToNumpy(self, frames):
        frames = ''.join(frames)
        return np.fromstring(frames, self.DTYPE);
        
    def handle_audio(self, buf=None, frame_count=None, time_info=None, status=None, realtime=True):
        if not self.mic and realtime: buf = self.wf.readframes(frame_count)

        if not buf: return

        self.ichunk += 1


        meanRMS = 1.0*sum(self.deque_mean)/max(len(self.deque_mean),1)
        meanFreq = 1.0*sum(self.deque_freq)/max(len(self.deque_freq),1)


        mean_rms = audioop.rms(buf,self.sampwidth) 
        mean_freq = 0.5*audioop.cross(buf,self.sampwidth) * self.RATE / self.CHUNK

        fourier = np.fft.fft(self.framesToNumpy(buf))
        magnitudes = np.abs(fourier[self.freqs_indices])


        low_indices = ((50.0 < self.freqs) & (self.freqs < 500.0)).astype(bool)
        mid_indices = ((500.0 < self.freqs) & (self.freqs < 2000.0)).astype(bool)
        high_indices = (2000.0 < self.freqs).astype(bool)

        low_freqs = self.freqs[low_indices]
        low_mags = magnitudes[low_indices]
        low_weighted = np.dot(low_freqs, low_mags)/np.sum(low_mags)
        low_mag_sum = np.sum(low_mags)

        mid_freqs = self.freqs[mid_indices]
        mid_mags = magnitudes[mid_indices]
        mid_weighted = np.dot(mid_freqs, mid_mags)/np.sum(mid_mags)
        mid_mag_sum = np.sum(mid_mags)

        high_freqs = self.freqs[high_indices]
        high_mags = magnitudes[high_indices]
        high_weighted = np.dot(high_freqs, high_mags)/np.sum(high_mags)
        high_mag_sum = np.sum(high_mags)

        mag_sum = low_mag_sum + mid_mag_sum + high_mag_sum

        # print "%4.0f %4.0f %4.0f %4.0f %4.0f %4.0f" % (low_weighted, mid_weighted, high_weighted, \
        #                                                np.sum(low_mags), np.sum(mid_mags), np.sum(high_mags))


        
        fact = max(0.1,min(1.0,meanRMS / 5000.0))
        rgb = [fact*100.0*low_mag_sum/mag_sum, fact*100.0*mid_mag_sum/mag_sum, fact*100.0*high_mag_sum/mag_sum]
        rgb = rgb[::-1]
        try:
            pass
            if RPI and realtime:
                self.led.switch_color_rgb(rgb[0], rgb[1], rgb[2])
        except: pass

        # print peak_frequencies

        # now want to find frequencies ordered by magnitudes

        # try:
            # plt.cla()
        # except: pass

        # try:
        #     # plt.plot(self.freqs, magnitudes)
        #     print time.time()-self.t0, meanFreq
        #     plt.scatter(time.time()-self.t0, meanFreq)
        #     plt.show()
        # except: 
        #     pass





        self.deque_mean.append(mean_rms)
        self.deque_freq.append(mean_freq)
        self.deque_time.append(time.time())




        if realtime:
            hue = max(0.11, min(0.9,1.0*(meanFreq-500)/1500))
            lum = max(0.05, min(1.0,1.0*(meanRMS-1500)/8000))
            # self.led.switch_color(hue, lum)

            meas_chunk_time = max((self.deque_time[-1] - self.deque_time[0]) / max(len(self.deque_time)-1,1), 0.001)
            pred_chunk_time = 1.0*self.CHUNK/self.RATE
            perfpct = 100.0*pred_chunk_time/meas_chunk_time # < 100%, we're computing slowly, >100% we're time-traveling (good?). ~100% we're good
            t = int(1.0 * self.ichunk * self.CHUNK / self.RATE)
            line = self.draw_bar( meanRMS, 0,500, 30, extra="[%3.0f%% speed] [%4is] [%5.1f Hz] [%1.2f %1.2f]" % (perfpct, t, meanFreq, hue,lum) )
            sys.stdout.write("\r"+ " "*100) # clear the whole line
            sys.stdout.write("\r" + line + " ")
            sys.stdout.flush()

        return (buf, pyaudio.paContinue)

    def draw_bar(self,val, lower,upper, size=50, extra=""):
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

        stream = p.open(format = self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK, stream_callback = self.handle_audio)
        print "starting"
        stream.start_stream()
        try:
            for i in xrange(10*self.RUN_SECONDS):
                time.sleep(0.1)
                # try:
                #     plt.pause(0.001)
                # except: pass


        except KeyboardInterrupt:
            print "Terminated"

        stream.stop_stream()
        stream.close()
        p.terminate()
        
    def listen_file_realtime(self, fname):
        self.mic = False

        self.wf = wave.open(fname, "rb")
        p = pyaudio.PyAudio()

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

        stream = open(fname, "rb")

        t0 = time.time()
        rms_list = []
        ichunk = 0
        while True:
            buf = stream.read(self.CHUNK)
            if not buf: break
            if len(buf) != self.CHUNK: break

            self.handle_audio(buf, realtime=False)
            ichunk += 1


        print "processed %i chunks in %.2f seconds (%i%% of realtime)" % (ichunk, time.time()-t0, 100.0*ichunk/(time.time()-t0) / (self.RATE / self.CHUNK))



if __name__ == '__main__':


    # lst = Listener(hmm_type=0)
    lst = Listener()
    # lst = Listener(do_keyphrase=True)
    # lst = Listener(hmm_type=0, do_keyphrase=True)

    # results_sig = lst.listen_file('sounds/test/office_bg_mac_16000_360.wav', shutup=True); print results_sig
    # lst.reset()
    # results_sig = lst.listen_file('sounds/test/home_navsa_pi_16000_120.wav', shutup=True); print results_sig
    # lst.reset()
    # lst.reset()
    # results_sig = lst.listen_file('sounds/test/home_navsa_pi_16000_240.wav', shutup=True); print results_sig

    # lst.listen_file_realtime('sounds/test/home_navsa_pi_16000_240.wav')

    # lst.listen_mic()
    # lst.listen_file_realtime('sounds/test/office_bg_mac_16000_360.wav')
    # lst.listen_file_realtime('sounds/test/psr_bg_laptop_16000_600.wav')
    # lst.listen_file_realtime('kano.wav')
    lst.listen_file('kano.wav')
    # lst.listen_file_realtime('izecold.wav')
