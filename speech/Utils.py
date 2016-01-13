import datetime, time
import os, sys

def say(text):
    # return 'espeak "%s" & ' % text
    # return '(espeak -w temp.wav "%s" && aplay temp.wav) & ' % text # does not slow down after a few words
    os.system('(espeak -w temp.wav "%s" && cat temp.wav > /dev/dsp) & ' % text) # for laptop
    # return 'mplayer -ao alsa -noconsolecontrols "http://translate.google.com/translate_tts?tl=en&client=t&q=%s" & ' % text # occasionally gets rate-limited
    
def toTimestamp(dt):
    # return int(dt.strftime("%s"))
    return int(time.mktime(dt.timetuple()))

def fromTimestamp(ts):
    return datetime.datetime.fromtimestamp(int(ts))

def humanReadableTime2(dt=None, sec=None):
    """ DEPRECATED...delete """
    if sec:
        seconds = sec
    else:
        seconds = dt.seconds
    roundedSeconds300 = round(float(seconds)/300.0)*300 # round number of seconds to closest 5 minute increment
    roundedSeconds10 = round(float(seconds)/10.0)*10 # round number of seconds to closest 10 second increment
    days, hours, minutes = int(roundedSeconds300//86400), int(roundedSeconds300//3600), int((roundedSeconds300%3600)/60)

    # print roundedSeconds300
    # print days, hours, minutes

    if days < 0:
        print "ERORR: negative time"
        return ""

    if days + hours + minutes == 0:
        # print seconds%60
        return "%i seconds" % (roundedSeconds10%60)
    if days + hours == 0:
        return "%i minutes" % minutes
    if days == 0:
        if hours == 1: return "an hour"
        else: return "%s hours" % hours
    else:
        if days == 1: return "a day"
        elif days > 3: return "a long time"
        else: return "%s days" % days

    return ""

def humanReadableTime3(dt=None, sec=None):
    """ DEPRECATED...delete """
    if sec:
        dt = datetime.timedelta(seconds=sec)

    # print dt

    if dt.seconds < 0:
        print "ERROR: negative time"
        return None

    days, hours, minutes, seconds = int(dt.seconds//86400), int(dt.seconds//3600), int((dt.seconds%3600)/60), dt.seconds%60
    # print days, hours,minutes, seconds

    if days + hours + minutes == 0:
        return "%i seconds" % seconds
    if days + hours == 0:
        if minutes == 1: return "a minute"
        elif minutes == 2: return "a couple of minutes"
        else: return "%i minutes" % minutes
    if days == 0:
        if hours == 1: return "an hour"
        if hours == 2: return "a couple of hours"
        else: return "%s hours" % hours
    else:
        if days == 1: return "a day"
        elif days > 3: return "a long time"
        else: return "%s days" % days

    return ""

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
