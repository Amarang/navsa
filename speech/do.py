import numpy as np
import sys, time
import signal

import Utils as u
from Process import Processor
from Trigger import Trigger
from Parse import Parser
from Lights import Lights

site = "apiai"
proc = Processor()
parser = Parser(site=site)
tr = Trigger(verbose=True)
led = Lights()

# proc.processTrainingSet(basedir="sounds/train/", signalword="oknavsa", savedir="data/")
# proc.processTrainingSet(basedir="16khz/", signalword="oknavsa", savedir="data/")
proc.loadTrainData("data/imagedata_15_15.npy")

#if not in this range, we want to not fingerprint it to save time and trouble
lower,upper = proc.getKeywordDurationRange()
tr.setParams({"MIN_WORD_TIME": lower, "MAX_WORD_TIME": upper})

# tr.setParams({"THRESHOLD": 1000})
tr.getAmbientLevels(duration=1.5)

print "Now will score realtime audio"

def myCallback(trigger, data, data_raw):
    print
    framerate = trigger.getFramerate()
    if not trigger.hasSaidKeyword():
        t0 = time.time()
        confidence = proc.getKeywordProbability(data, framerate)
        print "took %.2fms to classify" % (1000.0*(time.time()-t0))

        # if confidence > 0.45:
        if confidence > 0.01:
            print "duration: %.2f s, score: %.2f" % (1.0*len(data)/framerate, confidence)
            led.flash(duration=0.3)
            u.play("../sounds/notification.wav", blocking=False)
            # u.toast("What's up?")
            trigger.saidKeyword()
    else:
        print "duration: %.2f s" % (1.0*len(data)/framerate)

        out = u.get_voice(data_raw, site)
        print out
        parser.handle(out)
        trigger.finishedQuery()
        # led.flip(onoff="off")


stopper = tr.readMic(callback=myCallback)

tot_time = 100.0
# tot_time = 1.0

for i in range(int(tot_time*10)):
    time.sleep(1.0/10.0)

stopper()
