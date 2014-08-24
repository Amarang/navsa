import urllib, urllib2, datetime

# NAVSA - Not A Very Sophisticated Assistant
def sendMail(subject, body):
    url = 'https://api.mailgun.net/v2/samples.mailgun.org/messages'
    values = {
    'to' : 'typhoid.pwns@gmail.com',
    'subject' : subject,
    'html' : body,
    'from': ' NAVSA <navsa@samples.mailgun.org>',
    }

    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    passMgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passMgr.add_password(None, url, 'api', 'key-3ax6xnjp29jd6fds4gc373sgvjxteol0') # example
    # passMgr.add_password(None, url, 'api', 'key-11f650355cb466e2286da5bd59ee09fe') # my api
    authMgr = urllib2.HTTPBasicAuthHandler(passMgr)
    opener = urllib2.build_opener(authMgr)
    urllib2.install_opener(opener)

    response = urllib2.urlopen(req).read()
    print response

import tv
body = "Hi Nick <hr>"
body += tv.output
sendMail("TV listings for %s" % datetime.date.today(),body)
