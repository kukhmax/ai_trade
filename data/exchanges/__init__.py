# data/exchanges/__init__.py
from .bybit import BybitFetcher

class ExchangeInterface:
    async def get_klines(self, symbol, timeframe, *args, **kwargs):
        raise NotImplementedError
    async def get_current_price(self, symbol):
        raise NotImplementedError
    async def get_exchange_info(self, symbol):
        raise NotImplementedError
    async def get_24h_ticker(self, symbol):
        raise NotImplementedError

__all__ = ['BybitFetcher', 'ExchangeInterface']