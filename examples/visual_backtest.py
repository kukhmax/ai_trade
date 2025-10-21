# examples/visual_backtest.py
import asyncio
import plotly.io as pio
from core.universal_agent import UniversalAIAgent
from core.config import AppConfig
from backtesting.enhanced_backtester import EnhancedBacktester

async def run_visual_backtest():
    """Запуск бэктеста с визуализацией"""
    
    print("🚀 Запуск бэктеста с визуализацией...")
    
    # Инициализация
    config = AppConfig()
    agent = UniversalAIAgent(config)
    backtester = EnhancedBacktester(agent)
    
    # Параметры бэктеста
    symbol = "BTCUSDT"
    timeframe = "4h"
    methods = ["technical", "wyckoff", "elliott"]
    start_date = "2024-01-01"
    end_date = "2024-03-01"
    
    # Запуск расширенного бэктеста
    enhanced_result = await backtester.run_enhanced_backtest(
        symbol=symbol,
        timeframe=timeframe,
        analysis_methods=methods,
        start_date=start_date,
        end_date=end_date
    )
    
    # Генерация отчетов и графиков
    report = backtester.generate_comprehensive_report(
        enhanced_result, symbol, timeframe
    )
    
    # Сохранение графиков в HTML
    pio.write_html(report['main_chart'], 'backtest_main_chart.html')
    pio.write_html(report['metrics_dashboard'], 'backtest_metrics.html')
    pio.write_html(report['signals_timeline'], 'backtest_timeline.html')
    
    print("✅ Графики сохранены:")
    print("   - backtest_main_chart.html (основной график)")
    print("   - backtest_metrics.html (метрики производительности)")
    print("   - backtest_timeline.html (таймлайн сигналов)")
    
    # Вывод метрик
    print(f"\n📊 МЕТРИКИ БЭКТЕСТА:")
    print(f"Всего сделок: {report['metrics']['total_trades']}")
    print(f"Win Rate: {report['metrics']['win_rate']:.2%}")
    print(f"Общий PnL: ${report['metrics']['total_pnl']:.2f}")
    print(f"Средняя прибыль: ${report['metrics']['avg_win']:.2f}")
    print(f"Средний убыток: ${report['metrics']['avg_loss']:.2f}")
    print(f"Фактор прибыли: {report['metrics']['profit_factor']:.2f}")
    
    # Показать первые 5 сделок
    print(f"\n📋 ПОСЛЕДНИЕ СДЕЛКИ:")
    for i, trade in enumerate(report['trades'][:5]):
        status = "✅ ПРОФИТ" if trade['success'] else "❌ УБЫТОК"
        print(f"  {i+1}. {trade['entry_time'].strftime('%Y-%m-%d')} | "
              f"Вход: ${trade['entry_price']:.2f} | "
              f"Выход: ${trade['exit_price']:.2f} | "
              f"PnL: ${trade['pnl']:.2f} | {status}")

def main():
    """Главная функция с интерактивным выбором"""
    
    print("🎯 ИИ-Агент: Визуализация бэктеста")
    print("=" * 50)
    
    # Можно добавить интерактивный ввод параметров
    asyncio.run(run_visual_backtest())

if __name__ == "__main__":
    main()