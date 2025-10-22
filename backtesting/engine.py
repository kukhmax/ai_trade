import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from signals.generator import TradingSignal

@dataclass
class Trade:
    entry_time: pd.Timestamp
    exit_time: Optional[pd.Timestamp]
    symbol: str
    action: str
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    stop_loss: float
    take_profit: float
    pnl: Optional[float]
    status: str  # 'OPEN', 'CLOSED', 'STOPPED'

@dataclass
class BacktestResult:
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    max_drawdown: float
    sharpe_ratio: float
    trades: List[Trade]

class BacktestEngine:
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.trades = []
        self.open_trades = []
        
    def run_backtest(
        self,
        historical_data: pd.DataFrame,
        signal_generator: Callable,
        **kwargs
    ) -> BacktestResult:
        """Запуск бэктеста на исторических данных"""
        
        for i in range(len(historical_data)):
            if i < 50:  # Пропускаем первые 50 свечей для инициализации индикаторов
                continue
                
            current_data = historical_data.iloc[:i+1]
            current_price = current_data['close'].iloc[-1]
            current_time = current_data.index[-1]
            
            # Генерация сигнала
            signal = signal_generator(current_data, **kwargs)
            
            # Исполнение сигнала
            if signal.action in ['BUY', 'SELL'] and signal.confidence > 0.6:
                self._execute_trade(signal, current_price, current_time)
            
            # Проверка открытых позиций
            self._check_open_positions(current_price, current_time)
        
        return self._calculate_results()
    
    def _execute_trade(self, signal: TradingSignal, price: float, timestamp: pd.Timestamp):
        """Исполнение сделки"""
        # Расчет количества (риск 2% от капитала на сделку)
        risk_per_trade = self.current_capital * 0.02
        price_diff = abs(price - signal.stop_loss)
        quantity = risk_per_trade / price_diff if price_diff > 0 else 0
        
        trade = Trade(
            entry_time=timestamp,
            exit_time=None,
            symbol=signal.symbol,
            action=signal.action,
            entry_price=price,
            exit_price=None,
            quantity=quantity,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            pnl=None,
            status='OPEN'
        )
        
        self.open_trades.append(trade)
        self.trades.append(trade)
    
    def _check_open_positions(self, current_price: float, timestamp: pd.Timestamp):
        """Проверка условий выхода из открытых позиций"""
        for trade in self.open_trades[:]:
            if trade.action == 'BUY':
                # Проверка стоп-лосса
                if current_price <= trade.stop_loss:
                    self._close_trade(trade, current_price, timestamp, 'STOPPED')
                # Проверка тейк-профита
                elif current_price >= trade.take_profit:
                    self._close_trade(trade, current_price, timestamp, 'TAKE_PROFIT')
                    
            elif trade.action == 'SELL':
                # Проверка стоп-лосса
                if current_price >= trade.stop_loss:
                    self._close_trade(trade, current_price, timestamp, 'STOPPED')
                # Проверка тейк-профита
                elif current_price <= trade.take_profit:
                    self._close_trade(trade, current_price, timestamp, 'TAKE_PROFIT')
    
    def _close_trade(self, trade: Trade, price: float, timestamp: pd.Timestamp, reason: str):
        """Закрытие сделки"""
        trade.exit_time = timestamp
        trade.exit_price = price
        trade.status = 'CLOSED'
        
        # Расчет PnL
        if trade.action == 'BUY':
            trade.pnl = (price - trade.entry_price) * trade.quantity
        else:  # SELL
            trade.pnl = (trade.entry_price - price) * trade.quantity
        
        self.current_capital += trade.pnl
        self.open_trades.remove(trade)
    
    def _calculate_results(self) -> BacktestResult:
        """Расчет результатов бэктеста"""
        closed_trades = [t for t in self.trades if t.status == 'CLOSED']
        
        if not closed_trades:
            return BacktestResult(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                total_pnl=0.0,
                max_drawdown=0.0,
                sharpe_ratio=0.0,
                trades=[]
            )
        
        winning_trades = [t for t in closed_trades if t.pnl > 0]
        losing_trades = [t for t in closed_trades if t.pnl <= 0]
        
        total_pnl = sum(t.pnl for t in closed_trades)
        win_rate = len(winning_trades) / len(closed_trades)
        
        # Расчет максимальной просадки
        equity_curve = self._calculate_equity_curve()
        max_drawdown = self._calculate_max_drawdown(equity_curve)
        
        # Расчет Sharpe Ratio
        sharpe_ratio = self._calculate_sharpe_ratio(equity_curve)
        
        return BacktestResult(
            total_trades=len(closed_trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate,
            total_pnl=total_pnl,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            trades=closed_trades
        )
    
    def _calculate_equity_curve(self) -> pd.Series:
        """Расчет кривой капитала"""
        if not self.trades:
            return pd.Series([self.initial_capital])
        
        equity_data = []
        times = []
        current_equity = self.initial_capital
        
        for trade in self.trades:
            if trade.pnl is not None:
                current_equity += trade.pnl
                equity_data.append(current_equity)
                times.append(trade.exit_time)
        
        return pd.Series(equity_data, index=times)
    
    def _calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """Расчет максимальной просадки"""
        if len(equity_curve) < 2:
            return 0.0
            
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        return drawdown.min()
    
    def _calculate_sharpe_ratio(self, equity_curve: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Расчет коэффициента Шарпа"""
        if len(equity_curve) < 2:
            return 0.0
            
        returns = equity_curve.pct_change().dropna()
        if len(returns) < 2 or returns.std() == 0:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / 252)
        return excess_returns.mean() / excess_returns.std() * np.sqrt(252)