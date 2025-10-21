#!/usr/bin/env python3
"""
Визуализация бэктеста с графиками
"""

import asyncio
import plotly.io as pio
from datetime import datetime, timedelta
from core.universal_agent import UniversalAIAgent
from core.config import AppConfig
from backtesting.enhanced_backtester import EnhancedBacktester

async def run_visual_backtest():
    """Запуск бэктеста с визуализацией"""
    
    print("📈 ИИ-Агент: Визуализация бэктеста")
    print("=" * 50)
    
    # Инициализация
    config = AppConfig()
    agent = UniversalAIAgent(config)
    backtester = EnhancedBacktester(agent)
    
    # Параметры бэктеста
    symbol = "BTCUSDT"
    timeframe = "4h"
    methods = ["technical", "wyckoff"]
    start_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"🔍 Символ: {symbol}")
    print(f"⏰ Таймфрейм: {timeframe}")
    print(f"📅 Период: {start_date} - {end_date}")
    print(f"🔧 Методы: {', '.join(methods)}")
    print()
    
    try:
        print("🔄 Запуск расширенного бэктеста...")
        
        # Запуск бэктеста
        enhanced_result = await backtester.run_enhanced_backtest(
            symbol=symbol,
            timeframe=timeframe,
            analysis_methods=methods,
            start_date=start_date,
            end_date=end_date
        )
        
        print("✅ Бэктест завершен!")
        print("📊 Генерация отчетов и графиков...")
        
        # Генерация отчетов
        report = backtester.generate_comprehensive_report(
            enhanced_result, symbol, timeframe
        )
        
        # Сохранение графиков в HTML
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        main_chart_file = f"backtest_main_{symbol}_{timestamp}.html"
        metrics_file = f"backtest_metrics_{symbol}_{timestamp}.html"
        timeline_file = f"backtest_timeline_{symbol}_{timestamp}.html"
        
        pio.write_html(report['main_chart'], main_chart_file)
        pio.write_html(report['metrics_dashboard'], metrics_file)
        pio.write_html(report['signals_timeline'], timeline_file)
        
        print(f"\n✅ Графики сохранены:")
        print(f"   📈 Основной график: {main_chart_file}")
        print(f"   📊 Метрики: {metrics_file}")
        print(f"   🕒 Таймлайн: {timeline_file}")
        
        # Вывод метрик
        metrics = report['metrics']
        print(f"\n📊 МЕТРИКИ БЭКТЕСТА:")
        print(f"   📈 Всего сделок: {metrics['total_trades']}")
        print(f"   ✅ Выигрышных: {metrics['winning_trades']}")
        print(f"   ❌ Проигрышных: {metrics['losing_trades']}")
        print(f"   🎯 Win Rate: {metrics['win_rate']:.1%}")
        print(f"   💰 Общий PnL: ${metrics['total_pnl']:.2f}")
        print(f"   📉 Макс. просадка: {metrics['max_drawdown']:.1f}%")
        print(f"   ⚡ Фактор прибыли: {metrics['profit_factor']:.2f}")
        
        # Статистика по сделкам
        if metrics['total_trades'] > 0:
            print(f"\n📋 СТАТИСТИКА СДЕЛОК:")
            print(f"   📊 Средняя прибыль: ${metrics['avg_win']:.2f}")
            print(f"   📉 Средний убыток: ${metrics['avg_loss']:.2f}")
            print(f"   ⏱️ Средняя длительность: {metrics['avg_trade_duration']:.1f} дней")
            print(f"   🚀 Самая большая победа: ${metrics['largest_win']:.2f}")
            print(f"   🔻 Самый большой убыток: ${metrics['largest_loss']:.2f}")
        
        # Показать последние сделки
        trades = report['trades']
        if trades:
            print(f"\n📋 ПОСЛЕДНИЕ СДЕЛКИ:")
            for i, trade in enumerate(trades[-5:]):  # Последние 5 сделок
                status = "✅ ПРОФИТ" if trade['success'] else "❌ УБЫТОК"
                pnl_color = "green" if trade['pnl'] > 0 else "red"
                print(f"   {i+1}. {trade['entry_time'].strftime('%m/%d %H:%M')} | "
                      f"Вход: ${trade['entry_price']:.2f} | "
                      f"Выход: ${trade['exit_price']:.2f} | "
                      f"PnL: ${trade['pnl']:+.2f} | {status}")
        
        print(f"\n💡 Откройте файлы в браузере для просмотра интерактивных графиков!")
        
    except Exception as e:
        print(f"❌ Ошибка бэктеста: {e}")
        import traceback
        traceback.print_exc()

