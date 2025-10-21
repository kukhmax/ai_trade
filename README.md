# 🤖 ИИ-Агент для анализа крипторынка

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![DeepSeek](https://img.shields.io/badge/DeepSeek-API-green.svg)
![Binance](https://img.shields.io/badge/Binance-API-yellow.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

**Мощный ИИ-агент для анализа криптовалютных рынков с использованием DeepSeek API**

[Особенности](#-особенности) • [Установка](#-установка-и-настройка) • [Быстрый старт](#-быстрый-старт) • [Использование](#-веб-дашборд) • [Структура](#-структура-проекта)

</div>

## 🎯 Особенности

- **🤖 ИИ-анализ на базе DeepSeek** - централизованный анализ всех рыночных данных
- **📊 Мультиметодный анализ** - технический анализ, Вайкофф, волны Эллиотта, сентимент-анализ
- **🔍 Фундаментальный анализ** - новости, твиты, рыночные настроения
- **📈 Визуализация бэктеста** - интерактивные графики с точками входа/выхода
- **🎯 Торговые сигналы** - автоматическая генерация сигналов с уровнями стоп-лосса и тейк-профита
- **📊 Дашборд** - веб-интерфейс для управления анализами

## 🏗️ Структура проекта

```
crypto-ai-agent/
├── 📁 core/                          # Ядро системы
│   ├── __init__.py
│   ├── config.py                     # Конфигурация приложения
│   ├── agent.py                      # Базовый агент
│   └── universal_agent.py           # Универсальный ИИ-агент
├── 📁 data/                          # Работа с данными
│   ├── __init__.py
│   ├── fetcher.py                    # Получение данных с бирж
│   └── processor.py                  # Обработка данных
├── 📁 analysis/                      # Модули анализа
│   ├── __init__.py
│   ├── ai_core.py                   # ИИ-анализ через DeepSeek
│   ├── technical.py                  # Технический анализ
│   ├── wyckoff.py                    # Анализ по Вайкоффу
│   ├── elliott.py                    # Волны Эллиотта
│   └── sentiment.py                  # Анализ настроений
├── 📁 signals/                       # Генерация сигналов
│   ├── __init__.py
│   └── generator.py                  # Генератор торговых сигналов
├── 📁 backtesting/                   # Бэктестинг
│   ├── __init__.py
│   ├── engine.py                     # Движок бэктеста
│   ├── ai_backtester.py             # ИИ-бэктестер
│   ├── enhanced_backtester.py       # Расширенный бэктестер
│   └── metrics.py                    # Метрики производительности
├── 📁 visualization/                 # Визуализация
│   ├── __init__.py
│   └── backtest_plotter.py          # Построение графиков
├── 📁 examples/                      # Примеры использования
│   ├── __init__.py
│   ├── quick_start.py               # Быстрый старт
│   ├── universal_analysis.py        # Универсальный анализ
│   └── visual_backtest.py           # Визуализация бэктеста
├── 📁 dashboard/                     # Веб-дашборд
│   ├── __init__.py
│   └── live_dashboard.py            # Интерактивный дашборд
├── 📄 .env.example                   # Пример переменных окружения
├── 📄 requirements.txt               # Зависимости Python
├── 📄 cli.py                         # Командный интерфейс
├── 📄 setup.py                       # Установка пакета
└── 📄 README.md                      # Документация
```

## 🚀 Команды для запуска

### Быстрый старт
```bash
# Тестирование работы агента
python examples/quick_start.py

# Универсальный анализ
python examples/universal_analysis.py

# Визуализация бэктеста
python examples/visual_backtest.py
```

### Командный интерфейс (CLI)
```bash
# Анализ одной пары
python cli.py analyze BTCUSDT

# Анализ с разными методами
python cli.py analyze ETHUSDT --timeframe 1h --methods technical wyckoff elliott

# Анализ с выводом в JSON
python cli.py analyze ADAUSDT --format json

# Бэктест стратегии
python cli.py backtest BTCUSDT --start-date 2024-01-01 --end-date 2024-03-01

# Список популярных пар
python cli.py list
```

### Веб-дашборд
```bash
# Запуск интерактивного дашборда
python dashboard/live_dashboard.py
# Открыть в браузере: http://localhost:8050
```

### Параметры CLI команд

**Анализ:**
```bash
python cli.py analyze SYMBOL [OPTIONS]

Options:
  --timeframe, -t     Таймфрейм (15m, 1h, 4h, 1d) [default: 4h]
  --methods, -m       Методы анализа [default: technical, wyckoff]
  --no-news           Исключить анализ новостей
  --no-fundamental    Исключить фундаментальный анализ
  --format, -f        Формат вывода (text, json) [default: text]
  --exchange, -x      Биржа данных (bybit, binance)
```

**Бэктест:**
```bash
python cli.py backtest SYMBOL [OPTIONS]

Options:
  --timeframe, -t     Таймфрейм [default: 4h]
  --methods, -m       Методы анализа [default: technical, wyckoff]
  --start-date, -s    Начальная дата (YYYY-MM-DD) [required]
  --end-date, -e      Конечная дата (YYYY-MM-DD) [required]
  --format, -f        Формат вывода (text, json) [default: text]
  --exchange, -x      Биржа данных (bybit, binance)
```

## 🛠 Установка и настройка

### 1. Установка зависимостей
```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Установка пакетов
pip install -r requirements.txt
```

### 2. Настройка API ключей
```bash
# Копирование примера конфигурации
cp .env.example .env

# Редактирование .env файла
# Выбор биржи:
# EXCHANGE=bybit  # или binance
#
# Ключи DeepSeek:
# DEEPSEEK_API_KEY=your_key_here
#
# Ключи Binance (если используете Binance):
# BINANCE_API_KEY=your_key_here
# BINANCE_API_SECRET=your_secret_here
# BINANCE_TESTNET=True
#
# Ключи Bybit (если используете Bybit):
# BYBIT_API_KEY=your_key_here
# BYBIT_API_SECRET=your_secret_here
# BYBIT_MARKET_TYPE=linear  # или spot
# BYBIT_TESTNET=True
```

### 3. Проверка установки
```bash
# Тест работы агента
python examples/quick_start.py

# Тест CLI
python cli.py analyze BTCUSDT
```

## 📊 Примеры вывода

### Торговый сигнал
```
🎯 АНАЛИЗ BTCUSDT | 4h
==================================================
🟢 ПОКУПКА (уверенность: 85.2%)
💰 Текущая цена: $45,250.50

💡 ТОРГОВЫЕ УРОВНИ:
   📥 Вход: $45,250.50
   🛑 Стоп-лосс: $43,987.25
   🎯 Тейк-профит: $48,750.80
   📏 Риск/Прибыль: 1:2.8

📝 ОБОСНОВАНИЕ:
   Сильный бычий дивергенция на RSI, пробитие ключевого уровня сопротивления...

🔧 МЕТОДЫ АНАЛИЗА: technical, wyckoff, elliott
```

### Результаты бэктеста
```
📈 РЕЗУЛЬТАТЫ БЭКТЕСТА BTCUSDT
==================================================
📊 Основные метрики:
   📈 Всего сделок: 24
   ✅ Выигрышных: 18
   ❌ Проигрышных: 6
   🎯 Win Rate: 75.0%
   💰 Общий PnL: $1,245.50
   📉 Макс. просадка: -8.4%
   ⚡ Фактор прибыли: 2.35
```

## 🎯 Ключевые особенности

- **🤖 ИИ-анализ на DeepSeek** - централизованный анализ всех данных
- **📊 Мультиметодный анализ** - технический, Вайкофф, Эллиотт, сентимент
- **📈 Визуализация бэктеста** - интерактивные графики с точками входа/выхода
- **🎯 Торговые сигналы** - автоматическая генерация с уровнями SL/TP
- **🌐 Веб-дашборд** - интерактивный интерфейс управления
- **⚡ Командный интерфейс** - быстрый доступ через CLI

## 🔧 Расширенные возможности

### Создание кастомных стратегий
```python
from core.universal_agent import UniversalAIAgent
from core.config import AppConfig

agent = UniversalAIAgent(AppConfig())
result = await agent.analyze_pair(
    symbol="BTCUSDT",
    timeframe="4h", 
    analysis_methods=["technical", "wyckoff", "custom_strategy"],
    include_news=True
)
```

### Интеграция с другими биржами
```python
# Поддержка Bybit реализована через ccxt в data/exchanges/bybit.py
from core.universal_agent import UniversalAIAgent
from core.config import AppConfig

config = AppConfig()
config.exchange = 'bybit'  # или используйте CLI: --exchange bybit
agent = UniversalAIAgent(config)

result = await agent.analyze_pair(symbol="BTCUSDT", timeframe="4h", analysis_methods=["technical"]) 
```
