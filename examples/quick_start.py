#!/usr/bin/env python3
"""
Быстрый старт с ИИ-агентом для анализа крипторынка
"""

import asyncio
import logging
# Поддержка запуска как `python -m examples.quick_start` и как `python examples/quick_start.py`
try:
    from core.universal_agent import UniversalAIAgent
    from core.config import AppConfig
except ModuleNotFoundError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from core.universal_agent import UniversalAIAgent
    from core.config import AppConfig

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def quick_analysis():
    """Быстрый анализ основных криптопар"""
    
    print("🚀 ИИ-Агент: Быстрый старт анализа крипторынка")
    print("=" * 50)
    
    # Инициализация агента
    try:
        config = AppConfig()
        agent = UniversalAIAgent(config)
        print("✅ Агент успешно инициализирован")
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return
    
    # Список пар для анализа
    symbols = ["BTCUSDT", "ETHUSDT", "LTCUSDT"]
    timeframe = "1h"
    methods = ["technical", "wyckoff", "elliott"]
    
    print(f"\n📊 Анализ пар: {', '.join(symbols)}")
    print(f"⏰ Таймфрейм: {timeframe}")
    print(f"🔧 Методы: {', '.join(methods)}")
    print("-" * 50)
    
    for symbol in symbols:
        try:
            print(f"\n🔍 Анализируем {symbol}...")
            
            # Запуск анализа
            result = await agent.analyze_pair(
                symbol=symbol,
                timeframe=timeframe,
                analysis_methods=methods,
                include_news=False,
                include_fundamental=False
            )
            
            signal = result['ai_signal']
            
            # Цветовая индикация сигнала
            if signal.action == 'BUY':
                action_emoji = "🟢"
            elif signal.action == 'SELL':
                action_emoji = "🔴"
            else:
                action_emoji = "🟡"
            
            print(f"{action_emoji} {symbol}:")
            print(f"   Сигнал: {signal.action} (уверенность: {signal.confidence:.1%})")
            print(f"   Текущая цена: ${result['current_price']:.2f}")
            
            if signal.action != 'HOLD':
                print(f"   💰 Вход: ${signal.entry_price:.2f}")
                print(f"   🛑 Стоп-лосс: ${signal.stop_loss:.2f}")
                print(f"   🎯 Тейк-профит: ${signal.take_profit:.2f}")
            
            print(f"   📝 {signal.reasoning}")
            
        except Exception as e:
            print(f"❌ Ошибка анализа {symbol}: {e}")
            continue
    
    print("\n" + "=" * 50)
    print("✅ Анализ завершен!")

async def single_pair_analysis():
    """Детальный анализ одной пары"""
    
    print("\n🎯 Детальный анализ одной пары")
    print("=" * 50)
    
    config = AppConfig()
    agent = UniversalAIAgent(config)
    
    symbol = "BTCUSDT"
    timeframe = "1h"
    methods = ["technical", "wyckoff", "elliott", "sentiment"]
    
    try:
        print(f"🔍 Детальный анализ {symbol} на {timeframe}...")
        
        result = await agent.analyze_pair(
            symbol=symbol,
            timeframe=timeframe,
            analysis_methods=methods,
            include_news=True,
            include_fundamental=True
        )
        
        signal = result['ai_signal']
        
        print(f"\n📈 РЕЗУЛЬТАТЫ АНАЛИЗА {symbol}:")
        print(f"📊 Таймфрейм: {timeframe}")
        print(f"💰 Текущая цена: ${result['current_price']:.2f}")
        print(f"🎯 Итоговый сигнал: {signal.action}")
        print(f"📈 Уверенность: {signal.confidence:.1%}")
        
        if signal.action != 'HOLD':
            print(f"\n💡 ТОРГОВЫЕ УРОВНИ:")
            print(f"   📥 Цена входа: ${signal.entry_price:.2f}")
            print(f"   🛑 Стоп-лосс: ${signal.stop_loss:.2f} ({((signal.entry_price - signal.stop_loss) / signal.entry_price * 100):.1f}%)")
            print(f"   🎯 Тейк-профит: ${signal.take_profit:.2f} ({((signal.take_profit - signal.entry_price) / signal.entry_price * 100):.1f}%)")
            print(f"   📏 Риск/Прибыль: 1:{((signal.take_profit - signal.entry_price) / (signal.entry_price - signal.stop_loss)):.1f}")
        
        print(f"\n📝 ОБОСНОВАНИЕ:")
        print(f"   {signal.reasoning}")
        
        print(f"\n🔧 ИСПОЛЬЗОВАННЫЕ ИНДИКАТОРЫ:")
        for indicator in signal.indicators_used:
            print(f"   • {indicator}")
            
    except Exception as e:
        print(f"❌ Ошибка детального анализа: {e}")

def main():
    """Главная функция"""
    print("🤖 ИИ-Агент для анализа крипторынка")
    print("Версия 1.0 | Сделано с ❤️ для трейдеров")
    print()
    
    # Запуск быстрого анализа
    asyncio.run(quick_analysis())
    
    # Запуск детального анализа
    asyncio.run(single_pair_analysis())
    
    print("\n🎉 Готово! Используйте примеры в папке examples/ для более сложных сценариев.")

if __name__ == "__main__":
    main()