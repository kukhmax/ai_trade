import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
from ..backtesting.ai_backtester import AIBacktestResult

class BacktestPlotter:
    def __init__(self):
        self.color_scheme = {
            'buy': '#00FF00',
            'sell': '#FF0000',
            'hold': '#FFFF00',
            'profit': '#00FF00',
            'loss': '#FF0000',
            'equity': '#1f77b4',
            'price': '#2ecc71'
        }
    
    def create_backtest_chart(
        self,
        historical_data: pd.DataFrame,
        backtest_results: AIBacktestResult,
        symbol: str,
        timeframe: str
    ) -> go.Figure:
        """Создание комплексного графика бэктеста"""
        
        # Создаем субплоги
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=(
                f'Цена и точки входа/выхода - {symbol}',
                'Объемы торгов',
                'Кривая капитала'
            ),
            row_heights=[0.6, 0.2, 0.2]
        )
        
        # 1. График цены с точками входа/выхода
        self._add_price_chart(fig, historical_data, backtest_results, row=1)
        
        # 2. График объемов
        self._add_volume_chart(fig, historical_data, row=2)
        
        # 3. Кривая капитала
        self._add_equity_curve(fig, backtest_results, row=3)
        
        # Обновляем layout
        fig.update_layout(
            title=f"Результаты бэктеста {symbol} ({timeframe})<br>"
                  f"Точность: {backtest_results.accuracy:.2%} | "
                  f"Доходность: {backtest_results.total_return:.2f}%",
            height=1000,
            showlegend=True,
            xaxis_rangeslider_visible=False
        )
        
        return fig
    
    def _add_price_chart(self, fig: go.Figure, data: pd.DataFrame, 
                        results: AIBacktestResult, row: int):
        """Добавление графика цены с точками входа/выхода"""
        
        # Свечной график
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name='Price'
            ),
            row=row, col=1
        )
        
        # Точки входа (BUY)
        buy_signals = []
        sell_signals = []
        
        for result in results.detailed_results:
            if result['signal'].action == 'BUY' and result['signal'].confidence > 0.7:
                buy_signals.append({
                    'timestamp': result['timestamp'],
                    'price': result['actual_price'],
                    'confidence': result['signal'].confidence
                })
            elif result['signal'].action == 'SELL' and result['signal'].confidence > 0.7:
                sell_signals.append({
                    'timestamp': result['timestamp'],
                    'price': result['actual_price'],
                    'confidence': result['signal'].confidence
                })
        
        # Добавляем точки BUY
        if buy_signals:
            buy_df = pd.DataFrame(buy_signals)
            fig.add_trace(
                go.Scatter(
                    x=buy_df['timestamp'],
                    y=buy_df['price'],
                    mode='markers',
                    marker=dict(
                        symbol='triangle-up',
                        size=15,
                        color=self.color_scheme['buy'],
                        line=dict(width=2, color='white')
                    ),
                    name='BUY Signal',
                    hovertemplate=(
                        '<b>BUY</b><br>' +
                        'Время: %{x}<br>' +
                        'Цена: $%{y:.2f}<br>' +
                        'Уверенность: %{customdata:.2%}<extra></extra>'
                    ),
                    customdata=buy_df['confidence']
                ),
                row=row, col=1
            )
        
        # Добавляем точки SELL
        if sell_signals:
            sell_df = pd.DataFrame(sell_signals)
            fig.add_trace(
                go.Scatter(
                    x=sell_df['timestamp'],
                    y=sell_df['price'],
                    mode='markers',
                    marker=dict(
                        symbol='triangle-down',
                        size=15,
                        color=self.color_scheme['sell'],
                        line=dict(width=2, color='white')
                    ),
                    name='SELL Signal',
                    hovertemplate=(
                        '<b>SELL</b><br>' +
                        'Время: %{x}<br>' +
                        'Цена: $%{y:.2f}<br>' +
                        'Уверенность: %{customdata:.2%}<extra></extra>'
                    ),
                    customdata=sell_df['confidence']
                ),
                row=row, col=1
            )
        
        # Добавляем скользящие средние для контекста
        data['SMA_20'] = data['close'].rolling(20).mean()
        data['SMA_50'] = data['close'].rolling(50).mean()
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['SMA_20'],
                line=dict(color='orange', width=1),
                name='SMA 20'
            ),
            row=row, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['SMA_50'],
                line=dict(color='purple', width=1),
                name='SMA 50'
            ),
            row=row, col=1
        )
    
    def _add_volume_chart(self, fig: go.Figure, data: pd.DataFrame, row: int):
        """Добавление графика объемов"""
        
        colors = ['red' if close < open else 'green' 
                 for close, open in zip(data['close'], data['open'])]
        
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['volume'],
                marker_color=colors,
                name='Volume',
                opacity=0.7
            ),
            row=row, col=1
        )
    
    def _add_equity_curve(self, fig: go.Figure, results: AIBacktestResult, row: int):
        """Добавление кривой капитала"""
        
        # Создаем кривую капитала из детальных результатов
        equity_data = []
        current_equity = 10000
        
        for result in results.detailed_results:
            # Упрощенная логика изменения капитала
            if result['was_correct'] is True:
                current_equity *= 1.02
            elif result['was_correct'] is False:
                current_equity *= 0.98
            
            equity_data.append({
                'timestamp': result['timestamp'],
                'equity': current_equity
            })
        
        if equity_data:
            equity_df = pd.DataFrame(equity_data)
            
            fig.add_trace(
                go.Scatter(
                    x=equity_df['timestamp'],
                    y=equity_df['equity'],
                    line=dict(color=self.color_scheme['equity'], width=3),
                    name='Equity Curve',
                    fill='tozeroy',
                    fillcolor='rgba(30, 144, 255, 0.1)'
                ),
                row=row, col=1
            )
            
            # Добавляем линию начального капитала
            fig.add_hline(
                y=10000, 
                line_dash="dash", 
                line_color="gray",
                row=row, col=1
            )

    def create_performance_dashboard(self, results: AIBacktestResult) -> go.Figure:
        """Создание дашборда с метриками производительности"""
        
        metrics = {
            'Точность': results.accuracy * 100,
            'Общая доходность': results.total_return,
            'Buy & Hold доходность': results.buy_and_hold_return,
            'Коэффициент Шарпа': results.sharpe_ratio,
            'Максимальная просадка': results.max_drawdown,
            'Количество сигналов': results.signals_generated
        }
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=list(metrics.keys()),
            y=list(metrics.values()),
            marker_color=['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd', '#8c564b'],
            text=[f"{v:.2f}{'%' if k != 'Коэффициент Шарпа' and k != 'Количество сигналов' else ''}" 
                  for k, v in metrics.items()],
            textposition='auto',
        ))
        
        fig.update_layout(
            title="Метрики производительности бэктеста",
            yaxis_title="Значение",
            showlegend=False
        )
        
        return fig

    def create_signals_timeline(self, results: AIBacktestResult) -> go.Figure:
        """Создание таймлайна сигналов"""
        
        signals_data = []
        for result in results.detailed_results:
            if result['signal'].action != 'HOLD':
                signals_data.append({
                    'timestamp': result['timestamp'],
                    'signal': result['signal'].action,
                    'confidence': result['signal'].confidence,
                    'price': result['actual_price'],
                    'correct': result['was_correct']
                })
        
        if not signals_data:
            return go.Figure()
        
        signals_df = pd.DataFrame(signals_data)
        
        fig = go.Figure()
        
        # Правильные сигналы
        correct_signals = signals_df[signals_df['correct'] == True]
        if not correct_signals.empty:
            fig.add_trace(go.Scatter(
                x=correct_signals['timestamp'],
                y=correct_signals['price'],
                mode='markers',
                marker=dict(
                    symbol='star',
                    size=12,
                    color='green'
                ),
                name='Правильные сигналы',
                hovertemplate=(
                    '<b>Правильный %{customdata}</b><br>' +
                    'Время: %{x}<br>' +
                    'Цена: $%{y:.2f}<br>' +
                    'Уверенность: %{text:.2%}<extra></extra>'
                ),
                customdata=correct_signals['signal'],
                text=correct_signals['confidence']
            ))
        
        # Неправильные сигналы
        incorrect_signals = signals_df[signals_df['correct'] == False]
        if not incorrect_signals.empty:
            fig.add_trace(go.Scatter(
                x=incorrect_signals['timestamp'],
                y=incorrect_signals['price'],
                mode='markers',
                marker=dict(
                    symbol='x',
                    size=12,
                    color='red'
                ),
                name='Неправильные сигналы',
                hovertemplate=(
                    '<b>Неправильный %{customdata}</b><br>' +
                    'Время: %{x}<br>' +
                    'Цена: $%{y:.2f}<br>' +
                    'Уверенность: %{text:.2%}<extra></extra>'
                ),
                customdata=incorrect_signals['signal'],
                text=incorrect_signals['confidence']
            ))
        
        fig.update_layout(
            title="Таймлайн сигналов (зеленые - правильные, красные - неправильные)",
            yaxis_title="Цена",
            xaxis_title="Время"
        )
        
        return fig