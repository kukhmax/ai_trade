import pandas as pd
import numpy as np
from typing import List
from .engine import Trade

class BacktestMetrics:
    @staticmethod
    def calculate_equity_curve(trades: List[Trade], initial_capital: float) -> pd.Series:
        """Расчет кривой капитала"""
        if not trades:
            return pd.Series([initial_capital])
        
        equity = [initial_capital]
        times = [trades[0].entry_time]
        
        current_capital = initial_capital
        for trade in trades:
            if trade.pnl is not None:
                current_capital += trade.pnl
                equity.append(current_capital)
                times.append(trade.exit_time)
        
        return pd.Series(equity, index=times)
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: pd.Series) -> float:
        """Расчет максимальной просадки"""
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        return drawdown.min()
    
    @staticmethod
    def calculate_sharpe_ratio(equity_curve: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Расчет коэффициента Шарпа"""
        returns = equity_curve.pct_change().dropna()
        if len(returns) < 2:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / 252)
        return excess_returns.mean() / excess_returns.std() * np.sqrt(252)
    
    @staticmethod
    def calculate_calmar_ratio(total_return: float, max_drawdown: float, periods: int) -> float:
        """Расчет коэффициента Кальмара"""
        if max_drawdown == 0:
            return 0.0
        annual_return = total_return / (periods / 252)
        return annual_return / abs(max_drawdown)
    
    @staticmethod
    def generate_report(result, initial_capital: float) -> Dict:
        """Генерация отчета по бэктесту"""
        equity_curve = BacktestMetrics.calculate_equity_curve(result.trades, initial_capital)
        
        return {
            'initial_capital': initial_capital,
            'final_capital': initial_capital + result.total_pnl,
            'total_return': result.total_pnl / initial_capital * 100,
            'total_trades': result.total_trades,
            'winning_trades': result.winning_trades,
            'losing_trades': result.losing_trades,
            'win_rate': result.win_rate * 100,
            'max_drawdown': result.max_drawdown * 100,
            'sharpe_ratio': result.sharpe_ratio,
            'avg_profit_per_trade': result.total_pnl / result.total_trades if result.total_trades > 0 else 0,
            'profit_factor': abs(sum(t.pnl for t in result.trades if t.pnl > 0) / 
                               sum(t.pnl for t in result.trades if t.pnl < 0)) if any(t.pnl < 0 for t in result.trades) else float('inf')
        }