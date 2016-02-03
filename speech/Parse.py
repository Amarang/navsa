import pprint

import Utils as u
import datetime
from dateutil import parser

# json = u.get_text_api("set an alarm in 10 minutes and 32 seconds")
# json = u.get_text_api("turn off the lights")
# json = u.get_text_api("where should I get dinner")
# json = u.get_text_api("what's thirty-nine divided by the square root of 3")
# json = u.get_text_api("open netflix please")

pprint.pprint(json['result'])

myResult = {}
myResult["intent"] = json['result']['action']
myResult["query"] = json['result']['resolvedQuery']
myResult["now"] = datetime.datetime.now()

try: myResult["what"] = json['result']['parameters']['summary']
except: pass
try: myResult["answer"] = json['result']['parameters']['result']
except: pass
try: myResult["website"] = json['result']['parameters']['website']
except: pass
try:
    myResult["when"] = u.parseDatestring(json['result']['parameters']['time'])
    myResult["when"] = datetime.datetime.now()+u.parseOffset(json['result']['parameters']['time_offset'])
except: pass

pprint.pprint(myResult)

# possible intents:
# notifications.add
# suggest.food
# clock.timer_start
# clock.alarm_set
# smarthome.lights_off
# smarthome.lights_on
# calculator.math
# input.unknown
# browse.open
