import datetime

# ISOWEEKDAY
#         1: "Monday",
#         2: "Tuesday",
#         3: "Wednesday",
#         4: "Thursday",
#         5: "Friday",
#         6: "Saturday",
#         7: "Sunday",

def getSNT():
    output, outputDetail = "", ""
    if( datetime.datetime.now().isoweekday() in [2, 5] ):
        output += "There's an SNT meeting at 9:30am today. Vidyo link: https://vidyoportal.cern.ch/flex.html?roomdirect.html&key=eQuolbviCq96Fdc7pGgbcPdIY"

    return output, outputDetail

# print getSNT()
