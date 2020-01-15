#!/usr/bin/env python


import krakenex
import decimal
import time
import math

k = krakenex.API()
k.load_key('kraken.key')

# This programm uses Krakenx https://github.com/veox/python3-krakenex

#   this programm profits off volatility trading a coin back and forth on the Kraken exchange
#   does not currently adjust price target and as such programm will get hung on consistent trends or a price adjustment
#   profits off a coin with stable price and high frequency volatility
#   no api rate limiting currently but program sleeps should keep within allowance for tier 2


#   global variables
#   not implemented variables:
margin = 0.00025  # desired profit margin as a decimal percent i.e. 0.5% = 0.005
fee = 0.0032  # transaction fee (assumes always placing maker orders and never taker) double actual fee
# as 2 transactions required
totalMargin = float(1 + margin + fee)  # total trading margin with 1 added so it acts as multiplier
lastPriceBuyCryptoUsd = 0.52649  # last price bought USD at i.e number of USD for 1 XRP
# lastPriceUsdXpr = 0  # last price bought XRP at i.e number of xrp for 1 USD
lastOrderType = ""  # currently must set this to correct value every time


#   functions. need to be moved to another file


def truncate(number, digits) -> float:
    stepper = pow(10.0, digits)
    return math.trunc(stepper * number) / stepper


# function that returns current amount of USD
def updateusd():
    #   grab balance list
    balanceSheet = k.query_private('Balance')
    # grab result from balance
    totalBalance = balanceSheet['result']
    #   grab actual balance number
    x = totalBalance["ZUSD"]
    return float(x)  # leave 0.4% fee buffer


# function that returns current amount of XRP
def updatexrp():
    #   grab balance list
    balanceSheet = k.query_private('Balance')
    #   grab result from balance
    totalBalance = balanceSheet['result']
    #   grab actual balance number
    x = totalBalance["XXRP"]
    return 0.9965 * float(x)  # leave 0.4% fee buffer


# function that returns current amount of ZEC
def updatezec():
    #   grab balance list
    balanceSheet = k.query_private('Balance')
    #   grab result from balance
    totalBalance = balanceSheet['result']
    #   grab actual balance number
    x = totalBalance["XZEC"]
    return 0.996 * float(x)  # leave 0.4% fee buffer


def updateeth():
    #   grab balance list
    balanceSheet = k.query_private('Balance')
    #   grab result from balance
    totalBalance = balanceSheet['result']
    #   grab actual balance number
    x = totalBalance["XETH"]
    return 0.9969 * float(x)  # leave 0.4% fee buffer


# currently brokenish. doesnt look at last closed order. goes by amount of usd in account
def checklastOrdertype():  # function that returns the order type
    global lastOrderType
    cash = float(updateusd())
    if cash > 10:
        lastOrderType = "sell"
    else:
        lastOrderType = "buy"


def cryptoBuy(pair, price, volume):
    global lastOrderType
    global lastPriceBuyCryptoUsd
    truncnum = 2
    if pair == 'XXRPZUSD':
        truncnum = 5
    elif pair == 'XETHZUSD':
        truncnum = 2
    elif pair == 'XZECZUSD':
        truncnum = 2
    k.query_private('AddOrder',
                    {'pair': pair,  # pair = buy/sell so XXRPZUSD @ buy means buy XXRP with ZUSD
                     'type': 'buy',  # buy or sell
                     'ordertype': 'limit',  # market  or limit
                     'price': truncate(price, truncnum),  # the price to buy asset at
                     'volume': truncate(volume, 8)})  # number of currency
    lastOrderType = 'buy'
    lastPriceBuyCryptoUsd = truncate(price, truncnum)


def cryptoSell(pair, price, volume):
    global lastOrderType
    truncnum = 0
    if pair == 'XXRPZUSD':
        truncnum = 5
    elif pair == 'XETHZUSD':
        truncnum = 2
    elif pair == 'XZECZUSD':
        truncnum = 2

    k.query_private('AddOrder',
                    {'pair': pair,  # pair = buy/sell so XXRPZUSD & sell means sell XXRP for ZUSD
                     'type': 'sell',  # buy or sell
                     'ordertype': 'limit',  # market  or limit
                     'price': truncate(price, truncnum),  # the price to sell asset at
                     'volume': truncate(volume, 8)})  # number of currency
    lastOrderType = 'sell'


