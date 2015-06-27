import urllib, urllib2, datetime, json

# NAVSA - Not A Very Sophisticated Assistant
def sendMail(subject, body):
    url = 'https://api.mailgun.net/v2/sandbox96042724eeb049af864d017016a510a3.mailgun.org/messages'
    body = body.encode('ascii', 'ignore')
    values = {
            'to' : 'typhoid.pwns@gmail.com',
            'subject' : subject,
            'html' : body,
            'from': ' NAVSA <navsa@navsa.mailgun.org>',
            }

    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    passMgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    # passMgr.add_password(None, url, 'api', 'key-3ax6xnjp29jd6fds4gc373sgvjxteol0') # example
    passMgr.add_password(None, url, 'api', 'key-11f650355cb466e2286da5bd59ee09fe') # my api
    authMgr = urllib2.HTTPBasicAuthHandler(passMgr)
    opener = urllib2.build_opener(authMgr)
    urllib2.install_opener(opener)

    successful = True
    try:
        response = urllib2.urlopen(req).read()
        jsonResponse = json.loads(response)
        if( jsonResponse['message'] != "Queued. Thank you." ):
            successful = False
    except:
        print "couldn't get response!"
        successful = False
    return successful

def formatPrint(sep, text):
    out = ""
    if(len(text) > 1):
        out += sep*2
        out += text
    else:
        out += text

    return out



sep = "<br>"
body = "Hi Nick,"+sep*2

import tv
import weather
import move
import tpb
import barc
import snt
import fb
import arxiv
# import modified


weoutput, weoutputDetail = weather.getWeather()
print "got weather output"
tvoutput, tvoutputDetail = tv.getMovies()
print "got tv output"
moveoutput, moveoutputDetail = move.getWalk()
print "got gps output"
tpboutput, tpboutputDetail = tpb.getTPB()
print "got tpb output"
barcoutput, barcoutputDetail = barc.getBARC()
print "got barc output"
sntoutput, sntoutputDetail = snt.getSNT()
print "got snt output"
fboutput, fboutputDetail = fb.getFB(8.0)
print "got fb output"
arxivoutput, arxivoutputDetail = arxiv.getArxiv()
print "got arxiv output"
# modifiedoutput, modifiedoutputDetail = modified.getModified()
# print "got modified site output"

# summary content
body +=                  weoutput
body += formatPrint(sep, tvoutput)
body += formatPrint(sep, tpboutput)
body += formatPrint(sep, barcoutput)
body += formatPrint(sep, sntoutput)
body += formatPrint(sep, arxivoutput)
body += formatPrint(sep, moveoutput)
body += formatPrint(sep, fboutput)
# body += formatPrint(sep, modifiedoutput)

# salutation
body += sep*2
body += "Cheers,"+sep+"NAVSA"
body += sep*5

# detailed content
body += "<hr>"
body +=                  weoutputDetail
body += formatPrint(sep, moveoutputDetail)
body += formatPrint(sep, tvoutputDetail)
body += formatPrint(sep, tpboutputDetail)
body += formatPrint(sep, arxivoutputDetail)
body += formatPrint(sep, barcoutputDetail)
body += formatPrint(sep, sntoutputDetail)
body += formatPrint(sep, fboutputDetail)
# body += formatPrint(sep, modifiedoutputDetail)

# print body
if sendMail("Status update for %s" % datetime.date.today(),body):
    print "email sent successfully!"
else:
    print "ERROR sending email"
# sendMail("test","testbody")
