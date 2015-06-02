# -*- coding: utf-8 -*-
import requests, json
from requests_oauthlib import OAuth1 , OAuth1Session
import pickle, webbrowser, random, string, time, os, sys
from splinter import Browser
from pyvirtualdisplay import Display
from pprint import pprint
# import urllib

"""
This is an attempt to implement a python compatible version of the etrade API using the `requests` library
"""

# import client settings
import etrade_settings
client_Consumer_Key= etrade_settings.client_Consumer_Key
client_Consumer_Secret= etrade_settings.client_Consumer_Secret
sandboxMode = etrade_settings.sandboxMode


def urlRoot():
  """
  returns the root URL for the etrade API depending on sandboxMode <boolean>
  """

  if sandboxMode:
    return 'https://etwssandbox.etrade.com/{}/sandbox/rest/{}.json'
  else:
    return 'https://etws.etrade.com/{}/rest/{}.json'

def getRequestToken():
  """
  Returns a dict containing a pair of temporary token and secret

  """
  request_token_url = '{}/{}/{}'.format('https://etws.etrade.com','oauth','request_token')
  oauth = OAuth1Session(client_key=client_Consumer_Key, 
                        client_secret=client_Consumer_Secret,
                        callback_uri='oob')

  fetch_response = oauth.fetch_request_token(request_token_url)
  resource_owner_key = fetch_response['oauth_token']
  resource_owner_secret = fetch_response['oauth_token_secret']
 

  return fetch_response

def authorizeToken(requestTokenResponse):
  """
  Given a dict requestTokenResponse with the temporary oauth_token and oauth_token_secret,
  we generate a login link that a user should interact with to obtain an authCode <str>
  This process is automated with Splinter and pyvirtualdisplay
  """

  resource_owner_key = requestTokenResponse['oauth_token']
  resource_owner_secret = requestTokenResponse['oauth_token_secret']
  redirect_response = 'https://us.etrade.com/e/t/etws/authorize?key={}&token={}'.format(client_Consumer_Key,resource_owner_key)
  

  # print 'go to this link for authorization:', redirect_response

  # cannot parse redirect_response without a browser because the response is not pure json
  # oauth_response = oauth.parse_authorization_response(redirect_response)

  # Open URL in a new tab, if a browser window is already open.
  # webbrowser.open_new_tab(redirect_response)

  # Display allows the script to run in a linux cloud without a screen
  display = Display(visible=0, size=(1024, 768))
  display.start()


  # create a browser using Splinter library and simulate the workflow of a user logging in
  # various time.sleep(n) is inserted here to make sure login is successful even on slower connections
  with Browser() as browser:
    # Visit URL
    url = redirect_response
    browser.visit(url)
    
    if browser.is_element_present_by_name('txtPassword', wait_time=1):
      
      browser.fill('USER', etrade_settings.username)
      time.sleep(3)


      browser.find_by_name('txtPassword').click()
      
      time.sleep(3)
      # pprint(browser.html)

      browser.fill('PASSWORD', etrade_settings.userpass)
      # Find and click the 'logon' button
      browser.find_by_name('Logon').click()
      time.sleep(3)
      if browser.is_element_present_by_name('continueButton', wait_time=2):
        browser.find_by_name('continueButton').click()

      browser.find_by_value('Accept').click()
      time.sleep(3)
      # authCode = browser.find_by_xpath("//@type='text'").first.value
      authCode = browser.find_by_tag("input").first.value
      time.sleep(3)


  display.stop()
  
  return authCode



  # return redirect_response

