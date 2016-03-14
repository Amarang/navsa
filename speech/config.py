import sys, os

# API KEYS
WIT_AI_KEY = "5WGVQPPDHU7JH2J5WDBJHMJLRXB5WDTP" # wit.ai
API_AI_KEY = "002a2dfa653745fbac633448dbda41fd" # api.ai api key ('api', wow, that's confusing)
API_AI_SUB_KEY = "ac30feb1-4806-4ce5-9797-2785f19cb4f6" # api.ai subscription key

# LOCATION INFO
timezone = "America/Los_Angeles"

# MEH
nick = True

# AI API: witai or apiai
site = "witai"

# WHAT DEVICE
device = "pc"
if "linux" in sys.platform.lower():
    if nick:
        device = "mypi"
    else:
        device = "officepi"
elif "darwin" in sys.platform.lower(): device = "mac"
elif "cygwin" in sys.platform.lower(): device = "pc"

# VOICES
say_type = {}
say_type["pc"] = "fromMac"
say_type["mac"] = "regular"
say_type["officepi"] = "fromMac"
say_type["mypi"] = "fromMac"

default_voice = {}
default_voice["fromMac"] = "Samantha" # Veena
default_voice["cereproc"] = "Jess" # Hannah
default_voice["regular"] = "Samantha"

# SOME PATHS
logopath = "D:/Cygwin64/home/Nick/navsa/images/navsalogo.png"
toasterpath = "../bin/toast.exe"
cereprocpath = "../bin/cereproc.sh"
sounddir = "../sounds/"


if __name__=='__main__':
    import Utils as u
    u.say("my name is veena and I live in a mac", voice="Veena")


