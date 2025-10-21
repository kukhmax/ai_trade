import aiohttp
import json
from typing import Dict, List
from dataclasses import dataclass
import logging

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
        self.logger = logging.getLogger(__name__)
    
    async def analyze_news(self, symbol: str, news_data: List[Dict]) -> SentimentAnalysis:
        """Анализ новостей через DeepSeek API"""
        prompt = self._create_sentiment_prompt(symbol, news_data)
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a financial sentiment analysis expert. Analyze the given crypto news and provide sentiment analysis in JSON format."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "response_format": {"type": "json_object"}
                }
                
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    result = await response.json()
                    sentiment_data = json.loads(result['choices'][0]['message']['content'])
                    
                    return SentimentAnalysis(
                        overall_sentiment=sentiment_data.get('overall_sentiment', 'NEUTRAL'),
                        confidence=sentiment_data.get('confidence', 0.5),
                        positive_factors=sentiment_data.get('positive_factors', []),
                        negative_factors=sentiment_data.get('negative_factors', []),
                        score=sentiment_data.get('sentiment_score', 0.0)
                    )
                    
        except Exception as e:
            self.logger.error(f"Error in sentiment analysis: {e}")
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