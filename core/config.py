import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List, Dict, Any

load_dotenv()

@dataclass
class BinanceConfig:
    api_key: str = os.getenv('BINANCE_API_KEY', '')
    api_secret: str = os.getenv('BINANCE_API_SECRET', '')
    testnet: bool = True
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
    binance: BinanceConfig = BinanceConfig()
    deepseek: DeepSeekConfig = DeepSeekConfig()
    analysis: AnalysisConfig = AnalysisConfig()
    backtest: BacktestConfig = BacktestConfig()
    log_level: str = "INFO"
    
    def validate(self):
        """Проверка конфигурации"""
        if not self.deepseek.api_key:
            raise ValueError("DEEPSEEK_API_KEY не установлен в .env файле")
        
        if not self.binance.api_key:
            print("⚠️  BINANCE_API_KEY не установлен - некоторые функции будут ограничены")