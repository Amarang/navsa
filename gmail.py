import base64, commands, config, gmaillib

# https://github.com/thedjpetersen/gmaillib

account = gmaillib.account(config.gmail['u'], config.gmail['p'])
msgs = account.inbox(start=0,amount=10)
print msgs
print msgs[0]
print msgs[1]

