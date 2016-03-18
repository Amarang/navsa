import bs4
import datetime
from dateutil.parser import parse
import urllib2, urllib, re
import commands

links = []

def cullMovies(movies):

    thisYear = datetime.datetime.today().year
    names = [movie[0] for movie in movies]

    goodmovies = []
    for movie in movies:
        name, date, size, uploader, link = movie
        # if(uploader != 'YIFY'): continue
        if(size >= 1000): continue
        try:
            d1 = parse(date)
            days = (datetime.datetime.today() - d1).days
            # FIXME back to > 3
            if(days > 3): continue
            
        except:
            # if can't parse, probably means it has "y-day" or "45 mins ago" in it
            # in which case, it's recent enough to be within threshold of
            # consideration anyways
            pass

        m = re.search("\(([0-9]{4})\)", name)
        if(m): 
            year = int(m.groups()[0])
            if year != thisYear and year != thisYear-1:
                continue

        # # if this is 720p and we have a 1080p version, 
        # # then ignore the 720p one
        # if("720p" in name):
        #     tocheck = name.replace("720p","1080p")
        #     if(tocheck in names):
        #         continue

        goodmovies.append( [name, date, link] )

    # print goodmovies
    return goodmovies


def torrents():
    baseurl = "https://thepiratebay.se"
    cmd = "curl -s -m 20 " + baseurl + "/top/207"
    status,data = commands.getstatusoutput(cmd)
    bs = bs4.BeautifulSoup(data)

    movies = []
    for tr in bs.find_all('tr'):
        a = tr.find('div').a
        if(a is not None):
            name = a.text
            link = a['href']
            link = link.split("/")[:3]
            link = baseurl + "/".join(link)+"/"
        else:
            continue

        desc = tr.find('font')
        date, size, uploader = desc.text.split(",")
        date = date.replace("Uploaded", "").strip()
        date = " ".join(date.split())
        size = size.split()[1:]
        mult = 1024.0 if size[-1] == 'GiB' else 1
        size = float(size[0])*mult
        uploader = uploader.split()[-1]
        movies.append( [ name, date, size, uploader, link ] )

    return cullMovies(movies)

def getData():
    import movieRater

    output = ""
    outputDetail = ""


    try:
        movies = torrents()
    except:
        print "error reaching tpb"
        return output, outputDetail

    print "got torrents"

    initialpart = "I found these recent movie torrents: <ul>"

    nmovies = 0
    for movie in movies:
        name, date, link = movie

        print movie
        rating = None
        imdbID = None
        try:
            movieYear = re.findall(r'\d{4}', name)[0]
            movieName = name.split(movieYear)[0].replace("."," ").strip()
            rating, imdbID = movieRater.getMovieRating(movieName, movieYear, returnImdbID=True)
        except:
            try:
                movieName = name.split("(")[0]
                movieYear = name.split("(")[1].split(")")[0]
                rating, imdbID = movieRater.getMovieRating(movieName, movieYear, returnImdbID=True)
            except:
                pass

        if rating and imdbID:
            links.append(link)
            output += "<li>%s (%s) RATING: <b>%s</b> (http://www.imdb.com/title/%s/)</li>" % (name, link, rating, imdbID)
        else:
            links.append(link)
            output += "<li>%s (%s)</li>" % (name, link)

        nmovies += 1

        
    if nmovies > 0:
        output = initialpart + output
        output += "</ul>"
    return output, outputDetail

def downloadMovies(urls=[]):
    if not urls:
        urls = links[:]

    import filestream as fs
    fs.get(urls)

if __name__=='__main__':
    print getData()

