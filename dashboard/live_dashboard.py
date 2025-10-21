#!/usr/bin/env python3
"""
Интерактивный веб-дашборд для ИИ-агента
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.graph_objects as go
import pandas as pd
import asyncio
import logging
from datetime import datetime, timedelta
import json

from core.universal_agent import UniversalAIAgent
from core.config import AppConfig
from backtesting.enhanced_backtester import EnhancedBacktester

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BacktestDashboard:
    def __init__(self):
        self.app = dash.Dash(
            __name__, 
            external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'],
            meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
        )
        
        try:
            self.agent = UniversalAIAgent(AppConfig())
            self.backtester = EnhancedBacktester(self.agent)
            self.agent_ready = True
        except Exception as e:
            logger.error(f"Ошибка инициализации агента: {e}")
            self.agent_ready = False
        
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_layout(self):
        """Настройка layout дашборда"""
        
        self.app.layout = html.Div([
            # Заголовок
            html.Div([
                html.H1("🤖 ИИ-Агент: Анализ крипторынка", 
                       style={'textAlign': 'center', 'color': '#2ecc71', 'marginBottom': '20px'}),
                html.P("Мощный инструмент для анализа криптовалютных пар с использованием ИИ", 
                      style={'textAlign': 'center', 'color': '#7f8c8d'})
            ], className='row'),
            
            # Статус агента
            html.Div([
                html.Div([
                    html.H4("Статус системы", style={'marginBottom': '10px'}),
                    html.Div(
                        "✅ Агент готов к работе" if self.agent_ready else "❌ Агент не доступен",
                        style={
                            'padding': '10px',
                            'backgroundColor': '#2ecc71' if self.agent_ready else '#e74c3c',
                            'color': 'white',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'fontWeight': 'bold'
                        }
                    )
                ], className='six columns'),
                
                html.Div([
                    html.H4("Быстрый старт", style={'marginBottom': '10px'}),
                    html.P("Выберите пару и нажмите 'Анализировать' для получения сигнала")
                ], className='six columns'),
            ], className='row', style={'marginBottom': '30px'}),
            
            # Панель управления
            html.Div([
                html.Div([
                    html.Label("Торговая пара:"),
                    dcc.Input(
                        id='symbol-input', 
                        value='BTCUSDT', 
                        type='text',
                        style={'width': '100%', 'padding': '10px'}
                    )
                ], className='three columns'),
                
                html.Div([
                    html.Label("Таймфрейм:"),
                    dcc.Dropdown(
                        id='timeframe-dropdown',
                        options=[
                            {'label': '15 минут', 'value': '15m'},
                            {'label': '1 час', 'value': '1h'},
                            {'label': '4 часа', 'value': '4h'},
                            {'label': '1 день', 'value': '1d'}
                        ],
                        value='4h',
                        style={'width': '100%'}
                    )
                ], className='three columns'),
                
                html.Div([
                    html.Label("Методы анализа:"),
                    dcc.Checklist(
                        id='methods-checklist',
                        options=[
                            {'label': ' Технический', 'value': 'technical'},
                            {'label': ' Вайкофф', 'value': 'wyckoff'},
                            {'label': ' Эллиотт', 'value': 'elliott'},
                            {'label': ' Сентимент', 'value': 'sentiment'}
                        ],
                        value=['technical', 'wyckoff'],
                        style={'marginTop': '5px'}
                    )
                ], className='three columns'),
                
                html.Div([
                    html.Label("Действие:"),
                    html.Br(),
                    html.Button('📊 Анализировать', id='analyze-btn', n_clicks=0,
                               style={'backgroundColor': '#3498db', 'color': 'white', 'marginRight': '10px'}),
                    html.Button('📈 Бэктест', id='backtest-btn', n_clicks=0,
                               style={'backgroundColor': '#9b59b6', 'color': 'white'})
                ], className='three columns'),
            ], className='row', style={'marginBottom': '30px', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px'}),
            
            # Результаты анализа
            html.Div([
                html.Div([
                    html.H3("Результаты анализа", id='analysis-title'),
                    dcc.Loading(
                        id="analysis-loading",
                        type="circle",
                        children=html.Div(id="analysis-results")
                    )
                ], className='six columns', style={'padding': '20px'}),
                
                html.Div([
                    html.H3("График цены"),
                    dcc.Graph(id='price-chart')
                ], className='six columns', style={'padding': '20px'}),
            ], className='row'),
            
            # Бэктест
            html.Div([
                html.Div([
                    html.H3("Настройки бэктеста"),
                    html.Label("Период бэктеста:"),
                    dcc.DatePickerRange(
                        id='date-range',
                        start_date=pd.to_datetime('2024-01-01'),
                        end_date=pd.to_datetime(datetime.now().strftime('%Y-%m-%d')),
                        display_format='YYYY-MM-DD'
                    ),
                    html.Br(),
                    html.Button('🚀 Запустить бэктест', id='run-backtest-btn', n_clicks=0,
                               style={'backgroundColor': '#e67e22', 'color': 'white', 'marginTop': '10px'})
                ], className='four columns', style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px'}),
                
                html.Div([
                    html.H3("Результаты бэктеста"),
                    dcc.Loading(
                        id="backtest-loading",
                        type="circle",
                        children=html.Div(id="backtest-results")
                    )
                ], className='eight columns', style={'padding': '20px'}),
            ], className='row', id='backtest-section', style={'display': 'none'}),
            
            # Скрытые элементы для хранения данных
            dcc.Store(id='analysis-data'),
            dcc.Store(id='backtest-data'),
            
        ], style={'padding': '20px'})
    
    def setup_callbacks(self):
        """Настройка callback'ов"""
        
        @self.app.callback(
            [Output('analysis-results', 'children'),
             Output('price-chart', 'figure'),
             Output('analysis-data', 'data')],
            [Input('analyze-btn', 'n_clicks')],
            [State('symbol-input', 'value'),
             State('timeframe-dropdown', 'value'),
             State('methods-checklist', 'value')]
        )
        def update_analysis(n_clicks, symbol, timeframe, methods):
            if n_clicks == 0 or not self.agent_ready:
                return self._get_placeholder_analysis(), self._get_empty_chart(), None
            
            try:
                # Запуск анализа в отдельном потоке
                async def run_analysis():
                    return await self.agent.analyze_pair(
                        symbol=symbol,
                        timeframe=timeframe,
                        analysis_methods=methods,
                        include_news=True,
                        include_fundamental=True
                    )
                
                result = asyncio.run(run_analysis())
                
                # Создание графика цены
                price_chart = self._create_price_chart(result)
                
                return self._create_analysis_layout(result), price_chart, result
                
            except Exception as e:
                return self._create_error_layout(f"Ошибка анализа: {str(e)}"), self._get_empty_chart(), None
        
        @self.app.callback(
            [Output('backtest-section', 'style'),
             Output('backtest-results', 'children')],
            [Input('backtest-btn', 'n_clicks')]
        )
        def show_backtest_section(n_clicks):
            if n_clicks == 0:
                return {'display': 'none'}, html.Div("Настройте параметры и запустите бэктест")
            else:
                return {'display': 'block'}, html.Div("Настройте параметры бэктеста и нажмите 'Запустить бэктест'")
        
        @self.app.callback(
            Output('backtest-results', 'children', allow_duplicate=True),
            [Input('run-backtest-btn', 'n_clicks')],
            [State('symbol-input', 'value'),
             State('timeframe-dropdown', 'value'),
             State('methods-checklist', 'value'),
             State('date-range', 'start_date'),
             State('date-range', 'end_date')],
            prevent_initial_call=True
        )
        def run_backtest(n_clicks, symbol, timeframe, methods, start_date, end_date):
            if n_clicks == 0 or not self.agent_ready:
                return html.Div("Настройте параметры и запустите бэктест")
            
            try:
                async def run_async_backtest():
                    return await self.backtester.run_enhanced_backtest(
                        symbol=symbol,
                        timeframe=timeframe,
                        analysis_methods=methods,
                        start_date=start_date,
                        end_date=end_date
                    )
                
                result = asyncio.run(run_async_backtest())
                report = self.backtester.generate_comprehensive_report(result, symbol, timeframe)
                
                return self._create_backtest_layout(report, symbol, timeframe)
                
            except Exception as e:
                return self._create_error_layout(f"Ошибка бэктеста: {str(e)}")
    
    def _create_analysis_layout(self, result):
        """Создание layout с результатами анализа"""
        signal = result['ai_signal']
        
        # Цвет сигнала
        if signal.action == 'BUY':
            signal_color = '#2ecc71'
            signal_emoji = '🟢'
        elif signal.action == 'SELL':
            signal_color = '#e74c3c'
            signal_emoji = '🔴'
        else:
            signal_color = '#f39c12'
            signal_emoji = '🟡'
        
        return html.Div([
            html.Div([
                html.H4(f"{signal_emoji} Торговый сигнал", style={'color': signal_color}),
                html.P(f"Действие: {signal.action}", style={'fontSize': '24px', 'fontWeight': 'bold', 'color': signal_color}),
                html.P(f"Уверенность: {signal.confidence:.1%}"),
                html.P(f"Текущая цена: ${result['current_price']:.2f}"),
            ], style={'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px', 'marginBottom': '15px'}),
            
            html.Div([
                html.H5("📊 Параметры сделки"),
                html.Table([
                    html.Tr([html.Td("Цена входа:"), html.Td(f"${signal.entry_price:.2f}")]),
                    html.Tr([html.Td("Стоп-лосс:"), html.Td(f"${signal.stop_loss:.2f}")]),
                    html.Tr([html.Td("Тейк-профит:"), html.Td(f"${signal.take_profit:.2f}")]),
                ], style={'width': '100%'})
            ], style={'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px', 'marginBottom': '15px'}),
            
            html.Div([
                html.H5("📝 Обоснование"),
                html.P(signal.reasoning, style={'textAlign': 'justify'})
            ], style={'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px'}),
        ])
    
    def _create_price_chart(self, result):
        """Создание графика цены"""
        # Здесь можно добавить реальный график цены
        # Для демонстрации создаем простой линейный график
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=[1, 2, 3, 4, 5],
            y=[result['current_price'] * 0.95, result['current_price'] * 0.98, 
               result['current_price'], result['current_price'] * 1.02, result['current_price'] * 1.05],
            mode='lines+markers',
            name='Price'
        ))
        
        fig.update_layout(
            title=f"График цены {result['symbol']}",
            xaxis_title="Время",
            yaxis_title="Цена ($)",
            showlegend=True
        )
        
        return fig
    
    def _create_backtest_layout(self, report, symbol, timeframe):
        """Создание layout с результатами бэктеста"""
        metrics = report['metrics']
        
        return html.Div([
            html.H4(f"📈 Результаты бэктеста {symbol} ({timeframe})"),
            
            html.Div([
                html.Div([
                    html.H5("📊 Основные метрики"),
                    html.Table([
                        html.Tr([html.Td("Всего сделок:"), html.Td(metrics['total_trades'])]),
                        html.Tr([html.Td("Win Rate:"), html.Td(f"{metrics['win_rate']:.1%}")]),
                        html.Tr([html.Td("Общий PnL:"), html.Td(f"${metrics['total_pnl']:.2f}")]),
                        html.Tr([html.Td("Фактор прибыли:"), html.Td(f"{metrics['profit_factor']:.2f}")]),
                    ], style={'width': '100%'})
                ], className='six columns'),
                
                html.Div([
                    html.H5("⚡ Дополнительные метрики"),
                    html.Table([
                        html.Tr([html.Td("Макс. просадка:"), html.Td(f"{metrics['max_drawdown']:.1f}%")]),
                        html.Tr([html.Td("Средняя прибыль:"), html.Td(f"${metrics['avg_win']:.2f}")]),
                        html.Tr([html.Td("Средний убыток:"), html.Td(f"${metrics['avg_loss']:.2f}")]),
                        html.Tr([html.Td("Средняя длительность:"), html.Td(f"{metrics['avg_trade_duration']:.1f} дн.")]),
                    ], style={'width': '100%'})
                ], className='six columns'),
            ], className='row', style={'marginBottom': '20px'}),
            
            html.Div([
                html.H5("📋 Последние сделки"),
                html.Table([
                    html.Tr([
                        html.Th("Вход"),
                        html.Th("Выход"),
                        html.Th("Входная цена"),
                        html.Th("Выходная цена"),
                        html.Th("PnL"),
                        html.Th("Результат")
                    ])
                ] + [
                    html.Tr([
                        html.Td(trade['entry_time'].strftime('%m/%d %H:%M')),
                        html.Td(trade['exit_time'].strftime('%m/%d %H:%M')),
                        html.Td(f"${trade['entry_price']:.2f}"),
                        html.Td(f"${trade['exit_price']:.2f}"),
                        html.Td(f"${trade['pnl']:.2f}", style={'color': 'green' if trade['pnl'] > 0 else 'red'}),
                        html.Td("✅" if trade['success'] else "❌")
                    ]) for trade in report['trades'][:5]
                ], style={'width': '100%', 'fontSize': '12px'})
            ])
        ])
    
    def _get_placeholder_analysis(self):
        """Заглушка для анализа"""
        return html.Div([
            html.H4("Добро пожаловать в ИИ-Агент!"),
            html.P("Настройте параметры анализа и нажмите 'Анализировать' для получения торговых сигналов."),
            html.Ul([
                html.Li("Выберите торговую пару (например, BTCUSDT)"),
                html.Li("Выберите таймфрейм анализа"),
                html.Li("Выберите методы анализа"),
                html.Li("Нажмите кнопку 'Анализировать'")
            ])
        ])
    
    def _get_empty_chart(self):
        """Пустой график"""
        fig = go.Figure()
        fig.update_layout(
            title="График появится после анализа",
            xaxis_title="Время",
            yaxis_title="Цена ($)"
        )
        return fig
    
    def _create_error_layout(self, error_message):
        """Layout с ошибкой"""
        return html.Div([
            html.H4("❌ Ошибка"),
            html.P(error_message),
            html.P("Проверьте настройки и попробуйте снова.")
        ], style={'color': 'red'})
    
    def run_server(self, debug=True, port=8050):
        """Запуск сервера дашборда"""
        if not self.agent_ready:
            print("❌ Агент не инициализирован. Проверьте настройки API ключей.")
            return
        
        print(f"🚀 Запуск дашборда на http://localhost:{port}")
        print("💡 Откройте указанный URL в браузере")
        self.app.run_server(debug=debug, port=port)

# Запуск дашборда
if __name__ == "__main__":
    dashboard = BacktestDashboard()
    dashboard.run_server(debug=True, port=8050)