def accessToken(requestTokenResponse, verifier = None):
  """
  Using the authCode <str> generated by authorizeToken(), we pass this as verifier <str> 
  and the function returns a dict containing the persistent oauth token and secret
  """
  if verifier is None:
    verifier = raw_input('Paste the login verifier code here: ')

  access_token_url = 'https://etws.etrade.com/oauth/access_token'
  oauth = OAuth1Session(client_key = client_Consumer_Key,
                          client_secret=client_Consumer_Secret,
                          resource_owner_key=requestTokenResponse['oauth_token'],
                          resource_owner_secret=requestTokenResponse['oauth_token_secret'],
                          verifier=verifier)

  oauth_tokens = oauth.fetch_access_token(access_token_url)
  user_access_token = oauth_tokens.get('oauth_token')
  user_access_token_secret = oauth_tokens.get('oauth_token_secret')
  # print oauth_tokens
  return oauth_tokens

def renewAccessToken():
  """
  When the persistent token and secret is expired, the tokens will need to be renewed.
  The function returns a dict containing the renewed persistent oauth token and secret
  """
  url = 'https://etws.etrade.com/oauth/renew_access_token'

  try:
    user_tokens = pickle.load( open( 'user_tokens.p', "rb" ) )
  except IOError:
    # if the token file does not exist, it should be created
    return {'Error': 'user_tokens.p file missing'}


  oauth = OAuth1(client_key = client_Consumer_Key,
                client_secret=client_Consumer_Secret,
                resource_owner_key=user_tokens['oauth_token'],
                resource_owner_secret=user_tokens['oauth_token_secret']
  )

  r = requests.post(url=url, auth=oauth)

  # print r.content
  return r.content

def accessMethod(url, method = 'GET', payload = None):
  """
  This is a generic function that calls for url <str> and method <'GET' or 'POST'>. If using 'POST', a payload <dict> should be supplied
  function returns a dict containing the output of the url called.
  """

  try:
    user_tokens = pickle.load( open( 'user_tokens.p', "rb" ) )
  except IOError:
    # if the token file does not exist, it should be created
    return {'Error': 'user_tokens.p file missing'}


  # print user_tokens, client_Consumer_Key, client_Consumer_Secret


  if method == 'GET':
    oauth = OAuth1(client_key = client_Consumer_Key,
                client_secret=client_Consumer_Secret,
                resource_owner_key=user_tokens['oauth_token'],
                resource_owner_secret=user_tokens['oauth_token_secret']
    )
    r = requests.get(url = url, auth=oauth)
  elif method == 'POST':
    oauth = OAuth1(client_key = client_Consumer_Key,
                client_secret=client_Consumer_Secret,
                resource_owner_key=user_tokens['oauth_token'],
                resource_owner_secret=user_tokens['oauth_token_secret']
    )

    headers = {'Content-Type': 'application/json'}
    # r = requests.post(url = url, auth=oauth, data = json.dumps(payload), headers = headers)
    r = requests.post(url = url, auth=oauth, data = json.dumps(payload), headers = headers)
  else:
    raise "Invalid method: {}, please use only 'GET' or 'POST'".format()

  try:
    result = json.loads(r.text.encode('ascii', 'ignore')  )
  except:
    print 'problem parsing response as json...', r
    result = r.content

  return result

# Accounts

def listAccounts():
  """
  Lists all the accounts of the user. 
  For more info see etrade's documentation
  """
  url = urlRoot().format('accounts','accountlist')
  return accessMethod(url)

def getAccountBalance(AcctNumber):
  """
  Lists all the balance info on an account given an AcctNumber <str>. 
  For more info see etrade's documentation
  """
  url = urlRoot().format('accounts','accountbalance/{}'.format(str(AcctNumber)))
  return accessMethod(url)

def getAccountPositions(AcctNumber):
  """
  Lists all the positions in an account given an AcctNumber <str>. 
  For more info see etrade's documentation
  """
  url = urlRoot().format('accounts','accountpositions/{}'.format(str(AcctNumber)))
  return accessMethod(url)

def getTransactionHistory(AcctNumber):
  """
  Lists all the transaction history in an account given an AcctNumber <str>. 
  For more info see etrade's documentation
  """
  url = urlRoot().format('accounts',(AcctNumber+'/transactions'))
  return accessMethod(url)

