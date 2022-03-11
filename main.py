from multipledispatch import dispatch
from wazirx_sapi_client.rest import Client
import time
import os

# print(os.environ.get(''))
client = Client(api_key=os.environ.get('wazirx_api_key'),
                secret_key=os.environ.get('wazirx_secret_key'))


@dispatch()
def getfunds():
    request = client.send('funds_info', {'timestamp': int(time.time()*1000)})
    if request[0] == 200:
        funds = list(filter(lambda x: float(
            x['free'])+float(x['locked']) != 0, request[1]))
        return funds
    else:
        print(request[0])


@dispatch(str)
def getfunds(token):
    funds = getfunds()
    return sum(float(i['free'])+float(i['locked']) for i in funds if i['asset'] == token)


def getprice(token):
    return float(client.send('ticker', {'symbol': token+'inr'})[1]['lastPrice'])


def gettokens():
    funds = getfunds()
    tokens = [i['asset'] for i in funds]
    return tokens


def getorders(token):
    request = client.send(
        'all_orders', {'symbol': token+'inr', 'timestamp': int(time.time()*1000)})
    if request[0] == 200:
        orders = list(filter(lambda x: x['status'] != 'cancel', request[1]))
        return orders
    else:
        raise Exception(request[0])


def getbuyorders(token, onlydone=True):
    orders = getorders(token)
    if onlydone:
        buyorders = list(
            filter(lambda x: x['side'] == 'buy' and x['status'] == 'done', orders))
    else:
        buyorders = list(filter(lambda x: x['side'] == 'buy', orders))
    return buyorders


def getsellorders(token, onlydone=True):
    orders = getorders(token)
    if onlydone:
        sellorders = list(
            filter(lambda x: x['side'] == 'sell' and x['status'] == 'done', orders))
    else:
        sellorders = list(filter(lambda x: x['side'] == 'sell', orders))
    return sellorders


def totalbought(token):
    buyorders = getbuyorders(token)
    totalbought = sum([float(i['price'])*float(i['executedQty'])
                      for i in buyorders])
    return totalbought


def buyingaverage(token):
    buyorders = getbuyorders(token)
    buyingaverage = sum([float(i['price']) for i in buyorders])/len(buyorders)
    return buyingaverage


def totalsold(token):
    sellorders = getsellorders(token)
    totalsold = sum([float(i['price'])*float(i['executedQty'])
                    for i in sellorders])
    return totalsold


def sellingaverage(token):
    sellorders = getsellorders(token)
    sellingaverage = sum([float(i['price'])
                         for i in sellorders])/len(sellorders)
    return sellingaverage


def profit(token):
    return totalsold(token) - totalbought(token) + getfunds(token)*getprice(token)


print(profit('sol'))
