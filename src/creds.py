import os

#angel setup
username = os.environ.get('angel_username')
password = os.environ.get('angel_passwd')
api_key = os.environ.get('angel_apikey')
token = os.environ.get('angel_token')
feed_token = None
token_map = None

#stock info
portfolio_stk = os.environ.get('PORTFOLIO_STOCKS')
watchlist_stk = os.environ.get('WATCHLIST_STOCKS')

#twilio setup
account_sid = os.environ.get('account_sid')
auth_token = os.environ.get('auth_token')
#to_ph = os.environ.get('to_ph')
to_both = ['+917893514424','+918688277081']
to_only = '+917893514424'
from_ph = os.environ.get('from_ph')
messaging_service_sid = os.environ.get('msessaging_service_sid')
content_template_sid = os.environ.get('content_template_sid')
