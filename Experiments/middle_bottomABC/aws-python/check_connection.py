import boto.mturk.connection

hostlive = 'mechanicalturk.amazonaws.com'
hostsand = 'mechanicalturk.sandbox.amazonaws.com'

#Take in inputs from shell
if __name__ == "__main__":
    import sys
    if len(sys.argv)>1:
        hosttype = sys.argv[1]
    else:
        hosttype = 'sandbox'
else:
    hosttype = 'sandbox'

if hosttype=='live':
    HOST = hostlive
else:  #anything else but 'live' will send to sandbox
    HOST = hostsand


#HOST = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
#HOST = 'mechanicalturk.sandbox.amazonaws.com'
#HOST = 'mechanicalturk.amazonaws.com'

# get mturk connection
mtc = boto.mturk.connection.MTurkConnection(host=HOST)

# just check the balance
print mtc.get_account_balance()
mtc.close()
