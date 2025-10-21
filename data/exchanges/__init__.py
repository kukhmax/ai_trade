# data/exchanges/__init__.py
class ExchangeInterface:
    async def get_klines(self, symbol, timeframe):
        pass

class BybitFetcher(ExchangeInterface):
    # Реализация для Bybit
    pass