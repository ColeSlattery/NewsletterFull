import os
import statistics
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncpg
from dataclasses import dataclass

@dataclass
class HistoricalIpoData:
    """Data structure for historical IPO information"""
    cik: str
    name: str
    ticker: str
    sector: str
    industry: str
    ipo_date: datetime
    ipo_price: float
    proposed_price_low: Optional[float]
    proposed_price_high: Optional[float]
    shares_offered: Optional[int]
    raised_amount: Optional[float]
    revenue: Optional[float]
    net_income: Optional[float]
    revenue_growth_yoy: Optional[float]
    gross_margin: Optional[float]
    operating_margin: Optional[float]
    free_cash_flow: Optional[float]
    cash_burn: Optional[float]
    enterprise_value: Optional[float]
    market_cap_at_ipo: Optional[float]
    first_day_return: Optional[float]
    first_week_return: Optional[float]
    first_month_return: Optional[float]
    first_quarter_return: Optional[float]
    first_year_return: Optional[float]
    market_cap_category: str
    growth_stage: str
    data_completeness: float

@dataclass
class SimilarityMatch:
    """Data structure for IPO similarity matches"""
    ticker: str
    name: str
    similarity_score: float
    matching_factors: List[str]
    revenue_growth: Optional[float] = None
    gross_margin: Optional[float] = None
    market_cap: Optional[float] = None
    first_day_return: Optional[float] = None
    first_week_return: Optional[float] = None
    first_month_return: Optional[float] = None

@dataclass
class HistoricalBenchmark:
    """Data structure for historical benchmarks"""
    metric_name: str
    current_value: float
    historical_median: float
    historical_mean: float
    historical_std: float
    percentile_rank: float
    similar_ipos_median: float
    similar_ipos_mean: float
    similar_ipos_std: float
    similar_ipos_percentile: float

