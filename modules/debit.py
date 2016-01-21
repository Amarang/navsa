import re, base64, commands, config, gmaillib
from dateutil.parser import parse
import datetime

# https://github.com/thedjpetersen/gmaillib

def getAmounts(body):
        s = re.findall( r'Amount: \$([0-9\-\.\,]+)', body)
        values = []
        try:
            if s: values = map(lambda x: float(x.replace(",","")),s)
        except: pass
        return values

def getData():
    account = gmaillib.account(config.gmail['u'], config.gmail['p'])
    msgs = account.inbox(start=0,amount=10)
    transactions = []
    # print msgs
    for msg in msgs:

        try:
            if "alerts@info.capitalone.com" not in msg.sender_addr: continue
        except:
            continue

        debOrCred = None

        if "recent withdrawal" in msg.subject and "Transaction type: DEBIT POSTED" in msg.body: debOrCred = "debit"
        elif "direct deposit" in msg.subject and "Transaction type: ACH CREDIT" in msg.body: debOrCred = "credit"
        else: continue

        amounts = getAmounts(msg.body)
        date = parse(msg.date).replace(tzinfo=None)
        today = datetime.datetime.now()
        yesterday = (today-date).days == 0

        if len(amounts) < 1: continue

        if not yesterday: continue

        for amount in amounts:
            transactions.append( {"type": debOrCred, "amount": amount, "time": date} )


    output, outputDetail = "", ""
    if len(transactions) > 0:
        totDebits = 0.0
        totCredits = 0.0

        outputDetail += "Transaction details from yesterday (%s):" % (transactions[0]["time"].strftime("%m/%d/%y"))
        outputDetail += "<ul>"
        for trans in transactions:
            if trans["type"] == "debit": totDebits += trans["amount"]
            elif trans["type"] == "credit": totCredits += trans["amount"]
            outputDetail += "<li><b>%s</b> [%s]: %.2f</li>" % (trans["type"][:3].upper(), trans["time"].strftime("%I:%M%p"), trans["amount"])
        outputDetail += "</ul>"

        output += "Yesterday, you "
        if totDebits > 0 and totCredits > 0:
            output += "spent <font color='red'>$%.2f</font> and gained <font color='green'>$%.2f</font>." % (totDebits, totCredits)
        elif totDebits > 0:
            output += "<font color='red'>spent $%.2f.</font>" % totDebits
        elif totCredits > 0:
            output += "<font color='green'>gained $%.2f.</font>" % totCredits
        if totDebits > 50:
            output += "<br><b><font color='red'>Damn! You spent more than $50 yesterday!</font></b>"

    return output, outputDetail

if __name__=='__main__':
    print getData()
