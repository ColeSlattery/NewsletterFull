import os
import asyncio
from typing import List, Dict, Any
import yfinance as yf
from datetime import datetime, timedelta

class YahooFinanceService:
    def __init__(self):
        pass
        
    async def get_stock_data(self, companies: List[str]) -> Dict[str, Any]:
        """Get current stock data for multiple companies"""
        try:
            results = {}
            
            for company in companies:
                try:
                    # Get ticker info
                    ticker = yf.Ticker(company)
                    info = ticker.info
                    history = ticker.history(period="5d")
                    
                    if not history.empty:
                        latest_price = history['Close'].iloc[-1]
                        previous_close = history['Close'].iloc[-2] if len(history) > 1 else latest_price
                        change = latest_price - previous_close
                        change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
                        
                        results[company] = {
                            "symbol": company,
                            "current_price": float(latest_price),
                            "previous_close": float(previous_close),
                            "change": float(change),
                            "change_percent": float(change_percent),
                            "volume": int(history['Volume'].iloc[-1]),
                            "market_cap": info.get('marketCap', 0),
                            "pe_ratio": info.get('trailingPE', 0),
                            "eps": info.get('trailingEps', 0),
                            "dividend_yield": info.get('dividendYield', 0),
                            "sector": info.get('sector', ''),
                            "industry": info.get('industry', ''),
                            "company_name": info.get('longName', company),
                            "last_updated": datetime.now().isoformat()
                        }
                    else:
                        results[company] = {
                            "symbol": company,
                            "error": "No stock data available",
                            "last_updated": datetime.now().isoformat()
                        }
                        
                    # Rate limiting
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    print(f"Error fetching stock data for {company}: {str(e)}")
                    results[company] = {
                        "symbol": company,
                        "error": str(e),
                        "last_updated": datetime.now().isoformat()
                    }
                    
            return results
            
        except Exception as e:
            print(f"Error in YahooFinanceService.get_stock_data: {str(e)}")
            raise e
    
    async def get_historical_data(self, companies: List[str], period: str = "1mo") -> Dict[str, Any]:
        """Get historical stock data for companies"""
        try:
            results = {}
            
            for company in companies:
                try:
                    ticker = yf.Ticker(company)
                    history = ticker.history(period=period)
                    
                    if not history.empty:
                        # Convert to dictionary format
                        historical_data = []
                        for date, row in history.iterrows():
                            historical_data.append({
                                "date": date.strftime('%Y-%m-%d'),
                                "open": float(row['Open']),
                                "high": float(row['High']),
                                "low": float(row['Low']),
                                "close": float(row['Close']),
                                "volume": int(row['Volume'])
                            })
                        
                        results[company] = {
                            "symbol": company,
                            "historical_data": historical_data,
                            "period": period,
                            "last_updated": datetime.now().isoformat()
                        }
                    else:
                        results[company] = {
                            "symbol": company,
                            "historical_data": [],
                            "period": period,
                            "error": "No historical data available",
                            "last_updated": datetime.now().isoformat()
                        }
                        
                    # Rate limiting
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    print(f"Error fetching historical data for {company}: {str(e)}")
                    results[company] = {
                        "symbol": company,
                        "historical_data": [],
                        "period": period,
                        "error": str(e),
                        "last_updated": datetime.now().isoformat()
                    }
                    
            return results
            
        except Exception as e:
            print(f"Error in YahooFinanceService.get_historical_data: {str(e)}")
            raise e
    
    async def get_company_info(self, companies: List[str]) -> Dict[str, Any]:
        """Get detailed company information"""
        try:
            results = {}
            
            for company in companies:
                try:
                    ticker = yf.Ticker(company)
                    info = ticker.info
                    
                    # Calculate key IPO metrics
                    total_revenue = info.get('totalRevenue', 0)
                    net_income = info.get('netIncomeToCommon', 0)
                    revenue_growth = info.get('revenueGrowth', 0)
                    gross_margins = info.get('grossMargins', 0)
                    operating_margins = info.get('operatingMargins', 0)
                    free_cashflow = info.get('freeCashflow', 0)
                    total_debt = info.get('totalDebt', 0)
                    total_cash = info.get('totalCash', 0)
                    market_cap = info.get('marketCap', 0)
                    
                    # Calculate cash burn (negative free cash flow)
                    cash_burn = abs(free_cashflow) if free_cashflow < 0 else 0
                    
                    results[company] = {
                        "symbol": company,
                        "company_name": info.get('longName', company),
                        "sector": info.get('sector', ''),
                        "industry": info.get('industry', ''),
                        "description": info.get('longBusinessSummary', ''),
                        "website": info.get('website', ''),
                        "employees": info.get('fullTimeEmployees', 0),
                        "city": info.get('city', ''),
                        "state": info.get('state', ''),
                        "country": info.get('country', ''),
                        "exchange": info.get('exchange', ''),
                        "currency": info.get('currency', ''),
                        
                        # IPO Metrics
                        "proposed_price_low": info.get('regularMarketPrice', 0) * 0.9,  # Estimate
                        "proposed_price_high": info.get('regularMarketPrice', 0) * 1.1,  # Estimate
                        "shares_outstanding": info.get('sharesOutstanding', 0),
                        "implied_market_cap": market_cap,
                        "enterprise_value": info.get('enterpriseValue', 0),
                        
                        # Financial Metrics
                        "revenue": total_revenue,
                        "net_income": net_income,
                        "revenue_growth_yoy": revenue_growth,
                        "gross_margin": gross_margins,
                        "operating_margin": operating_margins,
                        
                        # Cash Flow
                        "cash_burn": cash_burn,
                        "free_cash_flow": free_cashflow,
                        
                        # Additional Metrics
                        "trailing_pe": info.get('trailingPE', 0),
                        "forward_pe": info.get('forwardPE', 0),
                        "peg_ratio": info.get('pegRatio', 0),
                        "price_to_sales": info.get('priceToSalesTrailing12Months', 0),
                        "price_to_book": info.get('priceToBook', 0),
                        "debt_to_equity": info.get('debtToEquity', 0),
                        "return_on_equity": info.get('returnOnEquity', 0),
                        "profit_margins": info.get('profitMargins', 0),
                        "earnings_growth": info.get('earningsGrowth', 0),
                        "dividend_yield": info.get('dividendYield', 0),
                        "payout_ratio": info.get('payoutRatio', 0),
                        "beta": info.get('beta', 0),
                        "52_week_high": info.get('fiftyTwoWeekHigh', 0),
                        "52_week_low": info.get('fiftyTwoWeekLow', 0),
                        "last_updated": datetime.now().isoformat()
                    }
                    
                    # Rate limiting
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    print(f"Error fetching company info for {company}: {str(e)}")
                    results[company] = {
                        "symbol": company,
                        "error": str(e),
                        "last_updated": datetime.now().isoformat()
                    }
                    
            return results
            
        except Exception as e:
            print(f"Error in YahooFinanceService.get_company_info: {str(e)}")
            raise e
    
    async def get_analyst_recommendations(self, companies: List[str]) -> Dict[str, Any]:
        """Get analyst recommendations for companies"""
        try:
            results = {}
            
            for company in companies:
                try:
                    ticker = yf.Ticker(company)
                    recommendations = ticker.recommendations
                    
                    if recommendations is not None and not recommendations.empty:
                        # Get latest recommendation
                        latest_rec = recommendations.iloc[-1]
                        
                        results[company] = {
                            "symbol": company,
                            "latest_recommendation": {
                                "date": latest_rec.name.strftime('%Y-%m-%d'),
                                "firm": latest_rec.get('firm', ''),
                                "to_grade": latest_rec.get('toGrade', ''),
                                "action": latest_rec.get('action', '')
                            },
                            "all_recommendations": recommendations.to_dict('records'),
                            "last_updated": datetime.now().isoformat()
                        }
                    else:
                        results[company] = {
                            "symbol": company,
                            "latest_recommendation": None,
                            "all_recommendations": [],
                            "error": "No recommendations available",
                            "last_updated": datetime.now().isoformat()
                        }
                        
                    # Rate limiting
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    print(f"Error fetching recommendations for {company}: {str(e)}")
                    results[company] = {
                        "symbol": company,
                        "latest_recommendation": None,
                        "all_recommendations": [],
                        "error": str(e),
                        "last_updated": datetime.now().isoformat()
                    }
                    
            return results
            
        except Exception as e:
            print(f"Error in YahooFinanceService.get_analyst_recommendations: {str(e)}")
            raise e
