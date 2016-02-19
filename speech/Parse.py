import re
from pprint import pprint

import Utils as u
import datetime, time
from dateutil import parser
import config


class Parser:
    def __init__(self):
        self.site = config.site
        pass

    def do_test(self, typ="apiai"):
        queries = [
                # "set an alarm in 10 minutes",
                # "remind me to do something in 5 minutes",
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
            print "\n\n"
            time.sleep(1)
            if typ=="apiai":
                self.handle_api_ai(u.get_text_api(q))
            elif typ=="witai":
                self.handle_wit_ai(u.get_text_wit(q))

    def say_text(self, text):
        print text
        u.say(text)

    def handle(self, json):
        if self.site == "apiai":
            self.handle_api_ai(json)
        elif self.site == "witai":
            self.handle_wit_ai(json)

    def handle_wit_ai(self, json):
        try:
            outcome = json["outcomes"][0]
            intent = outcome["intent"]
            confidence = outcome["confidence"]
            query = outcome["_text"]
        except:
            print "Couldn't get an intent from wit"
            pprint(json)
            return

        if confidence < 0.41:
            print "Confidence too low: %.2f" % confidence
            return
        pprint(json)

        if intent == "reminder":
            entities = outcome["entities"]
            what = entities["reminder"][0]["value"]
            when = entities["datetime"][0].get("value") or entities["datetime"][0].get("values")[0]["from"]["value"]
            when = datetime.datetime.strptime(when.split(".")[0],"%Y-%m-%dT%H:%M:%S")
            print intent, what, when
            self.intent_reminder(what, when)

        elif intent == "timer":
            normalized = outcome["entities"]["duration"][0]["normalized"]
            if normalized["unit"] == "second":
                seconds = normalized["value"] # seconds
                when = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
                print intent, when
                self.intent_alarm(when)
            else:
                print "I don't know how to handle the unit in:"
                pprint(normalized)

        elif intent == "onoff":
            obj = outcome["entities"]["object"][0]["value"]
            onoff = "on" in outcome["entities"]["on_off"][0]["value"]
            if obj in ["lights"]:
                print intent, obj, onoff
                self.intent_lights(onoff)

        elif intent == "open":
            obj = outcome["entities"]["object"][0]["value"]
            print intent, obj
            self.intent_open(obj)

        elif intent == "johncena":
            print intent
            self.intent_johncena()

        else:
            print "I don't know how to handle this:"
            pprint(json)

    def handle_api_ai(self, json):

        # these three should always be present
        intent = json['result']['action']
        query = json['result']['resolvedQuery']

        if intent in ["notifications.add"]: # remind me to do something in 1 hour
            what = json['result']['parameters']['summary']
            when = None
            try: when = u.parseDatestring(json['result']['parameters']['time'])
            except: pass
            try: when = datetime.datetime.now()+u.parseOffset(json['result']['parameters']['time_offset'])
            except: pass
            print intent, what, when
            self.intent_reminder(what, when)

        elif intent in ["clock.timer_start", "clock.alarm_set"]: # set a timer for 5 minutes
            when = None
            try: when = u.parseDatestring(json['result']['parameters']['time'])
            except: pass
            try: when = datetime.datetime.now()+u.parseOffset(json['result']['parameters']['time_offset'])
            except: pass
            print intent, when
            self.intent_alarm(when)

        elif intent in ["smarthome.lights_off", "smarthome.lights_on"]: # turn lights off
            onoff = "on" in intent
            print intent, onoff
            self.intent_lights(onoff)

        elif intent in ["calculator.math"]: # what is 3+3 divided by the square root of 3
            answer = json['result']['parameters']['result']
            print intent, answer
            self.intent_generalsay(answer)

        elif intent in ["browse.open"]: # open netflix
            website = json['result']['parameters']['website']
            print intent, website
            self.intent_open(website)

        elif intent in ["suggest.food"]: # where should I eat?
            print intent
            self.intent_suggestfood()

        elif intent in ["smalltalk.greetings", "name.get"]: # hi, what is [your/my] name?
            response = json['result']['metadata']['html']
            print intent
            self.intent_generalsay(response)

        elif "fulfillment" in json["result"] and "speech" in json["result"]["fulfillment"] and len(json["result"]["fulfillment"]["speech"]) > 0:
            tosay = json["result"]["fulfillment"]["speech"]
            print intent
            self.intent_generalsay(tosay)

        elif "metadata" in json["result"] and "html" in json["result"]["metadata"] and len(json["result"]["metadata"]["html"]) > 0:
            tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
            tosay = json["result"]["metadata"]["html"]
            tosay = tag_re.sub('', tosay)
            print intent
            self.intent_generalsay(tosay)

        else:
            pprint.pprint( json )
            print intent, query, now

    def intent_reminder(self, what, when):
        now = datetime.datetime.now()
        resp = "Okay, will remind you to %s in %s" % (what, u.humanReadableTime(when-now))
        print resp

    def intent_alarm(self, when):
        now = datetime.datetime.now()
        resp = "Okay, will alarm you in %s" % (u.humanReadableTime(when-now))
        print resp

    def intent_lights(self, onoff):
        resp = "Okay, turning lights %s" % ("on" if onoff else "off")
        print resp

    def intent_open(self, what):
        resp = "Okay, opening %s" % (what)
        print resp

    def intent_suggestfood(self):
        resp = "I don't know where you should eat, bro"
        print resp

    def intent_generalsay(self, tosay):
        resp = tosay
        print resp

    def intent_johncena(self):
        resp = "His name is JOHN CENA"
        print resp


if __name__ == '__main__':
    p = Parser()
    # p.do_test(typ="apiai")
    p.do_test(typ="witai")
