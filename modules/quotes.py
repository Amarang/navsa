import bs4, urllib2, datetime, random
import config
from dateutil.parser import parse


def getQuote():
    quotetype = config.quotes['type']
    with open("../misc/%s.txt" % quotetype) as fh:
        data = fh.readlines()

    quote = random.choice(data).strip()
    return "%s: %s" % (quotetype.title(),quote)


def getData():
    output = ""
    outputDetail = ""

    output += getQuote()

    return output, outputDetail


if __name__=='__main__':
    print getData()
