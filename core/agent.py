import pandas as pd
import asyncio
from typing import Dict, List, Optional
import logging
from .config import AppConfig
from ..data.fetcher import DataFetcher
from ..data.exchanges import BybitFetcher
from ..data.processor import DataProcessor
from ..analysis.technical import TechnicalAnalyzer
from ..analysis.wyckoff import WyckoffAnalyzer
from ..analysis.elliott import ElliottWaveAnalyzer
from ..analysis.sentiment import SentimentAnalyzer
from ..signals.generator import SignalGenerator

class CryptoAIAgent:
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Инициализация модулей
        if config.exchange == 'bybit':
            self.data_fetcher = BybitFetcher(config.bybit)
        else:
            self.data_fetcher = DataFetcher(config.binance)
        self.data_processor = DataProcessor()
        self.technical_analyzer = TechnicalAnalyzer()
        self.wyckoff_analyzer = WyckoffAnalyzer()
        self.elliott_analyzer = ElliottWaveAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer(
            config.deepseek.api_key, 
            config.deepseek.base_url
        )
        self.signal_generator = SignalGenerator()
        
        # Валидация конфигурации
        config.validate()
    
    async def analyze_pair(
        self, 
        symbol: str, 
        timeframe: str,
        indicators: List[str],
        include_sentiment: bool = True
    ) -> Dict:
        """Основной метод анализа пары"""
        try:
            self.logger.info(f"Анализ пары {symbol} на таймфрейме {timeframe}")
            
            # Получение данных
            df = await self.data_fetcher.get_klines(symbol, timeframe, limit=500)
            
            # Обработка данных
            df = self.data_processor.add_technical_indicators(df, indicators)
            
            # Получение текущей цены
            current_price = await self.data_fetcher.get_current_price(symbol)
            
            # Технический анализ
            technical_signal = self.technical_analyzer.analyze(df)
            
            # Анализ Вайкоффа
            wyckoff_phase = self.wyckoff_analyzer.analyze(df)
            
            # Анализ волн Эллиотта
            elliott_wave = self.elliott_analyzer.analyze(df)
            
            # Анализ настроений (опционально)
            sentiment_analysis = None
            if include_sentiment:
                news_data = await self._fetch_news_data(symbol)
                sentiment_analysis = await self.sentiment_analyzer.analyze_news(symbol, news_data)
            
            # Генерация сигнала
            trading_signal = self.signal_generator.generate_signal(
                symbol=symbol,
                technical=technical_signal,
                wyckoff=wyckoff_phase,
                elliott=elliott_wave,
                sentiment=sentiment_analysis,
                current_price=current_price
            )
            
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'current_price': current_price,
                'trading_signal': trading_signal,
                'technical_analysis': technical_signal,
                'wyckoff_analysis': wyckoff_phase,
                'elliott_analysis': elliott_wave,
                'sentiment_analysis': sentiment_analysis,
                'timestamp': pd.Timestamp.now()
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа {symbol}: {e}")
            raise
    
    async def _fetch_news_data(self, symbol: str) -> List[Dict]:
        """Получение новостных данных (заглушка)"""
        # Здесь можно интегрировать Cryptopanic API или другие источники
        return [
            {
                'title': f'Market analysis for {symbol}',
                'source': 'CryptoNews',
                'url': 'https://example.com',
                'published_at': pd.Timestamp.now().isoformat()
            }
        ]