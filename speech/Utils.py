import datetime, time
import os, sys

def say(text):
    if "linux" in sys.platform.lower(): # linux2 (office pi)
        os.system('(espeak -w temp.wav "%s" && aplay temp.wav) & ' % text) # does not slow down after a few words
    elif "darwin" in sys.platform.lower(): # darwin (office mac)
        os.system('say -v Vicki "%s" &' % text)
    elif "cygwin" in sys.platform.lower(): # cygwin (laptop)
        os.system('(espeak -w temp.wav "%s" && cat temp.wav > /dev/dsp) & ' % text)
    else:
        os.system('(espeak -w temp.wav "%s" && aplay temp.wav) & ' % text)
    
def toTimestamp(dt):
    return int(time.mktime(dt.timetuple()))

def fromTimestamp(ts):
    return datetime.datetime.fromtimestamp(int(ts))

def humanReadableTime(dt=None, sec=None, precision=2, past_tense='{} ago', future_tense='in {}'):
    if sec:
        dt = datetime.timedelta(seconds=sec)

    if type(dt) is not type(datetime.timedelta()):
        dt = datetime.datetime.now() - dt
     
    the_tense = past_tense
    if dt < datetime.timedelta(0): the_tense = future_tense
        
    dt = abs( dt )
    d = { 
        'year'   : dt.days / 365 ,
        'day'    : dt.days % 365 ,
        'hour'   : dt.seconds / 3600 ,
        'minute' : (dt.seconds / 60) % 60 ,
        'second' : dt.seconds % 60 ,
        'microsecond' : dt.microseconds
    }
    hlist = [] 
    count = 0
    units = ( 'year', 'day', 'hour', 'minute', 'second', 'microsecond' )
    for unit in units:
        if count >= precision: break # met precision
        if d[ unit ] == 0: continue # skip 0's
        s = '' if d[ unit ] == 1 else 's' # handle plurals
        hlist.append( '%s %s%s' % ( d[unit], unit, s ) )
        count += 1
    human_delta = ', '.join( hlist )
    return the_tense.format(human_delta) 

# now = datetime.datetime.now()
# dt = datetime.timedelta(seconds=180)
# then = now-dt
# print then,now
# # print humanReadableTime2(dt=now-then)
# print human(dt=now-then)
