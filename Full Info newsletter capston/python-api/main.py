from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

from services.trends_service import TrendsService
from services.yahoo_service import YahooFinanceService
from services.news_service import NewsService
from services.pythonanywhere_service import PythonAnywhereService
from services.openai_service import OpenAIService
from services.historical_analysis_service import HistoricalAnalysisService

# Load environment variables
load_dotenv()

app = FastAPI(title="IPO Hype Tracker API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
trends_service = TrendsService()
yahoo_service = YahooFinanceService()
news_service = NewsService()
pythonanywhere_service = PythonAnywhereService()
openai_service = OpenAIService()
historical_analysis_service = HistoricalAnalysisService()

# Pydantic models
class CompanyRequest(BaseModel):
    companies: List[str]

class HypeScoreRequest(BaseModel):
    company_name: str
    search_data: Dict[str, Any]
    news_data: Dict[str, Any]
    stock_data: Dict[str, Any]

class IPORequest(BaseModel):
    limit: Optional[int] = 10

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "IPO Hype Tracker API"}

# Google Trends endpoints
@app.post("/api/trends/search")
async def get_trends_data(request: CompanyRequest):
    """Get Google Trends data for multiple companies"""
    try:
        trends_data = await trends_service.get_trends_data(request.companies)
        return {"success": True, "data": trends_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/trends/interest-over-time")
async def get_interest_over_time(request: CompanyRequest):
    """Get interest over time for companies"""
    try:
        interest_data = await trends_service.get_interest_over_time(request.companies)
        return {"success": True, "data": interest_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Yahoo Finance endpoints
@app.post("/api/yahoo/stock-data")
async def get_stock_data(request: CompanyRequest):
    """Get stock data for multiple companies"""
    try:
        stock_data = await yahoo_service.get_stock_data(request.companies)
        return {"success": True, "data": stock_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/yahoo/historical-data")
async def get_historical_data(request: CompanyRequest):
    """Get historical stock data"""
    try:
        historical_data = await yahoo_service.get_historical_data(request.companies)
        return {"success": True, "data": historical_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/yahoo/company-info")
async def get_company_info(request: CompanyRequest):
    """Get detailed company information including financial metrics"""
    try:
        company_info = await yahoo_service.get_company_info(request.companies)
        return {"success": True, "data": company_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# News API endpoints
@app.post("/api/news/company-news")
async def get_company_news(request: CompanyRequest):
    """Get news articles for companies"""
    try:
        news_data = await news_service.get_company_news(request.companies)
        return {"success": True, "data": news_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/news/sentiment-analysis")
async def analyze_news_sentiment(request: CompanyRequest):
    """Analyze sentiment of news articles"""
    try:
        sentiment_data = await news_service.analyze_sentiment(request.companies)
        return {"success": True, "data": sentiment_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PythonAnywhere CSV Data endpoints
@app.get("/api/pythonanywhere/recent-ipos")
async def get_recent_ipos_from_csv():
    """Get recent IPOs from CSV file"""
    try:
        ipos_data = await pythonanywhere_service.get_recent_ipos()
        return ipos_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pythonanywhere/upcoming-ipos")
async def get_upcoming_ipos_from_csv():
    """Get upcoming IPOs from CSV file"""
    try:
        ipos_data = await pythonanywhere_service.get_upcoming_ipos()
        return ipos_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pythonanywhere/recent-ipo-tickers-and-prices")
async def get_recent_ipo_tickers_and_prices():
    """Get recent IPO tickers and prices from CSV file"""
    try:
        data = await pythonanywhere_service.get_recent_ipo_tickers_and_prices()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pythonanywhere/tickers-and-prices")
async def get_tickers_and_prices():
    """Get tickers and prices from CSV file"""
    try:
        data = await pythonanywhere_service.get_tickers_and_prices()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pythonanywhere/new-ipo-calendar")
async def get_new_ipo_calendar():
    """Get the consolidated IPO calendar from CSV file"""
    try:
        data = await pythonanywhere_service.get_new_ipo_calendar()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pythonanywhere/working-rolling")
async def get_working_rolling():
    """Get working rolling data from CSV file"""
    try:
        data = await pythonanywhere_service.get_working_rolling()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# OpenAI Hype Score endpoint
@app.post("/api/openai/hype-score")
async def generate_hype_score(request: HypeScoreRequest):
    """Generate AI-powered hype score for a company (uses GPT-4 mini to calculate score + analysis)"""
    try:
        hype_score = await openai_service.generate_hype_score(
            request.company_name,
            request.search_data,
            request.news_data,
            request.stock_data,
            ipo_calendar_data=None  # Can be added later if available
        )
        return {"success": True, "hype_score": hype_score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Historical Analysis endpoint (now uses GPT-4 mini to calculate score + analysis)
@app.post("/api/historical/ipo-analysis")
async def analyze_ipo_historically(request: HypeScoreRequest):
    """Generate AI-powered IPO analysis with hype score calculation and explanation"""
    try:
        # Use OpenAI service which:
        # 1. Uses GPT-4 mini to CALCULATE hype score using all data sources
        # 2. Uses GPT-4 mini to GENERATE analysis explaining the score
        hype_score_result = await openai_service.generate_hype_score(
            request.company_name,
            request.search_data,
            request.news_data,
            request.stock_data,
            ipo_calendar_data=None  # Can be added later if available
        )
        return {"success": True, "analysis": hype_score_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Combined data endpoint
@app.post("/api/combined/company-analysis")
async def get_company_analysis(request: CompanyRequest):
    """Get comprehensive analysis for companies (uses GPT-4 mini to calculate score + analysis)"""
    try:
        results = {}
        
        for company in request.companies:
            # Get all data sources
            trends_data = await trends_service.get_trends_data([company])
            stock_data = await yahoo_service.get_stock_data([company])
            news_data = await news_service.analyze_sentiment([company])  # Use sentiment analysis
            
            # Generate hype score (GPT-4 mini calculates score, then generates analysis)
            hype_score = await openai_service.generate_hype_score(
                company,
                trends_data.get(company, {}),
                news_data.get(company, {}),
                stock_data.get(company, {}),
                ipo_calendar_data=None  # Can be added later if available
            )
            
            results[company] = {
                "trends": trends_data.get(company, {}),
                "stock": stock_data.get(company, {}),
                "news": news_data.get(company, {}),
                "hype_score": hype_score
            }
        
        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
