import bs4, urllib, re, time, config
from datetime import datetime
from datetime import timedelta

def getData():
    timeInterval = config.facebook['timeInterval']
    notifications = []
    output, outputDetail = "", ""
    numNotifications = 0
    # timeInterval = 9.5
    """ go to http://www.facebook.com/notifications and click on
    Get notifications via RSS """
    url = config.facebook['rss']
    fbxml = bs4.BeautifulSoup(urllib.urlopen(url).read())
    print "got fb xml"
    currentdate = datetime.now()
    for i, item in enumerate(fbxml.rss.channel.findAll("item")):
    
        timestamp = re.search("\<pubdate>([A-Za-z,:0-9 ]+)-",str(item.pubdate))
        timestamp = timestamp.group(1).rstrip()
        notificationdate = datetime.strptime(timestamp, '%a, %d %b %Y %X')
        
        if (currentdate - notificationdate).seconds > timeInterval*60*60:
            break 

        numNotifications += 1
        
        desc = re.sub('<[^<]+?>', '', str(item.description))
        desc = desc.replace("&#039;","'")
        for s in ["\n","\r"]:
            desc = desc.replace(s,"")
        
        desc = desc.split("CDATA[")[-1].split("]]")[0]
        notifications.append( desc )
       
    if(numNotifications > 0):
        output += "You got %i facebook notification%s since midnight:" % (numNotifications, 's' if numNotifications > 1 else '')
        for notification in notifications:
            output += "<ul>"
            output += "<li>%s</li>" % notification
            output += "</ul>"
        # outputDetail += "Facebook notifications in past %.1f hours" % (timeInterval)
        # for notification in notifications:
            # outputDetail += "\n\t- %s" % (notification)
    return output, outputDetail

if __name__=='__main__':
    print getData()
