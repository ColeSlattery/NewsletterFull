import os
import asyncio
from typing import List, Dict, Any
from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime, timedelta

class TrendsService:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
        
    async def get_trends_data(self, companies: List[str]) -> Dict[str, Any]:
        """Get Google Trends data for multiple companies"""
        try:
            results = {}
            
            for company in companies:
                try:
                    # Build payload for the company
                    self.pytrends.build_payload([company], cat=0, timeframe='today 3-m', geo='US', gprop='')
                    
                    # Get interest over time
                    interest_over_time = self.pytrends.interest_over_time()
                    
                    if not interest_over_time.empty:
                        # Calculate average interest
                        avg_interest = interest_over_time[company].mean()
                        recent_interest = interest_over_time[company].tail(7).mean()
                        
                        # Get related queries
                        related_queries = self.pytrends.related_queries()
                        
                        results[company] = {
                            "average_interest": float(avg_interest),
                            "recent_interest": float(recent_interest),
                            "trend_score": float(recent_interest),  # Use recent as trend score
                            "related_queries": related_queries.get(company, {}).get('top', {}).to_dict() if related_queries.get(company) else {},
                            "last_updated": datetime.now().isoformat()
                        }
                    else:
                        results[company] = {
                            "average_interest": 0,
                            "recent_interest": 0,
                            "trend_score": 0,
                            "related_queries": {},
                            "last_updated": datetime.now().isoformat(),
                            "error": "No data available"
                        }
                        
                    # Rate limiting - wait between requests
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"Error fetching trends for {company}: {str(e)}")
                    results[company] = {
                        "average_interest": 0,
                        "recent_interest": 0,
                        "trend_score": 0,
                        "related_queries": {},
                        "last_updated": datetime.now().isoformat(),
                        "error": str(e)
                    }
                    
            return results
            
        except Exception as e:
            print(f"Error in TrendsService.get_trends_data: {str(e)}")
            raise e
    
    async def get_interest_over_time(self, companies: List[str]) -> Dict[str, Any]:
        """Get interest over time data for companies"""
        try:
            results = {}
            
            for company in companies:
                try:
                    # Build payload for the company
                    self.pytrends.build_payload([company], cat=0, timeframe='today 3-m', geo='US', gprop='')
                    
                    # Get interest over time
                    interest_over_time = self.pytrends.interest_over_time()
                    
                    if not interest_over_time.empty:
                        # Convert to dictionary with dates as keys
                        time_data = {}
                        for date, row in interest_over_time.iterrows():
                            time_data[date.strftime('%Y-%m-%d')] = float(row[company])
                        
                        results[company] = {
                            "time_series": time_data,
                            "last_updated": datetime.now().isoformat()
                        }
                    else:
                        results[company] = {
                            "time_series": {},
                            "last_updated": datetime.now().isoformat(),
                            "error": "No data available"
                        }
                        
                    # Rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"Error fetching interest over time for {company}: {str(e)}")
                    results[company] = {
                        "time_series": {},
                        "last_updated": datetime.now().isoformat(),
                        "error": str(e)
                    }
                    
            return results
            
        except Exception as e:
            print(f"Error in TrendsService.get_interest_over_time: {str(e)}")
            raise e
    
    async def get_related_topics(self, companies: List[str]) -> Dict[str, Any]:
        """Get related topics for companies"""
        try:
            results = {}
            
            for company in companies:
                try:
                    # Build payload for the company
                    self.pytrends.build_payload([company], cat=0, timeframe='today 3-m', geo='US', gprop='')
                    
                    # Get related topics
                    related_topics = self.pytrends.related_topics()
                    
                    if related_topics.get(company):
                        topics_data = related_topics[company].get('top', {})
                        results[company] = {
                            "related_topics": topics_data.to_dict() if not topics_data.empty else {},
                            "last_updated": datetime.now().isoformat()
                        }
                    else:
                        results[company] = {
                            "related_topics": {},
                            "last_updated": datetime.now().isoformat(),
                            "error": "No related topics found"
                        }
                        
                    # Rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"Error fetching related topics for {company}: {str(e)}")
                    results[company] = {
                        "related_topics": {},
                        "last_updated": datetime.now().isoformat(),
                        "error": str(e)
                    }
                    
            return results
            
        except Exception as e:
            print(f"Error in TrendsService.get_related_topics: {str(e)}")
            raise e
