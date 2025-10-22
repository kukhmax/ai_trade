import pandas as pd
import logging
from typing import Optional, Dict
import ccxt
from datetime import datetime

from core.config import BybitConfig

class BybitFetcher:
    def __init__(self, config: BybitConfig):
        self.logger = logging.getLogger(__name__)
        self.config = config
        # Инициализация клиента ccxt для Bybit
        self.exchange = ccxt.bybit({
            'apiKey': config.api_key,
            'secret': config.api_secret,
            'enableRateLimit': True,
            'timeout': config.request_timeout * 1000,
            'options': {
                'defaultType': config.market_type,
                # авто-калибровка разницы времени
                'adjustForTimeDifference': config.adjust_time,
                # окно допустимого рассинхрона времени (используется ccxt для подписи при необходимости)
                'recvWindow': config.recv_window,
                'recv_window': config.recv_window,
            },
        })
        try:
            # Включаем режим песочницы при необходимости
            self.exchange.setSandboxMode(config.testnet)
            # Явная калибровка времени: получаем серверное время и считаем дельту
            try:
                if config.adjust_time and getattr(self.exchange, 'has', {}).get('fetchTime', False):
                    server_ms = self.exchange.fetch_time()
                    local_ms = self.exchange.milliseconds()
                    diff = int(server_ms - local_ms)
                    # ccxt будет учитывать эту поправку при подписи
                    self.exchange.options['timeDifference'] = diff
                    self.logger.info(f"Синхронизация времени Bybit: {diff} мс")
            except Exception as te:
                self.logger.warning(f"Не удалось выполнить синхронизацию времени: {te}")
            # Загрузка рынков
            self.exchange.load_markets()
        except Exception as e:
            self.logger.warning(f"Не удалось загрузить рынки Bybit: {e}")

    def _normalize_symbol(self, symbol: str) -> str:
        """Нормализация символа под ccxt и выбранный тип рынка.
        Поддерживает вход вида BTCUSDT, BTC/USDT, BTC/USDT:USDT, btc-usdt, и т.п.
        Для linear деривативов предпочитает формат BTC/USDT:USDT.
        """
        s = (symbol or "").upper().replace('-', '/').replace('_', '/')
        if not s:
            return symbol
        # Если уже точное совпадение в списке символов — используем его
        try:
            symbols = getattr(self.exchange, 'symbols', []) or []
            if s in symbols:
                return s
        except Exception:
            symbols = []
        # Если уже указан сеттлмент (BTC/USDT:USDT), возвращаем как есть
        if ':' in s:
            return s
        # Обеспечим базовый формат BASE/QUOTE
        if '/' not in s:
            for q in ('USDT', 'USDC', 'USD'):
                if s.endswith(q):
                    base = s[:-len(q)]
                    s = f"{base}/{q}"
                    break
        candidate = s
        # Для деривативов (linear) попробуем добавить суффикс сеттлмента
        if self.config.market_type != 'spot':
            for settle in ('USDT', 'USDC'):
                with_settle = f"{candidate}:{settle}"
                if with_settle in symbols:
                    return with_settle
        # Если без сеттлмента символ существует — используем его
        if candidate in symbols and ':' not in candidate:
            return candidate
        # В противном случае возвращаем кандидат — ccxt попытается сопоставить
        return candidate

    def _parse_datetime_to_ms(self, date_str: Optional[str]) -> Optional[int]:
        if not date_str:
            return None
        try:
            # Поддержка форматов YYYY-MM-DD или ISO
            dt = pd.Timestamp(date_str)
            return int(dt.timestamp() * 1000)
        except Exception:
            try:
                dt = datetime.fromisoformat(date_str)
                return int(dt.timestamp() * 1000)
            except Exception:
                self.logger.warning(f"Не удалось распарсить дату: {date_str}")
                return None

    async def get_klines(
        self,
        symbol: str,
        interval: str,
        start_str: Optional[str] = None,
        end_str: Optional[str] = None,
        limit: int = 500
    ) -> pd.DataFrame:
        """Получение исторических свечей с Bybit через ccxt"""
        try:
            market_symbol = self._normalize_symbol(symbol)
            since = self._parse_datetime_to_ms(start_str)
            # Публичный метод fetch_ohlcv: не прокидываем приватные параметры
            ohlcv = self.exchange.fetch_ohlcv(market_symbol, timeframe=interval, since=since, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            # Приведение типов
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            self.logger.error(f"Ошибка получения свечей Bybit для {symbol}: {e}")
            raise

    async def get_current_price(self, symbol: str) -> float:
        """Текущая цена инструмента"""
        try:
            market_symbol = self._normalize_symbol(symbol)
            # Публичный метод fetch_ticker: не прокидываем приватные параметры
            ticker = self.exchange.fetch_ticker(market_symbol)
            # Используем 'last' как текущую цену
            return float(ticker.get('last') or ticker.get('close'))
        except Exception as e:
            self.logger.error(f"Ошибка получения цены Bybit для {symbol}: {e}")
            raise

    async def get_exchange_info(self, symbol: str) -> Dict:
        """Информация о рынке"""
        try:
            market_symbol = self._normalize_symbol(symbol)
            market = self.exchange.market(market_symbol)
            return {
                'symbol': market_symbol,
                'base': market.get('base'),
                'quote': market.get('quote'),
                'type': market.get('type'),
                'active': market.get('active')
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения информации о рынке Bybit для {symbol}: {e}")
            raise

    async def get_24h_ticker(self, symbol: str) -> Dict:
        """Статистика за 24 часа"""
        try:
            market_symbol = self._normalize_symbol(symbol)
            # Публичный метод fetch_ticker: не прокидываем приватные параметры
            ticker = self.exchange.fetch_ticker(market_symbol)
            return {
                'symbol': market_symbol,
                'last': float(ticker.get('last') or 0),
                'high': float(ticker.get('high') or 0),
                'low': float(ticker.get('low') or 0),
                'baseVolume': float(ticker.get('baseVolume') or 0),
                'quoteVolume': float(ticker.get('quoteVolume') or 0),
                'percentage': float(ticker.get('percentage') or 0)
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения 24h тикера Bybit для {symbol}: {e}")
            raise