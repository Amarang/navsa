import datetime, time
import os, sys

def web(filename,user="namin"):
    os.system("scp %s %s@uaf-8.t2.ucsd.edu:~/public_html/dump/ >& /dev/null" % (filename, user))
    print "Copied to uaf-8.t2.ucsd.edu/~%s/dump/%s" % (user, filename.split("/")[-1])

def say(text, voice="Samantha"):
    if "linux" in sys.platform.lower(): # linux2 (office pi)
        os.system('(espeak -w temp.wav "%s" && aplay temp.wav) & ' % text) # does not slow down after a few words
    elif "darwin" in sys.platform.lower(): # darwin (office mac)
        if "curry" in text.lower(): voice = "Veena"
        os.system('say -v %s "%s" &' % (voice, text))
    elif "cygwin" in sys.platform.lower(): # cygwin (laptop)
        os.system('(espeak -w temp.wav "%s" && cat temp.wav > /dev/dsp) & ' % text)
    else:
        os.system('(espeak -w temp.wav "%s" && aplay temp.wav) & ' % text)

def sayFromMac(text, voice="Samantha"):
    os.system("ssh -q namin@squark.physics.ucsb.edu 'cd ~/sandbox/sound ; say -v %s \"%s\" -o temp.aiff ; /usr/local/bin/sox temp.aiff temp.wav ' ; scp -q namin@squark.physics.ucsb.edu:~/sandbox/sound/temp.wav ." % (voice, text))

    if "linux" in sys.platform.lower(): # linux2 (office pi)
        os.system('aplay temp.wav &')
    elif "cygwin" in sys.platform.lower(): # cygwin (laptop)
        os.system('(cat temp.wav > /dev/dsp) & ')

def toast(text, title=""):
    if "darwin" in sys.platform.lower(): # darwin (office mac)
        # http://apple.stackexchange.com/questions/57412/how-can-i-trigger-a-notification-center-notification-from-an-applescript-or-shel
        # sounds in /System/Library/Sounds
        os.system("osascript -e 'display notification \"%s\" with title \"%s\" sound name \"Submarine.aiff\"'" % (text, title))
    elif "cygwin" in sys.platform.lower(): # cygwin (laptop)
        logopath = "D:/Cygwin64/home/Nick/navsa/images/navsalogo.png"
        toasterpath = "../bin/toast.exe"
        os.system("%s -t '%s' -m '%s' -p '%s'" % (toasterpath, title, text, logopath))

def play(fname):
    if "linux" in sys.platform.lower(): # linux2 (office pi)
        os.system('aplay %s' % fname) # does not slow down after a few words
    elif "darwin" in sys.platform.lower(): # darwin (office mac)
        os.system('afplay %s' % fname)
    elif "cygwin" in sys.platform.lower(): # cygwin (laptop)
        os.system('cat %s > /dev/dsp' % fname)
    else:
        os.system('cat %s > /dev/dsp' % fname)
    
def toTimestamp(dt):
    return int(time.mktime(dt.timetuple()))

def fromTimestamp(ts):
    return datetime.datetime.fromtimestamp(int(ts))

def humanReadableTime(dt=None, sec=None, precision=1):
    if sec is not None:
        sec = max(sec, 0)
        dt = datetime.timedelta(seconds=sec)

    if dt < datetime.timedelta(0): dt = datetime.timedelta(0)
        
    d = { 
        'year'   : dt.days / 365 ,
        'day'    : dt.days % 365 ,
        'hour'   : dt.seconds / 3600 ,
        'minute' : (dt.seconds / 60) % 60 ,
        'second' : dt.seconds % 60
    }
    hlist = [] 
    count = 0
    units = ( 'year', 'day', 'hour', 'minute', 'second' )
    for unit in units:
        if count >= precision: break # met precision
        if d[ unit ] == 0: continue # skip 0's
        s = '' if d[ unit ] == 1 else 's' # handle plurals
        hlist.append( '%s %s%s' % ( d[unit], unit, s ) )
        count += 1
    human_delta = ', '.join( hlist )
    return '{}'.format(human_delta) 

# now = datetime.datetime.now()
# dt = datetime.timedelta(seconds=180)
# then = now-dt
# print then,now
# # print humanReadableTime2(dt=now-then)
# print human(dt=now-then)
# print humanReadableTime(sec=-1)
