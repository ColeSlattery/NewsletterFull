import { pgTable, uuid, varchar, timestamp, integer, real, pgEnum, boolean } from 'drizzle-orm/pg-core';

// Enums
export const subscriberStatusEnum = pgEnum('subscriber_status', ['subscribed', 'unsubscribed']);

// Tables
export const subscribers = pgTable('subscribers', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  status: subscriberStatusEnum('status').notNull().default('subscribed'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  unsubToken: varchar('unsub_token', { length: 255 }).notNull().unique(),
});

export const ipoFilings = pgTable('ipo_filings', {
  id: uuid('id').primaryKey().defaultRandom(),
  cik: varchar('cik', { length: 20 }).notNull(),
  name: varchar('name', { length: 500 }).notNull(),
  ticker: varchar('ticker', { length: 10 }).notNull(),
  filingType: varchar('filing_type', { length: 50 }).notNull(),
  filedAt: timestamp('filed_at').notNull(),
  link: varchar('link', { length: 1000 }).notNull(),
  
  // IPO Metrics
  proposedPriceLow: real('proposed_price_low'),
  proposedPriceHigh: real('proposed_price_high'),
  sharesOffered: integer('shares_offered'),
  impliedMarketCap: real('implied_market_cap'),
  enterpriseValue: real('enterprise_value'),
  
  // Financial Metrics
  revenue: real('revenue'),
  netIncome: real('net_income'),
  revenueGrowthYoY: real('revenue_growth_yoy'),
  grossMargin: real('gross_margin'),
  operatingMargin: real('operating_margin'),
  
  // Cash Flow
  cashBurn: real('cash_burn'),
  freeCashFlow: real('free_cash_flow'),
  
  // AI Analysis
  hypeScore: real('hype_score'),
  aiAnalysis: varchar('ai_analysis', { length: 2000 }),
  
  // Metadata
  updatedAt: timestamp('updated_at').defaultNow(),
});

export const searchInterest = pgTable('search_interest', {
  id: uuid('id').primaryKey().defaultRandom(),
  cik: varchar('cik', { length: 20 }).notNull(),
  day: timestamp('day').notNull(),
  trendScore: integer('trend_score').notNull(),
  sentimentScore: real('sentiment_score').notNull(),
});

export const newsletterLog = pgTable('newsletter_log', {
  id: uuid('id').primaryKey().defaultRandom(),
  subject: varchar('subject', { length: 500 }).notNull(),
  sentAt: timestamp('sent_at').notNull().defaultNow(),
  recipients: integer('recipients').notNull(),
  campaignId: varchar('campaign_id', { length: 255 }).notNull(),
});

// Historical IPO Performance Database
export const historicalIpos = pgTable('historical_ipos', {
  id: uuid('id').primaryKey().defaultRandom(),
  cik: varchar('cik', { length: 20 }).notNull(),
  name: varchar('name', { length: 500 }).notNull(),
  ticker: varchar('ticker', { length: 10 }).notNull(),
  sector: varchar('sector', { length: 100 }),
  industry: varchar('industry', { length: 100 }),
  
  // IPO Details
  ipoDate: timestamp('ipo_date').notNull(),
  ipoPrice: real('ipo_price').notNull(),
  proposedPriceLow: real('proposed_price_low'),
  proposedPriceHigh: real('proposed_price_high'),
  sharesOffered: integer('shares_offered'),
  raisedAmount: real('raised_amount'),
  
  // Pre-IPO Financials (from S-1 filing)
  revenue: real('revenue'),
  netIncome: real('net_income'),
  revenueGrowthYoY: real('revenue_growth_yoy'),
  grossMargin: real('gross_margin'),
  operatingMargin: real('operating_margin'),
  freeCashFlow: real('free_cash_flow'),
  cashBurn: real('cash_burn'),
  enterpriseValue: real('enterprise_value'),
  marketCapAtIpo: real('market_cap_at_ipo'),
  
  // Performance Metrics
  firstDayReturn: real('first_day_return'), // % change on first day
  firstWeekReturn: real('first_week_return'),
  firstMonthReturn: real('first_month_return'),
  firstQuarterReturn: real('first_quarter_return'),
  firstYearReturn: real('first_year_return'),
  
  // Market Context
  marketCapCategory: varchar('market_cap_category', { length: 20 }), // micro, small, mid, large, mega
  growthStage: varchar('growth_stage', { length: 20 }), // early, growth, mature
  
  // Data Quality
  dataCompleteness: real('data_completeness'), // 0-1 score of how complete the data is
  lastUpdated: timestamp('last_updated').defaultNow(),
});