class HistoricalAnalysisService:
    """Service for analyzing historical IPO data and generating data-backed hype scores"""
    
    def __init__(self):
        self.base_url = os.getenv('PYTHON_API_URL', 'http://localhost:8000')
        self.db_url = os.getenv('DATABASE_URL')
        self.db_pool: Optional[asyncpg.Pool] = None
    
    async def _get_db_pool(self) -> Optional[asyncpg.Pool]:
        """Get or create database connection pool"""
        if not self.db_url:
            return None
        
        if self.db_pool is None:
            try:
                self.db_pool = await asyncpg.create_pool(
                    self.db_url,
                    min_size=1,
                    max_size=5,
                    command_timeout=30
                )
            except Exception as e:
                print(f"Error creating database pool: {e}")
                return None
        
        return self.db_pool
        
    async def analyze_ipo_hype_score(self, current_ipo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive historical analysis for IPO hype score calculation
        """
        try:
            # Step 1: Find similar historical IPOs
            similar_ipos = await self._find_similar_historical_ipos(current_ipo_data)
            
            # Step 2: Calculate historical benchmarks
            benchmarks = await self._calculate_historical_benchmarks(current_ipo_data, similar_ipos)
            
            # Step 3: Analyze search trends vs historical patterns
            search_analysis = await self._analyze_search_trends_historically(current_ipo_data, similar_ipos)
            
            # Step 4: Analyze news sentiment vs historical patterns
            sentiment_analysis = await self._analyze_sentiment_historically(current_ipo_data, similar_ipos)
            
            # Step 5: Calculate performance predictions based on historical data
            performance_predictions = await self._predict_performance_from_history(current_ipo_data, similar_ipos)
            
            # Step 6: Generate comprehensive hype score with statistical backing
            hype_score_data = await self._generate_data_backed_hype_score(
                current_ipo_data, 
                similar_ipos, 
                benchmarks, 
                search_analysis, 
                sentiment_analysis, 
                performance_predictions
            )
            
            return hype_score_data
            
        except Exception as e:
            print(f"Error in historical analysis: {str(e)}")
            return await self._get_fallback_hype_score(current_ipo_data)
    
    async def _find_similar_historical_ipos(self, current_ipo: Dict[str, Any]) -> List[SimilarityMatch]:
        """Find historically similar IPOs based on multiple criteria"""
        
        pool = await self._get_db_pool()
        if not pool:
            return []
        
        try:
            async with pool.acquire() as conn:
                # Find similar IPOs based on:
                # 1. Similar market cap category
                # 2. Similar growth stage
                # 3. Similar sector/industry
                # 4. Similar revenue growth range
                
                market_cap = current_ipo.get('implied_market_cap', 0)
                revenue_growth = current_ipo.get('revenue_growth_yoy', 0)
                sector = current_ipo.get('sector', '')
                industry = current_ipo.get('industry', '')
                
                # Calculate market cap category
                market_cap_category = None
                if market_cap:
                    market_cap_billions = market_cap / 1_000_000_000
                    if market_cap_billions < 0.3:
                        market_cap_category = "micro"
                    elif market_cap_billions < 2:
                        market_cap_category = "small"
                    elif market_cap_billions < 10:
                        market_cap_category = "mid"
                    elif market_cap_billions < 200:
                        market_cap_category = "large"
                    else:
                        market_cap_category = "mega"
                
                # Build query
                query = """
                    SELECT 
                        ticker, name, sector, industry,
                        revenue_growth_yoy, gross_margin, operating_margin,
                        market_cap_at_ipo, first_day_return, first_week_return,
                        first_month_return, market_cap_category, growth_stage
                    FROM historical_ipos
                    WHERE ipo_date < NOW()
                """
                params = []
                
                if market_cap_category:
                    query += " AND (market_cap_category = $1 OR market_cap_category IS NULL)"
                    params.append(market_cap_category)
                
                if sector:
                    query += f" AND (sector = ${len(params) + 1} OR sector IS NULL)"
                    params.append(sector)
                
                # Limit to recent IPOs (last 5 years) and limit results
                query += " AND ipo_date >= NOW() - INTERVAL '5 years'"
                query += " ORDER BY ipo_date DESC LIMIT 50"
                
                rows = await conn.fetch(query, *params)
                
                similar_matches = []
                for row in rows:
                    # Calculate similarity score
                    similarity_score = 0.0
                    factors = []
                    
                    if row['market_cap_category'] == market_cap_category:
                        similarity_score += 0.3
                        factors.append("market_cap")
                    
                    if row['sector'] == sector:
                        similarity_score += 0.2
                        factors.append("sector")
                    
                    if row['industry'] == industry:
                        similarity_score += 0.2
                        factors.append("industry")
                    
                    # Revenue growth similarity (±20%)
                    if row['revenue_growth_yoy'] and revenue_growth:
                        growth_diff = abs(row['revenue_growth_yoy'] - revenue_growth) / max(abs(revenue_growth), 1)
                        if growth_diff < 0.2:
                            similarity_score += 0.3
                            factors.append("revenue_growth")
                    
                    if similarity_score >= 0.3:  # Minimum similarity threshold
                        similar_matches.append(SimilarityMatch(
                            ticker=row['ticker'],
                            name=row['name'],
                            similarity_score=similarity_score,
                            matching_factors=factors,
                            revenue_growth=row['revenue_growth_yoy'],
                            gross_margin=row['gross_margin'],
                            first_day_return=row['first_day_return'],
                            first_week_return=row['first_week_return'],
                            first_month_return=row['first_month_return']
                        ))
                
                # Sort by similarity score
                similar_matches.sort(key=lambda x: x.similarity_score, reverse=True)
                return similar_matches[:10]  # Return top 10 matches
                
        except Exception as e:
            print(f"Error finding similar IPOs: {e}")
            return []
    
    async def _calculate_historical_benchmarks(self, current_ipo: Dict[str, Any], 
                                             similar_ipos: List[SimilarityMatch]) -> List[HistoricalBenchmark]:
        """Calculate historical benchmarks for key metrics"""
        
        pool = await self._get_db_pool()
        benchmarks = []
        
        if not pool:
            # Return empty benchmarks if no database connection
            return benchmarks
        
        try:
            async with pool.acquire() as conn:
                # Revenue Growth Benchmark
                current_revenue_growth = current_ipo.get('revenue_growth_yoy', 0)
                historical_growth_rates = await conn.fetch(
                    "SELECT revenue_growth_yoy FROM historical_ipos WHERE revenue_growth_yoy IS NOT NULL AND ipo_date >= NOW() - INTERVAL '5 years'"
                )
                historical_growth_rates = [float(row['revenue_growth_yoy']) for row in historical_growth_rates]
                similar_growth_rates = [ipo.revenue_growth for ipo in similar_ipos if ipo.revenue_growth is not None]

                benchmarks.append(HistoricalBenchmark(
                    metric_name="Revenue Growth YoY",
                    current_value=current_revenue_growth,
                    historical_median=statistics.median(historical_growth_rates) if historical_growth_rates else 0,
                    historical_mean=statistics.mean(historical_growth_rates) if historical_growth_rates else 0,
                    historical_std=statistics.stdev(historical_growth_rates) if len(historical_growth_rates) > 1 else 0,
                    percentile_rank=self._calculate_percentile_rank(current_revenue_growth, historical_growth_rates),
                    similar_ipos_median=statistics.median(similar_growth_rates) if similar_growth_rates else 0,
                    similar_ipos_mean=statistics.mean(similar_growth_rates) if similar_growth_rates else 0,
                    similar_ipos_std=statistics.stdev(similar_growth_rates) if len(similar_growth_rates) > 1 else 0,
                    similar_ipos_percentile=self._calculate_percentile_rank(current_revenue_growth, similar_growth_rates)
                ))

                # Gross Margin Benchmark
                current_gross_margin = current_ipo.get('gross_margin', 0)
                historical_margins = await conn.fetch(
                    "SELECT gross_margin FROM historical_ipos WHERE gross_margin IS NOT NULL AND ipo_date >= NOW() - INTERVAL '5 years'"
                )
                historical_margins = [float(row['gross_margin']) for row in historical_margins]
                similar_margins = [ipo.gross_margin for ipo in similar_ipos if ipo.gross_margin is not None]

                benchmarks.append(HistoricalBenchmark(
                    metric_name="Gross Margin",
                    current_value=current_gross_margin,
                    historical_median=statistics.median(historical_margins) if historical_margins else 0,
                    historical_mean=statistics.mean(historical_margins) if historical_margins else 0,
                    historical_std=statistics.stdev(historical_margins) if len(historical_margins) > 1 else 0,
                    percentile_rank=self._calculate_percentile_rank(current_gross_margin, historical_margins),
                    similar_ipos_median=statistics.median(similar_margins) if similar_margins else 0,
                    similar_ipos_mean=statistics.mean(similar_margins) if similar_margins else 0,
                    similar_ipos_std=statistics.stdev(similar_margins) if len(similar_margins) > 1 else 0,
                    similar_ipos_percentile=self._calculate_percentile_rank(current_gross_margin, similar_margins)
                ))

                # Market Cap Benchmark
                current_market_cap = current_ipo.get('implied_market_cap', 0)
                historical_market_caps = await conn.fetch(
                    "SELECT market_cap_at_ipo FROM historical_ipos WHERE market_cap_at_ipo IS NOT NULL AND ipo_date >= NOW() - INTERVAL '5 years'"
                )
                historical_market_caps = [float(row['market_cap_at_ipo']) for row in historical_market_caps]
                similar_market_caps = [ipo.market_cap for ipo in similar_ipos if ipo.market_cap is not None]

                benchmarks.append(HistoricalBenchmark(
                    metric_name="Market Cap",
                    current_value=current_market_cap,
                    historical_median=statistics.median(historical_market_caps) if historical_market_caps else 0,
                    historical_mean=statistics.mean(historical_market_caps) if historical_market_caps else 0,
                    historical_std=statistics.stdev(historical_market_caps) if len(historical_market_caps) > 1 else 0,
                    percentile_rank=self._calculate_percentile_rank(current_market_cap, historical_market_caps),
                    similar_ipos_median=statistics.median(similar_market_caps) if similar_market_caps else 0,
                    similar_ipos_mean=statistics.mean(similar_market_caps) if similar_market_caps else 0,
                    similar_ipos_std=statistics.stdev(similar_market_caps) if len(similar_market_caps) > 1 else 0,
                    similar_ipos_percentile=self._calculate_percentile_rank(current_market_cap, similar_market_caps)
                ))
        
        except Exception as e:
            print(f"Error calculating historical benchmarks: {e}")
        
        return benchmarks
    
    async def _analyze_search_trends_historically(self, current_ipo: Dict[str, Any], 
                                                similar_ipos: List[SimilarityMatch]) -> Dict[str, Any]:
        """Analyze current search trends against historical patterns"""
        current_trend_score = current_ipo.get('trend_score', 0) or 0
        average_interest = current_ipo.get('trend_average_interest', 0) or 0
        recent_interest = current_ipo.get('trend_recent_interest', 0) or 0
        live_data_available = bool(current_ipo.get('trend_data_available')) and ((average_interest + recent_interest) > 0 or current_trend_score > 0)
        trend_error = current_ipo.get('trend_error')

        pool = await self._get_db_pool()
        historical_trend_scores: List[float] = []
        similar_trend_scores: List[float] = []

        if pool:
            try:
                async with pool.acquire() as conn:
                    rows = await conn.fetch(
                        """
                        SELECT trend_score
                        FROM historical_search_trends
                        WHERE date >= NOW() - INTERVAL '18 months'
                        LIMIT 5000
                        """
                    )
                    historical_trend_scores = [float(row['trend_score']) for row in rows if row['trend_score'] is not None]

                    similar_tickers = [ipo.ticker for ipo in similar_ipos if ipo.ticker]
                    if similar_tickers:
                        rows = await conn.fetch(
                            """
                            SELECT trend_score
                            FROM historical_search_trends
                            WHERE ticker = ANY($1)
                              AND date >= NOW() - INTERVAL '18 months'
                            """,
                            similar_tickers
                        )
                        similar_trend_scores = [float(row['trend_score']) for row in rows if row['trend_score'] is not None]
            except Exception as e:
                print(f"Error analyzing search trends: {e}")

        if not historical_trend_scores:
            historical_trend_scores = [50.0]
        if not similar_trend_scores:
            similar_trend_scores = historical_trend_scores

        fallback_used = False
        fallback_source = 'live'
        effective_trend_score = float(current_trend_score)

        if not live_data_available or trend_error:
            # Fall back to historical medians
            fallback_used = True
            if similar_trend_scores:
                effective_trend_score = self._safe_median(similar_trend_scores, 55.0)
                fallback_source = 'similar'
            else:
                effective_trend_score = self._safe_median(historical_trend_scores, 55.0)
                fallback_source = 'historical'
        elif effective_trend_score <= 0 and recent_interest <= 0 and average_interest <= 0:
            # Treat flat data as missing and lean on historical peers
            fallback_used = True
            effective_trend_score = self._safe_median(similar_trend_scores, 55.0)
            fallback_source = 'similar'

        trend_percentile = self._calculate_percentile_rank(effective_trend_score, historical_trend_scores)
        similar_trend_percentile = self._calculate_percentile_rank(effective_trend_score, similar_trend_scores)

        if trend_percentile >= 90:
            trend_strength = "Exceptional"
            trend_impact = "Very High"
        elif trend_percentile >= 75:
            trend_strength = "Strong"
            trend_impact = "High"
        elif trend_percentile >= 50:
            trend_strength = "Moderate"
            trend_impact = "Medium"
        else:
            trend_strength = "Weak"
            trend_impact = "Low"

        if not fallback_used:
            data_confidence = 1.0
        elif fallback_source == 'similar':
            data_confidence = 0.75
        else:
            data_confidence = 0.6

        return {
            "current_trend_score": float(current_trend_score),
            "effective_trend_score": float(effective_trend_score),
            "historical_percentile": trend_percentile,
            "similar_ipos_percentile": similar_trend_percentile,
            "effective_percentile": similar_trend_percentile,
            "trend_strength": trend_strength,
            "trend_impact": trend_impact,
            "historical_median": self._safe_median(historical_trend_scores, 50.0),
            "similar_ipos_median": self._safe_median(similar_trend_scores, 50.0),
            "trend_volatility": statistics.stdev(historical_trend_scores) if len(historical_trend_scores) > 1 else 0,
            "data_available": live_data_available and not fallback_used,
            "used_historical_fallback": fallback_used,
            "fallback_source": fallback_source,
            "data_confidence": data_confidence,
            "historical_sample_size": len(historical_trend_scores),
            "similar_sample_size": len(similar_trend_scores)
        }
    
    async def _analyze_sentiment_historically(self, current_ipo: Dict[str, Any], 
                                           similar_ipos: List[SimilarityMatch]) -> Dict[str, Any]:
        """Analyze current sentiment against historical patterns"""
        current_sentiment = float(current_ipo.get('sentiment_score', 0) or 0)
        total_articles = int(current_ipo.get('news_total_articles', 0) or 0)
        live_data_available = bool(current_ipo.get('news_data_available')) and total_articles > 0
        news_error = current_ipo.get('news_error')

        pool = await self._get_db_pool()
        historical_sentiment_scores: List[float] = []
        similar_sentiment_scores: List[float] = []

        if pool:
            try:
                async with pool.acquire() as conn:
                    rows = await conn.fetch(
                        """
                        SELECT sentiment_score
                        FROM historical_news_sentiment
                        WHERE date >= NOW() - INTERVAL '18 months'
                        LIMIT 5000
                        """
                    )
                    historical_sentiment_scores = [float(row['sentiment_score']) for row in rows if row['sentiment_score'] is not None]

                    similar_tickers = [ipo.ticker for ipo in similar_ipos if ipo.ticker]
                    if similar_tickers:
                        rows = await conn.fetch(
                            """
                            SELECT sentiment_score
                            FROM historical_news_sentiment
                            WHERE ticker = ANY($1)
                              AND date >= NOW() - INTERVAL '18 months'
                            """,
                            similar_tickers
                        )
                        similar_sentiment_scores = [float(row['sentiment_score']) for row in rows if row['sentiment_score'] is not None]
            except Exception as e:
                print(f"Error analyzing historical sentiment: {e}")

        if not historical_sentiment_scores:
            historical_sentiment_scores = [0.0]
        if not similar_sentiment_scores:
            similar_sentiment_scores = historical_sentiment_scores

        fallback_used = False
        fallback_source = 'live'
        effective_sentiment = current_sentiment

        if not live_data_available or news_error:
            fallback_used = True
            if similar_sentiment_scores:
                effective_sentiment = self._safe_median(similar_sentiment_scores, 0.05)
                fallback_source = 'similar'
            else:
                effective_sentiment = self._safe_median(historical_sentiment_scores, 0.05)
                fallback_source = 'historical'
        elif total_articles == 0:
            fallback_used = True
            effective_sentiment = self._safe_median(similar_sentiment_scores, 0.05)
            fallback_source = 'similar'

        sentiment_percentile = self._calculate_percentile_rank(effective_sentiment, historical_sentiment_scores)
        similar_sentiment_percentile = self._calculate_percentile_rank(effective_sentiment, similar_sentiment_scores)

        if effective_sentiment > 0.2:
            sentiment_strength = "Extremely Positive"
        elif effective_sentiment > 0.1:
            sentiment_strength = "Very Positive"
        elif effective_sentiment > 0.02:
            sentiment_strength = "Moderately Positive"
        elif effective_sentiment < -0.05:
            sentiment_strength = "Negative"
        else:
            sentiment_strength = "Neutral/Negative"

        if not fallback_used:
            data_confidence = 1.0
        elif fallback_source == 'similar':
            data_confidence = 0.7
        else:
            data_confidence = 0.55

        return {
            "current_sentiment": current_sentiment,
            "effective_sentiment": effective_sentiment,
            "total_articles": total_articles,
            "historical_percentile": sentiment_percentile,
            "similar_ipos_percentile": similar_sentiment_percentile,
            "effective_percentile": similar_sentiment_percentile,
            "sentiment_strength": sentiment_strength,
            "historical_median": self._safe_median(historical_sentiment_scores, 0.0),
            "similar_ipos_median": self._safe_median(similar_sentiment_scores, 0.0),
            "data_available": live_data_available and not fallback_used,
            "used_historical_fallback": fallback_used,
            "fallback_source": fallback_source,
            "data_confidence": data_confidence,
            "historical_sample_size": len(historical_sentiment_scores),
            "similar_sample_size": len(similar_sentiment_scores)
        }
    
    async def _predict_performance_from_history(self, _current_ipo: Dict[str, Any], 
                                             similar_ipos: List[SimilarityMatch]) -> Dict[str, Any]:
        """Predict IPO performance based on historical similar IPOs"""
        
        pool = await self._get_db_pool()
        first_day_returns = []
        first_week_returns = []
        first_month_returns = []
        
        if pool:
            try:
                async with pool.acquire() as conn:
                    # Query historical performance data
                    historical_performance = await conn.fetch(
                        """
                        SELECT first_day_return, first_week_return, first_month_return
                        FROM historical_ipos
                        WHERE first_day_return IS NOT NULL 
                        AND ipo_date >= NOW() - INTERVAL '5 years'
                        """
                    )
                    
                    first_day_returns = [float(row['first_day_return']) for row in historical_performance if row['first_day_return'] is not None]
                    first_week_returns = [float(row['first_week_return']) for row in historical_performance if row['first_week_return'] is not None]
                    first_month_returns = [float(row['first_month_return']) for row in historical_performance if row['first_month_return'] is not None]
                    
                    # Also include similar IPOs' performance
                    for ipo in similar_ipos:
                        if ipo.first_day_return is not None:
                            first_day_returns.append(ipo.first_day_return)
                        if ipo.first_week_return is not None:
                            first_week_returns.append(ipo.first_week_return)
                        if ipo.first_month_return is not None:
                            first_month_returns.append(ipo.first_month_return)
            except Exception as e:
                print(f"Error predicting performance: {e}")
        
        # Calculate performance predictions
        predicted_first_day = statistics.median(first_day_returns)
        predicted_first_week = statistics.median(first_week_returns)
        predicted_first_month = statistics.median(first_month_returns)
        
        # Calculate volatility as a proxy for risk/uncertainty (lower is better)
        performance_volatility = statistics.stdev(first_day_returns) if len(first_day_returns) > 1 else 0
        
        return {
            "predicted_first_day_return": predicted_first_day,
            "predicted_first_week_return": predicted_first_week,
            "predicted_first_month_return": predicted_first_month,
            "performance_volatility": performance_volatility,
            "historical_sample_size": len(first_day_returns),
            "risk_level": "High" if performance_volatility > 0.3 else "Medium" if performance_volatility > 0.15 else "Low"
        }
    
    async def _generate_data_backed_hype_score(self, current_ipo: Dict[str, Any], 
                                             similar_ipos: List[SimilarityMatch],
                                             benchmarks: List[HistoricalBenchmark],
                                             search_analysis: Dict[str, Any],
                                             sentiment_analysis: Dict[str, Any],
                                             performance_predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive hype score with statistical backing"""
        
        # Calculate component scores
        financial_score = self._calculate_financial_score(benchmarks)
        trend_score = self._calculate_trend_score(search_analysis)
        sentiment_score = self._calculate_sentiment_score(sentiment_analysis)
        performance_score = self._calculate_performance_score(performance_predictions)
        similarity_score = self._calculate_similarity_score(similar_ipos)
        
        base_weights = {
            "financial": 0.28,
            "trend": 0.18,
            "sentiment": 0.18,
            "performance": 0.20,
            "similarity": 0.16
        }

        component_confidences = {
            "financial": 1.0 if benchmarks else 0.7,
            "trend": max(0.35, search_analysis.get("data_confidence", 0.6)),
            "sentiment": max(0.35, sentiment_analysis.get("data_confidence", 0.6)),
            "performance": min(1.0, 0.6 + 0.08 * performance_predictions.get("historical_sample_size", 0)),
            "similarity": min(1.0, 0.55 + 0.05 * len(similar_ipos))
        }

        weighted_weights = {
            key: base_weights[key] * max(component_confidences.get(key, 0.5), 0.25)
            for key in base_weights
        }
        total_weight = sum(weighted_weights.values())
        if total_weight == 0:
            weights = base_weights
        else:
            weights = {key: weighted_weights[key] / total_weight for key in weighted_weights}
        
        base_hype_score = (
            financial_score * weights["financial"] +
            trend_score * weights["trend"] +
            sentiment_score * weights["sentiment"] +
            performance_score * weights["performance"] +
            similarity_score * weights["similarity"]
        )

        # Apply a gentle optimism boost so newsletter scores surface stronger signals
        baseline_boost = 12.5
        optimism_multiplier = 1.1
        boosted_hype_score = (base_hype_score * optimism_multiplier) + baseline_boost
        final_hype_score = max(35.0, min(100.0, boosted_hype_score))
        
        # Generate detailed analysis
        analysis = self._generate_detailed_analysis(
            current_ipo, benchmarks, search_analysis, sentiment_analysis, 
            performance_predictions, similar_ipos
        )
        
        return {
            "hype_score": round(final_hype_score, 1),
            "component_scores": {
                "financial_score": round(financial_score, 1),
                "trend_score": round(trend_score, 1),
                "sentiment_score": round(sentiment_score, 1),
                "performance_score": round(performance_score, 1),
                "similarity_score": round(similarity_score, 1)
            },
            "weight_allocation": {k: round(v, 3) for k, v in weights.items()},
            "analysis": analysis,
            "key_factors": self._extract_key_factors(benchmarks, search_analysis, sentiment_analysis),
            "recommendation": self._generate_recommendation(final_hype_score),
            "risk_level": self._assess_risk_level(performance_predictions, benchmarks),
            "historical_context": {
                "similar_ipos_count": len(similar_ipos),
                "benchmarks_analyzed": len(benchmarks)
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def _calculate_percentile_rank(self, value: float, data: List[float]) -> float:
        """Calculate percentile rank of a value in a dataset"""
        if not data:
            return 50.0
        
        sorted_data = sorted(data)
        rank = sum(1 for x in sorted_data if x < value)
        return (rank / len(sorted_data)) * 100
    
    @staticmethod
    def _safe_median(values: List[float], default: float) -> float:
        """Safely compute the median of a list, returning a default when empty."""
        filtered = [float(v) for v in values if v is not None]
        if not filtered:
            return default
        if len(filtered) == 1:
            return float(filtered[0])
        try:
            return statistics.median(filtered)
        except statistics.StatisticsError:
            return float(filtered[0])

    def _calculate_financial_score(self, benchmarks: List[HistoricalBenchmark]) -> float:
        """Calculate financial score based on historical benchmarks"""
        if not benchmarks:
            return 50.0
        
        scores = []
        for benchmark in benchmarks:
            # Weight similar IPOs more heavily than general historical data
            similar_percentile = benchmark.similar_ipos_percentile
            general_percentile = benchmark.percentile_rank  # Use percentile_rank instead of historical_percentile
            
            # 70% weight on similar IPOs, 30% on general historical
            weighted_score = (similar_percentile * 0.7) + (general_percentile * 0.3)
            scores.append(weighted_score)
        
        return statistics.mean(scores)
    
    def _calculate_trend_score(self, search_analysis: Dict[str, Any]) -> float:
        """Calculate trend score based on historical search patterns"""
        percentile = search_analysis.get("effective_percentile", search_analysis.get("similar_ipos_percentile", 50))
        strength = search_analysis.get("trend_strength", "Moderate")
        data_confidence = search_analysis.get("data_confidence", 1.0)
        
        strength_multiplier = {
            "Exceptional": 1.2,
            "Strong": 1.1,
            "Moderate": 1.0,
            "Weak": 0.8
        }.get(strength, 1.0)
        
        base_score = min(100, percentile * strength_multiplier)
        confidence_multiplier = 0.6 + (0.4 * max(0.0, min(1.0, data_confidence)))
        score = base_score * confidence_multiplier
        
        return max(35.0, min(100, score))
    
    def _calculate_sentiment_score(self, sentiment_analysis: Dict[str, Any]) -> float:
        """Calculate sentiment score based on historical sentiment patterns"""
        percentile = sentiment_analysis.get("effective_percentile", sentiment_analysis.get("similar_ipos_percentile", 50))
        strength = sentiment_analysis.get("sentiment_strength", "Moderately Positive")
        data_confidence = sentiment_analysis.get("data_confidence", 1.0)
        
        strength_multiplier = {
            "Extremely Positive": 1.2,
            "Very Positive": 1.1,
            "Moderately Positive": 1.0,
            "Neutral/Negative": 0.7,
            "Negative": 0.6
        }.get(strength, 1.0)
        
        base_score = min(100, percentile * strength_multiplier)
        confidence_multiplier = 0.6 + (0.4 * max(0.0, min(1.0, data_confidence)))
        score = base_score * confidence_multiplier
        
        return max(30.0, min(100, score))
    
    def _calculate_performance_score(self, performance_predictions: Dict[str, Any]) -> float:
        """Calculate performance score based on historical performance predictions"""
        predicted_return = performance_predictions.get("predicted_first_day_return", 0)
        volatility = performance_predictions.get("performance_volatility", 0.2)
        
        # Convert predicted return to score (0-100)
        # 0% return = 50, 50% return = 100, -50% return = 0
        return_score = max(0, min(100, 50 + (predicted_return * 100)))
        
        # Adjust by volatility (lower volatility boosts score, higher reduces). Map volatility [0, 0.5+] to multiplier [1.1, 0.7]
        volatility = max(0.0, min(0.5, volatility))
        multiplier = 1.1 - (volatility * 0.8 / 0.5)
        return min(100, return_score * multiplier)
    
    def _calculate_similarity_score(self, similar_ipos: List[SimilarityMatch]) -> float:
        """Calculate similarity score based on how many similar IPOs were found"""
        if not similar_ipos:
            return 30.0  # Low score if no similar IPOs found
        
        # Average similarity score of top matches
        avg_similarity = statistics.mean([ipo.similarity_score for ipo in similar_ipos])
        
        # Bonus for having multiple high-quality matches
        quality_bonus = min(20, len(similar_ipos) * 5)
        
        return min(100, (avg_similarity * 100) + quality_bonus)
    
    # Removed overall confidence scoring: we present a single definitive hype score without a confidence field
    
    def _generate_detailed_analysis(self, _current_ipo: Dict[str, Any], 
                                  benchmarks: List[HistoricalBenchmark],
                                  search_analysis: Dict[str, Any],
                                  sentiment_analysis: Dict[str, Any],
                                  performance_predictions: Dict[str, Any],
                                  similar_ipos: List[SimilarityMatch]) -> str:
        """Generate detailed analysis with historical context"""
        
        analysis_parts = []
        
        # Financial analysis
        if benchmarks:
            top_benchmark = max(benchmarks, key=lambda b: b.similar_ipos_percentile)
            analysis_parts.append(
                f"Financial Analysis: {top_benchmark.metric_name} ranks in the {top_benchmark.similar_ipos_percentile:.1f}th percentile "
                f"compared to similar historical IPOs, indicating {'strong' if top_benchmark.similar_ipos_percentile > 75 else 'moderate' if top_benchmark.similar_ipos_percentile > 50 else 'weak'} financial positioning."
            )
        
        # Trend analysis
        trend_strength = search_analysis.get("trend_strength", "Moderate")
        trend_percentile = search_analysis.get("similar_ipos_percentile", 50)
        analysis_parts.append(
            f"Search Interest: Current trend strength is {trend_strength.lower()} with {trend_percentile:.1f}th percentile ranking "
            f"among similar historical IPOs, suggesting {'exceptional' if trend_percentile > 90 else 'strong' if trend_percentile > 75 else 'moderate'} market interest."
        )
        if search_analysis.get("used_historical_fallback"):
            analysis_parts.append("Live search activity was sparse; leveraged historical peer baselines to avoid penalising the score.")
        
        # Sentiment analysis
        sentiment_strength = sentiment_analysis.get("sentiment_strength", "Moderately Positive")
        sentiment_percentile = sentiment_analysis.get("similar_ipos_percentile", 50)
        analysis_parts.append(
            f"News Sentiment: {sentiment_strength} sentiment with {sentiment_percentile:.1f}th percentile ranking "
            f"compared to similar IPOs, indicating {'very positive' if sentiment_percentile > 90 else 'positive' if sentiment_percentile > 75 else 'neutral'} media coverage."
        )
        if sentiment_analysis.get("used_historical_fallback"):
            analysis_parts.append("Current media coverage is thin; sentiment pulled from historical peers to maintain balance.")
        
        # Performance prediction
        predicted_return = performance_predictions.get("predicted_first_day_return", 0)
        analysis_parts.append(
            f"Performance Prediction: Based on {len(similar_ipos)} similar historical IPOs, "
            f"predicted first-day return of {predicted_return:.1%}."
        )
        
        # Similar IPOs context
        if similar_ipos:
            avg_similarity = statistics.mean([ipo.similarity_score for ipo in similar_ipos])
            analysis_parts.append(
                f"Historical Context: Found {len(similar_ipos)} similar IPOs with average similarity score of {avg_similarity:.2f}, "
                f"providing strong historical precedent for analysis."
            )
        
        return " ".join(analysis_parts)
    
    def _extract_key_factors(self, benchmarks: List[HistoricalBenchmark],
                           search_analysis: Dict[str, Any],
                           sentiment_analysis: Dict[str, Any]) -> List[str]:
        """Extract key factors driving the hype score"""
        factors = []
        
        # Financial factors
        for benchmark in benchmarks:
            if benchmark.similar_ipos_percentile > 80:
                factors.append(f"Strong {benchmark.metric_name} vs similar IPOs")
            elif benchmark.similar_ipos_percentile < 30:
                factors.append(f"Weak {benchmark.metric_name} vs similar IPOs")
        
        # Trend factors
        trend_strength = search_analysis.get("trend_strength", "Moderate")
        if trend_strength in ["Exceptional", "Strong"]:
            factors.append(f"{trend_strength} search interest")
        
        # Sentiment factors
        sentiment_strength = sentiment_analysis.get("sentiment_strength", "Moderately Positive")
        if "Positive" in sentiment_strength:
            factors.append(f"{sentiment_strength} media sentiment")
        
        return factors[:5]  # Limit to top 5 factors
    
    def _generate_recommendation(self, hype_score: float) -> str:
        """Generate investment recommendation based on the definitive hype score"""
        if hype_score >= 85:
            return "Strong Buy"
        elif hype_score >= 70:
            return "Buy"
        elif hype_score >= 50:
            return "Hold"
        else:
            return "Sell"
    
    def _assess_risk_level(self, performance_predictions: Dict[str, Any], 
                         _benchmarks: List[HistoricalBenchmark]) -> str:
        """Assess risk level based on performance predictions and benchmarks"""
        volatility = performance_predictions.get("performance_volatility", 0.2)
        
        if volatility > 0.4:
            return "High"
        elif volatility > 0.2:
            return "Medium"
        else:
            return "Low"
    
    async def _get_fallback_hype_score(self, _current_ipo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback hype score when historical analysis fails"""
        return {
            "hype_score": 50.0,
            "component_scores": {
                "financial_score": 50.0,
                "trend_score": 50.0,
                "sentiment_score": 50.0,
                "performance_score": 50.0,
                "similarity_score": 30.0
            },
            "analysis": "Historical analysis unavailable. Using basic scoring methodology.",
            "key_factors": ["Limited historical data available"],
            "recommendation": "Hold",
            "risk_level": "High",
            "historical_context": {
                "similar_ipos_count": 0,
                "benchmarks_analyzed": 0
            },
            "last_updated": datetime.now().isoformat()
        }
