import asyncio
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from .config import AppConfig
from data.fetcher import DataFetcher
from data.exchanges import BybitFetcher
from analisis.ai_core import DeepSeekAnalyzer, AISignal

class UniversalAIAgent:
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        # Выбор фетчера по конфигу
        if config.exchange == 'bybit':
            self.data_fetcher = BybitFetcher(config.bybit)
        else:
            self.data_fetcher = DataFetcher(config.binance)
        # Используем ключ Gemini для ИИ-анализа
        self.ai_analyzer = DeepSeekAnalyzer(config.gemini.api_key)
        
        # Валидация конфигурации
        config.validate()
    
    async def analyze_pair(
        self,
        symbol: str,
        timeframe: str,
        analysis_methods: List[str],
        include_news: bool = True,
        include_fundamental: bool = True
    ) -> Dict:
        """Универсальный анализ пары через ИИ"""
        
        try:
            self.logger.info(f"ИИ-анализ {symbol} на {timeframe}")
            
            # Получение рыночных данных
            df = await self.data_fetcher.get_klines(symbol, timeframe, limit=200)
            current_price = await self.data_fetcher.get_current_price(symbol)
            
            # Сбор дополнительных данных
            news_data = await self._fetch_news(symbol) if include_news else None
            fundamental_data = await self._fetch_fundamental(symbol) if include_fundamental else None
            
            # Анализ через ИИ
            ai_signal = await self.ai_analyzer.analyze_market(
                symbol=symbol,
                df=df,
                analysis_methods=analysis_methods,
                timeframe=timeframe,
                news_data=news_data,
                fundamental_data=fundamental_data
            )
            
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'current_price': current_price,
                'ai_signal': ai_signal,
                'timestamp': datetime.now(),
                'data_points': len(df),
                'analysis_methods': analysis_methods
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка ИИ-анализа {symbol}: {e}")
            raise
    
    async def historical_analysis(
        self,
        symbol: str,
        timeframe: str,
        analysis_methods: List[str],
        start_date: str,
        end_date: str,
        step: str = '1d'
    ) -> List[Dict]:
        """Анализ исторических данных через ИИ"""
        
        try:
            # Получение полных исторических данных
            full_df = await self.data_fetcher.get_klines(
                symbol, timeframe, start_str=start_date, end_str=end_date
            )
            
            # Создание точек анализа
            analysis_points = self._generate_analysis_points(full_df, step)
            
            results = []
            for point in analysis_points:
                # Данные до точки анализа
                historical_data = full_df[full_df.index <= point]
                
                if len(historical_data) < 100:
                    continue
                
                # Анализ через ИИ
                ai_signal = await self.ai_analyzer.analyze_market(
                    symbol=symbol,
                    df=historical_data,
                    analysis_methods=analysis_methods,
                    timeframe=timeframe
                )
                
                # Фактическая цена на следующий период
                future_data = full_df[full_df.index > point]
                if not future_data.empty:
                    actual_next_price = future_data.iloc[0]['close']
                    price_change = ((actual_next_price - historical_data['close'].iloc[-1]) / 
                                   historical_data['close'].iloc[-1] * 100)
                else:
                    actual_next_price = None
                    price_change = None
                
                was_correct = self._evaluate_signal(ai_signal, price_change) if price_change is not None else None
                results.append({
                    'timestamp': point,
                    'signal': ai_signal,
                    'actual_price': historical_data['close'].iloc[-1],
                    'actual_next_price': actual_next_price,
                    'price_change': price_change,
                    'was_correct': was_correct,
                    'is_success': was_correct
                })
            
            return results
        except Exception as e:
            self.logger.error(f"Ошибка исторического анализа {symbol}: {e}")
            raise
    
    def _generate_analysis_points(self, df: pd.DataFrame, step: str) -> List[pd.Timestamp]:
        """Генерация точек анализа на основе шагов"""
        step_map = {'1h': '1h', '4h': '4h', '1d': '1d'}
        if step not in step_map:
            step = '1d'
        resampled = df.resample(step_map[step]).last()
        # Пропускаем самую последнюю свечу (неполную)
        return list(resampled.index[:-1])
    
    def _evaluate_signal(self, signal: AISignal, actual_change: float) -> bool:
        """Оценка успешности сигнала на основе фактического изменения цены"""
        if signal.action == 'BUY' and actual_change and actual_change > 0:
            return True
        if signal.action == 'SELL' and actual_change and actual_change < 0:
            return True
        return False
    
    async def _fetch_news(self, symbol: str) -> List[Dict]:
        """Получение новостей (заглушка)"""
        return [
            {
                "title": f"{symbol} sees increased on-chain activity amid market volatility",
                "source": "CryptoNews",
                "date": datetime.now().isoformat()
            },
            {
                "title": f"Whale movements suggest accumulation phase for {symbol}",
                "source": "CryptoInsider",
                "date": datetime.now().isoformat()
            }
        ]
    
    async def _fetch_fundamental(self, symbol: str) -> Dict:
        """Получение фундаментальных данных (заглушка)"""
        return {
            "market_cap": "$800B",
            "dominance": "52%",
            "onchain": {
                "active_addresses": "> 900k",
                "tx_volume": ">$10B"
            }
        }