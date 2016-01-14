import datetime

def getData():
    output, outputDetail = "", ""
    if( datetime.datetime.now().isoweekday() in [2, 5] ): # Tuesday, Friday
        output += "There's an SNT meeting at 9:30am today. Vidyo link: https://vidyoportal.cern.ch/flex.html?roomdirect.html&key=eQuolbviCq96Fdc7pGgbcPdIY"

    return output, outputDetail

if __name__=='__main__':
    print getData()
