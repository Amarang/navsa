import datetime, time
import os, sys
import config

def web(filename,user="namin"):
    os.system("scp %s %s@uaf-8.t2.ucsd.edu:~/public_html/dump/ >& /dev/null" % (filename, user))
    print "Copied to uaf-8.t2.ucsd.edu/~%s/dump/%s" % (user, filename.split("/")[-1])

def say(text, voice=None):
    device = config.device
    say_type = config.say_type[device]
    if not voice: voice = config.default_voice[say_type]

    cmd = ""
    if say_type == "cereproc":
        config.cereprocpath = "../bin/cereproc.sh"
        output="temp.wav"
        key="yveys9w8hipsc3di"
        cmd = "(%s -v %s -o %s -k %s -t \"%s\" ; " % (cereprocpath, voice, output, key, text)
        if device == "pi": cmd += 'aplay temp.wav; ) &'
        elif device == "pc": cmd += 'cat temp.wav > /dev/dsp ; ) &'
        elif device == "mac": cmd += 'afplay temp.wav ; ) &'
    elif say_type == "fromMac":
        cmd = """(ssh -q namin@squark.physics.ucsb.edu "cd ~/sandbox/sound ; say -v %s \\'%s\\' -o temp.aiff ; /usr/local/bin/sox temp.aiff temp.wav " ; scp -q namin@squark.physics.ucsb.edu:~/sandbox/sound/temp.wav . ; """ % (voice, text)
        if device == "pi": cmd += 'aplay temp.wav ; ) &'
        elif device == "pc": cmd += 'cat temp.wav > /dev/dsp ; ) &'
    elif say_type == "regular":
        if device == "pi": cmd = '(espeak -w temp.wav "%s" && aplay temp.wav) & ' % text
        elif device == "mac": cmd = 'say -v %s "%s" &' % (voice, text)
        elif device == "pc": cmd = '(espeak -w temp.wav "%s" && cat temp.wav > /dev/dsp) & ' % text
    else:
        print "unrecognized configuration! voice: %s, device: %s, say_type: %s" % (voice, device, say_type)
    if cmd: os.system(cmd)

def toast(text, title=""):
    cmd = ""
    if config.device == "mac":
        # http://apple.stackexchange.com/questions/57412/how-can-i-trigger-a-notification-center-notification-from-an-applescript-or-shel
        # sounds in /System/Library/Sounds
        cmd += "osascript -e 'display notification \"%s\" with title \"%s\" sound name \"Submarine.aiff\"'" % (text, title)
    elif config.device == "pc":
        config.logopath = "D:/Cygwin64/home/Nick/navsa/images/navsalogo.png"
        config.toasterpath = "../bin/toast.exe"
        cmd += "%s -t '%s' -m '%s' -p '%s'" % (toasterpath, title, text, logopath)
    if cmd: os.system(cmd)

def play(fname):
    cmd = ""
    if config.device == "pi": cmd += '(aplay %s) &' % fname
    elif config.device == "mac": cmd += '(afplay %s) &' % fname
    elif config.device == "pc": cmd += '(cat %s > /dev/dsp) &' % fname
    if cmd: os.system(cmd)

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

def timeit(func):
  def wrapper(*arg):
      t = time.time()
      res = func(*arg)
      print "%s took %.2f ms" % (func.func_name, time.time()-t)
      return res
  return wrapper

def get_voice_wit(data):
    url = "https://api.wit.ai/speech?v=20141022"
    headers = {"Authorization": "Bearer {0}".format(config.WIT_AI_KEY), "Content-Type": "audio/wav"}
    resp = requests.post(url, data=data, headers=headers)
    return resp.json()

def get_voice_api(data):
    url = "https://api.api.ai/v1/query?v=20150910"
    jd = json.dumps({"sessionId" : "1234567890", "lang": "en", "timezone": config.timezone})
    headers = { "Authorization": "Bearer {0}".format(config.API_AI_KEY), "ocp-apim-subscription-key": config.API_AI_SUB_KEY }
    files = { 'request': ('', jd, 'application/json'), 'voiceData': ('', data, 'audio/wav') }
    resp = requests.post(url, headers=headers, files=files)
    return resp.json()

def get_text_wit(query):
    url = 'https://api.wit.ai/message'
    params = {'access_token' : config.WIT_AI_KEY, 'q' : query }
    resp = requests.get(url, params=params)
    return resp.json()

def get_text_api(query):
    url = "https://api.api.ai/v1/query?v=20150910"
    params = {"lang": "en", "timezone": config.timezone, "query": query}
    headers = { "Authorization": "Bearer {0}".format(config.API_AI_KEY), "ocp-apim-subscription-key": config.API_AI_SUB_KEY }
    resp = requests.get(url, headers=headers, params=params)
    return resp.json()