def placeOrder(pair):
    global lastPriceBuyCryptoUsd
    global totalMargin
    global lastOrderType
    global curPair
    volumesell = 0
    lastPriceBuyCryptoUsd = float(lastPriceBuyCryptoUsd)
    if lastOrderType == 'sell':
        x = float(average24(pair))
        print('24 hour average = ' + str(x))
        y = float(lastTradePrice(pair))
        print('current price = ' + str(y))
        if y < x:
            print('current price below 24 hour average')
            print('placing limit at current price ')
            lastPriceBuyCryptoUsd = 0.99985 * y
        else:
            print('current price above 24 hour average = ' + str(x))
            print('placing limit at 24 hour + current average price with double weight on current')
            lastPriceBuyCryptoUsd = ((x + (y * 2.0)) / 3.0)
            print(lastPriceBuyCryptoUsd)
        volumebuy = float(updateusd()) / float(lastPriceBuyCryptoUsd)
        cryptoBuy(curPair, lastPriceBuyCryptoUsd, volumebuy)
        print('limit buy order placed for ' + str(volumebuy) + ' ' + curPair + ' at ' + str(
            lastPriceBuyCryptoUsd) + ' per ' + curPair)
    elif lastOrderType == 'buy':
        sellPrice = (totalMargin * float(lastPriceBuyCryptoUsd))
        x = lastTradePrice(pair)
        if x > sellPrice:
            sellPrice = (x * 1.0001)
        if pair == 'XXRPZUSD':
            volumesell = updatexrp()
        elif pair == 'XETHZUSD':
            volumesell = updateeth()
        elif pair == 'XZECZUSD':
            volumesell = updatezec()
        #volumesell = 0  # *(totalMargin*lastPriceBuyXrpUsd)fgn
        cryptoSell(curPair, sellPrice, volumesell)
        print('limit sell order placed to sell ' + str(truncate(volumesell, 8)) + ' ' + curPair + ' at ' + str(
            truncate(sellPrice, 5)) + ' per ' + str(pair))


def openOrders():
    # query servers
    open_orders = k.query_private('OpenOrders')
    res = open_orders['result']
    op = res['open']
    if op == {}:
        return False
    else:
        return True


def average24(pair):  # input pair and query as string and listnum as num in array you wish to grab
    ret = k.query_public('Ticker', data={'pair': pair})
    result = ret['result']
    resultPair = result[pair]
    average = resultPair['p']
    averageLast24 = average[1]
    return averageLast24


def lastTradePrice(pair):  # input pair and query as string and listnum as num in array you wish to grab
    ret = k.query_public('Ticker', data={'pair': pair})
    result = ret['result']
    resultPair = result[pair]
    average = resultPair['c']
    lastprice = average[0]
    # print('last price ' + str(pair) + ' ' + str(lastprice))
    return float(lastprice)


def openOrderPrice():  # function that returns the open order price, +1 api call
    th = k.query_private('OpenOrders', data={'trades': 'True'})
    time.sleep(.25)
    res = th['result']['open']
    for b in res:
        id = b
    trade = res[id]
    discrip = trade['descr']
    price = discrip['price']
    return float(price)


def spread(pair):  # returns tuple with current spread as number and percentage
    x = openOrderPrice()
    y = lastTradePrice(pair)
    spread = x - y
    spreadPercent = 100 * spread / x
    return spread, spreadPercent


def openOrderId():  # function that returns the open order id
    th = k.query_private('OpenOrders', data={'trades': 'True'})
    time.sleep(.25)
    res = th['result']['open']
    for b in res:
        openid = b
    return openid


def cancelOrder():  # cancel the current open order
    k.query_private('CancelOrder', data={'txid': openOrderId()})


# end functions


# main function, checks to see if open order. if yes sleeps, if not places order
counter = 0

curPair = 'XXRPZUSD'
while True:
    if openOrders():
        if counter % 10 == 0:  # display current spread first time and every 10th time
            (x, y) = spread(curPair)
            print('order current... spread = ' + str(truncate(x, 5)) + ' = ' + str(truncate(y, 5)) + '%')
        counter = counter + 1
        time.sleep(6)
    else:
        checklastOrdertype()
        print('last order type = ' + lastOrderType)
        counter = 0
        print("no current order")
        print("placing order")
        placeOrder(curPair)
        time.sleep(3)
