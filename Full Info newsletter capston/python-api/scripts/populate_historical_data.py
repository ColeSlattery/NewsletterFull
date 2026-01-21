"""
Script to populate historical IPO data from workingRolling.csv into PostgreSQL database.

This script:
1. Extracts IPO data from PythonAnywhere's workingRolling.csv
2. Calculates historical returns using Yahoo Finance
3. Fetches financial data for each IPO
4. Stores everything in the PostgreSQL database
"""

import os
import sys
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from decimal import Decimal

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncpg
import yfinance as yf
from dotenv import load_dotenv
from services.pythonanywhere_service import PythonAnywhereService
from services.yahoo_service import YahooFinanceService

# Load environment variables from parent directory's .env.local
import pathlib
env_path = pathlib.Path(__file__).parent.parent.parent / '.env.local'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Fallback to .env files in current or parent directory
    load_dotenv()
    load_dotenv(pathlib.Path(__file__).parent.parent.parent / '.env.local')

class HistoricalDataCollector:
    """Collects and stores historical IPO data"""
    
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        
        self.pythonanywhere_service = PythonAnywhereService()
        self.yahoo_service = YahooFinanceService()
        self.db_pool: Optional[asyncpg.Pool] = None
    
    async def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            self.db_pool = await asyncpg.create_pool(
                self.db_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            print("✓ Connected to PostgreSQL database")
        except Exception as e:
            print(f"✗ Error connecting to database: {e}")
            raise
    
    async def close_db(self):
        """Close database connection"""
        if self.db_pool:
            await self.db_pool.close()
            print("✓ Database connection closed")
    
    def extract_cik_from_accession(self, accession_no: str) -> Optional[str]:
        """Extract CIK from SEC accession number (format: 0001193125-25-221906)"""
        if not accession_no:
            return None
        try:
            # CIK is typically the first part before the dash
            parts = accession_no.split('-')
            if parts:
                # Remove leading zeros and get CIK
                cik = parts[0].lstrip('0')
                return cik if cik else None
        except Exception:
            pass
        return None
    
    def parse_ipo_price(self, price_data: Any) -> Optional[float]:
        """Extract IPO price from various data formats"""
        if not price_data:
            return None
        
        if isinstance(price_data, dict):
            # Try different keys
            if 'perShare' in price_data:
                return float(price_data['perShare'])
            if 'price' in price_data:
                return float(price_data['price'])
            if 'ipo_price' in price_data:
                return float(price_data['ipo_price'])
        
        if isinstance(price_data, (int, float)):
            return float(price_data)
        
        if isinstance(price_data, str):
            # Try to extract number from string
            try:
                # Remove $ and commas
                cleaned = price_data.replace('$', '').replace(',', '').strip()
                return float(cleaned)
            except ValueError:
                pass
        
        return None
    
    def calculate_market_cap_category(self, market_cap: Optional[float]) -> Optional[str]:
        """Categorize market cap"""
        if not market_cap:
            return None
        
        market_cap_billions = market_cap / 1_000_000_000
        
        if market_cap_billions < 0.3:
            return "micro"
        elif market_cap_billions < 2:
            return "small"
        elif market_cap_billions < 10:
            return "mid"
        elif market_cap_billions < 200:
            return "large"
        else:
            return "mega"
    
    def determine_growth_stage(self, revenue: Optional[float], revenue_growth: Optional[float]) -> Optional[str]:
        """Determine growth stage based on revenue and growth"""
        if not revenue:
            return None
        
        revenue_millions = revenue / 1_000_000
        
        if revenue_millions < 10:
            return "early"
        elif revenue_millions < 100:
            return "growth"
        else:
            return "mature"
    
    def calculate_data_completeness(self, ipo_data: Dict[str, Any]) -> float:
        """Calculate data completeness score (0-1)"""
        required_fields = [
            'name', 'ticker', 'ipo_date', 'ipo_price'
        ]
        
        optional_fields = [
            'revenue', 'net_income', 'revenue_growth_yoy', 'gross_margin',
            'operating_margin', 'free_cash_flow', 'market_cap_at_ipo',
            'first_day_return', 'first_week_return', 'first_month_return'
        ]
        
        required_count = sum(1 for field in required_fields if ipo_data.get(field))
        optional_count = sum(1 for field in optional_fields if ipo_data.get(field))
        
        required_score = required_count / len(required_fields)
        optional_score = optional_count / len(optional_fields) * 0.5
        
        return min(1.0, required_score + optional_score)
    
    async def calculate_historical_returns(self, ticker: str, ipo_date: datetime, ipo_price: float) -> Dict[str, Optional[float]]:
        """Calculate historical returns using Yahoo Finance"""
        returns = {
            'first_day_return': None,
            'first_week_return': None,
            'first_month_return': None,
            'first_quarter_return': None,
            'first_year_return': None
        }
        
        try:
            # Get historical data starting from IPO date
            ticker_obj = yf.Ticker(ticker)
            
            # Calculate target dates
            first_day = ipo_date + timedelta(days=1)  # Day after IPO
            first_week = ipo_date + timedelta(days=7)
            first_month = ipo_date + timedelta(days=30)
            first_quarter = ipo_date + timedelta(days=90)
            first_year = ipo_date + timedelta(days=365)
            
            # Get historical data (1 year from IPO)
            end_date = min(datetime.now(), first_year + timedelta(days=30))
            history = ticker_obj.history(start=ipo_date, end=end_date)
            
            if history.empty:
                return returns
            
            # Find closest trading days
            def get_closest_price(target_date: datetime) -> Optional[float]:
                """Get price on or after target date"""
                if target_date > datetime.now():
                    return None
                
                # Convert target_date to timezone-aware if history index is timezone-aware
                if history.index.tz is not None:
                    # If target_date is naive, make it timezone-aware
                    if target_date.tzinfo is None:
                        # Assume UTC for naive datetime
                        from datetime import timezone
                        target_date = target_date.replace(tzinfo=timezone.utc)
                
                # Find first trading day on or after target date
                after_date = history[history.index >= target_date]
                if not after_date.empty:
                    return float(after_date['Close'].iloc[0])
                
                # Fallback to last available price before target
                before_date = history[history.index < target_date]
                if not before_date.empty:
                    return float(before_date['Close'].iloc[-1])
                
                return None
            
            # Calculate returns
            day_price = get_closest_price(first_day)
            week_price = get_closest_price(first_week)
            month_price = get_closest_price(first_month)
            quarter_price = get_closest_price(first_quarter)
            year_price = get_closest_price(first_year)
            
            if day_price:
                returns['first_day_return'] = ((day_price - ipo_price) / ipo_price) * 100
            
            if week_price:
                returns['first_week_return'] = ((week_price - ipo_price) / ipo_price) * 100
            
            if month_price:
                returns['first_month_return'] = ((month_price - ipo_price) / ipo_price) * 100
            
            if quarter_price:
                returns['first_quarter_return'] = ((quarter_price - ipo_price) / ipo_price) * 100
            
            if year_price:
                returns['first_year_return'] = ((year_price - ipo_price) / ipo_price) * 100
            
            # Rate limiting
            await asyncio.sleep(0.2)
            
        except Exception as e:
            print(f"  ⚠ Error calculating returns for {ticker}: {str(e)}")
        
        return returns
    
    async def fetch_financial_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch financial data from Yahoo Finance"""
        financial_data = {
            'revenue': None,
            'revenue_growth_yoy': None,
            'net_income': None,
            'gross_margin': None,
            'operating_margin': None,
            'free_cash_flow': None,
            'cash_burn': None,
            'enterprise_value': None,
            'market_cap': None,
            'sector': None,
            'industry': None
        }
        
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            
            # Extract financial data
            total_revenue = info.get('totalRevenue', 0) or info.get('revenue', 0)
            if total_revenue:
                financial_data['revenue'] = float(total_revenue)
            
            # Revenue growth (trailing 12 months)
            revenue_growth = info.get('revenueGrowth', None)
            if revenue_growth is not None:
                financial_data['revenue_growth_yoy'] = float(revenue_growth) * 100
            
            net_income = info.get('netIncomeToCommon', 0) or info.get('netIncome', 0)
            if net_income:
                financial_data['net_income'] = float(net_income)
            
            gross_margins = info.get('grossMargins', None)
            if gross_margins is not None:
                financial_data['gross_margin'] = float(gross_margins) * 100
            
            operating_margins = info.get('operatingMargins', None)
            if operating_margins is not None:
                financial_data['operating_margin'] = float(operating_margins) * 100
            
            free_cashflow = info.get('freeCashflow', 0)
            if free_cashflow:
                financial_data['free_cash_flow'] = float(free_cashflow)
                if free_cashflow < 0:
                    financial_data['cash_burn'] = abs(float(free_cashflow))
            
            enterprise_value = info.get('enterpriseValue', 0)
            if enterprise_value:
                financial_data['enterprise_value'] = float(enterprise_value)
            
            market_cap = info.get('marketCap', 0)
            if market_cap:
                financial_data['market_cap'] = float(market_cap)
            
            sector = info.get('sector', '')
            if sector:
                financial_data['sector'] = str(sector)
            
            industry = info.get('industry', '')
            if industry:
                financial_data['industry'] = str(industry)
            
            # Rate limiting
            await asyncio.sleep(0.2)
            
        except Exception as e:
            print(f"  ⚠ Error fetching financial data for {ticker}: {str(e)}")
        
        return financial_data
    
    async def process_ipo_row(self, row: Dict[str, Any], index: int, total: int) -> Optional[Dict[str, Any]]:
        """Process a single IPO row and return structured data"""
        print(f"\n[{index + 1}/{total}] Processing: {row.get('name', 'Unknown')}")
        
        # Extract basic info
        ticker = row.get('ticker') or row.get('symbol', '').strip()
        name = row.get('name', '').strip()
        ipo_date_str = row.get('polygon_list_date', '')
        
        if not ticker or not name or not ipo_date_str:
            print(f"  ⚠ Skipping - missing required fields (ticker: {bool(ticker)}, name: {bool(name)}, date: {bool(ipo_date_str)})")
            return None
        
        # Parse IPO date
        try:
            ipo_date = datetime.fromisoformat(ipo_date_str.replace('Z', '+00:00'))
        except Exception:
            try:
                ipo_date = datetime.strptime(ipo_date_str, '%Y-%m-%d')
            except Exception:
                print(f"  ⚠ Skipping - invalid date format: {ipo_date_str}")
                return None
        
        # Skip if IPO date is in the future
        if ipo_date > datetime.now():
            print(f"  ⚠ Skipping - IPO date is in the future: {ipo_date_str}")
            return None
        
        # Extract CIK
        accession_no = row.get('accessionNo', '')
        cik = self.extract_cik_from_accession(accession_no) or ticker  # Use ticker as fallback
        
        # Extract IPO price
        ipo_price = self.parse_ipo_price(row.get('publicOfferingPrice'))
        if not ipo_price:
            # Try current price as fallback
            current_price = row.get('current_price')
            if current_price:
                ipo_price = float(current_price)
            else:
                print(f"  ⚠ Skipping - no IPO price available")
                return None
        
        # Extract other IPO details
        proposed_price_low = self.parse_ipo_price(row.get('proposedPriceLow'))
        proposed_price_high = self.parse_ipo_price(row.get('proposedPriceHigh'))
        
        # Extract shares offered and raised amount
        securities = row.get('securities', [])
        shares_offered = None
        raised_amount = None
        
        if securities and isinstance(securities, list) and len(securities) > 0:
            sec_info = securities[0]
            if isinstance(sec_info, dict):
                shares_offered_str = sec_info.get('shares', '0')
                try:
                    shares_offered = int(shares_offered_str.replace(',', ''))
                except:
                    pass
        
        proceeds = row.get('proceedsBeforeExpenses', {})
        if isinstance(proceeds, dict) and 'total' in proceeds:
            try:
                raised_amount = float(proceeds['total'])
            except:
                pass
        
        # Build IPO data structure
        ipo_data = {
            'cik': cik,
            'name': name,
            'ticker': ticker,
            'sector': row.get('sector', '').strip() or None,
            'industry': row.get('industry', '').strip() or None,
            'ipo_date': ipo_date,
            'ipo_price': ipo_price,
            'proposed_price_low': proposed_price_low,
            'proposed_price_high': proposed_price_high,
            'shares_offered': shares_offered,
            'raised_amount': raised_amount,
        }
        
        # Calculate historical returns
        print(f"  → Calculating historical returns...")
        returns = await self.calculate_historical_returns(ticker, ipo_date, ipo_price)
        ipo_data.update(returns)
        
        # Fetch financial data
        print(f"  → Fetching financial data...")
        financial_data = await self.fetch_financial_data(ticker)
        
        # Use financial data if available
        ipo_data['revenue'] = financial_data.get('revenue')
        ipo_data['revenue_growth_yoy'] = financial_data.get('revenue_growth_yoy')
        ipo_data['net_income'] = financial_data.get('net_income')
        ipo_data['gross_margin'] = financial_data.get('gross_margin')
        ipo_data['operating_margin'] = financial_data.get('operating_margin')
        ipo_data['free_cash_flow'] = financial_data.get('free_cash_flow')
        ipo_data['cash_burn'] = financial_data.get('cash_burn')
        ipo_data['enterprise_value'] = financial_data.get('enterprise_value')
        
        # Use sector/industry from financial data if not in CSV
        if not ipo_data['sector'] and financial_data.get('sector'):
            ipo_data['sector'] = financial_data['sector']
        if not ipo_data['industry'] and financial_data.get('industry'):
            ipo_data['industry'] = financial_data['industry']
        
        # Calculate market cap at IPO
        market_cap = financial_data.get('market_cap')
        if market_cap:
            ipo_data['market_cap_at_ipo'] = market_cap
        elif shares_offered and ipo_price:
            ipo_data['market_cap_at_ipo'] = shares_offered * ipo_price
        
        # Calculate market cap category and growth stage
        market_cap_at_ipo = ipo_data.get('market_cap_at_ipo')
        ipo_data['market_cap_category'] = self.calculate_market_cap_category(market_cap_at_ipo)
        ipo_data['growth_stage'] = self.determine_growth_stage(
            ipo_data.get('revenue'),
            ipo_data.get('revenue_growth_yoy')
        )
        
        # Calculate data completeness
        ipo_data['data_completeness'] = self.calculate_data_completeness(ipo_data)
        
        return ipo_data
    
    async def store_ipo_data(self, ipo_data: Dict[str, Any]) -> bool:
        """Store IPO data in database"""
        if not self.db_pool:
            return False
        
        try:
            async with self.db_pool.acquire() as conn:
                # Check if IPO already exists
                existing = await conn.fetchrow(
                    """
                    SELECT id FROM historical_ipos 
                    WHERE ticker = $1 AND ipo_date = $2
                    """,
                    ipo_data['ticker'],
                    ipo_data['ipo_date']
                )
                
                if existing:
                    # Update existing record
                    await conn.execute(
                        """
                        UPDATE historical_ipos SET
                            cik = $1,
                            name = $2,
                            sector = $3,
                            industry = $4,
                            ipo_price = $5,
                            proposed_price_low = $6,
                            proposed_price_high = $7,
                            shares_offered = $8,
                            raised_amount = $9,
                            revenue = $10,
                            net_income = $11,
                            revenue_growth_yoy = $12,
                            gross_margin = $13,
                            operating_margin = $14,
                            free_cash_flow = $15,
                            cash_burn = $16,
                            enterprise_value = $17,
                            market_cap_at_ipo = $18,
                            first_day_return = $19,
                            first_week_return = $20,
                            first_month_return = $21,
                            first_quarter_return = $22,
                            first_year_return = $23,
                            market_cap_category = $24,
                            growth_stage = $25,
                            data_completeness = $26,
                            last_updated = NOW()
                        WHERE ticker = $27 AND ipo_date = $28
                        """,
                        ipo_data['cik'],
                        ipo_data['name'],
                        ipo_data.get('sector'),
                        ipo_data.get('industry'),
                        ipo_data['ipo_price'],
                        ipo_data.get('proposed_price_low'),
                        ipo_data.get('proposed_price_high'),
                        ipo_data.get('shares_offered'),
                        ipo_data.get('raised_amount'),
                        ipo_data.get('revenue'),
                        ipo_data.get('net_income'),
                        ipo_data.get('revenue_growth_yoy'),
                        ipo_data.get('gross_margin'),
                        ipo_data.get('operating_margin'),
                        ipo_data.get('free_cash_flow'),
                        ipo_data.get('cash_burn'),
                        ipo_data.get('enterprise_value'),
                        ipo_data.get('market_cap_at_ipo'),
                        ipo_data.get('first_day_return'),
                        ipo_data.get('first_week_return'),
                        ipo_data.get('first_month_return'),
                        ipo_data.get('first_quarter_return'),
                        ipo_data.get('first_year_return'),
                        ipo_data.get('market_cap_category'),
                        ipo_data.get('growth_stage'),
                        ipo_data.get('data_completeness'),
                        ipo_data['ticker'],
                        ipo_data['ipo_date']
                    )
                    print(f"  ✓ Updated existing record")
                else:
                    # Insert new record
                    await conn.execute(
                        """
                        INSERT INTO historical_ipos (
                            cik, name, ticker, sector, industry,
                            ipo_date, ipo_price, proposed_price_low, proposed_price_high,
                            shares_offered, raised_amount,
                            revenue, net_income, revenue_growth_yoy,
                            gross_margin, operating_margin,
                            free_cash_flow, cash_burn, enterprise_value, market_cap_at_ipo,
                            first_day_return, first_week_return, first_month_return,
                            first_quarter_return, first_year_return,
                            market_cap_category, growth_stage, data_completeness
                        ) VALUES (
                            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,
                            $12, $13, $14, $15, $16, $17, $18, $19, $20,
                            $21, $22, $23, $24, $25, $26, $27, $28
                        )
                        """,
                        ipo_data['cik'],
                        ipo_data['name'],
                        ipo_data['ticker'],
                        ipo_data.get('sector'),
                        ipo_data.get('industry'),
                        ipo_data['ipo_date'],
                        ipo_data['ipo_price'],
                        ipo_data.get('proposed_price_low'),
                        ipo_data.get('proposed_price_high'),
                        ipo_data.get('shares_offered'),
                        ipo_data.get('raised_amount'),
                        ipo_data.get('revenue'),
                        ipo_data.get('net_income'),
                        ipo_data.get('revenue_growth_yoy'),
                        ipo_data.get('gross_margin'),
                        ipo_data.get('operating_margin'),
                        ipo_data.get('free_cash_flow'),
                        ipo_data.get('cash_burn'),
                        ipo_data.get('enterprise_value'),
                        ipo_data.get('market_cap_at_ipo'),
                        ipo_data.get('first_day_return'),
                        ipo_data.get('first_week_return'),
                        ipo_data.get('first_month_return'),
                        ipo_data.get('first_quarter_return'),
                        ipo_data.get('first_year_return'),
                        ipo_data.get('market_cap_category'),
                        ipo_data.get('growth_stage'),
                        ipo_data.get('data_completeness')
                    )
                    print(f"  ✓ Stored new record")
                
                return True
                
        except Exception as e:
            print(f"  ✗ Error storing data: {str(e)}")
            return False
    
    async def run(self, limit: Optional[int] = None, start_from: int = 0):
        """Main execution method"""
        print("=" * 80)
        print("HISTORICAL IPO DATA COLLECTION")
        print("=" * 80)
        
        # Connect to database
        await self.connect_db()
        
        try:
            # Fetch data from PythonAnywhere
            print("\n→ Fetching workingRolling.csv from PythonAnywhere...")
            csv_result = await self.pythonanywhere_service.get_working_rolling()
            
            if not csv_result.get('success'):
                print(f"✗ Error fetching CSV: {csv_result.get('error', 'Unknown error')}")
                return
            
            rows = csv_result.get('data', [])
            if not rows:
                print("✗ No data found in CSV")
                return
            
            print(f"✓ Found {len(rows)} rows in CSV")
            
            # Filter rows with IPO dates
            rows_with_dates = [
                row for row in rows 
                if row.get('polygon_list_date') and row.get('ticker')
            ]
            
            print(f"✓ Found {len(rows_with_dates)} IPOs with dates and tickers")
            
            # Apply limit if specified
            if limit:
                rows_with_dates = rows_with_dates[start_from:start_from + limit]
                print(f"→ Processing {len(rows_with_dates)} IPOs (limit: {limit}, start: {start_from})")
            
            # Process each IPO
            successful = 0
            failed = 0
            
            for i, row in enumerate(rows_with_dates):
                try:
                    ipo_data = await self.process_ipo_row(row, i, len(rows_with_dates))
                    
                    if ipo_data:
                        stored = await self.store_ipo_data(ipo_data)
                        if stored:
                            successful += 1
                        else:
                            failed += 1
                    else:
                        failed += 1
                    
                    # Progress update every 10 IPOs
                    if (i + 1) % 10 == 0:
                        print(f"\n📊 Progress: {i + 1}/{len(rows_with_dates)} | Success: {successful} | Failed: {failed}")
                    
                except Exception as e:
                    print(f"  ✗ Error processing row: {str(e)}")
                    failed += 1
                    continue
            
            print("\n" + "=" * 80)
            print(f"✓ COMPLETED: {successful} successful, {failed} failed")
            print("=" * 80)
            
        finally:
            await self.close_db()


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Populate historical IPO data')
    parser.add_argument('--limit', type=int, help='Limit number of IPOs to process')
    parser.add_argument('--start', type=int, default=0, help='Start from this index')
    args = parser.parse_args()
    
    collector = HistoricalDataCollector()
    await collector.run(limit=args.limit, start_from=args.start)


if __name__ == "__main__":
    asyncio.run(main())

