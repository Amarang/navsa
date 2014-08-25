import urllib, urllib2, json

def forecast():
    zipcode = 93117
    data = json.loads(urllib.urlopen("http://api.wunderground.com/api/48c1f91829cc66cb/forecast/q/CA/%s.json" % str(zipcode) ).read())

    today = data['forecast']['simpleforecast']['forecastday'][0]
    # print today

    windspeed = int(0.8 * today['avewind']['mph'] + 0.2 * today['maxwind']['mph'])
    winddir = today['avewind']['dir']
    if(len(winddir) == 3): winddir = winddir[0] # turn NNW crap into N since I don't care
    rainfall = float(today['qpf_allday']['in'])
    high, low = today['high']['fahrenheit'], today['low']['fahrenheit']
    conditions = today['conditions']
    conditionsIcon = today['icon_url']

    return windspeed, winddir, high, low, rainfall, conditions, conditionsIcon


def current():
    zipcode = 93117
    data = json.loads(urllib.urlopen("http://api.wunderground.com/api/48c1f91829cc66cb/conditions/q/CA/%s.json" % str(zipcode) ).read())

    # print data
    today = data['current_observation']
    # print today

    windspeed = int(0.8 * float(today['wind_mph']) + 0.2 * float(today['wind_gust_mph']))
    winddir = today['wind_dir']
    if(len(winddir) == 3): winddir = winddir[0] # turn NNW crap into N since I don't care
    temperature = int(today['temp_f'])
    conditions = today['weather']
    conditionsIcon = today['icon_url']

    return windspeed, winddir, temperature, conditions, conditionsIcon


def forecastStr( windspeed, winddir, high, low, rainfall, conditions, conditionsIcon ):
    return "<img src='{4}' /> The wind will be {0}mph{1}. The high for today is {2}F and tonight's low is {3}F.<br>".format(
            windspeed,
            "" if len(winddir) < 1 else " from %s" % winddir,
            high,
            low,
            conditionsIcon
            )

def currentStr( windspeed, winddir, temperature, conditions, conditionsIcon ):
    return "<img src='{3}' /> The wind is currently {0}mph{1}. The temperature is currently {2}F.<br>".format(
            windspeed,
            "" if len(winddir) < 1 else " from %s" % winddir,
            temperature,
            conditionsIcon
            )

def summary( cur, fc ):
    cur_windspeed, cur_winddir, cur_temperature, cur_conditions, cur_conditionsIcon = cur
    fc_windspeed, fc_winddir, fc_high, fc_low, fc_rainfall, fc_conditions, fc_conditionsIcon = fc

    response = ""

    if(fc_rainfall > 0):
        response += "<b>THERE IS A NON-ZERO CHANCE OF RAIN TODAY! You're lookin' at {0} inches, baby!</b><br>".format(fc_rainfall)

    response += "<img src='{1}' />Conditions today will be <b>{0}</b>. ".format(fc_conditions.lower(), fc_conditionsIcon)


    response += "It's {0}F right now, but will get to {1}F today and {2}F tonight. ".format(cur_temperature, fc_high, fc_low)
    # if(cur_windspeed > 16):
    #     response += "It's pretty windy right now ({0}mph). ".format(cur_windspeed)
    # elif(cur_windspeed > 10):
    #     response += "It's moderately windy right now ({0}mph). ".format(cur_windspeed)
    # elif(cur_windspeed > 5):
    #     response += "There's barely any wind right now ({0}mph). ".format(cur_windspeed)
    # else:
    #     response += "Winds are calm. "

    if(fc_windspeed > 16):
        response += "Today will be pretty windy ({0}mph). ".format(fc_windspeed)
    elif(fc_windspeed > 10):
        response += "Today will be moderately windy ({0}mph). ".format(fc_windspeed)
    elif(fc_windspeed > 5):
        response += "There will be barely any wind today ({0}mph). ".format(fc_windspeed)
    else:
        response += "Winds will be calm today. "
    # if(wind
    return response


def getWeather():
    output = ""
    outputDetail = ""

    fc = forecast()
    print "got forecast"
    cur = current()
    print "got current conditions"
    # fc = (11, "WSW", 70, 59, 0.1, "Clear", "url")
    # cur = (5, "WSW", 67, "Clear", "url")
    outputDetail += forecastStr(*fc)
    outputDetail += currentStr(*cur)
    output += summary( cur, fc )
    return output, outputDetail

# main()
