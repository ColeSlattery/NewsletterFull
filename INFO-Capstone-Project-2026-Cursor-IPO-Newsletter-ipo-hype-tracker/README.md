# IPO Hype Tracker Newsletter

A Next.js application for tracking IPO market trends and managing newsletter subscriptions.

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Setup

Create a `.env.local` file in the root directory with the following variables:

```env
# Database Configuration
# TODO: Replace with your actual Neon database URL
DATABASE_URL="postgresql://username:password@ep-xxxxx.us-east-1.aws.neon.tech/database_name?sslmode=require"

# Email Service (Required for newsletter)
# TODO: Get your API key from https://resend.com/api-keys
RESEND_API_KEY="re_xxxxxxxxxx"

# External API Keys (Optional - for real data integration)
# TODO: Get your API key from https://www.alphavantage.co/support/#api-key
ALPHAVANTAGE_API_KEY="your_alpha_vantage_key_here"

# TODO: Get your API key from your chosen sentiment analysis provider
SENTIMENT_API_KEY="your_sentiment_api_key_here"

# Application URLs
# TODO: Set to your production domain when deploying
NEXT_PUBLIC_BASE_URL="http://localhost:3000"
```

#### Required API Keys:

1. **Resend API Key** (Required for email sending):
   - Sign up at [https://resend.com/](https://resend.com/)
   - Add and verify your domain
   - Generate an API key
   - Add to `.env.local`

2. **Neon Database** (Required for data storage):
   - Create a database at [https://console.neon.tech/](https://console.neon.tech/)
   - Copy your connection string
   - Add to `.env.local`

### 3. Run Database Migrations

```bash
npm run db:generate
npm run db:migrate
```

### 4. Start Development Server

```bash
npm run dev
```

## Project Structure

- `app/` - Next.js App Router pages and API routes
- `db/` - Database schema and migrations
- `lib/` - Utility functions and database connection
- `emails/` - Email templates (to be added)

## API Endpoints

- `POST /api/subscribe` - Subscribe to newsletter
- `GET /api/unsubscribe?token=xxx` - Unsubscribe from newsletter
- `POST /api/newsletter/send` - Send newsletter to all subscribers (triggered by cron)

## Database Schema

- `subscribers` - Newsletter subscribers with unsub tokens
- `ipo_filings` - IPO filing information
- `search_interest` - Market interest tracking data
- `newsletter_log` - Newsletter sending logs

## Newsletter Features

- **Automated Sending**: Daily newsletter sent at 13:00 UTC (7:00 AM US/Mountain) via Vercel Cron
- **Email Template**: Beautiful HTML email with charts and IPO leaderboard
- **Chart Generation**: Automatic bar charts and trend charts using QuickChart API
- **Data Sources**: Integration points for SEC EDGAR, Google Trends, Alpha Vantage, and sentiment analysis
- **Unsubscribe**: One-click unsubscribe with secure tokens

## TODO for Developer

### Required Setup:
1. **Replace DATABASE_URL**: Update `.env.local` with your actual Neon database URL
2. **Add RESEND_API_KEY**: Get API key from Resend and add to `.env.local`
3. **Run migrations**: Execute `npm run db:generate` and `npm run db:migrate`
4. **Update email domain**: Replace placeholder domain in `lib/resend.ts`

### Optional Enhancements:
5. **Real Data Integration**: 
   - Replace mock data in `lib/edgar.ts` with actual SEC EDGAR API calls
   - Set up Google Trends integration in `lib/pytrends.ts`
   - Add Alpha Vantage API key for stock data in `lib/alphaVantage.ts`
   - Implement sentiment analysis in `lib/sentiment.ts`
6. **Production Deployment**: Deploy to Vercel and configure environment variables
7. **Authentication**: Add admin authentication for managing newsletters
8. **Analytics**: Implement newsletter analytics and tracking
9. **Testing**: Add email template testing endpoint
