#!/usr/bin/env python3
"""
Командный интерфейс для ИИ-агента
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from core.universal_agent import UniversalAIAgent
from core.config import AppConfig

async def analyze_command(args):
    """Команда анализа пары"""
    try:
        agent = UniversalAIAgent(AppConfig())
        
        result = await agent.analyze_pair(
            symbol=args.symbol.upper(),
            timeframe=args.timeframe,
            analysis_methods=args.methods,
            include_news=not args.no_news,
            include_fundamental=not args.no_fundamental
        )
        
        if args.format == 'json':
            # Вывод в JSON формате
            output = {
                'symbol': result['symbol'],
                'timeframe': result['timeframe'],
                'timestamp': result['timestamp'].isoformat(),
                'current_price': result['current_price'],
                'signal': {
                    'action': result['ai_signal'].action,
                    'confidence': result['ai_signal'].confidence,
                    'entry_price': result['ai_signal'].entry_price,
                    'stop_loss': result['ai_signal'].stop_loss,
                    'take_profit': result['ai_signal'].take_profit,
                    'reasoning': result['ai_signal'].reasoning,
                    'indicators_used': result['ai_signal'].indicators_used
                }
            }
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            # Красивый вывод в терминал
            signal = result['ai_signal']
            
            print(f"\n🎯 АНАЛИЗ {result['symbol']} | {result['timeframe']}")
            print("=" * 50)
            
            # Сигнал с цветовой индикацией
            if signal.action == 'BUY':
                action_str = "🟢 ПОКУПКА"
            elif signal.action == 'SELL':
                action_str = "🔴 ПРОДАЖА"
            else:
                action_str = "🟡 УДЕРЖАНИЕ"
            
            print(f"{action_str} (уверенность: {signal.confidence:.1%})")
            print(f"💰 Текущая цена: ${result['current_price']:.2f}")
            
            if signal.action != 'HOLD':
                print(f"\n💡 ТОРГОВЫЕ УРОВНИ:")
                print(f"   📥 Вход: ${signal.entry_price:.2f}")
                print(f"   🛑 Стоп-лосс: ${signal.stop_loss:.2f}")
                print(f"   🎯 Тейк-профит: ${signal.take_profit:.2f}")
                
                # Расчет риска/прибыли
                risk = signal.entry_price - signal.stop_loss
                reward = signal.take_profit - signal.entry_price
                if risk > 0:
                    rr_ratio = reward / risk
                    print(f"   📏 Риск/Прибыль: 1:{rr_ratio:.2f}")
            
            print(f"\n📝 ОБОСНОВАНИЕ:")
            print(f"   {signal.reasoning}")
            
            print(f"\n🔧 МЕТОДЫ АНАЛИЗА: {', '.join(result['analysis_methods'])}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

async def backtest_command(args):
    """Команда бэктеста"""
    try:
        from backtesting.enhanced_backtester import EnhancedBacktester
        
        agent = UniversalAIAgent(AppConfig())
        backtester = EnhancedBacktester(agent)
        
        print(f"🔍 Запуск бэктеста для {args.symbol}...")
        
        result = await backtester.run_enhanced_backtest(
            symbol=args.symbol.upper(),
            timeframe=args.timeframe,
            analysis_methods=args.methods,
            start_date=args.start_date,
            end_date=args.end_date
        )
        
        report = backtester.generate_comprehensive_report(result, args.symbol, args.timeframe)
        metrics = report['metrics']
        
        if args.format == 'json':
            # JSON вывод
            output = {
                'symbol': args.symbol,
                'timeframe': args.timeframe,
                'period': f"{args.start_date} to {args.end_date}",
                'metrics': metrics,
                'trades_count': len(report['trades'])
            }
            print(json.dumps(output, indent=2))
        else:
            # Текстовый вывод
            print(f"\n📈 РЕЗУЛЬТАТЫ БЭКТЕСТА {args.symbol}")
            print("=" * 50)
            
            print(f"📊 Основные метрики:")
            print(f"   📈 Всего сделок: {metrics['total_trades']}")
            print(f"   ✅ Выигрышных: {metrics['winning_trades']}")
            print(f"   ❌ Проигрышных: {metrics['losing_trades']}")
            print(f"   🎯 Win Rate: {metrics['win_rate']:.1%}")
            print(f"   💰 Общий PnL: ${metrics['total_pnl']:.2f}")
            print(f"   📉 Макс. просадка: {metrics['max_drawdown']:.1f}%")
            print(f"   ⚡ Фактор прибыли: {metrics['profit_factor']:.2f}")
            
            if metrics['total_trades'] > 0:
                print(f"\n📋 Статистика сделок:")
                print(f"   📊 Средняя прибыль: ${metrics['avg_win']:.2f}")
                print(f"   📉 Средний убыток: ${metrics['avg_loss']:.2f}")
                print(f"   🚀 Самая большая победа: ${metrics['largest_win']:.2f}")
                print(f"   🔻 Самый большой убыток: ${metrics['largest_loss']:.2f}")
            
            print(f"\n💡 Для визуализации используйте: python examples/visual_backtest.py")
            
    except Exception as e:
        print(f"❌ Ошибка бэктеста: {e}", file=sys.stderr)
        sys.exit(1)

async def list_command(args):
    """Команда списка доступных пар"""
    try:
        # Здесь можно добавить получение списка пар с биржи
        popular_pairs = [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "DOTUSDT",
            "LINKUSDT", "LTCUSDT", "BCHUSDT", "XLMUSDT", "XRPUSDT"
        ]
        
        if args.format == 'json':
            print(json.dumps({'pairs': popular_pairs}, indent=2))
        else:
            print("📊 Популярные торговые пары:")
            for i, pair in enumerate(popular_pairs, 1):
                print(f"   {i:2d}. {pair}")
            print(f"\n💡 Используйте: python cli.py analyze <SYMBOL> для анализа")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Главная функция CLI"""
    parser = argparse.ArgumentParser(
        description='🤖 ИИ-Агент для анализа крипторынка',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python cli.py analyze BTCUSDT
  python cli.py analyze ETHUSDT --timeframe 1h --methods technical wyckoff
  python cli.py backtest BTCUSDT --start-date 2024-01-01 --end-date 2024-03-01
  python cli.py list
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Команды')
    
    # Парсер для анализа
    analyze_parser = subparsers.add_parser('analyze', help='Анализ торговой пары')
    analyze_parser.add_argument('symbol', help='Торговая пара (например, BTCUSDT)')
    analyze_parser.add_argument('--timeframe', '-t', default='4h', 
                               choices=['15m', '1h', '4h', '1d'],
                               help='Таймфрейм анализа')
    analyze_parser.add_argument('--methods', '-m', nargs='+', 
                               default=['technical', 'wyckoff'],
                               choices=['technical', 'wyckoff', 'elliott', 'sentiment'],
                               help='Методы анализа')
    analyze_parser.add_argument('--no-news', action='store_true', 
                               help='Исключить анализ новостей')
    analyze_parser.add_argument('--no-fundamental', action='store_true',
                               help='Исключить фундаментальный анализ')
    analyze_parser.add_argument('--format', '-f', choices=['text', 'json'], 
                               default='text', help='Формат вывода')
    
    # Парсер для бэктеста
    backtest_parser = subparsers.add_parser('backtest', help='Запуск бэктеста')
    backtest_parser.add_argument('symbol', help='Торговая пара (например, BTCUSDT)')
    backtest_parser.add_argument('--timeframe', '-t', default='4h',
                               choices=['15m', '1h', '4h', '1d'],
                               help='Таймфрейм для бэктеста')
    backtest_parser.add_argument('--methods', '-m', nargs='+',
                               default=['technical', 'wyckoff'],
                               choices=['technical', 'wyckoff', 'elliott', 'sentiment'],
                               help='Методы анализа')
    backtest_parser.add_argument('--start-date', '-s', required=True,
                               help='Начальная дата (YYYY-MM-DD)')
    backtest_parser.add_argument('--end-date', '-e', required=True,
                               help='Конечная дата (YYYY-MM-DD)')
    backtest_parser.add_argument('--format', '-f', choices=['text', 'json'],
                               default='text', help='Формат вывода')
    
    # Парсер для списка пар
    list_parser = subparsers.add_parser('list', help='Список популярных пар')
    list_parser.add_argument('--format', '-f', choices=['text', 'json'],
                           default='text', help='Формат вывода')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Запуск соответствующей команды
    if args.command == 'analyze':
        asyncio.run(analyze_command(args))
    elif args.command == 'backtest':
        asyncio.run(backtest_command(args))
    elif args.command == 'list':
        asyncio.run(list_command(args))

if __name__ == "__main__":
    main()