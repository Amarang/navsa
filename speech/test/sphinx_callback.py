import sys, os, time
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *



# Create a decoder with certain model
config = Decoder.default_config()

config.set_string('-hmm', '/usr/local/share/pocketsphinx/model/en-us/en-us')
# config.set_string('-hmm', 'cmusphinx-en-us-5.2')

config.set_string('-dict', '7705.dic')
config.set_string('-lm', '7705.lm')
config.set_string('-logfn', 'dump.log')
# config.set_string('-debug', '1')


config.set_boolean('-bestpath', False) # supposedly speeds it up (default is True)
config.set_float('-vad_threshold', 3.0) # default is 2
config.set_float('-wip', 1e-4) #  0.005           Silence word transition probability
config.set_float('-silprob', 0.1) # 0.65            Word insertion penalty


chunk = 1024
rate = 16000

# Open file to read the data
# stream = open("../sounds/train/random8.wav", "rb")
# stream = open("../sounds/train/background_psr1.wav", "rb")
# stream = open("../sounds/train/oknavsa4.wav", "rb")
# stream = open("../sounds/train/random4.wav", "rb")
# stream = open("../sounds/train/oknavsa_bg1.wav", "rb")
# stream = open("../sounds/train/background_typing1.wav", "rb")
# FIXME 16kHz

# Alternatively you can read from microphone
import pyaudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True, frames_per_buffer=chunk)
stream.start_stream()

decoder = Decoder(config)
decoder.start_utt()

def callback(buf,frame_count, time_info, status):
    if buf:
        t0 = time.clock()
        decoder.process_raw(buf, False, False)
        print "process_raw took %.2f ms" % (1000.0*(time.clock()-t0))

        # t0 = time.clock()
        # print decoder.get_in_speech()
        # print "get in speech took %.2f ms" % (1000.0*(time.clock()-t0))

        if decoder.hyp() != None:
            print [(seg.word, seg.prob, seg.start_frame, seg.end_frame) for seg in decoder.seg()]
            print decoder.hyp().hypstr
            decoder.end_utt()
            decoder.start_utt()

    return (buf, pyaudio.paContinue)


stream = p.open(format = pyaudio.paInt16, channels=1, rate=rate, input=True, frames_per_buffer=chunk, stream_callback = callback)

print "starting"
stream.start_stream()
while True:
    try:
        pass
        # print "here"
        # time.sleep(1)
    except KeyboardInterrupt:
        stream.stop_stream()
        stream.close()
        p.terminate()
        print "* Killed Process"
        quit()
