import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class ElliottWave:
    wave_type: str  # 'IMPULSE', 'CORRECTIVE'
    current_wave: str  # '1', '2', '3', '4', '5', 'A', 'B', 'C'
    confidence: float
    targets: Dict
    invalid_level: float

class ElliottWaveAnalyzer:
    def __init__(self):
        self.fibonacci_ratios = [0.236, 0.382, 0.5, 0.618, 0.786, 1.0, 1.272, 1.618]
    
    def analyze(self, df: pd.DataFrame) -> ElliottWave:
        """Анализ волн Эллиотта"""
        # Идентификация экстремумов
        peaks, valleys = self._find_extremes(df)
        
        if len(peaks) < 2 or len(valleys) < 2:
            return ElliottWave(
                wave_type='UNKNOWN',
                current_wave='UNKNOWN',
                confidence=0.0,
                targets={},
                invalid_level=0.0
            )
        
        # Анализ структуры волн
        wave_structure = self._analyze_wave_structure(peaks, valleys, df)
        
        return wave_structure
    
    def _find_extremes(self, df: pd.DataFrame, window: int = 5) -> Tuple[List, List]:
        """Поиск локальных экстремумов"""
        if len(df) < window * 2:
            return [], []
            
        highs = df['high']
        lows = df['low']
        
        # Поиск пиков
        peaks = []
        for i in range(window, len(highs) - window):
            if all(highs[i] > highs[i-j] for j in range(1, window+1)) and \
               all(highs[i] > highs[i+j] for j in range(1, window+1)):
                peaks.append((df.index[i], highs[i]))
        
        # Поиск впадин
        valleys = []
        for i in range(window, len(lows) - window):
            if all(lows[i] < lows[i-j] for j in range(1, window+1)) and \
               all(lows[i] < lows[i+j] for j in range(1, window+1)):
                valleys.append((df.index[i], lows[i]))
        
        return peaks[-10:], valleys[-10:]  # Возвращаем последние 10 экстремумов
    
    def _analyze_wave_structure(self, peaks: List, valleys: List, df: pd.DataFrame) -> ElliottWave:
        """Анализ волновой структуры"""
        if not peaks or not valleys:
            return self._get_default_wave()
        
        # Простой анализ тренда
        current_price = df['close'].iloc[-1]
        recent_high = max([p[1] for p in peaks[-3:]]) if peaks else current_price
        recent_low = min([v[1] for v in valleys[-3:]]) if valleys else current_price
        
        # Определение типа тренда
        if current_price > recent_high * 0.95:
            wave_type = 'IMPULSE'
            current_wave = '3'  # Предполагаем волну 3
            confidence = 0.6
        elif current_price < recent_low * 1.05:
            wave_type = 'CORRECTIVE'
            current_wave = 'A'
            confidence = 0.5
        else:
            wave_type = 'UNKNOWN'
            current_wave = 'UNKNOWN'
            confidence = 0.3
        
        # Расчет целей по Фибоначчи
        targets = self._calculate_fibonacci_targets(recent_low, recent_high, wave_type)
        
        return ElliottWave(
            wave_type=wave_type,
            current_wave=current_wave,
            confidence=confidence,
            targets=targets,
            invalid_level=recent_low * 0.95 if wave_type == 'IMPULSE' else recent_high * 1.05
        )
    
    def _calculate_fibonacci_targets(self, low: float, high: float, wave_type: str) -> Dict:
        """Расчет целей по Фибоначчи"""
        price_range = high - low
        
        if wave_type == 'IMPULSE':
            return {
                '0.382': high + price_range * 0.382,
                '0.618': high + price_range * 0.618,
                '1.0': high + price_range,
                '1.618': high + price_range * 1.618
            }
        else:  # CORRECTIVE
            return {
                '0.382': high - price_range * 0.382,
                '0.5': high - price_range * 0.5,
                '0.618': high - price_range * 0.618,
                '0.786': high - price_range * 0.786
            }
    
    def _get_default_wave(self) -> ElliottWave:
        """Волна по умолчанию"""
        return ElliottWave(
            wave_type='UNKNOWN',
            current_wave='UNKNOWN',
            confidence=0.0,
            targets={},
            invalid_level=0.0
        )