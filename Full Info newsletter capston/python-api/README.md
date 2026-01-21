# IPO Hype Tracker Python API

A FastAPI-based microservice that provides data from multiple sources for the IPO Hype Tracker newsletter.

## Features

- **Google Trends Integration** (pytrends)
- **Yahoo Finance Integration** (yfinance)
- **News API Integration** (NewsAPI.org)
- **SEC EDGAR API Integration**
- **OpenAI Integration** for hype score generation

## Setup

### 1. Install Dependencies

```bash
cd python-api
pip install -r requirements.txt
```

### 2. Environment Variables

Copy `env.example` to `.env` and fill in your API keys:

```bash
cp env.example .env
```

Required API keys:
- `OPENROUTER_API_KEY` - For AI-powered hype score generation (replaces OpenAI)
- `NEWS_API_KEY` - For news sentiment analysis

Note: Using Yahoo Finance (free) for stock data - no API key required

### 3. Run the API

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
- `GET /health` - Check API status

### Google Trends
- `POST /api/trends/search` - Get trends data for companies
- `POST /api/trends/interest-over-time` - Get interest over time data

### Yahoo Finance
- `POST /api/yahoo/stock-data` - Get current stock data
- `POST /api/yahoo/historical-data` - Get historical stock data

### News API
- `POST /api/news/company-news` - Get news articles for companies
- `POST /api/news/sentiment-analysis` - Analyze news sentiment

### SEC EDGAR
- `POST /api/sec/ipo-filings` - Get recent IPO filings
- `POST /api/sec/company-filings` - Get SEC filings for companies

### OpenAI
- `POST /api/openai/hype-score` - Generate AI-powered hype score

### Combined Analysis
- `POST /api/combined/company-analysis` - Get comprehensive company analysis

## Example Usage

### Get Company Analysis
```bash
curl -X POST "http://localhost:8000/api/combined/company-analysis" \
  -H "Content-Type: application/json" \
  -d '{"companies": ["AAPL", "TSLA", "GOOGL"]}'
```

### Generate Hype Score
```bash
curl -X POST "http://localhost:8000/api/openai/hype-score" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Tesla",
    "search_data": {"trend_score": 85},
    "news_data": {"sentiment_score": 0.7},
    "stock_data": {"change_percent": 5.2}
  }'
```

## API Rate Limits

- **Google Trends**: 10 requests per second (built-in rate limiting)
- **Yahoo Finance**: No official limits (rate limiting implemented)
- **News API**: 1000 requests per day (free tier)
- **SEC EDGAR**: 10 requests per second (built-in rate limiting)
- **OpenRouter**: Based on your plan and model selection

## Error Handling

All endpoints return structured responses:
```json
{
  "success": true,
  "data": {...}
}
```

Or on error:
```json
{
  "success": false,
  "error": "Error message"
}
```

## Development

### Adding New Services

1. Create a new service file in `services/`
2. Add the service to `main.py`
3. Create endpoints for the service
4. Update this README

### Testing

```bash
# Test individual services
python -c "from services.trends_service import TrendsService; print('Trends service loaded')"
```

## Deployment

The API can be deployed to:
- **Heroku** - Add Procfile and requirements.txt
- **Railway** - Automatic Python detection
- **AWS Lambda** - Use Mangum adapter
- **Docker** - Add Dockerfile

## Integration with Next.js

The Next.js app calls this Python API for data:

```typescript
const response = await fetch('http://localhost:8000/api/combined/company-analysis', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ companies: ['AAPL', 'TSLA'] })
});
```
