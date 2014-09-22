import base64, commands, config

def getBalance():
    u = base64.urlsafe_b64decode(config.barc['u'])
    p = base64.urlsafe_b64decode(config.barc['p'])

    req = """
    curl "https://mybarc.ucsb.edu/SIWeb/login.do" --data "userid=%s&password=%s&submitButton=Student+Login&fromJSP=L&doValidate=true"
    """.strip() % (u, p)

    data = commands.getstatusoutput(req)[1]
    for line in data.split("\n"):
        if "Balance on your account" in line and not "Current" in line:
            balance = line.split(">")[-2].split("<")[0]
            balance = "".join([e for e in balance if e in "0123456789."])
            return balance

def getBARC():
    output = ""
    outputDetail = ""

    balance = float(getBalance())

    if(balance > 0):
        output += "Your BARC balance is <b>%.2f</b>!" % balance

    return output, outputDetail

# print getBARC()
