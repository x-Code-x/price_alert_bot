import urllib 
import requests
import collections
from enum import Enum, unique
from cache import cache
from candle import Candle

import logger_config


class RestApiBinance:    
    BASE_URL="https://api.binance.com/"
    PATH_CANDLESTICK_DATA = "api/v1/klines"
    PATH_EXCHANGEINFO = "api/v1/exchangeInfo"
    PATH_PRICE = "api/v3/ticker/price"

    def __init__(self):
        self.logger = logger_config.instance

    def get_candles(self, symbol, interval, limit= 500):
        query_params = {}
        query_params["symbol"] = symbol
        query_params["interval"] = interval.value
        query_params["limit"] = limit
        query=urllib.parse.urlencode(query_params)

        url = self.BASE_URL + self.PATH_CANDLESTICK_DATA
        self.logger.debug("requesting: "+ url + " - "+str(query))
        r = requests.request("GET", url,params= query)
        return self.parse_candles(r.json())

    def parse_candles(self, json):
        candles={}
        for c in json:
            candles[c[0]] = Candle(float(c[1]), float(c[2]), float(c[3]), float(c[4]), c[0],c[6], float(c[5]))
        return candles
    
    @cache("binance.exchangeinfo", 30000)
    def get_exchangeinfo(self):
        url = self.BASE_URL + self.PATH_EXCHANGEINFO
        self.logger.debug("requesting: "+ url)
        r = requests.request("GET", url)
        return r.json()

    @cache("binance.pairs", 30000)
    def get_pairs(self):
        pairs=[]
        info = self.get_exchangeinfo()
        for s in info["symbols"]:
            pairs.append((s["baseAsset"],s["quoteAsset"]))
        return pairs

    @cache("binance.symbols", 30000)
    def get_symbols(self):
        info = self.get_exchangeinfo()
        symbols = []
        for s in info["symbols"]:
            symbols.append(s["symbol"])
        return symbols

    @cache("binance.prices", 3000)
    def get_prices(self):
        url = self.BASE_URL + self.PATH_PRICE
        self.logger.debug("requesting: "+ url)
        r = requests.request("GET", url)
        js = r.json()
        prices = {}
        for price in js:
            prices[price["symbol"]] = float(price["price"])
        return prices


            
@unique
class CandleInterval(Enum):
    ONE_MINUTE = "1m"
    THREE_MINUTE = "3m"
    FIVE_MINUTE = "5m"
    FIFTEEN_MINUTE = "15m"
    THIRTY_MINUTE = "30m"
    ONE_HOUR = "1h"
    TWO_HOUR = "2h"
    FOUR_HOUR = "4h"
    SIX_HOUR = "6h"
    EIGHT_HOUR = "8h"
    TWELVE_HOUR = "12h"
    ONE_DAY = "1d"
    THREE_DAY = "3d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1M"

    def __str__(self):
        return self.value

    #to enable checking wether a value is a valid enum
    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_ 