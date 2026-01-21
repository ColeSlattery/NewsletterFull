import os
import asyncio
import httpx
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class NewsService:
    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY')
        self.base_url = 'https://newsapi.org/v2'
        self.gdelt_url = 'https://api.gdeltproject.org/api/v2/doc/doc'
        self.http_timeout = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=30.0)
        self.default_headers = {'User-Agent': 'IPO-Hype-Tracker/1.0'}

    async def _fetch_newsapi_articles(self, client: httpx.AsyncClient, company: str) -> Tuple[List[Dict[str, Any]], str]:
        """Fetch articles for a company using NewsAPI."""
        if not self.api_key:
            return [], "NEWS_API_KEY not found"

        url = f"{self.base_url}/everything"
        params = {
            'q': company,
            'apiKey': self.api_key,
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 20,
            'from': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        }

        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get('status') != 'ok':
                return [], data.get('message', 'Unknown NewsAPI error')

            articles: List[Dict[str, Any]] = []
            for article in data.get('articles', []):
                url_value = article.get('url') or ''
                articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': url_value,
                    'source': article.get('source', {}).get('name', ''),
                    'published_at': article.get('publishedAt', ''),
                    'content': article.get('content', ''),
                    'url_to_image': article.get('urlToImage', ''),
                    'source_type': 'newsapi'
                })

            return articles, ''

        except httpx.HTTPStatusError as e:
            return [], f"HTTP {e.response.status_code}"
        except (httpx.RequestError, ValueError, KeyError) as e:
            return [], str(e)

    async def _fetch_gdelt_articles(self, client: httpx.AsyncClient, company: str) -> Tuple[List[Dict[str, Any]], str]:
        """Fetch articles for a company using the GDELT Doc API."""
        params = {
            'query': f'"{company}"',
            'mode': 'artlist',
            'format': 'json',
            'maxrecords': 50,
            'sort': 'DateDesc'
        }

        try:
            response = await client.get(self.gdelt_url, params=params)
            response.raise_for_status()
            data = response.json()

            articles_raw = data.get('articles', [])
            articles: List[Dict[str, Any]] = []
            for article in articles_raw:
                article_url = article.get('url') or article.get('sourceurl') or ''
                published = article.get('seendate') or ''
                tone = _safe_float(article.get('tone'))
                summary = article.get('extrasummary') or article.get('documentcloudtext') or ''

                articles.append({
                    'title': article.get('title', ''),
                    'description': summary,
                    'url': article_url,
                    'source': article.get('domain', article.get('sourcecountry', 'GDELT')), 
                    'published_at': published,
                    'content': summary,
                    'tone': tone,
                    'source_type': 'gdelt'
                })

            return articles, ''

        except httpx.HTTPStatusError as e:
            return [], f"HTTP {e.response.status_code}"
        except (httpx.RequestError, ValueError, KeyError) as e:
            return [], str(e)

    @staticmethod
    def _merge_articles(primary: List[Dict[str, Any]], secondary: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge article lists from multiple sources while removing duplicates by URL."""
        merged: List[Dict[str, Any]] = []
        seen_urls = set()

        for collection in (primary, secondary):
            for article in collection:
                url_value = (article.get('url') or '').strip()
                key = url_value.lower()
                if key and key in seen_urls:
                    continue
                if key:
                    seen_urls.add(key)
                merged.append(article)

        return merged

    async def get_company_news(self, companies: List[str]) -> Dict[str, Any]:
        """Get news articles for multiple companies"""
        try:
            results = {}
            
            async with httpx.AsyncClient(timeout=self.http_timeout, headers=self.default_headers) as client:
                for company in companies:
                    try:
                        newsapi_task = self._fetch_newsapi_articles(client, company)
                        gdelt_task = self._fetch_gdelt_articles(client, company)
                        newsapi_articles, gdelt_articles = await asyncio.gather(newsapi_task, gdelt_task)

                        combined_articles = self._merge_articles(newsapi_articles[0], gdelt_articles[0])
                        total_articles = len(combined_articles)

                        metadata: Dict[str, Any] = {
                            'company': company,
                            'articles': combined_articles,
                            'total_articles': total_articles,
                            'last_updated': datetime.now().isoformat(),
                            'source_breakdown': {
                                'newsapi': len(newsapi_articles[0]),
                                'gdelt': len(gdelt_articles[0])
                            }
                        }

                        # Surface errors if both sources failed
                        newsapi_error = newsapi_articles[1]
                        gdelt_error = gdelt_articles[1]
                        if newsapi_error and gdelt_error:
                            metadata['error'] = f"NewsAPI: {newsapi_error}; GDELT: {gdelt_error}"
                        elif newsapi_error:
                            metadata['warnings'] = {'newsapi': newsapi_error}
                        elif gdelt_error:
                            metadata['warnings'] = {'gdelt': gdelt_error}

                        results[company] = metadata

                        await asyncio.sleep(0.1)

                    except (httpx.HTTPError, httpx.RequestError, ValueError, KeyError, asyncio.TimeoutError) as e:
                        print(f"Error fetching news for {company}: {str(e)}")
                        results[company] = {
                            'company': company,
                            'articles': [],
                            'total_articles': 0,
                            'error': str(e),
                            'last_updated': datetime.now().isoformat(),
                            'source_breakdown': {
                                'newsapi': 0,
                                'gdelt': 0
                            }
                        }
                        await asyncio.sleep(0.1)

            return results
            
        except Exception as e:
            print(f"Error in NewsService.get_company_news: {str(e)}")
            raise e
    
    async def analyze_sentiment(self, companies: List[str]) -> Dict[str, Any]:
        """Analyze sentiment of news articles for companies"""
        try:
            # First get the news articles
            news_data = await self.get_company_news(companies)
            results = {}
            
            for company, company_news in news_data.items():
                try:
                    if 'error' in company_news:
                        results[company] = {
                            'company': company,
                            'sentiment_score': 0,
                            'sentiment_label': 'neutral',
                            'positive_count': 0,
                            'negative_count': 0,
                            'neutral_count': 0,
                            'error': company_news['error'],
                            'last_updated': datetime.now().isoformat()
                        }
                        continue
                    
                    articles = company_news.get('articles', [])
                    if not articles:
                        results[company] = {
                            'company': company,
                            'sentiment_score': 0,
                            'sentiment_label': 'neutral',
                            'positive_count': 0,
                            'negative_count': 0,
                            'neutral_count': 0,
                            'error': 'No articles found',
                            'last_updated': datetime.now().isoformat()
                        }
                        continue
                    
                    # Simple sentiment analysis based on keywords
                    # In production, you'd use a proper sentiment analysis API
                    positive_keywords = ['growth', 'profit', 'success', 'positive', 'increase', 'gain', 'up', 'rise', 'bullish', 'strong', 'excellent', 'outstanding']
                    negative_keywords = ['loss', 'decline', 'decrease', 'down', 'fall', 'bearish', 'weak', 'poor', 'negative', 'crash', 'drop', 'trouble']
                    
                    positive_count = 0
                    negative_count = 0
                    neutral_count = 0
                    
                    for article in articles:
                        text = f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}".lower()
                        
                        positive_score = sum(1 for keyword in positive_keywords if keyword in text)
                        negative_score = sum(1 for keyword in negative_keywords if keyword in text)
                        
                        if positive_score > negative_score:
                            positive_count += 1
                        elif negative_score > positive_score:
                            negative_count += 1
                        else:
                            neutral_count += 1
                    
                    total_articles = len(articles)
                    sentiment_score = (positive_count - negative_count) / total_articles if total_articles > 0 else 0
                    
                    # Normalize to -1 to 1 scale
                    sentiment_score = max(-1, min(1, sentiment_score))
                    
                    if sentiment_score > 0.1:
                        sentiment_label = 'positive'
                    elif sentiment_score < -0.1:
                        sentiment_label = 'negative'
                    else:
                        sentiment_label = 'neutral'
                    
                    results[company] = {
                        'company': company,
                        'sentiment_score': sentiment_score,
                        'sentiment_label': sentiment_label,
                        'positive_count': positive_count,
                        'negative_count': negative_count,
                        'neutral_count': neutral_count,
                        'total_articles': total_articles,
                        'last_updated': datetime.now().isoformat()
                    }
                    
                except (ValueError, KeyError) as e:
                    print(f"Error analyzing sentiment for {company}: {str(e)}")
                    results[company] = {
                        'company': company,
                        'sentiment_score': 0,
                        'sentiment_label': 'neutral',
                        'positive_count': 0,
                        'negative_count': 0,
                        'neutral_count': 0,
                        'error': str(e),
                        'last_updated': datetime.now().isoformat()
                    }
                    
            return results
            
        except Exception as e:
            print(f"Error in NewsService.analyze_sentiment: {str(e)}")
            raise e
    
    async def get_market_news(self) -> Dict[str, Any]:
        """Get general market news"""
        try:
            if not self.api_key:
                raise ValueError("NEWS_API_KEY not found in environment variables")
                
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/everything"
                params = {
                    'q': 'IPO OR "initial public offering" OR "going public"',
                    'apiKey': self.api_key,
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'pageSize': 20,
                    'from': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
                }
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data['status'] == 'ok':
                    articles = []
                    for article in data.get('articles', []):
                        articles.append({
                            'title': article.get('title', ''),
                            'description': article.get('description', ''),
                            'url': article.get('url', ''),
                            'source': article.get('source', {}).get('name', ''),
                            'published_at': article.get('publishedAt', ''),
                            'content': article.get('content', ''),
                            'url_to_image': article.get('urlToImage', '')
                        })
                    
                    return {
                        'articles': articles,
                        'total_articles': len(articles),
                        'last_updated': datetime.now().isoformat()
                    }
                else:
                    return {
                        'articles': [],
                        'total_articles': 0,
                        'error': f"API Error: {data.get('message', 'Unknown error')}",
                        'last_updated': datetime.now().isoformat()
                    }
                    
        except Exception as e:
            print(f"Error in NewsService.get_market_news: {str(e)}")
            raise e
