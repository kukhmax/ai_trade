import json
import pandas as pd
from typing import Dict, List, Any
import logging
from dataclasses import dataclass
from google import genai
import asyncio

@dataclass
class AISignal:
    action: str  # BUY/SELL/HOLD
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    reasoning: str
    timeframe: str
    indicators_used: List[str]

class DeepSeekAnalyzer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "gemini-2.0-flash"
        self.logger = logging.getLogger(__name__)
        # Официальный клиент Gemini
        self.client = genai.Client(api_key=self.api_key, http_options={"api_version": "v1"})
    
    async def analyze_market(
        self,
        symbol: str,
        df: pd.DataFrame,
        analysis_methods: List[str],
        timeframe: str,
        news_data: List[Dict] = None,
        fundamental_data: Dict = None
    ) -> AISignal:
        """Основной метод анализа через ИИ API"""
        
        # Подготовка данных для ИИ
        market_context = self._prepare_market_context(
            symbol, df, analysis_methods, timeframe, news_data, fundamental_data
        )
        
        # Создание промпта для ИИ
        prompt = self._create_analysis_prompt(market_context)
        
        # Запрос к ИИ API
        response = await self._query_ai(prompt)
        
        # Парсинг ответа
        return self._parse_ai_response(response, symbol, timeframe)
    
    def _prepare_market_context(
        self,
        symbol: str,
        df: pd.DataFrame,
        analysis_methods: List[str],
        timeframe: str,
        news_data: List[Dict],
        fundamental_data: Dict
    ) -> Dict[str, Any]:
        """Подготовка полного контекста рынка для ИИ"""
        
        context = {
            'symbol': symbol,
            'timeframe': timeframe,
            'current_price': df['close'].iloc[-1],
            'price_action': self._summarize_price_action(df),
            'volume_analysis': self._analyze_volume(df),
            'requested_methods': analysis_methods,
            'technical_indicators': self._calculate_technical_indicators(df),
            'key_levels': self._find_key_levels(df),
            'market_sentiment': self._get_market_sentiment(df),
            'news_summary': self._summarize_news(news_data) if news_data else "Новости не предоставлены",
            'fundamental_data': fundamental_data or {}
        }
        
        # Добавляем специфические методы анализа
        if 'wyckoff' in analysis_methods:
            context['wyckoff_analysis'] = self._analyze_wyckoff_patterns(df)
        
        if 'elliott' in analysis_methods:
            context['elliott_analysis'] = self._analyze_elliott_waves(df)
        
        return context
    
    def _create_analysis_prompt(self, context: Dict) -> str:
        """Создание детального промпта для ИИ"""
        
        prompt = f"""
        Ты - профессиональный трейдер и финансовый аналитик с 20-летним опытом. 
        Проанализируй следующие рыночные данные и дай торговую рекомендацию.

        СИМВОЛ: {context['symbol']}
        ТАЙМФРЕЙМ: {context['timeframe']}
        ТЕКУЩАЯ ЦЕНА: {context['current_price']:.2f}

        ДАННЫХ ДЛЯ АНАЛИЗА:

        1. Ценовое действие:
        {context['price_action']}

        2. Анализ объема:
        {context['volume_analysis']}

        3. Технические индикаторы:
        {json.dumps(context['technical_indicators'], indent=2)}

        4. Ключевые уровни:
        Поддержка: {context['key_levels']['support']}
        Сопротивление: {context['key_levels']['resistance']}

        5. Рыночные настроения:
        {context['market_sentiment']}

        6. Новостной фон:
        {context['news_summary']}

        7. Запрошенные методы анализа: {', '.join(context['requested_methods'])}

        {self._add_specialized_analysis(context)}

        ПРОШУ ПРОАНАЛИЗИРОВАТЬ И ДАТЬ РЕКОМЕНДАЦИЮ:

        - Действие (BUY/SELL/HOLD)
        - Уровень уверенности (0-1)
        - Цена входа
        - Стоп-лосс
        - Тейк-профит
        - Подробное обоснование

        ОТВЕТ В ФОРМАТЕ JSON:
        {{
            "action": "BUY/SELL/HOLD",
            "confidence": 0.85,
            "entry_price": 50000.0,
            "stop_loss": 48500.0,
            "take_profit": 53000.0,
            "reasoning": "Подробное объяснение решения...",
            "timeframe": "4h",
            "indicators_used": ["RSI", "MACD", "Wyckoff"]
        }}
        """
        
        return prompt
    
    def _add_specialized_analysis(self, context: Dict) -> str:
        """Добавление специализированного анализа в промпт"""
        specialized = ""
        
        if 'wyckoff_analysis' in context:
            specialized += f"""
            8. Анализ Вайкоффа:
            {context['wyckoff_analysis']}
            """
        
        if 'elliott_analysis' in context:
            specialized += f"""
            9. Волны Эллиотта:
            {context['elliott_analysis']}
            """
            
        return specialized
    
    async def _query_ai(self, prompt: str) -> Dict:
        """Запрос к Gemini API через официальный SDK"""
        # Простейшие ретраи для временных ошибок перегрузки (503/UNAVAILABLE)
        for attempt in range(3):
            try:
                def _call():
                    return self.client.models.generate_content(
                        model=self.model,
                        contents=prompt,
                        config={
                            "temperature": 0.3,
                            "max_output_tokens": 2000,
                        },
                    )
                result = await asyncio.to_thread(_call)

                # Пытаемся извлечь текст ответа
                content_text = getattr(result, 'text', None)
                if not isinstance(content_text, str) or not content_text:
                    try:
                        as_dict = getattr(result, 'to_dict', None)
                        if callable(as_dict):
                            asd = as_dict()
                            candidates = asd.get("candidates") if isinstance(asd, dict) else None
                            if isinstance(candidates, list) and candidates:
                                content = (candidates[0].get("content") or {})
                                parts = content.get("parts") or []
                                if isinstance(parts, list) and parts:
                                    content_text = parts[0].get("text")
                    except Exception:
                        pass

                if not content_text or not isinstance(content_text, str):
                    self.logger.error("Gemini SDK: не удалось извлечь текст ответа")
                    return self._get_fallback_response()

                # Пробуем распарсить как чистый JSON
                parsed = self._try_parse_json(content_text)
                if parsed is not None:
                    return parsed

                # Если не получилось — fallback
                self.logger.error(f"Gemini SDK: ответ не JSON. Фрагмент: {content_text[:200]}")
                return self._get_fallback_response()

            except Exception as e:
                msg = str(e)
                if '503' in msg or 'UNAVAILABLE' in msg:
                    # Бэкофф перед повтором
                    await asyncio.sleep(1.0 * (attempt + 1))
                    continue
                self.logger.error(f"Gemini SDK error: {e}")
                return self._get_fallback_response()

        # Все попытки исчерпаны
        self.logger.error("Gemini SDK: все попытки запроса исчерпаны (503/UNAVAILABLE)")
        return self._get_fallback_response()
    
    def _try_parse_json(self, text: str) -> Dict[str, Any] | None:
        """Пытаемся распарсить JSON, при необходимости вырезая блок {...}."""
        try:
            return json.loads(text)
        except Exception:
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(text[start:end+1])
                except Exception:
                    return None
            return None

    def _parse_ai_response(self, response: Dict, symbol: str, timeframe: str) -> AISignal:
        """Парсинг ответа от ИИ"""
        try:
            return AISignal(
                action=response.get('action', 'HOLD'),
                confidence=response.get('confidence', 0.0),
                entry_price=response.get('entry_price', 0.0),
                stop_loss=response.get('stop_loss', 0.0),
                take_profit=response.get('take_profit', 0.0),
                reasoning=response.get('reasoning', 'Анализ не удался'),
                timeframe=timeframe,
                indicators_used=response.get('indicators_used', [])
            )
        except Exception as e:
            self.logger.error(f"Error parsing AI response: {e}")
            return self._get_fallback_signal()
    
    def _summarize_price_action(self, df: pd.DataFrame) -> str:
        """Суммаризация ценового действия"""
        current = df.iloc[-1]
        prev = df.iloc[-2]
        
        trend = "Восходящий" if current['close'] > df['close'].iloc[-20] else "Нисходящий"
        volatility = (df['high'] - df['low']).tail(10).mean()
        
        return f"""
        Тренд: {trend}
        Последняя свеча: {('Бычья' if current['close'] > current['open'] else 'Медвежья')}
        Волатильность: {volatility:.2f}
        Изменение к предыдущей свече: {((current['close'] - prev['close']) / prev['close'] * 100):.2f}%
        """
    
    def _calculate_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """Расчет технических индикаторов"""
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + gain / loss))
        
        # MACD
        ema12 = df['close'].ewm(span=12).mean()
        ema26 = df['close'].ewm(span=26).mean()
        macd = ema12 - ema26
        macd_signal = macd.ewm(span=9).mean()
        
        # Скользящие средние
        sma20 = df['close'].rolling(20).mean()
        sma50 = df['close'].rolling(50).mean()
        
        return {
            'rsi': round(rsi.iloc[-1], 2),
            'macd': round(macd.iloc[-1], 2),
            'macd_signal': round(macd_signal.iloc[-1], 2),
            'sma_20': round(sma20.iloc[-1], 2),
            'sma_50': round(sma50.iloc[-1], 2),
            'price_vs_sma20': f"{((df['close'].iloc[-1] - sma20.iloc[-1]) / sma20.iloc[-1] * 100):.2f}%"
        }
    
    def _analyze_volume(self, df: pd.DataFrame) -> str:
        """Анализ объема"""
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].tail(20).mean()
        volume_ratio = current_volume / avg_volume
        
        return f"""
        Текущий объем: {current_volume:.0f}
        Средний объем (20 периодов): {avg_volume:.0f}
        Соотношение объема: {volume_ratio:.2f}x
        """
    
    def _find_key_levels(self, df: pd.DataFrame) -> Dict:
        """Поиск ключевых уровней"""
        # Упрощенная логика для демонстрации
        recent_low = df['low'].tail(50).min()
        recent_high = df['high'].tail(50).max()
        current_price = df['close'].iloc[-1]
        
        return {
            'support': [recent_low * 0.99, recent_low * 0.98],
            'resistance': [recent_high * 1.01, recent_high * 1.02],
            'current_zone': 'support' if current_price < (recent_high + recent_low) / 2 else 'resistance'
        }
    
    def _get_market_sentiment(self, df: pd.DataFrame) -> str:
        """Анализ рыночных настроений с защитой от недостатка данных"""
        if df is None or df.empty or 'close' not in df.columns:
            return (
                "Настроения: Неопределённые\n"
                "Изменение за 1 день: 0.00%\n"
                "Изменение за 7 дней: 0.00%\n"
            )

        last = df['close'].iloc[-1]

        # Безопасное вычисление изменения за 1 день (24 бара для часового ТФ)
        if len(df) > 24:
            base_1d = df['close'].iloc[-24]
        elif len(df) > 1:
            base_1d = df['close'].iloc[0]
        else:
            base_1d = last

        price_change_1d = ((last - base_1d) / base_1d * 100) if base_1d else 0.0

        # Безопасное вычисление изменения за 7 дней (168 баров для часового ТФ)
        if len(df) > 168:
            base_7d = df['close'].iloc[-168]
        elif len(df) > 24:
            base_7d = df['close'].iloc[-24]
        elif len(df) > 1:
            base_7d = df['close'].iloc[0]
        else:
            base_7d = last

        price_change_7d = ((last - base_7d) / base_7d * 100) if base_7d else 0.0

        sentiment = "Бычий" if price_change_1d > 0 else "Медвежий"

        return f"""
        Настроения: {sentiment}
        Изменение за 1 день: {price_change_1d:.2f}%
        Изменение за 7 дней: {price_change_7d:.2f}%
        """
    
    def _analyze_wyckoff_patterns(self, df: pd.DataFrame) -> str:
        """Анализ паттернов Вайкоффа"""
        volume_avg = df['volume'].rolling(20).mean().iloc[-1]
        current_volume = df['volume'].iloc[-1]
        
        if current_volume > volume_avg * 1.5 and df['close'].iloc[-1] > df['open'].iloc[-1]:
            return "Возможна фаза накопления - высокий объем на росте"
        elif current_volume > volume_avg * 1.5 and df['close'].iloc[-1] < df['open'].iloc[-1]:
            return "Возможна фаза распределения - высокий объем на падении"
        else:
            return "Неясная фаза - требуется больше данных"
    
    def _analyze_elliott_waves(self, df: pd.DataFrame) -> str:
        """Анализ волн Эллиотта"""
        price_trend = "восходящий" if df['close'].iloc[-1] > df['close'].iloc[-50] else "нисходящий"
        return f"Предполагаемый {price_trend} тренд. Требуется больше данных для точной идентификации волн."
    
    def _summarize_news(self, news_data: List[Dict]) -> str:
        """Суммаризация новостей"""
        if not news_data:
            return "Новости отсутствуют"
        
        sentiments = [news.get('sentiment', 'neutral') for news in news_data]
        positive_count = sentiments.count('positive')
        negative_count = sentiments.count('negative')
        
        return f"""
        Всего новостей: {len(news_data)}
        Позитивных: {positive_count}
        Негативных: {negative_count}
        Нейтральных: {len(sentiments) - positive_count - negative_count}
        """
    
    def _get_fallback_response(self) -> Dict:
        """Запасной ответ при ошибках API"""
        return {
            "action": "HOLD",
            "confidence": 0.0,
            "entry_price": 0.0,
            "stop_loss": 0.0,
            "take_profit": 0.0,
            "reasoning": "Ошибка подключения к API",
            "timeframe": "N/A",
            "indicators_used": []
        }
    
    def _get_fallback_signal(self) -> AISignal:
        """Сигнал по умолчанию при ошибках"""
        return AISignal(
            action='HOLD',
            confidence=0.0,
            entry_price=0.0,
            stop_loss=0.0,
            take_profit=0.0,
            reasoning='Ошибка анализа',
            timeframe='N/A',
            indicators_used=[]
        )