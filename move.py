import os, sys, json, urllib, urllib2
import datetime, calendar
import commands
from dateutil.parser import parse
import delta

# instructions for request:
# open a new tab in chrome
# press F12
# paste and go to url:
# https://maps.google.com/locationhistory/b/0/kml?startTime=1373666400000&endTime=1373752800000
# in developer tools pane, go to network tab and right click on the kml?startTime= entry and get the curl information, paste below and make appropriate modifications

def getData(numDays=1):
    output = ""
    outputDetail = ""


    debugOffset = datetime.timedelta(days=0)
    # start of yesterday
    startTime = 1000*calendar.timegm((datetime.date.today() - datetime.timedelta(days=numDays) - debugOffset).timetuple())
    # start of today
    endTime = 1000*calendar.timegm((datetime.date.today() - debugOffset).timetuple())
    # so this finds movement for yesterday

    req = """
    curl -s "https://maps.google.com/locationhistory/b/0/kml?startTime={0}&endTime={1}" -H "pragma: no-cache" -H "dnt: 1" -H "accept-encoding: gzip,deflate,sdch" -H "accept-language: en-US,en;q=0.8" -H "user-agent: Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36" -H "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" -H "cache-control: no-cache" -H "cookie: __utma=237271068.1314368753.1407135089.1407575073.1407997803.3; __utmz=237271068.1407997803.3.3.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not"%"20provided); PREF=ID=3d023c2d3e1fc702:U=bbe304aaf6d27f56:FF=0:LD=en:TM=1400275580:LM=1400277412:GM=1:S=X9mioYwbSugVHY50; HSID=ADTNJ0fvYHuX8U6nf; SSID=AHd0wwFVxRy8OUgK3; APISID=1wchem-1kDkWXAuF/A5lHRl4OM_OXEA2ho; SAPISID=FgPEldioxBc9II5j/AO6_68zIpj1WqrGpj; SID=DQAAAE8BAADE_RPpBtsGJ7M5-C-VneZfhchwfOMuKMKe4wDe-ThQr22If9z8_dWa2wZA_zd8rvD1eqJUeZzsDT2suaVEECw5Ny0aEL_UDdD63FRpQXETIg_fcxqF9pAvWRR8Mq_fG_Mm3LcJ3yBUUX6QecVWmJiGif4uR5pN2HgYesUK5VvI1qnOKIwa7RHztQCD7z8B8LWHMhh1A_tGbrUjRmnR_1ix5hMqwwUiBiow75DiFNcp4MLJVGMUO7LBVg0OjH3vLGOYzFgwerImx4zcIdFL2TKmSklcnffENXKh0NZdjbrjkdgmkJxppi58uNSG23N4QkPvz-rPpZHUekEKjkf0dZ0xOet_WimU6-wXOXC41xKLUyEDsvXxSu_XQJXnt2vd2Fig7EI19tfuC61DMEPsZU1mFK_v0eYmHWIgnjjkbZXOKuj0tDsNNjDVIwLATVLUTT4; NID=67=dkJEOSQjBF2j_vHEi9fO9R4UbfRp5KMKBk93iBupR9yg6c0C--a-5oOOIunl3aUJIqoA60xU-K9kH-vdtRfaSFEaM_U1y7edr1fNFRWQlKxku0cgsSKwNlQeXQsDhso2k_EMtKTy-aWmWISDJ09tGMd3qbKKbkZ3jW5oGUfnCY0JEpyZxNawGwKM7ue1cQOMSN6mn0KYNcFGae1te-PIuW-upOQps8zLeKynQcTm_NsG-oypHwh0IgTktKplkuDymWuljsvaNNnhfobz3rXXz10cj-X5tkRsSw; S=billing-ui=v75U22CtZbHmrtKxFcw71g:billing-ui-efe=v75U22CtZbHmrtKxFcw71g" -H "x-client-data: CLq1yQEIjbbJAQijtskBCKm2yQEIxLbJAQiehsoBCLiIygEI64jKAQj5k8oB" --compressed
    """.format(startTime, endTime)
    # print req
    req = req.strip()

    status, kml = commands.getstatusoutput(req)


    # print output
    # kml = open("history-08-18-2014.kml","r").read()

    kml = kml.split('\n')
    times = []
    coords = []
    for line in kml:
        if("<when>" in line):
            timeStr = line.strip().replace("<when>","").replace("</when>","")
            times.append(parse(timeStr))
        elif("<gx:coord>" in line):
            coordStr = line.strip().replace("<gx:coord>","").replace("</gx:coord>","")
            coord = coordStr.split(" ")
            coords.append( (float(coord[0]), float(coord[1])) )
        else:
            continue

    if(len(coords) != len(times)): 
        print "ERROR, lengths don't match up", len(coords), len(times)
        print "will continue by using the minimum of the two, but check please"
        
    # print len(coords)
    # print len(times)

    totalDist = 0.0
    sumSpeed = 0.0
    numPoints = min(len(coords), len(times))
    numHops = 0
    for i in range(numPoints)[:-1]:
        p1, p2 = coords[i], coords[i+1]
        t1, t2 = times[i], times[i+1]



        dist = delta.distance(p1,p2)
        speed = delta.speed(p1,p2, t1,t2)

        if(dist > 1.0): continue
        if(speed > 12): continue

        if(dist < 0.02): continue
        if(speed < 0.2): continue

        # print dist, speed, t1, t2

        totalDist += dist
        sumSpeed += speed
        numHops += 1

    if(numHops < 1): numHops = 999999

    output += "Yesterday, you walked a distance of %.1f miles with an average walking speed of %.1f mph." % (totalDist, sumSpeed/numHops)
    outputDetail += "Yesterday, you walked a distance of %.1f miles with an average walking speed of %.1f mph.<br>" % (totalDist, sumSpeed/numHops)
    outputDetail += "There were a total of %i good data points. " % (numHops)
    outputDetail += "You can get the KML file at https://maps.google.com/locationhistory/b/0/kml?startTime=%i&endTime=%i <br>" % (startTime, endTime)
    outputDetail += "The GUI map is at https://maps.google.com/locationhistory/b/0 <br>"

    return output, outputDetail