// Historical Search Trends for IPOs
export const historicalSearchTrends = pgTable('historical_search_trends', {
  id: uuid('id').primaryKey().defaultRandom(),
  cik: varchar('cik', { length: 20 }).notNull(),
  ticker: varchar('ticker', { length: 10 }).notNull(),
  date: timestamp('date').notNull(),
  trendScore: integer('trend_score').notNull(),
  searchVolume: integer('search_volume'),
  relatedQueries: varchar('related_queries', { length: 1000 }), // JSON string of related search terms
});

// Historical News Sentiment for IPOs
export const historicalNewsSentiment = pgTable('historical_news_sentiment', {
  id: uuid('id').primaryKey().defaultRandom(),
  cik: varchar('cik', { length: 20 }).notNull(),
  ticker: varchar('ticker', { length: 10 }).notNull(),
  date: timestamp('date').notNull(),
  sentimentScore: real('sentiment_score').notNull(), // -1 to 1
  totalArticles: integer('total_articles').notNull(),
  positiveArticles: integer('positive_articles').notNull(),
  negativeArticles: integer('negative_articles').notNull(),
  neutralArticles: integer('neutral_articles').notNull(),
  avgSentimentScore: real('avg_sentiment_score'), // Average sentiment across all articles
});

// IPO Similarity Matches
export const ipoSimilarityMatches = pgTable('ipo_similarity_matches', {
  id: uuid('id').primaryKey().defaultRandom(),
  currentCik: varchar('current_cik', { length: 20 }).notNull(),
  historicalCik: varchar('historical_cik', { length: 20 }).notNull(),
  similarityScore: real('similarity_score').notNull(), // 0-1 score of how similar
  similarityFactors: varchar('similarity_factors', { length: 1000 }), // JSON of matching factors
  sectorMatch: boolean('sector_match').default(false),
  sizeMatch: boolean('size_match').default(false),
  growthMatch: boolean('growth_match').default(false),
  financialMatch: boolean('financial_match').default(false),
  createdAt: timestamp('created_at').defaultNow(),
});

// Export types for TypeScript
export type Subscriber = typeof subscribers.$inferSelect;
export type NewSubscriber = typeof subscribers.$inferInsert;
export type IpoFiling = typeof ipoFilings.$inferSelect;
export type NewIpoFiling = typeof ipoFilings.$inferInsert;
export type SearchInterest = typeof searchInterest.$inferSelect;
export type NewSearchInterest = typeof searchInterest.$inferInsert;
export type NewsletterLog = typeof newsletterLog.$inferSelect;
export type NewNewsletterLog = typeof newsletterLog.$inferInsert;
export type HistoricalIpo = typeof historicalIpos.$inferSelect;
export type NewHistoricalIpo = typeof historicalIpos.$inferInsert;
export type HistoricalSearchTrend = typeof historicalSearchTrends.$inferSelect;
export type NewHistoricalSearchTrend = typeof historicalSearchTrends.$inferInsert;
export type HistoricalNewsSentiment = typeof historicalNewsSentiment.$inferSelect;
export type NewHistoricalNewsSentiment = typeof historicalNewsSentiment.$inferInsert;
export type IpoSimilarityMatch = typeof ipoSimilarityMatches.$inferSelect;
export type NewIpoSimilarityMatch = typeof ipoSimilarityMatches.$inferInsert;
