import bs4
import datetime
from dateutil.parser import parse
import urllib2, urllib

def torrents():
    # data = open("tpb.txt", "r").read().strip().split("\n")
    # data2 = open("tpb.txt", "r").read()
    data = urllib2.urlopen("http://thepiratebay.se/top/207").read()

    baseurl = "http://thepiratebay.se"
    # print data2
    # bs = bs4.BeautifulSoup(data2)
    bs = bs4.BeautifulSoup(data)

    movies = []
    for tr in bs.find_all('tr'):
        a = tr.find('div').a
        if(a is not None):
            name = a.text
            link = a['href']
            # /torrent/11049465/Million_Dollar_Arm_
            link = link.split("/")[:3]
            link = baseurl + "/".join(link)+"/"
            # print baseurl+a['href']
        else:
            continue

        desc = tr.find('font')
        # print desc.text
        date, size, uploader = desc.text.split(",")
        date = date.replace("Uploaded", "").strip()
        date = " ".join(date.split())
        size = size.split()[1:]
        mult = 1024.0 if size[-1] == 'GiB' else 1
        size = float(size[0])*mult
        uploader = uploader.split()[-1]
        # print date, size, uploader
        movies.append( [ name, date, size, uploader, link ] )
        # print tr.find('div').find('a').text

    goodmovies = []
    for movie in movies:
        # print movie
        name, date, size, uploader, link = movie
        if(uploader != 'YIFY'): continue
        if(size > 1000): continue
        # print date
        try:

            d1 = parse(date)
            days = (datetime.datetime.today() - d1).days
            if(days > 2): continue
            
        except:
            # if can't parse, probably means it has "y-day" or "45 mins ago" in it
            # in which case, it's recent enough to be within threshold of
            # consideration anyways
            pass

        
        goodmovies.append( [name, date, link] )
    return goodmovies

def getTPB():
    output = ""
    outputDetail = ""

    movies = torrents()
    print "got torrents"

    if(len(movies) > 0):
        output += "Additionally, I found these recent movie torrents:"
    output += "<ul>"
    for movie in movies:
        name, date, link = movie
        output += "<li>%s (%s)</li>" % (name, link)
        
    output += "</ul>"
    return output, outputDetail

        
# print getTPB()
