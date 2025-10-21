import pandas as pd
import numpy as np
from typing import Dict, List

class DataProcessor:
    @staticmethod
    def add_technical_indicators(df: pd.DataFrame, indicators: List[str]) -> pd.DataFrame:
        """Добавление технических индикаторов"""
        df = df.copy()
        
        if 'RSI' in indicators:
            df = DataProcessor._add_rsi(df)
            
        if 'MACD' in indicators:
            df = DataProcessor._add_macd(df)
            
        if 'BB' in indicators:
            df = DataProcessor._add_bollinger_bands(df)
            
        if 'EMA' in indicators:
            df = DataProcessor._add_ema(df)
            
        if 'SMA' in indicators:
            df = DataProcessor._add_sma(df)
            
        return df
    
    @staticmethod
    def _add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Добавление RSI"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        return df
    
    @staticmethod
    def _add_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """Добавление MACD"""
        ema_fast = df['close'].ewm(span=fast).mean()
        ema_slow = df['close'].ewm(span=slow).mean()
        df['macd'] = ema_fast - ema_slow
        df['macd_signal'] = df['macd'].ewm(span=signal).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        return df
    
    @staticmethod
    def _add_bollinger_bands(df: pd.DataFrame, period: int = 20, std: int = 2) -> pd.DataFrame:
        """Добавление полос Боллинджера"""
        df['bb_middle'] = df['close'].rolling(period).mean()
        bb_std = df['close'].rolling(period).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * std)
        df['bb_lower'] = df['bb_middle'] - (bb_std * std)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        return df
    
    @staticmethod
    def _add_ema(df: pd.DataFrame, periods: List[int] = [20, 50]) -> pd.DataFrame:
        """Добавление EMA"""
        for period in periods:
            df[f'ema_{period}'] = df['close'].ewm(span=period).mean()
        return df
    
    @staticmethod
    def _add_sma(df: pd.DataFrame, periods: List[int] = [20, 50]) -> pd.DataFrame:
        """Добавление SMA"""
        for period in periods:
            df[f'sma_{period}'] = df['close'].rolling(period).mean()
        return df
    
    @staticmethod
    def detect_support_resistance(df: pd.DataFrame, window: int = 20) -> Dict:
        """Обнаружение уровней поддержки и сопротивления"""
        highs = df['high'].rolling(window=window, center=True).max()
        lows = df['low'].rolling(window=window, center=True).min()
        
        resistance_levels = highs[highs == df['high']].dropna().tail(5).tolist()
        support_levels = lows[lows == df['low']].dropna().tail(5).tolist()
        
        return {
            'resistance': sorted(list(set(resistance_levels))),
            'support': sorted(list(set(support_levels)))
        }