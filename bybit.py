import keys

from pybit.unified_trading import HTTP
import time

test = False

# Definition of the account
if not test:
    session = HTTP(api_key = keys.bybitPKey, api_secret = keys.bybitSKey)
else:
    session = HTTP(testnet = True, api_key = keys.testbybitPKey, api_secret = keys.testbybitSKey)

# All requests will return a dictionnary containing retCode, retMsg, result, retExtInfo, time
# In our case, inside result we have the category, and the list of pairs
bybitpairs = set()

# Retrieves pairs in perpetual
def getPairs():
    # Get all the pairs in perpetual
    pairs = session.get_tickers(category="linear")
    for p in pairs['result']['list']:
        # print(float(p['fundingRate']) * 100)
        bybitpairs.add(p.keys)
        print(p['symbol'] + " with " + p['fundingRate'])

# Gets the fundingRate of a given coin
def getFundingRate(coin):
    try:
        pair = session.get_tickers(category="linear", symbol=coin)['result']['list'][0]
        value = float(pair['fundingRate']) * 100
        apy = float(pair['fundingRate']) * 365 * 3 * 100
        print(coin + " has a funding rate of " + str(value))
        print("This coin brings an APY of " + str(apy) + "%!")
    except:
        print("Coin does not exist in this mode!")

# Retrieve the best funding rate for a pair that exists in spot and future
# TODO: Not optimal at all, O(n^2) at worst
def bestFundingRate():
    perppairs = session.get_tickers(category="linear")
    spotpairs = session.get_tickers(category="spot")
    top = 0
    for p in perppairs['result']['list']:
        if p['fundingRate'] != '' and float(p['fundingRate']) > top and any(p['symbol'] == s['symbol'] for s in spotpairs['result']['list']):
            coin = p
            top = float(coin['fundingRate'])
    print("And the winner is, " + coin['symbol'] + " with " + str(float(coin['fundingRate']) * 100) + "!")
    apy = float(coin['fundingRate']) * 365 * 3 * 100
    print("This coin brings an APY of " + str(apy) + "%!")
    return coin
        
# To execute this function, need to upgrade_to_unified_trading_account()
def getWallet():
    wallet = session.get_wallet_balance(accountType="UNIFIED")
    print("Total value of wallet is: " + wallet['result']['list'][0]['totalEquity'] + "💲")

# Get amount of a coin
def getCoinBalance(wantedcoin):
    coinsum = session.get_wallet_balance(accountType="UNIFIED", coin=wantedcoin)
    print("Total value of this coin is: " + coinsum['result']['list'][0]['coin'][0]['usdValue'] + "💲")

# Wait for superposition of coin on spot and perpetual
# Requires the dictionnary of the coin
# TODO: Just use threads to execute jobs simultanous
# TODO: Use sockets to retrieve live time information
def enterArbitrage(coin):
    spot = session.get_tickers(category="spot", symbol=coin['symbol'])['result']['list'][0]
    perp = session.get_tickers(category="linear", symbol=coin['symbol'])['result']['list'][0]
    while spot['lastPrice'] != perp['lastPrice']:
        print("spot " + spot['lastPrice'] + " and perp " + perp['lastPrice'])
        time.sleep(0.2)
        spot = session.get_tickers(category="spot", symbol=coin['symbol'])['result']['list'][0]
        perp = session.get_tickers(category="linear", symbol=coin['symbol'])['result']['list'][0]
    quantity = str(float(spot['lastPrice']) * 10)
    session.place_order(
        category="spot",
        symbol=coin['symbol'],
        side="Buy",
        orderType="Limit",
        qty=quantity,
        price=spot['lastPrice'])
    session.place_order(
        category="linear",
        symbol=coin['symbol'],
        side="Sell",
        orderType="Limit",
        qty=quantity,
        price=spot['lastPrice'])
    
