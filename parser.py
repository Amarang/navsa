import json, datetime, urllib2, urllib
from dateutil.parser import parse

### INFO: ###
# uses API at https://tvmedia.3scale.net/docs
# possible mail apis
    # use GoogleAPI for search
    # use Mailgun API http://www.mailgun.com/
    # use mandrillAPI https://mandrillapp.com

# url = "http://api.tvmedia.ca/tv/v2/lineups/2433/listings?api_key=1a8889539bd4d38cfef23821b8dbb0de&end=%s+00%%3A00%%3A00" % ( datetime.date.today()+datetime.timedelta(days=1) )
# jsontxt = urllib2.urlopen(url).read()

jsontxt = open("input2.json").read()
data = json.loads(jsontxt)

def getImdbLink(title, year):
    query = "%s (%s) imdb" % (title, year)
    query = urllib.quote(query)
    data = json.loads(urllib2.urlopen("http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%s" % query).read())
    return data["responseData"]["results"][0]["url"]


def dictTime(value):
    date = parse(value)
    date -= datetime.timedelta(hours=7) # GMT to Pacific (DST?!)
    return date


def formatTime(date,showAmpm=True):
    formatStr = "%I"
    if(date.minute != 0):
        formatStr += ":%M"
    if(showAmpm): formatStr += "%p"
    return date.strftime(formatStr).lstrip('0') # un-zeropad

def showInfo(show):
    line = ""
    date = dictTime(show['listDateTime'])

    duration = int(show['duration'])
    line += "[%s-%s] " % (formatTime(date,False), formatTime(date+datetime.timedelta(minutes=duration)))
    genres = show['showType'].split(", ")[1:]
    line += "<b>%s</b> (%s) - %s (#%s)" % (show['episodeTitle'], show['year'], show['channelName'], show['channelNum'])
    line += "<p style='text-indent:24pt'> "
    line += "%s; %s " % ( ", ".join(genres), show['description'] )
    # line += "(%s)" % getImdbLink(show['episodeTitle'], show['year'])
    line += "</p> "
    return line



channels = []
for channel in data:
    if( int(channel['number']) in [4, 11, 14, 27, 28, 40, 62] ):
        channels.append(channel)

shows = {}
for channel in channels:
    listings = channel['listings']
    for listing in listings:
        if listing['showName'] == "Movie":
            channelName = channel['callsign']
            # add channel info to dict
            listing['channelNum'] = channel['number']
            listing['channelName'] = channelName
            try:
                shows[channelName].append(listing)
            except:
                shows[channelName] = [listing]

output = ""
for channel in shows.keys():
    for show in shows[channel]:
        #### make cuts ####
        # don't recommend if it's got a bad time
        hour = dictTime(show['listDateTime']).hour % 12
        if not(6 <= hour <= 10): continue
        if int(show['year']) < 2000: continue

        output += showInfo(show)

# print output
