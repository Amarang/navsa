import pprint

import Utils as u
import datetime, time
from dateutil import parser


class Parser:
    def __init__(self):
        pass

    def test_api_ai(self):
        queries = [
                "set an alarm in 10 minutes and 32 seconds",
                # "turn off the lights",
                # "where should I get dinner",
                # "what's thirty-nine divided by the square root of 3",
                # "open netflix please",
                # "hi navsa",
                # "what is my name",
                # "what is your name?",
                # "will donald trump win?"
            ]
        for q in queries:
            print "\n\n\n"
            time.sleep(1)
            self.handle_api_ai(u.get_text_api(q))

    def say_text(self, text):
        print text
        u.say(text)

    def handle_api_ai(self, json):

        # these three should always be present
        intent = json['result']['action']
        query = json['result']['resolvedQuery']
        now = datetime.datetime.now()

        if intent in ["notifications.add"]: # remind me to do something in 1 hour
            what = json['result']['parameters']['summary']
            when = None
            try: when = u.parseDatestring(json['result']['parameters']['time'])
            except: pass
            try: when = now+u.parseOffset(json['result']['parameters']['time_offset'])
            except: pass

            print intent, what, when
            print "Okay, will remind you to %s in %s" % (what, u.humanReadableTime(when-now))


        elif intent in ["clock.timer_start", "clock.alarm_set"]: # set a timer for 5 minutes
            when = None
            try: when = u.parseDatestring(json['result']['parameters']['time'])
            except: pass
            try: when = now+u.parseOffset(json['result']['parameters']['time_offset'])
            except: pass

            print intent, when
            self.say_text( "Okay, will alarm you in %s" % (u.humanReadableTime(when-now)) )


        elif intent in ["smarthome.lights_off", "smarthome.lights_on"]: # turn lights off
            onoff = "on" in intent

            print intent
            self.say_text( "Okay, turning lights %s" % ("on" if onoff else "off") )


        elif intent in ["calculator.math"]: # what is 3+3 divided by the square root of 3
            answer = json['result']['parameters']['result']
            
            print intent, answer
            self.say_text( "%s" % (answer) )


        elif intent in ["browse.open"]: # open netflix
            website = json['result']['parameters']['website']

            print intent, website
            self.say_text( "Okay, opening %s" % (website) )


        elif intent in ["suggest.food"]: # where should I eat?

            print intent
            self.say_text( "I don't know where you should eat bro" )


        elif intent in ["smalltalk.greetings", "name.get"]: # hi, what is [your/my] name?
            response = json['result']['metadata']['html']

            print intent
            self.say_text( "%s" % (response) )


        elif "fulfillment" in json["result"] and "speech" in json["result"]["fulfillment"]:
            tosay = json["result"]["fulfillment"]["speech"]

            print intent
            self.say_text( "%s" % (tosay) )


        else:

            pprint.pprint( json )

            print intent, query, now



if __name__ == '__main__':
    p = Parser()
    p.test_api_ai()