def getTransactionDetails(detailsURL):
  """
  Lists details on a specific trade given a URL
  For more info see etrade's documentation
  """
  return accessMethod(detailsURL+'.json')


def getOptionChains(chainType, expirationMonth, expirationYear, underlier, skipAdjusted = True):
  """
  Gets Option Chain information according to an underlier <str> stock/company
  sample usage:
  pprint (getOptionChains(expirationMonth=04,
                          expirationYear=2015,
                          chainType='PUT',
                          skipAdjusted=True,
                          underlier='GOOG'))
  """

  if skipAdjusted:
    skipAdjusted = 'true'
  else:
    skipAdjusted = 'false'

  url = urlRoot().format('market','optionchains') + '?' + \
    'chainType={}&'.format(chainType) + \
    'expirationMonth={}&'.format(expirationMonth) + \
    'expirationYear={}&'.format(expirationYear) + \
    'underlier={}&'.format(underlier) + \
    'skipAdjusted={}'.format(skipAdjusted)

  return accessMethod(url)

def getOptionExpireDate(underlier):
  """
  Returns the expiration date of the most recent option chain for the underlier <str>

  sample usage:
  getOptionExpireDate('GOOG'))
  """
  url = urlRoot().format('market','optionexpiredate') + '?' + \
   'underlier={}'.format(underlier)
  return accessMethod(url)

def lookupProduct(company, assetType ='EQ'):
  """
  assetType <str> can only by EQ for Equity or MF for mutual fund
  company <str> is the ticker of the company

  sample usage:
  lookupProduct('GOOG')

  """
  # 
  url = urlRoot().format('market','productlookup') + '?' + \
   'company={}&'.format(company) + \
   'type={}'.format(assetType)
  print url
  return accessMethod(url)

def getQuote(symbolStringCSV, detailFlag = 'ALL' ):
  """
  Returns the live quote of a single or many companies
  symbolStringCSV <str> is a comma separated value of tickers
  detailFlag <'ALL' or 'INTRADAY'> specifies whether all data is returned or just a subset with intraday

  sample usage:
  getQuote('TVIX, GOOG', detailFlag = 'INTRADAY')

  """
  url = urlRoot().format('market','quote/'+symbolStringCSV) + '?' + \
   'detailFlag={}'.format(detailFlag)
  # print url
  return accessMethod(url)

# Order API

def listOrders(AcctNumber, marker = None):
  """
  Lists all orders made during the day for an accounts given AcctNumber <str>
  marker <str> retreives different pages of orders if the number of orders exceed a certain number.
  For more information on limits, see etrade's documentation

  sample usage:
  pprint(listOrders('35832156'))

  """
  # rather complex, need to parse for useful parts of all orders of the day
  url = urlRoot().format('order','orderlist/{}'.format(AcctNumber))+ '?' + \
   'count={}'.format(25)

  if not(marker is None):
    # if marker is not none then extend the url to include param
    url += '&marker={}'.format(marker)


  # check for marker if it is absent or empty '', then there are no more pages left, API is restrained to return 25 orders max at a time
  resp = accessMethod(url)
  # print resp

  try:
    numOfOrders = resp['GetOrderListResponse']['orderListResponse']['count']
  except:
    numOfOrders = 0

  # print 'number of orders: ', resp['GetOrderListResponse']['orderListResponse']['count']

  if numOfOrders == 0:
    return None
  elif 'marker' in resp['GetOrderListResponse']['orderListResponse']:
    print 'there are more orders'
    marker = resp['GetOrderListResponse']['orderListResponse']['marker']
    resp = resp + listOrders(AcctNumber, marker )
    return resp
  else:
    return resp['GetOrderListResponse']['orderListResponse']['orderDetails']

