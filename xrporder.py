#!/usr/bin/env python3

# This file is part of krakenex.
# Licensed under the Simplified BSD license. See `examples/LICENSE.txt`.

import krakenex
import time

k = krakenex.API()
k.load_key('kraken.key')


# the price to sell asset at so if pair: XXRPZUSD and price: 1 and volume: 2
# this means sell 2 xrp at price $1 per XRP

def xrpBuy(price, volume):
    global lastOrder
    global  las
    k.query_private('AddOrder',
                         {'pair': 'XXRPZUSD',  # pair = buy/sell so XXRPZUSD @ buy means buy XXRP with ZUSD
                          'type': 'buy',  # buy or sell
                          'ordertype': 'limit',  # market  or limit
                          'price': price,  # the price to buy asset at
                          'volume': volume})  # number of currency



def xrpSell(price, volume):
    k.query_private('AddOrder',
                         {'pair': 'XXRPZUSD',  # pair = buy/sell so XXRPZUSD @ sell means sell XXRP for ZUSD
                          'type': 'sell',  # buy or sell
                          'ordertype': 'limit',  # market  or limit
                          'price': price,  # the price to sell asset at
                          'volume': volume})  # number of currency



def openOrderId():   # function that returns the open order id
    th = k.query_private('OpenOrders', data={'trades': 'True'})
    time.sleep(.25)
    res = th['result']['open']
    for b in res:
        openid = b
    return openid


def cancelOrder():  # cancel the current open order
    k.query_private('CancelOrder', data={'txid': openOrderId()})


cancelOrder()
