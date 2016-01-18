import urllib, urllib2, datetime, json

# NAVSA - Not A Very Sophisticated Assistant
def sendMail(subject, body):
    url = 'https://api.mailgun.net/v2/sandbox96042724eeb049af864d017016a510a3.mailgun.org/messages'
    body = body.encode('utf-8')
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

moduleNames = [ "weather", "tv", "tpb", "barc", "move", "snt", "fb", "arxiv", "debit" ]
# moduleNames = [ "weather", "tpb", "barc", "snt", "fb", "arxiv", "debit" ]
data = {}

for moduleName in moduleNames:
    try:
        module = __import__("modules.%s" % moduleName, fromlist=[''])
        output, outputDetail = module.getData()
        data[moduleName] = [output,outputDetail]
        print "got %s" % moduleName
    except:
        print "[warning] couldn't get %s" % moduleName

sep = "<br>"
body = "Hi Nick,"+sep*2

summaries = ["weather", "tv", "tpb", "barc", "snt", "arxiv", "debit", "fb", "move"]
details = ["tv", "tpb", "arxiv", "barc", "snt", "debit", "fb", "move"]
for summary in summaries:
    try:
        text = data[summary][0]
        if len(text) > 1:
            body += sep*2
        body += text
    except:
        print "[warning] couldn't get summary for %s" % summary

# salutation
body += sep*2
body += "Cheers,"+sep+"NAVSA"
body += sep*5
body += "<hr>"

for detail in details:
    try:
        text = data[detail][1]
        if len(text) > 1:
            body += sep*2
        body += text
    except:
        print "[warning] couldn't get details for %s" % detail


if sendMail("Status update for %s" % datetime.date.today(),body):
    print "email sent successfully!"
else:
    print "ERROR sending email"

# sendMail("test","testbody")
