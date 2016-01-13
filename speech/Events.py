import threading
import time, datetime
import os, sys
import atexit, shelve
import Utils as u

DELAY = 2 # seconds
THRESHOLD = 20 # seconds
TIMEFILE = "times.db"

class Events:
    def __init__(self, delay=2, threshold=20, timefile=TIMEFILE):
        self.DELAY=delay # how often to check
        self.THRESHOLD=threshold # how many seconds within a trigger time to act
        self.TIMEFILE=timefile # output/input file
        self.doLoop = False

        self.shelf = shelve.open(TIMEFILE, writeback=True)

        if(len(self.shelf.keys()) < 1): self.shelf["events"] = [] # empty db

        self.thread = threading.Thread(target=self.loop)
        self.thread.setDaemon(True)
        atexit.register(self.saveShelf)

    def saveShelf(self):
        self.shelf.close()
        print "[times] Saved shelf"

    def checkTimes(self):
        print "[times] checking events"
        leftoverEvents = []
        print self.shelf['events']
        for event in self.shelf['events']:
            if len(event) < 3: continue

            ta,tb,action = event
            tb = u.toTimestamp(tb)
            now = u.toTimestamp(datetime.datetime.now())
            print now-tb
            secsLeft = int(now-tb)
            if secsLeft > -self.THRESHOLD:
                self.handleTime(event)
                continue

            leftoverEvents.append(event)

        self.shelf['events'] = leftoverEvents[:]

    def handleTime(self,event):
        print "[times] handling time"
        ta, tb, action = event
        dt = (datetime.datetime.now() - ta)

        words = ""
        if action == "ALARM":
            words = "Nick, %s ago you asked me to alarm you. Beep. Beep. Beep." % (u.humanReadableTime(dt=dt))
        else:
            words = "Nick, %s ago you asked me to remind you to %s" % (u.humanReadableTime(dt=dt), action)
        print "[times] %s" % words
        u.say(words)

    def addEvent(self,dta,dtb,action):
        self.shelf["events"].append([dta, dtb, action])

    def printEvents(self):
        print self.shelf["events"]

    def startLoop(self):
        self.doLoop = True
        self.thread.start()

    def stopLoop(self):
        self.doLoop = False # doesn't actually kill the thread

    def loop(self):
        while self.doLoop:
            self.checkTimes()
            time.sleep(self.DELAY)

if __name__ == '__main__':
    events = Events()
    events.startLoop()

    while True:
        test = raw_input("test")
        print test
        if test == "e":
            events.stopLoop()
        if test == "p":
            events.printEvents()
        if test == "a":
            now = u.fromTimestamp(1450306547)
            when = u.fromTimestamp(1452286516+1000) # do `date +%s` to get current time
            events.addEvent(now,when, "another thing")

