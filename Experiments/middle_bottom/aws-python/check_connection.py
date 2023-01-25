import boto.mturk.connection

# HOST = 'mechanicalturk.sandbox.amazonaws.com'
HOST = 'mechanicalturk.amazonaws.com'

# get mturk connection
mtc = boto.mturk.connection.MTurkConnection(host=HOST)

# just check the balance
print mtc.get_account_balance()
mtc.close()