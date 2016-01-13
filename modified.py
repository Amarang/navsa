import urllib2
import datetime
from dateutil.parser import parse

import config

def getData():

    output = ""
    outputDetail = ""
    
    for site in config.modified:
        url = site['url']
        name = site['name']


        # site = 'http://online.kitp.ucsb.edu/~doug/phys205/'

        # response = urllib2.urlopen(site)
        response = urllib2.urlopen(url)
        modifiedDate = response.info().dict['last-modified']

        d1 = parse(modifiedDate).replace(tzinfo=None)
        # print d1
        # print datetime.datetime.today()
        hours = (datetime.datetime.today() - d1).seconds / 3600.0
        
        if(hours < 24.0):
            output += "<br>%s website changed %i hours ago (%s)" % (name, int(hours), url)

        outputDetail += "<br>%s website last modified %i hours ago (%s) with header:<br>%s" % (name, int(hours), url, response.info())


    return output, outputDetail

        # print url, name, hours
# getModified()
