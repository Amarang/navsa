import base64, commands, config

def getBalance():
    u = base64.urlsafe_b64decode(config.barc['u'][::-1])
    p = base64.urlsafe_b64decode(config.barc['p'][::-1])

    req = """
    curl "https://mybarc.ucsb.edu/SIWeb/login.do" --data "userid=%s&password=%s&submitButton=Student+Login&fromJSP=L&doValidate=true"
    """.strip() % (u, p)

    data = commands.getstatusoutput(req)[1]
    for line in data.split("\n"):
        if "Balance on your account" in line and not "Current" in line:
            balance = line.split(">")[-2].split("<")[0]
            balance = "".join([e for e in balance if e in "-0123456789."])
            return balance

def getBARC():
    output = ""
    outputDetail = ""

    balance = float(getBalance())

    # offset gives me the ability to handle tuition not being paid for weeks upon weeks
    offset = float(config.barc['offset'])

    if(offset > 0):
        balance -= offset

        if(balance > 0):
            output += "Your BARC balance (subtracting offset of %.2f) is <b>$%.2f</b>!" % (offset, balance)
        elif(balance < 0):
            output += "Your BARC balance was paid off. You are now at <b>$%.2f</b> (defined offset is %.2f)!" % (balance+offset, offset)
        else: 
            pass

    else:
        if(balance > 0):
            output += "Your BARC balance is <b>$%.2f</b>!" % balance

    outputDetail += "Your BARC balance is <b>$%.2f</b> with an offset of %.2f." % (balance, offset)

    return output, outputDetail

# print getBARC()
