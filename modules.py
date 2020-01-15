#!/usr/bin/env python


import krakenex

import decimal
import time

k = krakenex.API()
k.load_key('kraken.key')

# This programm uses Krakenx https://github.com/veox/python3-krakenex

#   this programm profits off volatility trading a coin back and forth on the Kraken exchange
#   does not currently adjust price target and as such programm will get hung on consistent trends or a price adjustment
#   profits off a coin with stable price and high frequency volatility
#   no api rate limiting currently but program sleeps should keep within allowance for tier 2


#   global variables
#   not implemented variables: lastc
numUsd = 0
numXrp = 0
numZec = 0
margin = 0.005  # desired profit margin as a decimal percent i.e. 0.5% = 0.005
fee = 0.0016  # transaction fee (assumes always placing maker orders and never taker)
totalMargin = 1 + margin + fee  # total trading margin
lastPriceBuyXrpUsd = 0.43  # last price bought USD at i.e number of USD for 1 XRP
lastPriceUsdXpr = 0  # last price bought XRP at i.e number of xrp for 1 USD
#lastOrder = ""


#   functions. need to be moved to another file


#   function to update all values to current balance in account. leaves 1% as fee buffer
#   note: buffer may be unnecessary if fee always applied to base currency. need to test
#   uses global variables
def updatebalance():
    #   grab balance list
    balanceSheet = k.query_private('Balance')
    # grab result from balance
    totalBalance = balanceSheet['result']
    # grab usd from balance
    global numUsd
    numUsd = 0.99 * totalBalance['ZUSD']
    # grab xrp from balance
    global numXrp
    numXrp = 0.99 * totalBalance["XXRP"]
    #   grab zec from balance
    global numZec
    numZec = 0.99 * totalBalance["XZEC"]


# function that returns current amount of USD
def updateusd():
    #   grab balance list
    balanceSheet = k.query_private('Balance')
    # grab result from balance
    totalBalance = balanceSheet['result']
    #   grab actual balance number
    x = totalBalance["ZUSD"]
    return 0.99 * x  # leave 1% fee buffer


# function that returns current amount of XRP
def updatexrp():
    #   grab balance list
    balanceSheet = k.query_private('Balance')
    #   grab result from balance
    totalBalance = balanceSheet['result']
    #   grab actual balance number
    x = totalBalance["XXRP"]
    return 0.99 * x  # leave 1% fee buffer


# function that returns current amount of ZEC
def updatezec():
    #   grab balance list
    balanceSheet = k.query_private('Balance')
    #   grab result from balance
    totalBalance = balanceSheet['result']
    #   grab actual balance number
    x = totalBalance["XZEC"]
    return 0.99 * x  # leave 1% fee buffer


def lastOrderIDAndPair():   # function that returns the ordertxid of last order and the traded pair
    th = k.query_private('TradesHistory')
    time.sleep(.25)
    res = th['result']
    trades = res['trades']
    order = trades['TDL5IO-H2WGZ-C3DSIR']
    orderID = order['ordertxid']
    type = order['pair']
    return orderID, type    # returns tuple with ID and pair type (buy/sell)


def lastOrderID():   # function that returns the ordertxid
    th = k.query_private('TradesHistory')
    time.sleep(.25)
    res = th['result']
    trades = res['trades']
    order = trades['TDL5IO-H2WGZ-C3DSIR']
    orderID = order['ordertxid']
    return orderID   # returns ID


def lastOrderPair():   # function that returns the traded pair
    th = k.query_private('TradesHistory')
    time.sleep(.25)
    res = th['result']
    trades = res['trades']
    order = trades['TDL5IO-H2WGZ-C3DSIR']
    type = order['pair']
    return type    # returns pair type (buy/sell)


def placeOrder():
    global lastPriceBuyXrpUsd
    global totalMargin
    lastOrder = lastOrderPair()
    if lastOrder == 'ZUSDXXRP':
        volume = updateusd()/lastPriceBuyXrpUsd
        xrpBuy(lastPriceBuyXrpUsd, volume)
    elif lastOrder == 'XXRPZUSD':
        sellPrice = totalMargin*lastPriceBuyXrpUsd
        volume = updatexrp()/sellPrice
        xrpSell(sellPrice, volume)


def openOrders():
    # prepare request
    req_data = {'docalcs': 'true'}
    # query servers
    open_positions = k.query_private('OpenPositions', req_data)
    total = len(open_positions['result'])
    return total


def xrpBuy(price, volume):
    global lastOrder
    k.query_private('AddOrder',
                         {'pair': 'XXRPZUSD',  # pair = buy/sell so XXRPZUSD @ buy means buy XXRP with ZUSD
                          'type': 'buy',  # buy or sell
                          'ordertype': 'limit',  # market  or limit
                          'price': price,  # the price to buy asset at
                          'volume': volume})  # number of currency


def xrpSell(price, volume):
    k.query_private('AddOrder',
                         {'pair': 'ZUSDXXRP',  # pair = buy/sell so XXRPZUSD @ sell means sell XXRP for ZUSD
                          'type': 'sell',  # buy or sell
                          'ordertype': 'limit',  # market  or limit
                          'price': price,  # the price to sell asset at
                          'volume': volume})  # number of currency