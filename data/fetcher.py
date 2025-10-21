import pandas as pd
import numpy as np
from binance.client import Client
from binance.enums import *
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Union
from ..core.config import BinanceConfig

class DataFetcher:
    def __init__(self, config: BinanceConfig):
        self.client = Client(config.api_key, config.api_secret, testnet=config.testnet)
        self.logger = logging.getLogger(__name__)
        
    async def get_klines(
        self, 
        symbol: str, 
        interval: str, 
        start_str: Optional[str] = None,
        end_str: Optional[str] = None,
        limit: int = 500
    ) -> pd.DataFrame:
        """Получение исторических данных"""
        try:
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                start_str=start_str,
                end_str=end_str,
                limit=limit
            )
            
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Конвертация типов
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col])
                
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}")
            raise
            
    async def get_current_price(self, symbol: str) -> float:
        """Получение текущей цены"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            self.logger.error(f"Error getting current price for {symbol}: {e}")
            raise
            
    async def get_exchange_info(self, symbol: str) -> Dict:
        """Получение информации о паре"""
        return self.client.get_symbol_info(symbol)
    
    async def get_24h_ticker(self, symbol: str) -> Dict:
        """Получение статистики за 24 часа"""
        return self.client.get_24hr_ticker(symbol=symbol)