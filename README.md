# 🤖 ИИ-Агент для анализа крипторынка

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![DeepSeek](https://img.shields.io/badge/DeepSeek-API-green.svg)
![Binance](https://img.shields.io/badge/Binance-API-yellow.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

**Мощный ИИ-агент для анализа криптовалютных рынков с использованием DeepSeek API**

[Особенности](#-особенности) • [Установка](#-установка) • [Быстрый старт](#-быстрый-старт) • [Использование](#-использование) • [Структура](#-структура-проекта)

</div>

## 🎯 Особенности

- **🤖 ИИ-анализ на базе DeepSeek** - централизованный анализ всех рыночных данных
- **📊 Мультиметодный анализ** - технический анализ, Вайкофф, волны Эллиотта, сентимент-анализ
- **🔍 Фундаментальный анализ** - новости, твиты, рыночные настроения
- **📈 Визуализация бэктеста** - интерактивные графики с точками входа/выхода
- **🎯 Торговые сигналы** - автоматическая генерация сигналов с уровнями стоп-лосса и тейк-профита
- **📊 Дашборд** - веб-интерфейс для управления анализами

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-username/crypto-ai-agent.git
cd crypto-ai-agent
```

### 2. Установка зависимостей

```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt
```

### 3. Настройка API ключей

Создайте файл `.env` в корневой директории:

```env
# DeepSeek API (обязательно)
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Binance API (рекомендуется для реальных данных)
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret

# Дополнительные API (опционально)
CRYPTOPANIC_API_KEY=your_cryptopanic_key
TWITTER_BEARER_TOKEN=your_twitter_token
```

### 4. Быстрая проверка работы

```bash
# Тестовый запуск
python examples/quick_start.py
```

## 📦 Установка

### Системные требования

- Python 3.8 или выше
- 4GB+ оперативной памяти
- Стабильное интернет-соединение

### Пошаговая установка

#### 1. Получение API ключей

**DeepSeek API:**
1. Зарегистрируйтесь на [DeepSeek Platform](https://platform.deepseek.com/)
2. Перейдите в раздел API Keys
3. Создайте новый API ключ
4. Сохраните ключ в `.env` файл

**Binance API (рекомендуется):**
1. Войдите в аккаунт Binance
2. Перейдите в [API Management](https://www.binance.com/en/my/settings/api-management)
3. Создайте новый API ключ
4. Разрешите доступ к Spot & Margin Trading
5. Сохраните ключ и секрет в `.env`

#### 2. Установка Python пакетов

```bash
# Базовые зависимости
pip install python-binance pandas numpy requests plotly dash

# Или полная установка из requirements.txt
pip install -r requirements.txt
```

#### 3. Проверка установки

```python
# test_installation.py
from core.config import AppConfig
from data.fetcher import DataFetcher
import asyncio

async def test():
    config = AppConfig()
    fetcher = DataFetcher(config.binance)
    
    try:
        price = await fetcher.get_current_price('BTCUSDT')
        print(f"✅ Установка успешна! Текущая цена BTC: ${price}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

asyncio.run(test())
```

## 🏗️ Структура проекта

```
crypto-ai-agent/
├── 📁 core/                 # Ядро системы
│   ├── agent.py            # Главный ИИ-агент
│   ├── config.py           # Конфигурация
│   └── universal_agent.py  # Универсальный анализатор
├── 📁 data/                # Работа с данными
│   ├── fetcher.py          # Получение данных с бирж
│   └── processor.py        # Обработка данных
├── 📁 analysis/            # Модули анализа
│   ├── ai_core.py          # ИИ-анализ через DeepSeek
│   ├── technical.py        # Технический анализ
│   ├── wyckoff.py          # Анализ по Вайкоффу
│   ├── elliott.py          # Волны Эллиотта
│   └── sentiment.py        # Анализ настроений
├── 📁 backtesting/         # Бэктестинг
│   ├── engine.py           # Движок бэктеста
│   ├── enhanced_backtester.py
│   └── metrics.py          # Метрики производительности
├── 📁 visualization/       # Визуализация
│   └── backtest_plotter.py # Построение графиков
├── 📁 signals/            # Генерация сигналов
│   └── generator.py        # Генератор торговых сигналов
├── 📁 examples/           # Примеры использования
│   ├── quick_start.py
│   ├── visual_backtest.py
│   └── universal_analysis.py
├── 📁 dashboard/          # Веб-дашборд
│   └── live_dashboard.py
├── 📄 .env               # Переменные окружения
├── 📄 requirements.txt   # Зависимости
└── 📄 README.md         # Документация
```

## 🎮 Использование

### 1. Базовый анализ пары

```python
from core.universal_agent import UniversalAIAgent
from core.config import AppConfig
import asyncio

async def analyze_btc():
    agent = UniversalAIAgent(AppConfig())
    
    result = await agent.analyze_pair(
        symbol="BTCUSDT",
        timeframe="4h",
        analysis_methods=["technical", "wyckoff", "elliott", "sentiment"],
        include_news=True,
        include_fundamental=True
    )
    
    signal = result['ai_signal']
    print(f"🎯 Сигнал: {signal.action}")
    print(f"📊 Уверенность: {signal.confidence:.2%}")
    print(f"💰 Цена входа: ${signal.entry_price:.2f}")
    print(f"🛑 Стоп-лосс: ${signal.stop_loss:.2f}")
    print(f"🎯 Тейк-профит: ${signal.take_profit:.2f}")
    print(f"📝 Обоснование: {signal.reasoning}")

asyncio.run(analyze_btc())
```

### 2. Командная строка

```bash
# Анализ одной пары
python cli.py analyze BTCUSDT --timeframe 4h --methods technical wyckoff

# Анализ с выводом в JSON
python cli.py analyze ETHUSDT --timeframe 1d --format json

# Анализ без новостей
python cli.py analyze SOLUSDT --no-news --no-fundamental
```

### 3. Бэктестирование с визуализацией

```python
from backtesting.enhanced_backtester import EnhancedBacktester
from core.universal_agent import UniversalAIAgent
import asyncio

async def run_backtest():
    agent = UniversalAIAgent(AppConfig())
    backtester = EnhancedBacktester(agent)
    
    result = await backtester.run_enhanced_backtest(
        symbol="BTCUSDT",
        timeframe="4h",
        analysis_methods=["technical", "wyckoff"],
        start_date="2024-01-01",
        end_date="2024-03-01"
    )
    
    # Генерация графиков
    report = backtester.generate_comprehensive_report(result, "BTCUSDT", "4h")
    
    # Сохранение в HTML
    import plotly.io as pio
    pio.write_html(report['main_chart'], 'backtest_results.html')
    print("✅ График сохранен в backtest_results.html")

asyncio.run(run_backtest())
```

### 4. Веб-дашборд

```bash
# Запуск интерактивного дашборда
python dashboard/live_dashboard.py

# Откройте в браузере: http://localhost:8050
```

## 📊 Методы анализа

### Технический анализ
- RSI, MACD, Bollinger Bands
- Скользящие средние (SMA, EMA)
- Уровни поддержки/сопротивления
- Анализ объема

### Анализ Вайкоффа
- Фазы накопления/распределения
- Паттерны Spring/Upthrust
- Анализ спроса/предложения

### Волны Эллиотта
- Идентификация импульсных волн
- Коррекционные волны
- Соотношения Фибоначчи

### Сентимент-анализ
- Анализ новостей через DeepSeek
- Настроения социальных сетей
- Фундаментальные факторы

## ⚙️ Конфигурация

### Настройка параметров анализа

```python
# custom_config.py
from core.config import AppConfig, AnalysisConfig

class CustomConfig(AppConfig):
    def __init__(self):
        super().__init__()
        self.analysis.default_timeframes = ['1h', '4h', '1d']
        self.analysis.supported_indicators = [
            'RSI', 'MACD', 'BB', 'EMA', 'VWAP', 'ATR'
        ]
        self.deepseek.model = "deepseek-chat"  # Модель DeepSeek
```

### Кастомные промпты для ИИ

```python
# analysis/custom_prompts.py
CUSTOM_PROMPTS = {
    'conservative': """
    Будь консервативным аналитиком. Рискуй минимально.
    Давай сигналы только при уверенности выше 80%.
    """,
    
    'aggressive': """
    Будь агрессивным трейдером. Ищи высокодоходные возможности.
    Принимай риски при уверенности от 60%.
    """
}
```

## 📈 Примеры вывода

### Торговый сигнал
```
🎯 BTCUSDT | 4h
📊 Сигнал: BUY (уверенность: 85%)
💰 Вход: $45,250.50
🛑 Стоп-лосс: $43,987.25  
🎯 Тейк-профит: $48,750.80
📝 Обоснование: Сильный бычий дивергенция на RSI, пробитие ключевого 
уровня сопротивления на высоком объеме. Фаза накопления по Вайкоффу 
завершена, начинается импульсный рост.
```

### Результаты бэктеста
```
📊 РЕЗУЛЬТАТЫ БЭКТЕСТА:
Периодов анализа: 150
Сгенерировано сигналов: 45
Точность сигналов: 72.50%
Общая доходность: 24.80%
Buy & Hold доходность: 18.20%
Коэффициент Шарпа: 1.85
Максимальная просадка: -8.40%
```

## 🐛 Устранение неисправностей

### Частые проблемы

**Ошибка: "Invalid API Key"**
```bash
# Проверьте .env файл
cat .env
# Убедитесь что ключи правильные и без кавычек
```

**Ошибка: "Connection timeout"**
```python
# Увеличьте таймауты в config.py
self.request_timeout = 30
```

**Ошибка: "Module not found"**
```bash
# Переустановите зависимости
pip install --force-reinstall -r requirements.txt
```

### Логирование

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔧 Расширение функциональности

### Добавление нового метода анализа

1. Создайте файл в `analysis/`:
```python
# analysis/harmonic.py
from dataclasses import dataclass

@dataclass
class HarmonicPattern:
    pattern_type: str
    confidence: float

class HarmonicAnalyzer:
    def analyze(self, df) -> HarmonicPattern:
        # Ваша логика анализа
        pass
```

2. Интегрируйте в ИИ-агент:
```python
# В universal_agent.py
from analysis.harmonic import HarmonicAnalyzer

class UniversalAIAgent:
    def __init__(self):
        self.harmonic_analyzer = HarmonicAnalyzer()
```

### Подключение новых бирж

```python
# data/exchanges/__init__.py
class ExchangeInterface:
    async def get_klines(self, symbol, timeframe):
        pass

class BybitFetcher(ExchangeInterface):
    # Реализация для Bybit
    pass
```

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. Подробнее см. в файле LICENSE.

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие проекта!

1. Форкните репозиторий
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add amazing feature'`)
4. Запушите branch (`git push origin feature/amazing-feature`) 
5. Откройте Pull Request

## 📞 Поддержка

- 📧 Email: support@crypto-ai-agent.com
- 💬 Issues: [GitHub Issues](https://github.com/your-username/crypto-ai-agent/issues)
- 📚 Документация: [Wiki](https://github.com/your-username/crypto-ai-agent/wiki)

## ⚠️ Предупреждение

**ВАЖНО**: Этот инструмент предназначен для образовательных и исследовательских целей. 

- Не является финансовой рекомендацией
- Торговля криптовалютами связана с высокими рисками
- Всегда тестируйте стратегии на исторических данных
- Используйте только те средства, которые можете позволить себе потерять

---

<div align="center">

**Сделано с ❤️ для сообщества трейдеров**

[⬆️ Наверх](#-ии-агент-для-анализа-крипторынка)

</div>