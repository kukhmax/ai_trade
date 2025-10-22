import pandas as pd
import numpy as np
from typing import List, Dict, Callable
from dataclasses import dataclass
from analisis.ai_core import AISignal

@dataclass
class AIBacktestResult:
    total_periods: int
    signals_generated: int
    correct_signals: int
    accuracy: float
    total_return: float
    buy_and_hold_return: float
    sharpe_ratio: float
    max_drawdown: float
    detailed_results: List[Dict]

class AIBacktester:
    def __init__(self, ai_agent):
        self.ai_agent = ai_agent
    
    async def run_backtest(
        self,
        symbol: str,
        timeframe: str,
        analysis_methods: List[str],
        start_date: str,
        end_date: str,
        initial_capital: float = 10000.0
    ) -> AIBacktestResult:
        """Запуск бэктеста с ИИ-анализом"""
        
        # Получение исторических анализов
        historical_analysis = await self.ai_agent.historical_analysis(
            symbol=symbol,
            timeframe=timeframe,
            analysis_methods=analysis_methods,
            start_date=start_date,
            end_date=end_date,
            step='1d'
        )
        
        # Симуляция торговли
        portfolio = initial_capital
        positions = 0
        trades = []
        equity_curve = [initial_capital]
        
        for analysis in historical_analysis:
            signal = analysis['signal']
            current_price = analysis['actual_price']
            
            # Исполнение сигнала
            if signal.action == 'BUY' and signal.confidence > 0.7 and positions == 0:
                # Покупаем
                positions = portfolio / current_price
                portfolio = 0
                entry_trade = {
                    'type': 'BUY',
                    'timestamp': analysis['timestamp'],
                    'price': current_price,
                    'confidence': signal.confidence,
                    'reasoning': signal.reasoning
                }
                trades.append(entry_trade)
                
            elif signal.action == 'SELL' and signal.confidence > 0.7 and positions > 0:
                # Продаем
                portfolio = positions * current_price
                positions = 0
                exit_trade = {
                    'type': 'SELL', 
                    'timestamp': analysis['timestamp'],
                    'price': current_price,
                    'pnl': portfolio - initial_capital,
                    'confidence': signal.confidence,
                    'reasoning': signal.reasoning
                }
                trades.append(exit_trade)
                equity_curve.append(portfolio)
        
        # Расчет финального капитала
        if positions > 0:
            final_price = historical_analysis[-1]['actual_price']
            final_portfolio = positions * final_price
        else:
            final_portfolio = portfolio
        
        # Расчет метрик
        accuracy = self._calculate_accuracy(historical_analysis)
        total_return = (final_portfolio - initial_capital) / initial_capital * 100
        
        # Buy and Hold для сравнения
        first_price = historical_analysis[0]['actual_price']
        last_price = historical_analysis[-1]['actual_price']
        buy_hold_return = (last_price - first_price) / first_price * 100
        
        return AIBacktestResult(
            total_periods=len(historical_analysis),
            signals_generated=len([a for a in historical_analysis if a['signal'].action != 'HOLD']),
            correct_signals=len([a for a in historical_analysis if a['was_correct']]),
            accuracy=accuracy,
            total_return=total_return,
            buy_and_hold_return=buy_hold_return,
            sharpe_ratio=self._calculate_sharpe_ratio(equity_curve),
            max_drawdown=self._calculate_max_drawdown(equity_curve),
            detailed_results=historical_analysis
        )
    
    def _calculate_accuracy(self, results: List[Dict]) -> float:
        """Расчет точности сигналов"""
        evaluated = [r for r in results if r['was_correct'] is not None]
        if not evaluated:
            return 0.0
        
        correct = len([r for r in evaluated if r['was_correct']])
        return correct / len(evaluated)
    
    def _calculate_sharpe_ratio(self, equity_curve: List[float]) -> float:
        """Расчет коэффициента Шарпа"""
        if len(equity_curve) < 2:
            return 0.0
        
        returns = pd.Series(equity_curve).pct_change().dropna()
        if returns.std() == 0:
            return 0.0
        
        return (returns.mean() / returns.std()) * (252 ** 0.5)
    
    def _calculate_max_drawdown(self, equity_curve: List[float]) -> float:
        """Расчет максимальной просадки"""
        peak = equity_curve[0]
        max_dd = 0.0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
        
        return max_dd * 100