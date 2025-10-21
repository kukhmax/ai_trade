# cli.py
import argparse
import asyncio
import json
from core.universal_agent import UniversalAIAgent
from core.config import AppConfig

async def analyze_command(args):
    """Команда анализа"""
    agent = UniversalAIAgent(AppConfig())
    
    result = await agent.analyze_pair(
        symbol=args.symbol,
        timeframe=args.timeframe,
        analysis_methods=args.methods,
        include_news=not args.no_news,
        include_fundamental=not args.no_fundamental
    )
    
    if args.format == 'json':
        print(json.dumps({
            'symbol': result['symbol'],
            'signal': result['ai_signal'].action,
            'confidence': result['ai_signal'].confidence,
            'entry_price': result['ai_signal'].entry_price,
            'stop_loss': result['ai_signal'].stop_loss,
            'take_profit': result['ai_signal'].take_profit,
            'reasoning': result['ai_signal'].reasoning
        }, indent=2))
    else:
        signal = result['ai_signal']
        print(f"🎯 {result['symbol']} | {result['timeframe']}")
        print(f"📊 Сигнал: {signal.action} (уверенность: {signal.confidence:.2%})")
        print(f"💰 Вход: ${signal.entry_price:.2f}")
        print(f"🛑 Стоп-лосс: ${signal.stop_loss:.2f}")
        print(f"🎯 Тейк-профит: ${signal.take_profit:.2f}")
        print(f"📝 Обоснование: {signal.reasoning}")

def main():
    parser = argparse.ArgumentParser(description='ИИ-агент для анализа крипторынка')
    subparsers = parser.add_subparsers(dest='command')
    
    # Парсер для анализа
    analyze_parser = subparsers.add_parser('analyze', help='Анализ пары')
    analyze_parser.add_argument('symbol', help='Торговая пара (например, BTCUSDT)')
    analyze_parser.add_argument('--timeframe', '-t', default='4h', 
                               help='Таймфрейм (1m, 5m, 1h, 4h, 1d)')
    analyze_parser.add_argument('--methods', '-m', nargs='+', 
                               default=['technical', 'wyckoff'],
                               help='Методы анализа')
    analyze_parser.add_argument('--no-news', action='store_true', 
                               help='Исключить анализ новостей')
    analyze_parser.add_argument('--no-fundamental', action='store_true',
                               help='Исключить фундаментальный анализ')
    analyze_parser.add_argument('--format', '-f', choices=['text', 'json'], 
                               default='text', help='Формат вывода')
    
    args = parser.parse_args()
    
    if args.command == 'analyze':
        asyncio.run(analyze_command(args))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()