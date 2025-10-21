#!/usr/bin/env python3
"""
Универсальный анализ с ИИ-агентом
"""

import asyncio
import json
from datetime import datetime, timedelta
from core.universal_agent import UniversalAIAgent
from core.config import AppConfig

async def comprehensive_analysis():
    """Комплексный анализ с различными методами"""
    
    print("🎯 ИИ-Агент: Комплексный анализ рынка")
    print("=" * 60)
    
    # Инициализация
    config = AppConfig()
    agent = UniversalAIAgent(config)
    
    # Параметры анализа
    symbol = "BTCUSDT"
    timeframes = ["1h", "4h", "1d"]
    methods_combinations = [
        ["technical"],
        ["technical", "wyckoff"],
        ["technical", "elliott"],
        ["technical", "wyckoff", "elliott", "sentiment"]
    ]
    
    print(f"🔍 Символ: {symbol}")
    print(f"⏰ Таймфреймы: {', '.join(timeframes)}")
    print()
    
    for timeframe in timeframes:
        print(f"\n📊 АНАЛИЗ НА ТАЙМФРЕЙМЕ {timeframe}:")
        print("-" * 40)
        
        for methods in methods_combinations:
            try:
                print(f"\n🔧 Методы: {', '.join(methods)}")
                
                result = await agent.analyze_pair(
                    symbol=symbol,
                    timeframe=timeframe,
                    analysis_methods=methods,
                    include_news=True,
                    include_fundamental=True
                )
                
                signal = result['ai_signal']
                
                # Визуализация результата
                confidence_bar = "█" * int(signal.confidence * 20) + "░" * (20 - int(signal.confidence * 20))
                
                if signal.action == 'BUY':
                    action_str = "🟢 ПОКУПКА"
                elif signal.action == 'SELL':
                    action_str = "🔴 ПРОДАЖА"
                else:
                    action_str = "🟡 УДЕРЖАНИЕ"
                
                print(f"   {action_str} | Уверенность: {confidence_bar} {signal.confidence:.1%}")
                
                if signal.action != 'HOLD':
                    print(f"   💰 Вход: ${signal.entry_price:.2f}")
                    print(f"   🛑 Стоп: ${signal.stop_loss:.2f}")
                    print(f"   🎯 Профит: ${signal.take_profit:.2f}")
                
                # Краткое обоснование
                reasoning_short = signal.reasoning[:100] + "..." if len(signal.reasoning) > 100 else signal.reasoning
                print(f"   📝 {reasoning_short}")
                
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
                continue
    
    print("\n" + "=" * 60)
    print("✅ Комплексный анализ завершен!")

async def multi_timeframe_analysis():
    """Мультитаймфреймный анализ"""
    
    print("\n🕒 МУЛЬТИТАЙМФРЕЙМНЫЙ АНАЛИЗ")
    print("=" * 50)
    
    config = AppConfig()
    agent = UniversalAIAgent(config)
    
    symbol = "ETHUSDT"
    timeframes = ["15m", "1h", "4h", "1d"]
    methods = ["technical", "wyckoff"]
    
    print(f"🔍 Анализ {symbol} на multiple таймфреймах...")
    print()
    
    signals_summary = {}
    
    for timeframe in timeframes:
        try:
            result = await agent.analyze_pair(
                symbol=symbol,
                timeframe=timeframe,
                analysis_methods=methods,
                include_news=False
            )
            
            signal = result['ai_signal']
            signals_summary[timeframe] = {
                'action': signal.action,
                'confidence': signal.confidence,
                'price': result['current_price']
            }
            
            print(f"⏰ {timeframe:>4}: {signal.action:>6} ({(signal.confidence*100):3.0f}%) - ${result['current_price']:.2f}")
            
        except Exception as e:
            print(f"⏰ {timeframe:>4}: ❌ Ошибка")
            continue
    
    # Сводка по всем таймфреймам
    print(f"\n📋 СВОДКА ПО ТАЙМФРЕЙМАМ:")
    buy_count = sum(1 for s in signals_summary.values() if s['action'] == 'BUY')
    sell_count = sum(1 for s in signals_summary.values() if s['action'] == 'SELL')
    hold_count = sum(1 for s in signals_summary.values() if s['action'] == 'HOLD')
    
    print(f"   🟢 ПОКУПКА: {buy_count} таймфреймов")
    print(f"   🔴 ПРОДАЖА: {sell_count} таймфреймов")
    print(f"   🟡 УДЕРЖАНИЕ: {hold_count} таймфреймов")
    
    # Общая рекомендация
    if buy_count > sell_count and buy_count > hold_count:
        overall_signal = "🟢 ПРЕОБЛАДАЕТ ПОКУПКА"
    elif sell_count > buy_count and sell_count > hold_count:
        overall_signal = "🔴 ПРЕОБЛАДАЕТ ПРОДАЖА"
    else:
        overall_signal = "🟡 НЕОПРЕДЕЛЕННОСТЬ"
    
    print(f"   🎯 ОБЩАЯ РЕКОМЕНДАЦИЯ: {overall_signal}")

async def export_analysis_results():
    """Экспорт результатов анализа в JSON"""
    
    print("\n💾 ЭКСПОРТ РЕЗУЛЬТАТОВ АНАЛИЗА")
    print("=" * 50)
    
    config = AppConfig()
    agent = UniversalAIAgent(config)
    
    symbol = "BTCUSDT"
    timeframe = "4h"
    methods = ["technical", "wyckoff", "elliott", "sentiment"]
    
    try:
        print(f"🔍 Анализ {symbol} для экспорта...")
        
        result = await agent.analyze_pair(
            symbol=symbol,
            timeframe=timeframe,
            analysis_methods=methods,
            include_news=True,
            include_fundamental=True
        )
        
        # Подготовка данных для экспорта
        export_data = {
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
            },
            'analysis_methods': result['analysis_methods'],
            'data_points': result['data_points']
        }
        
        # Сохранение в JSON файл
        filename = f"analysis_{symbol}_{timeframe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Результаты сохранены в файл: {filename}")
        print(f"📊 Данные для {symbol} на {timeframe} успешно экспортированы")
        
    except Exception as e:
        print(f"❌ Ошибка экспорта: {e}")

def main():
    """Главная функция"""
    print("🤖 ИИ-Агент: Универсальный анализ крипторынка")
    print("Версия 1.0 | Комплексные методы анализа")
    print()
    
    # Запуск различных типов анализа
    asyncio.run(comprehensive_analysis())
    asyncio.run(multi_timeframe_analysis())
    asyncio.run(export_analysis_results())
    
    print("\n🎉 Универсальный анализ завершен!")
    print("💡 Используйте визуализацию для просмотра графиков и бэктестов.")

if __name__ == "__main__":
    main()