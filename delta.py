import math
from dateutil.parser import parse

radiusEarth = 3956.547 # miles
def distance(p1, p2):
    lat1, long1 = p1
    lat2, long2 = p2
    milesPerDegLat = math.pi*radiusEarth/180.0
    milesPerDegLong = 2.0*math.pi*radiusEarth*math.cos(lat1*math.pi/180.0)/360.0

    dx = abs(long2-long1)*milesPerDegLong
    dy = abs(lat2-lat1)*milesPerDegLat

    return math.sqrt(dx**2 + dy**2)

def speed(p1, p2, t1, t2):
    dx = distance(p1, p2)
    dt = 1.0*(t2-t1).seconds / 3600.0
    if(dt < 0.01): dt = 10000.0
    return dx/dt # miles per hour

    
# p1 = -119.8466145,34.4127158
# p2 = -119.8467415,34.4127081
# t1 = parse("2014-08-23T12:44:35.285-07:00")
# t2 = parse("2014-08-23T12:45:20.290-07:00")

# print distance(p1, p2)
# print speed(p1, p2, t1, t2)



            # <when>2014-08-23T12:44:35.285-07:00</when>
            # <gx:coord>-119.8466145 34.4127158 -15</gx:coord>
            # <when>2014-08-23T12:45:20.290-07:00</when>
            # <gx:coord>-119.8467415 34.4127081 -10</gx:coord>


