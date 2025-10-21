import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List, Dict, Any

load_dotenv()


def env_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return str(val).strip().lower() in ("1", "true", "yes", "y", "on")


@dataclass
class BinanceConfig:
    api_key: str = os.getenv('BINANCE_API_KEY', '')
    api_secret: str = os.getenv('BINANCE_API_SECRET', '')
    testnet: bool = env_bool('BINANCE_TESTNET', True)
    request_timeout: int = 30


@dataclass
class BybitConfig:
    api_key: str = os.getenv('BYBIT_API_KEY', '')
    api_secret: str = os.getenv('BYBIT_API_SECRET', '')
    testnet: bool = env_bool('BYBIT_TESTNET', True)
    # spot или linear (USDT perpetual). По умолчанию linear
    market_type: str = os.getenv('BYBIT_MARKET_TYPE', 'linear')
    request_timeout: int = 30


@dataclass
class DeepSeekConfig:
    api_key: str = os.getenv('DEEPSEEK_API_KEY', '')
    base_url: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-chat"
    temperature: float = 0.3
    max_tokens: int = 2000


@dataclass
class AnalysisConfig:
    default_timeframes: List[str] = None
    supported_indicators: List[str] = None
    min_confidence: float = 0.6
    max_historical_days: int = 365
    
    def __post_init__(self):
        if self.default_timeframes is None:
            self.default_timeframes = ['1h', '4h', '1d', '1w']
        if self.supported_indicators is None:
            self.supported_indicators = ['RSI', 'MACD', 'BB', 'EMA', 'SMA', 'VWAP']


@dataclass
class BacktestConfig:
    initial_capital: float = 10000.0
    risk_per_trade: float = 0.02  # 2%
    commission: float = 0.001     # 0.1%


@dataclass
class AppConfig:
    # Выбор биржи: 'bybit' или 'binance'
    exchange: str = os.getenv('EXCHANGE', 'bybit').lower()
    binance: BinanceConfig = BinanceConfig()
    bybit: BybitConfig = BybitConfig()
    deepseek: DeepSeekConfig = DeepSeekConfig()
    analysis: AnalysisConfig = AnalysisConfig()
    backtest: BacktestConfig = BacktestConfig()
    log_level: str = "INFO"
    
    def validate(self):
        """Проверка конфигурации"""
        if not self.deepseek.api_key:
            raise ValueError("DEEPSEEK_API_KEY не установлен в .env файле")
        
        if self.exchange not in ['bybit', 'binance']:
            raise ValueError("EXCHANGE должен быть 'bybit' или 'binance'")
        
        if self.exchange == 'bybit':
            if not self.bybit.api_key or not self.bybit.api_secret:
                print("⚠️  BYBIT_API_KEY/SECRET не установлены - некоторые функции будут ограничены")
        elif self.exchange == 'binance':
            if not self.binance.api_key:
                print("⚠️  BINANCE_API_KEY не установлен - некоторые функции будут ограничены")