def previewEquityOrder(AcctNumber, symbol, orderAction, quantity, priceType, 
                        clientOrderId = None,
                        limitPrice = None, 
                        stopPrice = None,
                        allOrNone = False, 
                        reserveOrder = False, 
                        reserveQuantity = None, 
                        marketSession = 'REGULAR',
                        orderTerm = 'GOOD_FOR_DAY',
                        routingDestination = 'AUTO'
                      ):

  """
  Used to stage an order to specify all the order details before actually sending the trade.
  Returns liveParams <dict> required to place the trade and also resp <dict> which are responses from the API regarding the staged trade.
  For example resp might tell you if the trade is staged correctly and free of syntax errors

  For more information, see etrade's documentation

  """

  # generate a 20 alphanum random client order ID, needed later for actual order generation:
  if clientOrderId is None:
    clientOrderId = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(20))

  EquityOrderRequest = {
       "accountId": AcctNumber,

       "symbol": symbol,
       "orderAction": orderAction,
       "clientOrderId": clientOrderId,
       "priceType": priceType, 
       "quantity": quantity,

       "marketSession": marketSession,
       "orderTerm": orderTerm,
       "routingDestination": routingDestination
       
     }

  # special cases for conditional inputs
  if priceType == 'STOP':
    EquityOrderRequest['stopPrice'] = stopPrice
  elif priceType == 'LIMIT':
    EquityOrderRequest['limitPrice'] = limitPrice
  elif priceType == 'STOP_LIMIT':
    EquityOrderRequest['stopPrice'] = stopPrice
    EquityOrderRequest['limitPrice'] = limitPrice

  if reserveOrder == True:
    EquityOrderRequest['reserveOrder'] = 'TRUE'
    EquityOrderRequest['reserveQuantity'] = reserveQuantity


  params = {
   "PreviewEquityOrder": {
    "-xmlns": "http://order.etws.etrade.com",
    'EquityOrderRequest' : EquityOrderRequest
    }
   }

   # sample params used for testing
  # params = {
  #  "PreviewEquityOrder": {
  #    "-xmlns": "http://order.etws.etrade.com",
  #    "EquityOrderRequest": {
  #      "accountId": "83405188",
  #      "stopPrice": "197",
  #      "quantity": "4",
  #      "symbol": "IBM",
  #      "orderAction": "BUY",
  #      "priceType": "STOP",
  #      "marketSession": "REGULAR",
  #      "orderTerm": "GOOD_FOR_DAY",
  #      "clientOrderId": "random123456"
  #    }
  #  }
  # }

  # these are the params needed for placing actual order
  liveParams = {
   "PlaceEquityOrder": {
    "-xmlns": "http://order.etws.etrade.com",
    'EquityOrderRequest' : EquityOrderRequest
    }
   }




  url = urlRoot().format('order','previewequityorder')

  resp = accessMethod(url = url, method = 'POST', payload = params )

  return liveParams, resp

def placeEquityOrder(liveParams):
  """
  liveParams <dict> an dict output generated by previewEquityOrder()
  function actually places the order that was previously staged via previewEquityOrder(), returns a dict that indicates status of trade

  """
  # liveParams should be generated through previewEquityOrder
  url = urlRoot().format('order','placeequityorder')
  resp = accessMethod(url = url, method = 'POST', payload = liveParams )
  return resp

