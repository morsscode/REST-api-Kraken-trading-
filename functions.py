#!/usr/bin/env python
# functions based on krakenex


import krakenex
import decimal
import time

k = krakenex.API()
k.load_key('kraken.key')  #load


def openOrderId():   # function that returns the open order id
    th = k.query_private('OpenOrders', data={'trades': 'True'})
    time.sleep(.25)
    res = th['result']['open']
    for b in res:
        id = b
    return id


def openOrderPrice():   # function that returns the open order price +1 api call
    th = k.query_private('OpenOrders', data={'trades': 'True'})
    time.sleep(.25)
    res = th['result']['open']
    for b in res:
        id = b
    trade = res[id]
    discrip = trade['descr']
    price = discrip['price']
    return float(price)


def closedOrderId():   # function that returns the open order id
    th = k.query_private('ClosedOrders')
    time.sleep(.25)
    #res = th['result']['open']
    print(th)
    #for b in res:
     #   id = b
    #return id


def cancelOrder():  # cancel the current open order
    k.query_private('CancelOrder', data={'txid': openOrderId()})



def trades():
    th = k.query_private("QueryTrades", data={"txid": '2'})
    print(th)


def tickerData(pair, query, listNum):  # input pair and query as string and listnum as num in array you wish to grab
    ret = k.query_public('Ticker', data = {'pair': pair})
    result = ret['result']
    resultPair = result[pair]
    average = resultPair[query]
    averageLast24 = average[listNum]
    return averageLast24


def lastTradePrice(pair):  # input pair and query as string and listnum as num in array you wish to grab
    ret = k.query_public('Ticker', data={'pair': pair})
    result = ret['result']
    resultPair = result[pair]
    average = resultPair['c']
    lastprice = average[0]
    print('last price ' + str(pair) + ' ' + str(lastprice))
    return float(lastprice)


def updateeth():
    #   grab balance list
    balanceSheet = k.query_private('Balance')
    #   grab result from balance
    totalBalance = balanceSheet['result']
    #   grab actual balance number
    x = totalBalance["XETH"]
    return 0.996 * float(x)  # leave 0.4% fee buffer


# function that returns current amount of USD
def updateusd():
    #   grab balance list
    balanceSheet = k.query_private('Balance')
    # grab result from balance
    totalBalance = balanceSheet['result']
    #   grab actual balance number
    x = totalBalance["ZUSD"]
    return float(x)  # leave 0.4% fee buffer


def spread(pair):   # returns tuple with current spread as number and percentage
    x = openOrderPrice()
    y = lastTradePrice(pair)
    spread = x - y
    spreadPercent = 100*spread/x
    return spread, spreadPercent

#lastTradePrice('XZECZUSD')
#(x, y) = spread('XXRPZUSD')
#print('spread = ' + str(x) + ' = ' + str(y) + ' percent')
#print(tickerData('XZECZUSD', 'p', 1))
#closedOrderId()
print(lastTradePrice('XXRPZUSD'))