# etradePythonAPI

Applying machine learning methods to investing could be a fun thing to do, but there are barriers for investors even if they are well versed in Python. It is quite difficult to implement SciPy or NumPy models when most of the brokerage houses only provide APIs with Java or C++ examples. This is an open source library I've written that allows easy integration with Etrade's API for those investors who are looking to write programs in Python.

## Before initial use:
  * Edit settings file in etrade_settings.py
  * Request a consumer key and secret key from etrade

## Example workflow:
```
import etradepy as et
et.Login()
et.listAccounts()
```

## Functions available (work in progess):
listAccounts()
  * Lists all the accounts of the user. 
  * For more info see etrade's documentation

getAccountBalance(AcctNumber)

getAccountPositions(AcctNumber)

getTransactionHistory(AcctNumber)

getTransactionDetails(detailsURL)

getOptionChains(chainType, expirationMonth, expirationYear, underlier, skipAdjusted = True)

getOptionExpireDate(underlier)

lookupProduct(company, assetType ='EQ')

getQuote(symbolStringCSV, detailFlag = 'ALL' )

listOrders(AcctNumber, marker = None)

previewEquityOrder(AcctNumber, symbol, orderAction, quantity, priceType, 
                        clientOrderId = None,
                        limitPrice = None, 
                        stopPrice = None,
                        allOrNone = False, 
                        reserveOrder = False, 
                        reserveQuantity = None, 
                        marketSession = 'REGULAR',
                        orderTerm = 'GOOD_FOR_DAY',
                        routingDestination = 'AUTO',
                        *args,
                        **kwargs
                      )

placeEquityOrder(liveParams)

previewEquityOrderChange(AcctNumber, orderNum, quantity, priceType, 
                        clientOrderId = None,
                        limitPrice = None, 
                        stopPrice = None,
                        allOrNone = False, 
                        reserveOrder = False, 
                        reserveQuantity = None, 
                        orderTerm = 'GOOD_FOR_DAY',
                        *args,
                        **kwargs
                      )

placeEquityOrderChange(liveParams)

cancelOrder(AcctNumber, orderNum)

## Authentication / Non-trading related methods (work in progess):

getLimits()

getNotifications()

login()