async def compare_strategies():
    """Сравнение разных стратегий анализа"""
    
    print("\n🔬 СРАВНЕНИЕ СТРАТЕГИЙ АНАЛИЗА")
    print("=" * 50)
    
    config = AppConfig()
    agent = UniversalAIAgent(config)
    backtester = EnhancedBacktester(agent)
    
    symbol = "ETHUSDT"
    timeframe = "1h"
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    strategies = [
        {"name": "Только технический", "methods": ["technical"]},
        {"name": "Технический + Вайкофф", "methods": ["technical", "wyckoff"]},
        {"name": "Технический + Эллиотт", "methods": ["technical", "elliott"]},
        {"name": "Все методы", "methods": ["technical", "wyckoff", "elliott", "sentiment"]}
    ]
    
    results = []
    
    for strategy in strategies:
        try:
            print(f"🔍 Тестируем: {strategy['name']}...")
            
            result = await backtester.run_enhanced_backtest(
                symbol=symbol,
                timeframe=timeframe,
                analysis_methods=strategy['methods'],
                start_date=start_date,
                end_date=end_date
            )
            
            metrics = result.metrics
            
            results.append({
                'strategy': strategy['name'],
                'total_trades': metrics['total_trades'],
                'win_rate': metrics['win_rate'],
                'total_pnl': metrics['total_pnl'],
                'profit_factor': metrics['profit_factor']
            })
            
            print(f"   ✅ Завершено: {metrics['total_trades']} сделок, Win Rate: {metrics['win_rate']:.1%}")
            
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            continue
    
    # Вывод результатов сравнения
    if results:
        print(f"\n🏆 РЕЗУЛЬТАТЫ СРАВНЕНИЯ СТРАТЕГИЙ:")
        print("-" * 70)
        print(f"{'Стратегия':<25} {'Сделки':<8} {'Win Rate':<10} {'PnL':<12} {'Profit Factor':<15}")
        print("-" * 70)
        
        for result in sorted(results, key=lambda x: x['total_pnl'], reverse=True):
            pnl_color = "🟢" if result['total_pnl'] > 0 else "🔴"
            print(f"{result['strategy']:<25} {result['total_trades']:<8} {result['win_rate']:<10.1%} "
                  f"{pnl_color} ${result['total_pnl']:<10.2f} {result['profit_factor']:<15.2f}")
        
        # Лучшая стратегия
        best_strategy = max(results, key=lambda x: x['total_pnl'])
        print(f"\n🎯 ЛУЧШАЯ СТРАТЕГИЯ: {best_strategy['strategy']}")
        print(f"   💰 PnL: ${best_strategy['total_pnl']:.2f}")
        print(f"   🎯 Win Rate: {best_strategy['win_rate']:.1%}")

def main():
    """Главная функция"""
    print("🤖 ИИ-Агент: Визуализация бэктеста и анализ стратегий")
    print("Версия 1.0 | Интерактивные графики и метрики")
    print()
    
    # Запуск визуального бэктеста
    asyncio.run(run_visual_backtest())
    
    # Сравнение стратегий
    asyncio.run(compare_strategies())
    
    print("\n🎉 Визуализация завершена!")
    print("💡 Откройте HTML файлы в браузере для просмотра интерактивных графиков.")

if __name__ == "__main__":
    main()