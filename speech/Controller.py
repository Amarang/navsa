from bottle import post, route, run, request
import os, sys
import urllib, urllib2, json, datetime, time
import Utils as u
import Events

# Test with:
#   import urllib
#   import urllib2
#   data = urllib.urlencode({'words' : 'this is a test', 'type' : 'voice' })
#   req = urllib2.Request('http://localhost:8080/say', data)
#   response = urllib2.urlopen(req)
#   the_page = response.read()


API_KEY = "5WGVQPPDHU7JH2J5WDBJHMJLRXB5WDTP"

def getWit(query):
    data = {'access_token' : API_KEY, 'q' : query }
    response = urllib2.urlopen('https://api.wit.ai/message?'+urllib.urlencode(data)).read()
    out = json.loads(response)
    return out

# def say(text):
#     # return 'espeak "%s" & ' % text
#     # return '(espeak -w temp.wav "%s" && aplay temp.wav) & ' % text # does not slow down after a few words
#     return '(espeak -w temp.wav "%s" && cat temp.wav > /dev/dsp) & ' % text # for laptop
#     # return 'mplayer -ao alsa -noconsolecontrols "http://translate.google.com/translate_tts?tl=en&client=t&q=%s" & ' % text # occasionally gets rate-limited

def wit(words):
    intent = None

    try:
        out = getWit(words)
        print out
        intent = out["outcomes"][0]["intent"]
    except:
        print "Couldn't get wit (or intent) stuff for: %s" % words
        return

    if intent == "reminder":
        entities = out["outcomes"][0]["entities"]
        what = entities["reminder"][0]["value"]
        when = entities["datetime"][0].get("value") or entities["datetime"][0].get("values")[0]["from"]["value"]

        when = datetime.datetime.strptime(when.split(".")[0],"%Y-%m-%dT%H:%M:%S")
        now = datetime.datetime.now()
        dt = when - now
        events.addEvent(now, when, what)

    elif intent == "timer":
        seconds = out["outcomes"][0]["entities"]["duration"][0]["normalized"]["value"] # seconds

        now = datetime.datetime.now()
        when = now + datetime.timedelta(seconds=seconds)
        dt = when - now
        events.addEvent(now, when, "ALARM")

def handleWords(words,reqType=None):
    if reqType == "meterMaker":
        u.say(words)

    elif reqType == "voice":

      if("Search, or say" in words or "Ok Google" in words or "Okay Google" in words): return

      if (   "his name is" in words
          or "is name his" in words
          or "what's his name" in words
          or "what is his" in words
          or "what is name" in words
          or "his name his" in words
          or "whats the name" in words  ):
          # os.system('aplay johncena_nointro.wav')
          os.system('cat johncena_nointro.wav > /dev/dsp')
          return

      if("john cena" in words):
          os.system('cat johncena.wav > /dev/dsp')
          # os.system('aplay johncena.wav')
          return

      if(words.strip().lower().startswith("say")): 
          words = " ".join(words.split("say", 1)[1:])
          u.say(words)
          return

      wit(words)
      return

    u.say(words)
    return
    # return 'say -v Vicki "%s" &' % words # MAC

@post('/say')
def getWords():
    d = dict(request.forms)
    # print d
    words = d["words"]
    reqType = d["type"] if "type" in d else None
    # print words, reqType
    # print "test"
    handleWords(words,reqType)
    # os.system(cmd)

if __name__ == '__main__':
    events = Events.Events(delay=3,threshold=10,timefile="times.db")
    events.startLoop()


    # handleWords("remind me to take the trash out in 1 minute", "voice")

    run(host="0.0.0.0", port=8080)

