import os
import importlib
from typing import Dict, Any, Optional, TYPE_CHECKING
from openai import AsyncOpenAI
import json

if TYPE_CHECKING:  # pragma: no cover
    from services.historical_analysis_service import HistoricalAnalysisService as _HistoricalAnalysisService


def _load_historical_analysis_service():
    try:
        module = importlib.import_module("services.historical_analysis_service")
    except ModuleNotFoundError:
        module = importlib.import_module("historical_analysis_service")
    return getattr(module, "HistoricalAnalysisService")

class OpenAIService:
    def __init__(self):
        # Use OpenRouter API endpoint - access to multiple AI models
        # Available models: openai/gpt-4, openai/gpt-3.5-turbo, anthropic/claude-3-sonnet, etc.
        # See: https://openrouter.ai/models
        # Initialize OpenRouter client with headers in default_headers parameter
        self.client = AsyncOpenAI(
            api_key=os.getenv('OPENROUTER_API_KEY'),
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "IPO Hype Tracker"
            }
        )
        HistoricalAnalysisServiceCls = _load_historical_analysis_service()
        self.historical_analysis = HistoricalAnalysisServiceCls()
        
    async def generate_hype_score(self, company_name: str, search_data: Dict[str, Any], 
                                news_data: Dict[str, Any], stock_data: Dict[str, Any],
                                ipo_calendar_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate AI-powered hype score using GPT-4 mini in two steps:
        1. Calculate hype score (0-100) as cumulative confidence in positive IPO movement
        2. Generate analysis explaining why that score was given
        """
        try:
            historical_analysis = await self._get_historical_analysis(
                company_name, search_data, news_data, stock_data
            )
            
            # Check if OpenRouter API key is available
            if not os.getenv('OPENROUTER_API_KEY'):
                print(f"[OpenAI Service] WARNING: OPENROUTER_API_KEY not set. Returning historical analysis only for {company_name}")
                return self._build_result_dict(company_name, historical_analysis, historical_analysis.get("hype_score", 50))
            
            # Step 1: Calculate hype score
            print(f"[OpenAI Service] Calling GPT-4 mini to calculate hype score for {company_name}...")
            hype_score_result = await self._calculate_hype_score_with_ai(
                company_name, search_data, news_data, stock_data, historical_analysis, ipo_calendar_data
            )
            hype_score = hype_score_result.get("hype_score", 50)
            
            # Step 2: Generate analysis
            print(f"[OpenAI Service] Calling GPT-4 mini to generate analysis for {company_name}...")
            analysis_result = await self._generate_analysis_with_ai(
                company_name, hype_score, search_data, news_data, stock_data, historical_analysis, ipo_calendar_data
            )
            
            # Combine results
            return self._build_result_dict(company_name, historical_analysis, hype_score, analysis_result)
            
        except Exception as e:
            print(f"Error generating hype score for {company_name}: {str(e)}")
            raise e
    
    async def _get_historical_analysis(self, company_name: str, search_data: Dict[str, Any],
                                      news_data: Dict[str, Any], stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get historical analysis for additional context"""
        trend_score = search_data.get("trend_score")
        average_interest = search_data.get("average_interest", 0)
        recent_interest = search_data.get("recent_interest", 0)
        trend_error = search_data.get("error")
        trend_data_available = (
            (trend_score is not None and trend_score > 0)
            or (average_interest or 0) > 0
            or (recent_interest or 0) > 0
        ) and not trend_error

        total_articles = news_data.get("total_articles", news_data.get("totalArticles", 0))
        news_error = news_data.get("error")
        news_data_available = (total_articles or 0) > 0 and not news_error

        current_ipo_data = {
            "company_name": company_name,
            "ticker": stock_data.get("symbol") or stock_data.get("ticker") or news_data.get("symbol", ""),
            "sector": stock_data.get("sector", ""),
            "industry": stock_data.get("industry", ""),
            "revenue_growth_yoy": stock_data.get("revenue_growth_yoy", 0),
            "gross_margin": stock_data.get("gross_margin", 0),
            "implied_market_cap": stock_data.get("market_cap", 0),
            "trend_score": trend_score if trend_score is not None else 0,
            "trend_average_interest": average_interest,
            "trend_recent_interest": recent_interest,
            "trend_data_available": trend_data_available,
            "trend_error": trend_error,
            "sentiment_score": news_data.get("sentiment_score", 0),
            "news_total_articles": total_articles,
            "news_positive_count": news_data.get("positive_count", 0),
            "news_negative_count": news_data.get("negative_count", 0),
            "news_neutral_count": news_data.get("neutral_count", 0),
            "news_data_available": news_data_available,
            "news_error": news_error,
            "revenue": stock_data.get("revenue", 0),
            "net_income": stock_data.get("net_income", 0),
            "operating_margin": stock_data.get("operating_margin", 0),
            "free_cash_flow": stock_data.get("free_cash_flow", 0),
            "cash_burn": stock_data.get("cash_burn", 0),
            "enterprise_value": stock_data.get("enterprise_value", 0)
        }
        return await self.historical_analysis.analyze_ipo_hype_score(current_ipo_data)
    
    async def _calculate_hype_score_with_ai(self, company_name: str, search_data: Dict[str, Any],
                                          news_data: Dict[str, Any], stock_data: Dict[str, Any],
                                          historical_analysis: Dict[str, Any],
                                          ipo_calendar_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Use GPT-4 mini to calculate hype score (0-100) as cumulative confidence in positive IPO movement"""
        prompt = self._build_hype_score_calculation_prompt(
            company_name, search_data, news_data, stock_data, historical_analysis, ipo_calendar_data
        )
        
        system_message = """You are an expert financial analyst specializing in IPO market analysis. 
        Your task is to calculate a single hype score (0-100) that represents cumulative confidence 
        that this IPO will move in a positive direction. Consider ALL available data sources including 
        search trends, news sentiment, financial metrics, stock performance, historical comparisons, 
        and market conditions. The score should be your best estimate of the likelihood of positive 
        performance. Return ONLY a JSON object with the hype_score field."""
        
        try:
            response = await self._call_openai_api(system_message, prompt, temperature=0.1, max_tokens=500)
            parsed = self._parse_json_response(response)
            
            # Validate and clamp hype score
            hype_score = parsed.get("hype_score", 50)
            hype_score = max(0, min(100, float(hype_score)))
            return {"hype_score": round(hype_score, 1)}
            
        except Exception as e:
            print(f"Error calculating hype score with AI: {str(e)}")
            return {"hype_score": historical_analysis.get("hype_score", 50)}
    
    async def _generate_analysis_with_ai(self, company_name: str, hype_score: float,
                                       search_data: Dict[str, Any], news_data: Dict[str, Any],
                                       stock_data: Dict[str, Any], historical_analysis: Dict[str, Any],
                                       ipo_calendar_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Use GPT-4 mini to generate analysis explaining why the hype score was given"""
        prompt = self._build_analysis_generation_prompt(
            company_name, hype_score, search_data, news_data, stock_data, historical_analysis, ipo_calendar_data
        )
        
        system_message = """You are an expert financial analyst specializing in IPO market analysis. 
        Your task is to provide a comprehensive analysis explaining WHY the given hype score was calculated. 
        Reference specific data points from all available sources (trends, news, financials, historical comparisons) 
        to justify the score. Be specific about which factors drove the score higher or lower. 
        Focus on actionable insights for investors."""
        
        try:
            response = await self._call_openai_api(system_message, prompt, temperature=0.2, max_tokens=1500)
            parsed = self._parse_json_response(response)
            
            return {
                "analysis": parsed.get("analysis", response),
                "key_factors": parsed.get("key_factors", []),
                "recommendation": parsed.get("recommendation", self._get_recommendation_from_score(hype_score)),
                "risk_level": parsed.get("risk_level", "Medium"),
                "market_outlook": parsed.get("market_outlook", "")
            }
            
        except Exception as e:
            print(f"Error generating analysis with AI: {str(e)}")
            return {
                "analysis": historical_analysis.get("analysis", ""),
                "key_factors": historical_analysis.get("key_factors", []),
                "recommendation": self._get_recommendation_from_score(hype_score),
                "risk_level": historical_analysis.get("risk_level", "Medium"),
                "market_outlook": ""
            }
    
    async def _call_openai_api(self, system_message: str, user_prompt: str,
                              temperature: float = 0.2, max_tokens: int = 1500) -> str:
        """Common method to call OpenAI API via OpenRouter"""
        # OpenRouter API call - headers should be set at client initialization
        # The AsyncOpenAI client for OpenRouter doesn't accept headers in create() method
        response = await self.client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    
    def _build_hype_score_calculation_prompt(self, company_name: str, search_data: Dict[str, Any],
                                           news_data: Dict[str, Any], stock_data: Dict[str, Any],
                                           historical_analysis: Dict[str, Any],
                                           ipo_calendar_data: Optional[Dict[str, Any]] = None) -> str:
        """Build prompt for calculating hype score using all available data"""
        component_scores = historical_analysis.get("component_scores", {})
        historical_context = historical_analysis.get("historical_context", {})
        
        prompt = f"""Calculate a hype score (0-100) for {company_name} that represents your cumulative confidence that this IPO will move in a positive direction. Use ALL the data below to make this assessment.

{self._format_search_trends_data(search_data)}
{self._format_news_sentiment_data(news_data)}
{self._format_financial_data(stock_data)}
HISTORICAL ANALYSIS DATA:
- Financial Score: {component_scores.get('financial_score', 50)}/100
- Trend Score: {component_scores.get('trend_score', 50)}/100
- Sentiment Score: {component_scores.get('sentiment_score', 50)}/100
- Performance Score: {component_scores.get('performance_score', 50)}/100
- Similarity Score: {component_scores.get('similarity_score', 50)}/100
- Similar IPOs Analyzed: {historical_context.get('similar_ipos_count', 0)}
- Benchmarks Analyzed: {historical_context.get('benchmarks_analyzed', 0)}
"""
        
        if ipo_calendar_data:
            prompt += f"""
IPO CALENDAR DATA:
- Expected IPO Date: {ipo_calendar_data.get('expected_date', 'N/A')}
- Proposed Price Range: ${ipo_calendar_data.get('proposed_price_low', 0):.2f} - ${ipo_calendar_data.get('proposed_price_high', 0):.2f}
- Shares Offered: {ipo_calendar_data.get('shares_offered', 0):,}
"""
        
        prompt += """
Consider ALL these factors together:
- Search trend strength indicates market interest
- News sentiment shows media/public perception
- Financial metrics show company health and growth potential
- Stock performance shows market reaction
- Historical comparisons show how similar IPOs performed
- IPO calendar data shows timing and pricing expectations

Return ONLY a JSON object in this exact format:
{
    "hype_score": 85.5
}

The hype score should be a number from 0-100 representing your cumulative confidence that this IPO will move in a positive direction based on ALL the data provided.
"""
        return prompt
    
    def _build_analysis_generation_prompt(self, company_name: str, hype_score: float,
                                         search_data: Dict[str, Any], news_data: Dict[str, Any],
                                         stock_data: Dict[str, Any], historical_analysis: Dict[str, Any],
                                         ipo_calendar_data: Optional[Dict[str, Any]] = None) -> str:
        """Build prompt for generating analysis explaining the hype score"""
        component_scores = historical_analysis.get("component_scores", {})
        
        prompt = f"""Explain WHY the hype score of {hype_score}/100 was calculated for {company_name}. This score represents cumulative confidence that the IPO will move in a positive direction.

The hype score was calculated using the following data:

{self._format_search_trends_data(search_data)}
{self._format_news_sentiment_data(news_data)}
FINANCIAL DATA:
- Revenue Growth YoY: {stock_data.get('revenue_growth_yoy', 0):.1%}
- Gross Margin: {stock_data.get('gross_margin', 0):.1%}
- Operating Margin: {stock_data.get('operating_margin', 0):.1%}
- Net Income: ${stock_data.get('net_income', 0):,.0f}
- Free Cash Flow: ${stock_data.get('free_cash_flow', 0):,.0f}
- Market Cap: ${stock_data.get('market_cap', 0):,.0f}

HISTORICAL COMPONENT SCORES:
- Financial: {component_scores.get('financial_score', 50)}/100
- Trend: {component_scores.get('trend_score', 50)}/100
- Sentiment: {component_scores.get('sentiment_score', 50)}/100
- Performance: {component_scores.get('performance_score', 50)}/100

Provide a detailed analysis explaining:
1. Why this specific hype score ({hype_score}/100) was calculated
2. Which data sources contributed most to this score (positively or negatively)
3. Key factors driving the confidence level
4. Investment recommendation based on the score
5. Risk assessment
6. Market outlook for this IPO

Return your response as JSON:
{{
    "analysis": "Detailed explanation of why the hype score was {hype_score}/100, referencing specific data points...",
    "key_factors": ["Factor 1", "Factor 2", "Factor 3"],
    "recommendation": "Buy/Hold/Sell",
    "risk_level": "Low/Medium/High",
    "market_outlook": "Brief outlook statement"
}}
"""
        return prompt
    
    def _format_search_trends_data(self, search_data: Dict[str, Any]) -> str:
        """Format search trends data for prompts"""
        return f"""SEARCH TRENDS DATA (Google Trends):
- Trend Score: {search_data.get('trend_score', 50)}
- Recent Interest: {search_data.get('recent_interest', 50)}
- Average Interest: {search_data.get('average_interest', 50)}
"""
    
    def _format_news_sentiment_data(self, news_data: Dict[str, Any]) -> str:
        """Format news sentiment data for prompts"""
        return f"""NEWS SENTIMENT DATA:
- Sentiment Score: {news_data.get('sentiment_score', 0):.2f} (range: -1 to +1)
- Total Articles: {news_data.get('total_articles', 0)}
- Positive Articles: {news_data.get('positive_count', 0)}
- Negative Articles: {news_data.get('negative_count', 0)}
- Neutral Articles: {news_data.get('neutral_count', 0)}
"""
    
    def _format_financial_data(self, stock_data: Dict[str, Any]) -> str:
        """Format financial data for prompts"""
        return f"""FINANCIAL DATA (Yahoo Finance):
- Price Change %: {stock_data.get('change_percent', 0):.2f}%
- Volume: {stock_data.get('volume', 0):,}
- Market Cap: ${stock_data.get('market_cap', 0):,.0f}
- P/E Ratio: {stock_data.get('pe_ratio', 0) if stock_data.get('pe_ratio') else 'N/A'}
- Revenue: ${stock_data.get('revenue', 0):,.0f}
- Revenue Growth YoY: {stock_data.get('revenue_growth_yoy', 0):.1%}
- Net Income: ${stock_data.get('net_income', 0):,.0f}
- Gross Margin: {stock_data.get('gross_margin', 0):.1%}
- Operating Margin: {stock_data.get('operating_margin', 0):.1%}
- Free Cash Flow: ${stock_data.get('free_cash_flow', 0):,.0f}
- Cash Burn: ${stock_data.get('cash_burn', 0):,.0f}
- Enterprise Value: ${stock_data.get('enterprise_value', 0):,.0f}
- Shares Outstanding: {stock_data.get('shares_outstanding', 0):,}
"""
    
    def _build_result_dict(self, company_name: str, historical_analysis: Dict[str, Any],
                          hype_score: float, analysis_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Build the result dictionary structure"""
        if analysis_result:
            return {
                "company_name": company_name,
                "hype_score": hype_score,
                "analysis": analysis_result.get("analysis", ""),
                "key_factors": analysis_result.get("key_factors", []),
                "recommendation": analysis_result.get("recommendation", self._get_recommendation_from_score(hype_score)),
                "risk_level": analysis_result.get("risk_level", "Medium"),
                "component_scores": historical_analysis.get("component_scores", {}),
                "historical_context": historical_analysis.get("historical_context", {}),
                "market_outlook": analysis_result.get("market_outlook", ""),
                "last_updated": historical_analysis.get("last_updated", "2024-01-01T00:00:00Z")
            }
        else:
            return {
                "company_name": company_name,
                "hype_score": hype_score,
                "analysis": historical_analysis.get("analysis", ""),
                "key_factors": historical_analysis.get("key_factors", []),
                "recommendation": historical_analysis.get("recommendation", "Hold"),
                "risk_level": historical_analysis.get("risk_level", "Medium"),
                "component_scores": historical_analysis.get("component_scores", {}),
                "historical_context": historical_analysis.get("historical_context", {}),
                "last_updated": historical_analysis.get("last_updated", "2024-01-01T00:00:00Z")
            }
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from AI response"""
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {str(e)}")
            return {}
    
    def _get_recommendation_from_score(self, hype_score: float) -> str:
        """Get recommendation based on hype score"""
        if hype_score >= 85:
            return "Strong Buy"
        elif hype_score >= 70:
            return "Buy"
        elif hype_score >= 50:
            return "Hold"
        else:
            return "Sell"
    
    async def generate_newsletter_summary(self, companies_data: Dict[str, Any]) -> str:
        """Generate a newsletter summary using OpenRouter"""
        try:
            if not os.getenv('OPENROUTER_API_KEY'):
                raise ValueError("OPENROUTER_API_KEY not found in environment variables")
            
            prompt = f"""Generate a professional newsletter summary for IPO Hype Tracker based on the following company data:

{json.dumps(companies_data, indent=2)}

Create a compelling newsletter summary that includes:
1. Market overview
2. Top performing companies
3. Key insights
4. Investment recommendations

Keep it professional, engaging, and informative for investors.
"""
            
            system_message = "You are a financial newsletter writer specializing in IPO market analysis. Write engaging, professional content for investors."
            response = await self._call_openai_api(system_message, prompt, temperature=0.7, max_tokens=1500)
            return response
            
        except Exception as e:
            print(f"Error generating newsletter summary: {str(e)}")
            raise e