def previewEquityOrderChange(AcctNumber, orderNum, quantity, priceType, 
                        clientOrderId = None,
                        limitPrice = None, 
                        stopPrice = None,
                        allOrNone = False, 
                        reserveOrder = False, 
                        reserveQuantity = None, 
                        orderTerm = 'GOOD_FOR_DAY',
                        **kwargs
                      ):

  """
  For an active order, the order params may be changed. 
  clientOrderId <str> is supplied by the API on the original trade.

  Returns liveParams <dict> required to place the changes trade and also resp <dict> which are responses from the API regarding the staged trade.
  For example resp might tell you if the trade is staged correctly and free of syntax errors.

  For more information, see etrade's documentation
  """
  # generate a 20 alphanum random client order ID, needed later for actual order generation:
  if clientOrderId is None:
    clientOrderId = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(20))

  changeEquityOrderRequest = {
       "accountId": AcctNumber,
       "orderNum": orderNum,

       "clientOrderId": clientOrderId,
       "priceType": priceType, 
       "quantity": quantity,

       "orderTerm": orderTerm,
       
     }

  # special cases for conditional inputs
  if priceType == 'STOP':
    changeEquityOrderRequest['stopPrice'] = stopPrice
  elif priceType == 'LIMIT':
    changeEquityOrderRequest['limitPrice'] = limitPrice
  elif priceType == 'STOP_LIMIT':
    changeEquityOrderRequest['stopPrice'] = stopPrice
    changeEquityOrderRequest['limitPrice'] = limitPrice

  if reserveOrder == True:
    changeEquityOrderRequest['reserveOrder'] = 'TRUE'
    changeEquityOrderRequest['reserveQuantity'] = reserveQuantity

  if allOrNone == False:
    changeEquityOrderRequest['allOrNone'] = 'FALSE'
  else:
    changeEquityOrderRequest['allOrNone'] = 'TRUE'

  params = {
   "previewChangeEquityOrder": {
    "-xmlns": "http://order.etws.etrade.com",
    'changeEquityOrderRequest' : changeEquityOrderRequest
    }
   }

  liveParams = {
   "placeChangeEquityOrder": {
    "-xmlns": "http://order.etws.etrade.com",
    'changeEquityOrderRequest' : changeEquityOrderRequest
    }
   }

  url = urlRoot().format('order','previewchangeequityorder')
  resp = accessMethod(url = url, method = 'POST', payload = params )
  return liveParams, resp

def placeEquityOrderChange(liveParams):
  """
  liveParams <dict> an dict output generated by previewEquityOrderChange()
  function actually places the order change that was previously staged via previewEquityOrderChange(), 
  returns a dict that indicates status of trade

  """
  # liveParams should be generated through previewEquityOrderChange
  url = urlRoot().format('order','placechangeequityorder')
  resp = accessMethod(url = url, method = 'POST', payload = liveParams )
  return resp

def cancelOrder(AcctNumber, orderNum):
  """
  Cancels an active order given an AcctNumber <str> and orderNum <int>.
  The orderNum can be found when the trade is first placed via the output of placeEquityOrder() 
  Returns a dict to indicate whether cancelOrder is successful
  """

  url = urlRoot().format('order','cancelorder')
  params = {
   "cancelOrder": {
     "-xmlns": "http://order.etws.etrade.com",
     "cancelOrderRequest": {
       "accountId": AcctNumber,
       "orderNum": orderNum
     }
   }
 }
  resp = accessMethod(url = url, method = 'POST', payload = params )
  return resp

# Limits API

def getLimits():
  """
  Returns the limits of the API
  """
  url = urlRoot().format('statuses','limits')
  return accessMethod(url)

# Notifications API

def getNotifications():
  """
  Returns messages for developers
  """
  # gets message for developers only, doesn't seem to work on sandbox.
  url = urlRoot().format('notification','getmessagelist')
  return accessMethod(url)

def login():
  """
  Tries to inititate the login process and creates a token for the user
  """
  testState = listAccounts()

  if 'Error' in testState:
    print 'trying to renew token...'
    # try renewing access token first,
    renewAccessToken()
    testState = listAccounts()

  if 'Error' in testState:
  # if testState == {u'Error': {u'message': u'oauth_problem=token_expired'}} or testState == {u'Error': {u'message': u'oauth_problem=token_rejected'}} or testState == {u'Error': {u'message': u'Invalid access token used'}}:
    # if it doesn't work then try manual login process
    print 'trying to manually login... '
    r = getRequestToken()
    authCode = authorizeToken(r)
    oauth_tokens = accessToken(r, verifier = authCode)
    pickle.dump( oauth_tokens, open( 'user_tokens.p', "wb" ) )




if __name__ == "__main__":
  a = 3
  pass
  # etst





