import numpy as np
import sys, time
import signal

import Utils as u
from Process import Processor
from Trigger import Trigger
from Parse import Parser

proc = Processor(DO_NUDGE=True,DO_STRETCH=True,Nfreq=12,Ntime=12, alg="logistic")
parser = Parser()
tr = Trigger()

# proc.processTrainingSet(basedir="sounds/train/", signalword="oknavsa", savedir="data/")
# proc.processTrainingSet(basedir="16khz/", signalword="oknavsa", savedir="data/")
proc.loadTrainData("data/imagedata_12_12.npy")

#if not in this range, we want to not fingerprint it to save time and trouble
lower,upper = proc.getKeywordDurationRange()
tr.setParams({"MIN_WORD_TIME": lower, "MAX_WORD_TIME": upper})

# tr.setParams({"THRESHOLD": 1000})
tr.getAmbientLevels(duration=0.5)

print "Now will score realtime audio"

def myCallback(trigger, data, data_raw):
    print
    framerate = trigger.getFramerate()
    if not trigger.hasSaidKeyword():
        confidence = proc.getKeywordProbability(data, framerate)
        if confidence > 0.60:
            u.play("../sounds/notification.wav")
            # u.toast("What's up?")
            trigger.saidKeyword()
        print "duration: %.2f s, score: %.2f" % (1.0*len(data)/framerate, confidence)
    else:
        print "duration: %.2f s" % (1.0*len(data)/framerate)

        # out = u.get_voice_api(data_raw)
        # parser.handle_api_ai(out)


stopper = tr.readMic(verbose=True, callback=myCallback)

tot_time = 100.0
# tot_time = 1.0

for i in range(int(tot_time*10)):
    time.sleep(1.0/10.0)

stopper()
