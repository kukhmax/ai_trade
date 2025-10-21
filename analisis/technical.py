import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class TechnicalSignal:
    signal_type: str  # 'BUY', 'SELL', 'HOLD'
    strength: float  # 0-1
    indicators: Dict
    confidence: float
    description: str

class TechnicalAnalyzer:
    def __init__(self):
        self.indicators_weight = {
            'rsi': 0.2,
            'macd': 0.25,
            'bollinger': 0.2,
            'volume': 0.15,
            'trend': 0.2
        }
    
    def analyze(self, df: pd.DataFrame) -> TechnicalSignal:
        """Комплексный технический анализ"""
        signals = []
        strengths = []
        
        # Анализ RSI
        rsi_signal, rsi_strength = self._analyze_rsi(df)
        signals.append(rsi_signal)
        strengths.append(rsi_strength)
        
        # Анализ MACD
        macd_signal, macd_strength = self._analyze_macd(df)
        signals.append(macd_signal)
        strengths.append(macd_strength)
        
        # Анализ Боллинджера
        bb_signal, bb_strength = self._analyze_bollinger_bands(df)
        signals.append(bb_signal)
        strengths.append(bb_strength)
        
        # Анализ объема
        volume_signal, volume_strength = self._analyze_volume(df)
        signals.append(volume_signal)
        strengths.append(volume_strength)
        
        # Анализ тренда
        trend_signal, trend_strength = self._analyze_trend(df)
        signals.append(trend_signal)
        strengths.append(trend_strength)
        
        # Взвешенное решение
        final_signal, final_strength, confidence = self._weighted_decision(
            signals, strengths
        )
        
        return TechnicalSignal(
            signal_type=final_signal,
            strength=final_strength,
            indicators={
                'rsi': rsi_signal,
                'macd': macd_signal,
                'bollinger': bb_signal,
                'volume': volume_signal,
                'trend': trend_signal
            },
            confidence=confidence,
            description=self._generate_signal_description(final_signal, final_strength)
        )
    
    def _analyze_rsi(self, df: pd.DataFrame, oversold: int = 30, overbought: int = 70) -> Tuple[str, float]:
        """Анализ RSI"""
        if 'rsi' not in df.columns:
            return 'HOLD', 0.0
            
        current_rsi = df['rsi'].iloc[-1]
        
        if current_rsi < oversold:
            return 'BUY', (oversold - current_rsi) / oversold
        elif current_rsi > overbought:
            return 'SELL', (current_rsi - overbought) / (100 - overbought)
        else:
            return 'HOLD', 0.0
    
    def _analyze_macd(self, df: pd.DataFrame) -> Tuple[str, float]:
        """Анализ MACD"""
        if 'macd' not in df.columns or 'macd_signal' not in df.columns:
            return 'HOLD', 0.0
            
        current_macd = df['macd'].iloc[-1]
        current_signal = df['macd_signal'].iloc[-1]
        prev_macd = df['macd'].iloc[-2]
        prev_signal = df['macd_signal'].iloc[-2]
        
        # Пересечение сигнальной линии
        if prev_macd < prev_signal and current_macd > current_signal:
            return 'BUY', min(abs(current_macd - current_signal) * 10, 1.0)
        elif prev_macd > prev_signal and current_macd < current_signal:
            return 'SELL', min(abs(current_macd - current_signal) * 10, 1.0)
        else:
            return 'HOLD', 0.0
    
    def _analyze_bollinger_bands(self, df: pd.DataFrame) -> Tuple[str, float]:
        """Анализ полос Боллинджера"""
        if 'bb_upper' not in df.columns or 'bb_lower' not in df.columns:
            return 'HOLD', 0.0
            
        current_price = df['close'].iloc[-1]
        bb_upper = df['bb_upper'].iloc[-1]
        bb_lower = df['bb_lower'].iloc[-1]
        bb_middle = df['bb_middle'].iloc[-1]
        
        if current_price <= bb_lower:
            return 'BUY', min((bb_lower - current_price) / bb_lower * 10, 1.0)
        elif current_price >= bb_upper:
            return 'SELL', min((current_price - bb_upper) / bb_upper * 10, 1.0)
        else:
            return 'HOLD', 0.0
    
    def _analyze_volume(self, df: pd.DataFrame) -> Tuple[str, float]:
        """Анализ объема"""
        if len(df) < 21:
            return 'HOLD', 0.0
            
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].tail(20).mean()
        volume_ratio = current_volume / avg_volume
        
        if volume_ratio > 1.5 and df['close'].iloc[-1] > df['open'].iloc[-1]:
            return 'BUY', min((volume_ratio - 1) / 2, 1.0)
        elif volume_ratio > 1.5 and df['close'].iloc[-1] < df['open'].iloc[-1]:
            return 'SELL', min((volume_ratio - 1) / 2, 1.0)
        else:
            return 'HOLD', 0.0
    
    def _analyze_trend(self, df: pd.DataFrame) -> Tuple[str, float]:
        """Анализ тренда"""
        if len(df) < 50:
            return 'HOLD', 0.0
            
        sma_20 = df['close'].rolling(20).mean().iloc[-1]
        sma_50 = df['close'].rolling(50).mean().iloc[-1]
        current_price = df['close'].iloc[-1]
        
        # Определение тренда
        if current_price > sma_20 > sma_50:
            return 'BUY', 0.7
        elif current_price < sma_20 < sma_50:
            return 'SELL', 0.7
        else:
            return 'HOLD', 0.3
    
    def _weighted_decision(self, signals: List[str], strengths: List[float]) -> Tuple[str, float, float]:
        """Взвешенное принятие решения"""
        buy_power = 0.0
        sell_power = 0.0
        
        for i, (signal, strength) in enumerate(zip(signals, strengths)):
            weight = list(self.indicators_weight.values())[i]
            
            if signal == 'BUY':
                buy_power += strength * weight
            elif signal == 'SELL':
                sell_power += strength * weight
        
        if buy_power > sell_power and buy_power > 0.3:
            return 'BUY', buy_power, buy_power - sell_power
        elif sell_power > buy_power and sell_power > 0.3:
            return 'SELL', sell_power, sell_power - buy_power
        else:
            return 'HOLD', max(buy_power, sell_power), abs(buy_power - sell_power)
    
    def _generate_signal_description(self, signal: str, strength: float) -> str:
        """Генерация описания сигнала"""
        strength_level = "слабый" if strength < 0.4 else "средний" if strength < 0.7 else "сильный"
        
        descriptions = {
            'BUY': f"{strength_level.capitalize()} сигнал на покупку",
            'SELL': f"{strength_level.capitalize()} сигнал на продажу", 
            'HOLD': "Рекомендация удерживать позицию или оставаться вне рынка"
        }
        
        return descriptions.get(signal, "Неопределенный сигнал")