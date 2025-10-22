import json
from typing import Dict, List
from dataclasses import dataclass
import logging
from google import genai
import asyncio

@dataclass
class SentimentAnalysis:
    overall_sentiment: str  # 'BULLISH', 'BEARISH', 'NEUTRAL'
    confidence: float
    positive_factors: List[str]
    negative_factors: List[str]
    score: float

class SentimentAnalyzer:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = "gemini-2.0-flash"
        self.logger = logging.getLogger(__name__)
        # Официальный клиент Gemini
        self.client = genai.Client(api_key=self.api_key, http_options={"api_version": "v1"})
    
    async def analyze_news(self, symbol: str, news_data: List[Dict]) -> SentimentAnalysis:
        """Анализ новостей через официальный Gemini SDK"""
        prompt = self._create_sentiment_prompt(symbol, news_data)
        
        # Простейшие ретраи для временных ошибок перегрузки (503/UNAVAILABLE)
        for attempt in range(3):
            try:
                def _call():
                    return self.client.models.generate_content(
                        model=self.model,
                        contents=prompt,
                        config={
                            "temperature": 0.3,
                            "max_output_tokens": 800,
                        },
                    )
                
                result = await asyncio.to_thread(_call)
                
                # Извлекаем агрегированный текст
                content_text = None
                try:
                    content_text = getattr(result, 'text', None)
                except Exception:
                    content_text = None
                
                if not content_text:
                    try:
                        as_dict = getattr(result, 'to_dict', None)
                        if callable(as_dict):
                            asd = as_dict()
                            candidates = asd.get('candidates') if isinstance(asd, dict) else None
                            if isinstance(candidates, list) and candidates:
                                content = (candidates[0].get('content') or {})
                                parts = content.get('parts') or []
                                if isinstance(parts, list) and parts:
                                    content_text = parts[0].get('text')
                    except Exception:
                        pass
                
                if not content_text or not isinstance(content_text, str):
                    self.logger.error("Gemini SDK: не удалось извлечь текст ответа (sentiment)")
                    return self._get_default_sentiment()
                
                # Парсим JSON
                sentiment_data = self._try_parse_json(content_text)
                if sentiment_data is None:
                    self.logger.error(f"Gemini SDK: ответ не JSON (sentiment). Фрагмент: {content_text[:200]}")
                    return self._get_default_sentiment()
                
                return SentimentAnalysis(
                    overall_sentiment=sentiment_data.get('overall_sentiment', 'NEUTRAL'),
                    confidence=sentiment_data.get('confidence', 0.5),
                    positive_factors=sentiment_data.get('positive_factors', []),
                    negative_factors=sentiment_data.get('negative_factors', []),
                    score=sentiment_data.get('sentiment_score', 0.0)
                )
            except Exception as e:
                msg = str(e)
                if '503' in msg or 'UNAVAILABLE' in msg:
                    await asyncio.sleep(1.0 * (attempt + 1))
                    continue
                self.logger.error(f"Error in sentiment analysis: {e}")
                return self._get_default_sentiment()
        
        # Все попытки исчерпаны
        self.logger.error("Gemini SDK: все попытки запроса исчерпаны (503/UNAVAILABLE) (sentiment)")
        return self._get_default_sentiment()
    
    def _create_sentiment_prompt(self, symbol: str, news_data: List[Dict]) -> str:
        """Создание промпта для анализа настроений"""
        if not news_data:
            news_text = "Новости отсутствуют"
        else:
            news_text = "\n".join([f"- {news.get('title', 'No title')} ({news.get('source', 'Unknown')})" 
                                  for news in news_data[:5]])
        
        prompt = f"""
        Analyze the sentiment for {symbol} based on the following news:
        
        {news_text}
        
        Return your analysis in JSON format with the following structure:
        {{
            "overall_sentiment": "BULLISH/BEARISH/NEUTRAL",
            "confidence": 0.0-1.0,
            "sentiment_score": -1.0 to 1.0,
            "positive_factors": ["list", "of", "positive", "factors"],
            "negative_factors": ["list", "of", "negative", "factors"]
        }}
        
        Be objective and focus on factual impact on the cryptocurrency price.
        """
        
        return prompt
    
    def _get_default_sentiment(self) -> SentimentAnalysis:
        """Сентимент-анализ по умолчанию"""
        return SentimentAnalysis(
            overall_sentiment='NEUTRAL',
            confidence=0.0,
            positive_factors=[],
            negative_factors=[],
            score=0.0
        )