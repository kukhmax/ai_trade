# dashboard/live_dashboard.py
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
from core.universal_agent import UniversalAIAgent
from core.config import AppConfig
from backtesting.enhanced_backtester import EnhancedBacktester

class BacktestDashboard:
    def __init__(self):
        self.app = dash.Dash(__name__)
        self.agent = UniversalAIAgent(AppConfig())
        self.backtester = EnhancedBacktester(self.agent)
        
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_layout(self):
        """Настройка layout дашборда"""
        
        self.app.layout = html.Div([
            html.H1("🎯 ИИ-Агент: Дашборд бэктеста", 
                   style={'textAlign': 'center', 'color': '#2ecc71'}),
            
            html.Div([
                html.Div([
                    html.Label("Торговая пара:"),
                    dcc.Input(id='symbol-input', value='BTCUSDT', type='text')
                ], className='six columns'),
                
                html.Div([
                    html.Label("Таймфрейм:"),
                    dcc.Dropdown(
                        id='timeframe-dropdown',
                        options=[
                            {'label': '1 час', 'value': '1h'},
                            {'label': '4 часа', 'value': '4h'},
                            {'label': '1 день', 'value': '1d'}
                        ],
                        value='4h'
                    )
                ], className='six columns'),
            ], className='row'),
            
            html.Div([
                html.Div([
                    html.Label("Методы анализа:"),
                    dcc.Checklist(
                        id='methods-checklist',
                        options=[
                            {'label': 'Технический анализ', 'value': 'technical'},
                            {'label': 'Вайкофф', 'value': 'wyckoff'},
                            {'label': 'Волны Эллиотта', 'value': 'elliott'},
                            {'label': 'Сентимент-анализ', 'value': 'sentiment'}
                        ],
                        value=['technical', 'wyckoff']
                    )
                ], className='six columns'),
                
                html.Div([
                    html.Label("Период:"),
                    dcc.DatePickerRange(
                        id='date-range',
                        start_date=pd.to_datetime('2024-01-01'),
                        end_date=pd.to_datetime('2024-03-01')
                    )
                ], className='six columns'),
            ], className='row'),
            
            html.Button('Запустить бэктест', id='run-backtest', n_clicks=0,
                       style={'backgroundColor': '#2ecc71', 'color': 'white'}),
            
            dcc.Loading(
                id="loading",
                type="circle",
                children=html.Div(id="backtest-results")
            )
        ])
    
    def setup_callbacks(self):
        """Настройка callback'ов"""
        
        @self.app.callback(
            Output('backtest-results', 'children'),
            Input('run-backtest', 'n_clicks'),
            [Input('symbol-input', 'value'),
             Input('timeframe-dropdown', 'value'),
             Input('methods-checklist', 'value'),
             Input('date-range', 'start_date'),
             Input('date-range', 'end_date')]
        )
        def update_backtest(n_clicks, symbol, timeframe, methods, start_date, end_date):
            if n_clicks == 0:
                return html.Div("Настройте параметры и нажмите 'Запустить бэктест'")
            
            # Запуск бэктеста в отдельном потоке
            import asyncio
            result = asyncio.run(self.run_async_backtest(
                symbol, timeframe, methods, start_date, end_date
            ))
            
            return self.create_results_layout(result)
        
        async def run_async_backtest(self, symbol, timeframe, methods, start_date, end_date):
            """Асинхронный запуск бэктеста"""
            enhanced_result = await self.backtester.run_enhanced_backtest(
                symbol=symbol,
                timeframe=timeframe,
                analysis_methods=methods,
                start_date=start_date,
                end_date=end_date
            )
            
            report = self.backtester.generate_comprehensive_report(
                enhanced_result, symbol, timeframe
            )
            
            return report
        
        def create_results_layout(self, report):
            """Создание layout с результатами"""
            
            return html.Div([
                html.H3("Результаты бэктеста"),
                
                # Основной график
                dcc.Graph(figure=report['main_chart']),
                
                # Метрики
                html.Div([
                    html.Div([
                        html.H4("Ключевые метрики"),
                        html.Table([
                            html.Tr([html.Td("Всего сделок:"), html.Td(report['metrics']['total_trades'])]),
                            html.Tr([html.Td("Win Rate:"), html.Td(f"{report['metrics']['win_rate']:.2%}")]),
                            html.Tr([html.Td("Общий PnL:"), html.Td(f"${report['metrics']['total_pnl']:.2f}")]),
                            html.Tr([html.Td("Фактор прибыли:"), html.Td(f"{report['metrics']['profit_factor']:.2f}")]),
                        ])
                    ], className='six columns'),
                    
                    # График метрик
                    html.Div([
                        dcc.Graph(figure=report['metrics_dashboard'])
                    ], className='six columns')
                ], className='row'),
                
                # История сделок
                html.H4("История сделок"),
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
                        html.Td(trade['entry_time'].strftime('%Y-%m-%d %H:%M')),
                        html.Td(trade['exit_time'].strftime('%Y-%m-%d %H:%M')),
                        html.Td(f"${trade['entry_price']:.2f}"),
                        html.Td(f"${trade['exit_price']:.2f}"),
                        html.Td(f"${trade['pnl']:.2f}", 
                               style={'color': 'green' if trade['pnl'] > 0 else 'red'}),
                        html.Td("✅" if trade['success'] else "❌")
                    ]) for trade in report['trades'][:10]  # Показываем первые 10 сделок
                ])
            ])
    
    def run_server(self, debug=True, port=8050):
        """Запуск сервера дашборда"""
        self.app.run_server(debug=debug, port=port)

# Запуск дашборда
if __name__ == "__main__":
    dashboard = BacktestDashboard()
    dashboard.run_server()