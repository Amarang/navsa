import urllib
import urllib2

def sendMail(subject, body):
    url = 'https://api.mailgun.net/v2/samples.mailgun.org/messages'
    values = {
    'to' : 'typhoid.pwns@gmail.com',
    # 'subject' : 'Status Update',
    # 'text' : 'test text\n\t\t\ttest \ttext<b>test</b><i>test2</><br>test3',
    'subject' : subject,
    # 'text' : body,
    # 'html' : '<b>test</b><br><i>test2</i>',
    'html' : body,
    'from': ' HelperBot <bot@samples.mailgun.org>',
    }

    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    passMgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passMgr.add_password(None, url, 'api', 'key-3ax6xnjp29jd6fds4gc373sgvjxteol0')
    authMgr = urllib2.HTTPBasicAuthHandler(passMgr)
    opener = urllib2.build_opener(authMgr)
    urllib2.install_opener(opener)

    response = urllib2.urlopen(req).read()
    print response

# sendMail("statusupdate2","test<br> <p style='text-indent:24pt'>test2</p>")

import parser
body = "Hi Nick <hr>"
body += parser.output
sendMail("statusupdate2",parser)
