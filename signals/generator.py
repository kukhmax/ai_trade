from typing import Dict, List, Optional
from dataclasses import dataclass
import pandas as pd
from analisis.technical import TechnicalSignal
from analisis.wyckoff import WyckoffPhase
from analisis.elliott import ElliottWave
from analisis.sentiment import SentimentAnalysis

@dataclass
class TradingSignal:
    symbol: str
    action: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float
    entry_price: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    timeframe: str
    reasons: List[str]
    timestamp: pd.Timestamp

class SignalGenerator:
    def __init__(self):
        self.min_confidence = 0.6
        self.confidence_weights = {
            'technical': 0.4,
            'wyckoff': 0.3,
            'elliott': 0.2,
            'sentiment': 0.1
        }
    
    def generate_signal(
        self,
        symbol: str,
        technical: TechnicalSignal,
        wyckoff: WyckoffPhase,
        elliott: ElliottWave,
        sentiment: SentimentAnalysis,
        current_price: float
    ) -> TradingSignal:
        """Генерация финального торгового сигнала"""
        
        # Совмещение сигналов от разных методов
        combined_signal, combined_confidence, reasons = self._combine_signals(
            technical, wyckoff, elliott, sentiment
        )
        
        if combined_confidence < self.min_confidence:
            return TradingSignal(
                symbol=symbol,
                action='HOLD',
                confidence=combined_confidence,
                entry_price=None,
                stop_loss=None,
                take_profit=None,
                timeframe='N/A',
                reasons=reasons,
                timestamp=pd.Timestamp.now()
            )
        
        # Расчет уровней стоп-лосса и тейк-профита
        stop_loss, take_profit = self._calculate_levels(
            combined_signal, current_price, technical, wyckoff
        )
        
        return TradingSignal(
            symbol=symbol,
            action=combined_signal,
            confidence=combined_confidence,
            entry_price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            timeframe='4h',  # Можно сделать динамическим
            reasons=reasons,
            timestamp=pd.Timestamp.now()
        )
    
    def _combine_signals(self, technical, wyckoff, elliott, sentiment):
        """Совмещение сигналов от разных анализов"""
        signals = []
        confidences = []
        reasons = []
        
        # Технический анализ
        if technical.signal_type != 'HOLD':
            signals.append(technical.signal_type)
            confidences.append(technical.confidence * self.confidence_weights['technical'])
            reasons.append(f"Технический анализ: {technical.description}")
        
        # Анализ Вайкоффа
        if wyckoff.phase_type in ['MARKUP', 'ACCUMULATION']:
            signals.append('BUY')
            confidences.append(wyckoff.confidence * self.confidence_weights['wyckoff'])
            reasons.append(f"Фаза Вайкоффа: {wyckoff.phase_type}")
        elif wyckoff.phase_type in ['MARKDOWN', 'DISTRIBUTION']:
            signals.append('SELL') 
            confidences.append(wyckoff.confidence * self.confidence_weights['wyckoff'])
            reasons.append(f"Фаза Вайкоффа: {wyckoff.phase_type}")
        
        # Анализ волн Эллиотта
        if elliott.wave_type == 'IMPULSE':
            signals.append('BUY')
            confidences.append(elliott.confidence * self.confidence_weights['elliott'])
            reasons.append(f"Волны Эллиотта: {elliott.wave_type} волна {elliott.current_wave}")
        elif elliott.wave_type == 'CORRECTIVE':
            signals.append('SELL')
            confidences.append(elliott.confidence * self.confidence_weights['elliott'])
            reasons.append(f"Волны Эллиотта: {elliott.wave_type} волна {elliott.current_wave}")
        
        # Анализ настроений
        if sentiment.overall_sentiment == 'BULLISH':
            signals.append('BUY')
            confidences.append(sentiment.confidence * self.confidence_weights['sentiment'])
            reasons.append("Позитивный новостной фон")
        elif sentiment.overall_sentiment == 'BEARISH':
            signals.append('SELL')
            confidences.append(sentiment.confidence * self.confidence_weights['sentiment'])
            reasons.append("Негативный новостной фон")
        
        if not signals:
            return 'HOLD', 0.0, ["Недостаточно данных для сигнала"]
        
        # Подсчет преобладающего сигнала
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')
        
        if buy_count > sell_count:
            final_signal = 'BUY'
            final_confidence = sum(confidences) / len(signals)
        elif sell_count > buy_count:
            final_signal = 'SELL'
            final_confidence = sum(confidences) / len(signals)
        else:
            final_signal = 'HOLD'
            final_confidence = 0.0
        
        return final_signal, final_confidence, reasons
    
    def _calculate_levels(self, signal, current_price, technical, wyckoff):
        """Расчет уровней стоп-лосса и тейк-профита"""
        if signal == 'BUY':
            stop_loss = current_price * 0.98  # -2%
            take_profit = current_price * 1.06  # +6%
            
            # Используем уровни поддержки из анализа Вайкоффа
            if wyckoff.key_levels.get('support'):
                nearest_support = max([level for level in wyckoff.key_levels['support'] 
                                      if level < current_price], default=None)
                if nearest_support:
                    stop_loss = nearest_support * 0.995  # Чуть ниже поддержки
                
        elif signal == 'SELL':
            stop_loss = current_price * 1.02  # +2%
            take_profit = current_price * 0.94  # -6%
            
            # Используем уровни сопротивления из анализа Вайкоффа
            if wyckoff.key_levels.get('resistance'):
                nearest_resistance = min([level for level in wyckoff.key_levels['resistance'] 
                                         if level > current_price], default=None)
                if nearest_resistance:
                    stop_loss = nearest_resistance * 1.005  # Чуть выше сопротивления
        else:
            stop_loss = None
            take_profit = None
        
        return stop_loss, take_profit