import pandas as pd
import numpy as np
from typing import List, Dict
from dataclasses import dataclass
from ..core.universal_agent import UniversalAIAgent
from ..visualization.backtest_plotter import BacktestPlotter

@dataclass
class EnhancedBacktestResult:
    basic_results: any
    equity_curve: pd.DataFrame
    trade_history: List[Dict]
    metrics: Dict
    visualization_data: Dict

class EnhancedBacktester:
    def __init__(self, ai_agent: UniversalAIAgent):
        self.ai_agent = ai_agent
        self.plotter = BacktestPlotter()
    
    async def run_enhanced_backtest(
        self,
        symbol: str,
        timeframe: str,
        analysis_methods: List[str],
        start_date: str,
        end_date: str,
        initial_capital: float = 10000.0
    ) -> EnhancedBacktestResult:
        """Запуск расширенного бэктеста с полными данными для визуализации"""
        
        # Получаем исторические данные для графика
        historical_data = await self.ai_agent.data_fetcher.get_klines(
            symbol, timeframe, start_str=start_date, end_str=end_date
        )
        
        # Запускаем стандартный бэктест
        basic_results = await self.ai_agent.historical_analysis(
            symbol=symbol,
            timeframe=timeframe,
            analysis_methods=analysis_methods,
            start_date=start_date,
            end_date=end_date
        )
        
        # Создаем детальную историю сделок
        trade_history = self._create_trade_history(basic_results, initial_capital)
        
        # Создаем кривую капитала
        equity_curve = self._create_equity_curve(trade_history, initial_capital)
        
        # Расчет дополнительных метрик
        metrics = self._calculate_enhanced_metrics(basic_results, trade_history, equity_curve)
        
        # Подготавливаем данные для визуализации
        visualization_data = {
            'historical_data': historical_data,
            'trade_signals': basic_results,
            'equity_curve': equity_curve,
            'metrics': metrics
        }
        
        return EnhancedBacktestResult(
            basic_results=basic_results,
            equity_curve=equity_curve,
            trade_history=trade_history,
            metrics=metrics,
            visualization_data=visualization_data
        )
    
    def _create_trade_history(self, results: List[Dict], initial_capital: float) -> List[Dict]:
        """Создание детальной истории сделок"""
        
        trades = []
        position = None
        portfolio = initial_capital
        
        for i, result in enumerate(results):
            signal = result['signal']
            
            if signal.action == 'BUY' and signal.confidence > 0.7 and position is None:
                # Открываем длинную позицию
                position = {
                    'entry_time': result['timestamp'],
                    'entry_price': result['actual_price'],
                    'size': portfolio / result['actual_price'],
                    'entry_signal': signal
                }
                
            elif signal.action == 'SELL' and signal.confidence > 0.7 and position is not None:
                # Закрываем позицию
                exit_price = result['actual_price']
                pnl = (exit_price - position['entry_price']) * position['size']
                
                trade = {
                    'entry_time': position['entry_time'],
                    'exit_time': result['timestamp'],
                    'entry_price': position['entry_price'],
                    'exit_price': exit_price,
                    'size': position['size'],
                    'pnl': pnl,
                    'pnl_percent': (pnl / portfolio) * 100,
                    'duration': (result['timestamp'] - position['entry_time']).days,
                    'type': 'LONG',
                    'success': pnl > 0
                }
                
                trades.append(trade)
                portfolio += pnl
                position = None
        
        return trades
    
    def _create_equity_curve(self, trades: List[Dict], initial_capital: float) -> pd.DataFrame:
        """Создание детальной кривой капитала"""
        
        if not trades:
            return pd.DataFrame({'equity': [initial_capital]})
        
        equity_data = []
        current_equity = initial_capital
        
        for trade in trades:
            # Добавляем точку до сделки
            equity_data.append({
                'timestamp': trade['entry_time'],
                'equity': current_equity
            })
            
            # Добавляем точку после сделки
            current_equity += trade['pnl']
            equity_data.append({
                'timestamp': trade['exit_time'],
                'equity': current_equity
            })
        
        return pd.DataFrame(equity_data)
    
    def _calculate_enhanced_metrics(self, results: List[Dict], trades: List[Dict], 
                                  equity_curve: pd.DataFrame) -> Dict:
        """Расчет расширенных метрик"""
        
        if not trades:
            return {}
        
        winning_trades = [t for t in trades if t['success']]
        losing_trades = [t for t in trades if not t['success']]
        
        total_pnl = sum(trade['pnl'] for trade in trades)
        avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
        
        return {
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(trades),
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': abs(avg_win / avg_loss) if avg_loss != 0 else float('inf'),
            'largest_win': max(t['pnl'] for t in trades) if trades else 0,
            'largest_loss': min(t['pnl'] for t in trades) if trades else 0,
            'avg_trade_duration': np.mean([t['duration'] for t in trades]) if trades else 0
        }
    
    def generate_comprehensive_report(self, result: EnhancedBacktestResult, 
                                    symbol: str, timeframe: str) -> Dict:
        """Генерация комплексного отчета с графиками"""
        
        # Основной график бэктеста
        main_chart = self.plotter.create_backtest_chart(
            historical_data=result.visualization_data['historical_data'],
            backtest_results=result.basic_results,
            symbol=symbol,
            timeframe=timeframe
        )
        
        # Дашборд метрик
        metrics_dashboard = self.plotter.create_performance_dashboard(result.basic_results)
        
        # Таймлайн сигналов
        signals_timeline = self.plotter.create_signals_timeline(result.basic_results)
        
        return {
            'main_chart': main_chart,
            'metrics_dashboard': metrics_dashboard,
            'signals_timeline': signals_timeline,
            'trades': result.trade_history,
            'metrics': result.metrics,
            'equity_curve': result.equity_curve
        }