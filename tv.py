import json, datetime, urllib2, urllib
from dateutil.parser import parse
import movieRater

### INFO: ###
# uses API at https://tvmedia.3scale.net/docs
# possible mail apis
    # use GoogleAPI for search
    # use Mailgun API http://www.mailgun.com/
    # use mandrillAPI https://mandrillapp.com


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

def showInfo(show, rating=-1.0):
    line = ""
    date = dictTime(show['listDateTime'])

    duration = int(show['duration'])
    line += "[%s-%s] " % (formatTime(date,False), formatTime(date+datetime.timedelta(minutes=duration)))
    genres = show['showType'].split(", ")[1:]
    line += "<b>%s</b> (%s) - %s (#%s)" % (show['episodeTitle'], show['year'], show['channelName'], show['channelNum'])
    if(rating > 0): line += " RATING: <b>%.1f</b> " % rating
    line += "<p style='text-indent:24pt'> "
    line += "%s; %s " % ( ", ".join(genres), show['description'] )
    try:
        # line += "(%s)" % getImdbLink(show['episodeTitle'], show['year'])
        if(len(show['imdbID']) > 3):
            line += "(http://www.imdb.com/title/%s/)" % (show['imdbID'])
    except:
        print "couldn't get imdblink for %s (%s) imdb" % (show['episodeTitle'], show['year'])
    line += "</p> "
    return line



def getMovies():

    url = "http://api.tvmedia.ca/tv/v2/lineups/2433/listings?api_key=1a8889539bd4d38cfef23821b8dbb0de&end=%s+00%%3A00%%3A00" % ( datetime.date.today()+datetime.timedelta(days=1) )
    jsontxt = urllib2.urlopen(url).read()

    # jsontxt = open("input.json").read()
    data = json.loads(jsontxt)

    print "got tv json"


    output = ""
    outputDetail = ""

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

    movies = []
    for channel in shows.keys():
        for show in shows[channel]:
            #### make cuts ####
            # don't recommend if it's got a bad time
            date = dictTime(show['listDateTime'])
            hour = date.hour
            isWeekend = date.weekday() in [5, 6]
            if(isWeekend):
                if not(2+12 <= hour <= 11+12): continue
            else:
                if not(6+12 <= hour <= 10+12): continue
            if int(show['year']) < 1990: continue

            rating, imdbID = movieRater.getMovieRating(show['episodeTitle'],show['year'], True) 
            show['imdbID'] = imdbID
            movies.append([show, rating])
            # output += showInfo(show)

    print "got movie ratings"

    # sort movies by rating
    movies.sort(key=lambda x: x[-1])
    movies = movies[::-1]
    for movie in movies:
        outputDetail += showInfo(movie[0], movie[-1])

    if(len(movies) > 0):
        if(movies[0][-1] > 7.0): # threshold for best movie
            bestMovie = movies[0]
            description = bestMovie[0]['description']
            output += "After work, treat yourself to \"<b>{0}</b>\" as it has a Nick rating of {1}. Watch it on channel {2} at {3}. In short, {4}".format(
                    bestMovie[0]['episodeTitle'],
                    bestMovie[-1],
                    bestMovie[0]['channelNum'],
                    formatTime(dictTime(bestMovie[0]['listDateTime'])),
                    description[0].lower()+description[1:]
                    )
        else:
            output += "There are no high-ranked movies that I think you would like, but check out the ones I have listed anyways. Maybe you can correct my algorithm if there's something wrong with me."
    else:
        output += "There are no movies that would interest you."


    # print output
    # print outputDetail
    return output, outputDetail
