import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class WyckoffPhase:
    phase_type: str  # 'ACCUMULATION', 'DISTRIBUTION', 'MARKUP', 'MARKDOWN'
    confidence: float
    current_stage: str
    description: str
    key_levels: Dict

class WyckoffAnalyzer:
    def __init__(self):
        self.min_volume_threshold = 1.2
    
    def analyze(self, df: pd.DataFrame) -> WyckoffPhase:
        """Анализ фазы по Вайкоффу"""
        # Анализ объема
        volume_analysis = self._analyze_volume_patterns(df)
        
        # Анализ ценовых действий
        price_analysis = self._analyze_price_action(df)
        
        # Определение фазы
        phase_type, confidence, stage = self._determine_phase(
            volume_analysis, price_analysis
        )
        
        # Ключевые уровни
        key_levels = self._identify_key_levels(df)
        
        return WyckoffPhase(
            phase_type=phase_type,
            confidence=confidence,
            current_stage=stage,
            description=self._generate_phase_description(phase_type, stage),
            key_levels=key_levels
        )
    
    def _analyze_volume_patterns(self, df: pd.DataFrame) -> Dict:
        """Анализ паттернов объема"""
        if len(df) < 20:
            return {'volume_ratio': 1.0, 'is_high_volume': False, 'volume_trend': 'stable'}
            
        volume_ma = df['volume'].rolling(20).mean()
        current_volume = df['volume'].iloc[-1]
        volume_ratio = current_volume / volume_ma.iloc[-1] if volume_ma.iloc[-1] > 0 else 1.0
        
        return {
            'volume_ratio': volume_ratio,
            'is_high_volume': volume_ratio > self.min_volume_threshold,
            'volume_trend': 'increasing' if df['volume'].iloc[-1] > df['volume'].iloc[-5] else 'decreasing'
        }
    
    def _analyze_price_action(self, df: pd.DataFrame) -> Dict:
        """Анализ ценового действия"""
        if len(df) < 20:
            return {'range_ratio': 1.0, 'green_candles': 0, 'red_candles': 0, 'trend_strength': 0.0}
            
        price_range = df['high'] - df['low']
        avg_range = price_range.rolling(20).mean()
        current_range_ratio = price_range.iloc[-1] / avg_range.iloc[-1] if avg_range.iloc[-1] > 0 else 1.0
        
        # Определение типа свечей
        recent_data = df.tail(5)
        green_candles = len(recent_data[recent_data['close'] > recent_data['open']])
        red_candles = len(recent_data[recent_data['close'] < recent_data['open']])
        
        return {
            'range_ratio': current_range_ratio,
            'green_candles': green_candles,
            'red_candles': red_candles,
            'trend_strength': self._calculate_trend_strength(df)
        }
    
    def _calculate_trend_strength(self, df: pd.DataFrame) -> float:
        """Расчет силы тренда"""
        if len(df) < 20:
            return 0.0
            
        # Простой расчет силы тренда через линейную регрессию
        prices = df['close'].tail(20).values
        x = np.arange(len(prices))
        correlation = np.corrcoef(x, prices)[0, 1]
        
        return correlation if not np.isnan(correlation) else 0.0
    
    def _determine_phase(self, volume_analysis: Dict, price_analysis: Dict) -> tuple:
        """Определение фазы рынка"""
        volume_ratio = volume_analysis['volume_ratio']
        trend_strength = price_analysis['trend_strength']
        
        if volume_ratio > 1.5 and trend_strength > 0.7:
            return 'MARKUP', min(volume_ratio - 1, 0.8), 'impulse'
        elif volume_ratio > 1.5 and trend_strength < -0.7:
            return 'MARKDOWN', min(volume_ratio - 1, 0.8), 'impulse'
        elif volume_ratio < 0.8 and abs(trend_strength) < 0.3:
            if price_analysis['green_candles'] > price_analysis['red_candles']:
                return 'ACCUMULATION', 0.6, 'testing'
            else:
                return 'DISTRIBUTION', 0.6, 'testing'
        else:
            return 'UNKNOWN', 0.3, 'consolidation'
    
    def _identify_key_levels(self, df: pd.DataFrame) -> Dict:
        """Идентификация ключевых уровней"""
        if len(df) < 50:
            return {'support': [], 'resistance': []}
            
        # Поиск локальных минимумов и максимумов
        highs = df['high'].tail(50)
        lows = df['low'].tail(50)
        
        resistance_levels = highs.nlargest(3).tolist()
        support_levels = lows.nsmallest(3).tolist()
        
        return {
            'support': sorted(list(set(support_levels))),
            'resistance': sorted(list(set(resistance_levels)))
        }
    
    def _generate_phase_description(self, phase_type: str, stage: str) -> str:
        """Генерация описания фазы"""
        descriptions = {
            'ACCUMULATION': f"Фаза накопления - {stage} стадия",
            'DISTRIBUTION': f"Фаза распределения - {stage} стадия", 
            'MARKUP': f"Фаза роста - {stage} движение",
            'MARKDOWN': f"Фаза падения - {stage} движение",
            'UNKNOWN': "Неопределенная фаза рынка"
        }
        
        return descriptions.get(phase_type, "Неизвестная фаза")