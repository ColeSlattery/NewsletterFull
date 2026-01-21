"""
Nightly precomputation job for IPO search trends and news sentiment.

This script:
1. Pulls upcoming and recent IPOs from PythonAnywhere CSVs
2. Collects Google Trends and combined NewsAPI/GDELT sentiment data
3. Stores the aggregated metrics in PostgreSQL cache tables

Run with:
    python3 scripts/precompute_daily_metrics.py --limit 50 --include-upcoming --include-recent
"""

import asyncio
import os
import sys
import json
import argparse
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import asyncpg  # type: ignore
from dotenv import load_dotenv  # type: ignore

try:
    from services.pythonanywhere_service import PythonAnywhereService
    from services.trends_service import TrendsService
    from services.news_service import NewsService
except ImportError:  # pragma: no cover - fallback for CLI execution
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from services.pythonanywhere_service import PythonAnywhereService  # type: ignore
    from services.trends_service import TrendsService  # type: ignore
    from services.news_service import NewsService  # type: ignore

# Load environment variables, prioritising the repo-level .env.local
import pathlib

env_path = pathlib.Path(__file__).parent.parent.parent / '.env.local'
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()


def normalise_company_fields(row: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Extract company name, ticker, and CIK from a CSV row with varied field names."""
    company = (
        row.get('Company')
        or row.get('company')
        or row.get('Issuer')
        or row.get('Company Name')
        or row.get('name')
    )
    ticker = (
        row.get('Symbol')
        or row.get('Ticker')
        or row.get('ticker')
        or row.get('symbol')
    )
    cik = (
        row.get('CIK')
        or row.get('cik')
        or row.get('Sec CIK')
        or row.get('SEC CIK')
    )

    if ticker:
        ticker = ticker.strip().upper()
    if cik:
        cik = cik.strip()

    return (
        company.strip() if isinstance(company, str) else company,
        ticker,
        cik,
    )


class NightlyPrecomputeJob:
    """Coordinates nightly precomputation for IPO analytics."""

    def __init__(self, limit: Optional[int], include_recent: bool, include_upcoming: bool):
        self.limit = limit
        self.include_recent = include_recent
        self.include_upcoming = include_upcoming

        self.db_url = os.getenv('DATABASE_URL')
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable is not set")

        self.pythonanywhere_service = PythonAnywhereService()
        self.trends_service = TrendsService()
        self.news_service = NewsService()

        self.db_pool: Optional[asyncpg.Pool] = None

    async def connect_db(self) -> None:
        """Create the asyncpg connection pool."""
        if self.db_pool is None:
            self.db_pool = await asyncpg.create_pool(
                self.db_url,
                min_size=1,
                max_size=10,
                command_timeout=60,
            )
            print("✓ Connected to PostgreSQL")

    async def close_db(self) -> None:
        """Close the asyncpg connection pool."""
        if self.db_pool is not None:
            await self.db_pool.close()
            print("✓ Database connection closed")

    async def load_ipos(self) -> List[Dict[str, Any]]:
        """Load IPO rows from PythonAnywhere CSVs and normalise the structure."""
        tasks = []
        if self.include_recent:
            tasks.append(self.pythonanywhere_service.get_recent_ipos())
        if self.include_upcoming:
            tasks.append(self.pythonanywhere_service.get_upcoming_ipos())

        results = await asyncio.gather(*tasks) if tasks else []
        combined: List[Dict[str, Any]] = []
        for response in results:
            if isinstance(response, dict) and response.get('success') and response.get('data'):
                combined.extend(response['data'])

        seen_tickers = set()
        normalised: List[Dict[str, Any]] = []
        for row in combined:
            company, ticker, cik = normalise_company_fields(row)
            if not company or not ticker:
                continue
            if ticker in seen_tickers:
                continue
            seen_tickers.add(ticker)
            normalised.append(
                {
                    'company_name': company,
                    'ticker': ticker,
                    'cik': cik or f'UNKNOWN-{ticker}',
                }
            )

        if self.limit is not None:
            normalised = normalised[: self.limit]

        print(f"✓ Loaded {len(normalised)} IPO candidates for precomputation")
        return normalised

    async def fetch_trends(self, companies: List[str]) -> Dict[str, Any]:
        """Fetch Google Trends data for the list of company names."""
        try:
            return await self.trends_service.get_trends_data(companies)
        except Exception as exc:  # pylint: disable=broad-except
            print(f"⚠️  Trends fetch failed: {exc}")
            return {}

    async def fetch_sentiment(self, companies: List[str]) -> Dict[str, Any]:
        """Fetch combined NewsAPI + GDELT sentiment for the list of companies."""
        try:
            return await self.news_service.analyze_sentiment(companies)
        except Exception as exc:  # pylint: disable=broad-except
            print(f"⚠️  Sentiment fetch failed: {exc}")
            return {}

    async def store_search_trend(
        self,
        conn: asyncpg.Connection,
        cik: str,
        ticker: str,
        company_name: str,
        trends: Dict[str, Any],
    ) -> None:
        """Persist trend metrics for a single company."""
        entry = trends.get(company_name)
        if not entry:
            return

        now = datetime.utcnow()
        trend_score = float(entry.get('trend_score', 0))
        search_volume = entry.get('average_interest')
        related_queries = entry.get('related_queries') or {}

        await conn.execute(
            """
            INSERT INTO historical_search_trends (cik, ticker, date, trend_score, search_volume, related_queries)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            cik,
            ticker,
            now,
            int(round(trend_score)),
            int(round(search_volume)) if isinstance(search_volume, (int, float)) else None,
            json.dumps(related_queries),
        )

    async def store_news_sentiment(
        self,
        conn: asyncpg.Connection,
        cik: str,
        ticker: str,
        company_name: str,
        sentiment: Dict[str, Any],
    ) -> None:
        """Persist news sentiment metrics for a single company."""
        entry = sentiment.get(company_name)
        if not entry:
            return

        now = datetime.utcnow()
        sentiment_score = float(entry.get('sentiment_score', 0))
        total_articles = int(entry.get('total_articles', 0) or 0)
        positive = int(entry.get('positive_count', 0) or 0)
        negative = int(entry.get('negative_count', 0) or 0)
        neutral = int(entry.get('neutral_count', 0) or 0)

        await conn.execute(
            """
            INSERT INTO historical_news_sentiment (
                cik,
                ticker,
                date,
                sentiment_score,
                total_articles,
                positive_articles,
                negative_articles,
                neutral_articles,
                avg_sentiment_score
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """,
            cik,
            ticker,
            now,
            sentiment_score,
            total_articles,
            positive,
            negative,
            neutral,
            sentiment_score,
        )

    async def run(self) -> None:
        """Execute the nightly workflow end-to-end."""
        await self.connect_db()
        try:
            ipos = await self.load_ipos()
            if not ipos:
                print("⚠️  No IPOs found to precompute")
                return

            company_names = [record['company_name'] for record in ipos]
            print("→ Fetching Google Trends data...")
            trends = await self.fetch_trends(company_names)
            print("→ Fetching news sentiment (NewsAPI + GDELT)...")
            sentiment = await self.fetch_sentiment(company_names)

            stored_trends = stored_sentiment = 0

            async with self.db_pool.acquire() as conn:  # type: ignore[arg-type]
                for record in ipos:
                    cik = record['cik']
                    ticker = record['ticker']
                    name = record['company_name']

                    try:
                        await self.store_search_trend(conn, cik, ticker, name, trends)
                        stored_trends += 1
                    except Exception as exc:  # pylint: disable=broad-except
                        print(f"⚠️  Failed to store trend for {ticker}: {exc}")

                    try:
                        await self.store_news_sentiment(conn, cik, ticker, name, sentiment)
                        stored_sentiment += 1
                    except Exception as exc:  # pylint: disable=broad-except
                        print(f"⚠️  Failed to store sentiment for {ticker}: {exc}")

            print(f"✓ Stored {stored_trends} trend rows and {stored_sentiment} sentiment rows")
        finally:
            await self.close_db()


async def async_main(args: argparse.Namespace) -> None:
    job = NightlyPrecomputeJob(
        limit=args.limit,
        include_recent=not args.skip_recent,
        include_upcoming=not args.skip_upcoming,
    )
    await job.run()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Nightly IPO precomputation job")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of IPOs to process")
    parser.add_argument("--skip-recent", action="store_true", help="Skip recent IPOs dataset")
    parser.add_argument("--skip-upcoming", action="store_true", help="Skip upcoming IPOs dataset")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()

