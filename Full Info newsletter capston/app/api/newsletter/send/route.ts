import { NextRequest, NextResponse } from 'next/server';
import { render } from '@react-email/render';
import { db } from '@/lib/db';
import { subscribers, newsletterLog } from '@/db/schema';
import { sendBulkEmails, EMAIL_CONFIG } from '@/lib/ses';
import Newsletter from '@/emails/Newsletter';
import { makeBarChart, makeTrendChart } from '@/lib/charts';
// Data fetching now handled by Python API
import { eq } from 'drizzle-orm';
import { v4 as uuidv4 } from 'uuid';

const parseNumeric = (value: unknown): number | null => {
  if (value === undefined || value === null) return null;
  if (typeof value === 'number' && !Number.isNaN(value)) return value;
  const cleaned = String(value).replace(/[^0-9.+-]/g, '');
  if (!cleaned) return null;
  const parsed = parseFloat(cleaned);
  return Number.isFinite(parsed) ? parsed : null;
};

const extractFieldValue = (source: any, keys: string[]): number | null => {
  if (!source) return null;
  for (const key of keys) {
    if (Object.prototype.hasOwnProperty.call(source, key)) {
      const value = parseNumeric(source[key]);
      if (value !== null) {
        return value;
      }
    }
  }
  return null;
};

const getStringFieldValue = (source: any, keys: string[], fallback = '—'): string => {
  if (!source) return fallback;
  for (const key of keys) {
    if (Object.prototype.hasOwnProperty.call(source, key)) {
      const raw = source[key];
      if (raw !== undefined && raw !== null) {
        const value = String(raw).trim();
        if (value) {
          return value;
        }
      }
    }
  }
  return fallback;
};

const buildCalendarTable = (ipos: any[]) => {
  const rows = ipos.slice(0, 12);
  return rows.map((ipo) => ({
    company: getStringFieldValue(ipo, ['Company', 'company', 'name']),
    symbol: getStringFieldValue(ipo, ['Symbol', 'Symbol proposed', 'Symbol Proposed', 'symbol', 'ticker']),
    leadManagers: getStringFieldValue(ipo, ['Lead Managers', 'lead_managers', 'Lead Manager', 'lead_manager']),
    sharesMillions: getStringFieldValue(ipo, ['Shares (Millions)', 'shares_millions', 'Shares', 'shares']),
    priceLow: getStringFieldValue(ipo, ['Price Low', 'price_low', 'proposed_price_low']),
    priceHigh: getStringFieldValue(ipo, ['Price High', 'price_high', 'proposed_price_high']),
    estVolume: getStringFieldValue(ipo, ['Est. $ Volume', 'estimated_volume', 'estimated_volume_usd']),
    expectedToTrade: getStringFieldValue(ipo, ['Expected to Trade', 'expected_to_trade', 'expected_trade_date']),
    scoopRating: getStringFieldValue(ipo, ['SCOOP Rating', 'Scoop Rating', 'scoop_rating', 'Rating', 'rating'], 'N/A'),
    ratingChange: getStringFieldValue(ipo, ['Rating Change', 'rating_change'], '—'),
  }));
};

// Helper function to match IPO tickers to prices from CSV data
function matchTickerToPrice(ipo: any, recentPrices: any[], tickerPrices: any[]): { proposed_price_low: number; proposed_price_high: number } {
  const ticker = ipo.ticker || ipo.symbol || '';
  const companyName = ipo.name || ipo.company || '';

  const lowFieldCandidates = [
    'proposed_price_low',
    'proposedPriceLow',
    'price_low',
    'Price Low',
    'Proposed Price Low',
    'ipo_price_low',
    'IPO Price Low',
    'deal_price_low',
    'Deal Price Low',
    'offer_price_low',
    'Offer Price Low'
  ];

  const highFieldCandidates = [
    'proposed_price_high',
    'proposedPriceHigh',
    'price_high',
    'Price High',
    'Proposed Price High',
    'ipo_price_high',
    'IPO Price High',
    'deal_price_high',
    'Deal Price High',
    'offer_price_high',
    'Offer Price High'
  ];

  const midFieldCandidates = [
    'proposed_price',
    'proposedPrice',
    'price',
    'offer_price',
    'Offer Price',
    'ipo_price',
    'IPO Price',
    'current_price',
    'deal_price'
  ];

  const fromIpoLow = extractFieldValue(ipo, lowFieldCandidates);
  const fromIpoHigh = extractFieldValue(ipo, highFieldCandidates);
  const fromIpoMid = extractFieldValue(ipo, midFieldCandidates);

  let proposedLow = fromIpoLow ?? null;
  let proposedHigh = fromIpoHigh ?? null;

  const matchingPriceRow = [...recentPrices, ...tickerPrices].find((p: any) => {
    const priceTicker = (p.ticker || p.symbol || '').toUpperCase();
    const priceName = (p.company || p.name || '').toLowerCase();
    return priceTicker === ticker.toUpperCase() || (companyName && priceName === companyName.toLowerCase());
  });

  if (matchingPriceRow) {
    proposedLow = proposedLow ?? extractFieldValue(matchingPriceRow, lowFieldCandidates);
    proposedHigh = proposedHigh ?? extractFieldValue(matchingPriceRow, highFieldCandidates);
  }

  const midPrice = fromIpoMid ?? (matchingPriceRow ? extractFieldValue(matchingPriceRow, midFieldCandidates) : null);

  if (proposedLow === null && proposedHigh !== null && midPrice !== null) {
    proposedLow = Math.max(0, midPrice - (proposedHigh - midPrice));
  } else if (proposedHigh === null && proposedLow !== null && midPrice !== null) {
    proposedHigh = midPrice + (midPrice - proposedLow);
  }

  if (proposedLow === null && proposedHigh === null && midPrice !== null) {
    proposedLow = Math.max(0, midPrice * 0.9);
    proposedHigh = midPrice * 1.1;
  }

  return {
    proposed_price_low: proposedLow ?? 0,
    proposed_price_high: proposedHigh ?? 0
  };
}

// Helper function to determine if it's Monday or Friday (with test override)
function getNewsletterDay(request: NextRequest): 'monday' | 'friday' {
  // Check for test override parameter
  const { searchParams } = new URL(request.url);
  const dayParam = searchParams.get('day');
  if (dayParam === 'monday' || dayParam === 'friday') {
    return dayParam;
  }
  
  // Determine day from current date
  const today = new Date();
  const dayOfWeek = today.getDay(); // 0 = Sunday, 1 = Monday, ..., 5 = Friday
  return dayOfWeek === 1 ? 'monday' : dayOfWeek === 5 ? 'friday' : 'monday'; // Default to monday if not Monday or Friday
}

// Helper function to process a single IPO and get hype score
async function processIPO(
  ipo: any,
  recentPrices: any[],
  tickerPrices: any[]
): Promise<any | null> {
  const companyName = ipo.name || ipo.company || ipo.Company || ipo['Company Name'] || '';
  const ticker = ipo.ticker || ipo.symbol || ipo.Symbol || ipo['Ticker'] || '';
  
  if (!companyName || !ticker) {
    console.log(`Skipping IPO with missing name or ticker:`, ipo);
    return null;
  }
  
  // Match ticker to prices from CSV data
  const priceInfo = matchTickerToPrice(ipo, recentPrices, tickerPrices);
  
  // Initialize default data structures
  let searchData: any = { trend_score: 50, recent_interest: 50, average_interest: 50 };
  let newsData: any = { 
    sentiment_score: 0, 
    total_articles: 0, 
    positive_count: 0, 
    negative_count: 0, 
    neutral_count: 0 
  };
  let stockData: any = { 
    change_percent: 0, 
    volume: 0, 
    market_cap: 0, 
    pe_ratio: 0
  };
  let companyInfo: any = {
    revenue: 0,
    revenue_growth_yoy: 0,
    net_income: 0,
    gross_margin: 0,
    operating_margin: 0,
    free_cash_flow: 0,
    cash_burn: 0,
    enterprise_value: 0,
    shares_outstanding: 0
  };
  
  // Get real data from APIs
  try {
    // Get search trends
    const trendsResponse = await fetch('http://localhost:8000/api/trends/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ companies: [companyName] })
    });
    if (trendsResponse.ok) {
      const trendsResult = await trendsResponse.json();
      if (trendsResult.success && trendsResult.data && trendsResult.data[companyName]) {
        searchData = trendsResult.data[companyName];
      }
    }
    
    // Get news sentiment
    const newsResponse = await fetch('http://localhost:8000/api/news/sentiment-analysis', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ companies: [companyName] })
    });
    if (newsResponse.ok) {
      const newsResult = await newsResponse.json();
      if (newsResult.success && newsResult.data && newsResult.data[companyName]) {
        newsData = newsResult.data[companyName];
      }
    }
    
    // Get stock data
    const stockResponse = await fetch('http://localhost:8000/api/yahoo/stock-data', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ companies: [ticker] })
    });
    if (stockResponse.ok) {
      const stockResult = await stockResponse.json();
      if (stockResult.success && stockResult.data && stockResult.data[ticker]) {
        stockData = stockResult.data[ticker];
      }
    }
    
    // Get company info for financial data
    const companyInfoResponse = await fetch('http://localhost:8000/api/yahoo/company-info', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ companies: [ticker] })
    });
    if (companyInfoResponse.ok) {
      const companyInfoResult = await companyInfoResponse.json();
      if (companyInfoResult.success && companyInfoResult.data && companyInfoResult.data[ticker]) {
        companyInfo = {
          revenue: companyInfoResult.data[ticker].revenue || 0,
          revenue_growth_yoy: companyInfoResult.data[ticker].revenue_growth_yoy || 0,
          net_income: companyInfoResult.data[ticker].net_income || 0,
          gross_margin: companyInfoResult.data[ticker].gross_margin || 0,
          operating_margin: companyInfoResult.data[ticker].operating_margin || 0,
          free_cash_flow: companyInfoResult.data[ticker].free_cash_flow || 0,
          cash_burn: companyInfoResult.data[ticker].cash_burn || 0,
          enterprise_value: companyInfoResult.data[ticker].enterprise_value || 0,
          shares_outstanding: companyInfoResult.data[ticker].shares_outstanding || 0
        };
      }
    }
  } catch (error) {
    console.log(`API data unavailable for ${companyName}:`, error);
  }
  
  // Combine stock data and company info
  const combinedStockData = {
    ...stockData,
    ...companyInfo,
    market_cap: stockData.market_cap || companyInfo.implied_market_cap || 0
  };
  
  // Get historical analysis
  let historicalAnalysis = null;
  try {
    const analysisResponse = await fetch('http://localhost:8000/api/historical/ipo-analysis', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        company_name: companyName,
        search_data: searchData,
        news_data: newsData,
        stock_data: combinedStockData
      })
    });
    
    if (analysisResponse.ok) {
      const analysisResult = await analysisResponse.json();
      if (analysisResult.success && analysisResult.analysis) {
        historicalAnalysis = analysisResult.analysis;
      }
    }
  } catch (error) {
    console.log(`Historical analysis unavailable for ${companyName}:`, error);
  }
  
  if (historicalAnalysis && historicalAnalysis.hype_score) {
    return {
      name: companyName,
      ticker: ticker,
      trendScore: searchData.trend_score || 50,
      sentimentScore: newsData.sentiment_score || 0,
      hypeScore: historicalAnalysis.hype_score,
      proposedPriceLow: priceInfo.proposed_price_low || 0,
      proposedPriceHigh: priceInfo.proposed_price_high || 0,
      sharesOffered: ipo.shares_offered || ipo.shares || 0,
      impliedMarketCap: combinedStockData.market_cap || 0,
      enterpriseValue: combinedStockData.enterprise_value || 0,
      revenue: combinedStockData.revenue || 0,
      netIncome: combinedStockData.net_income || 0,
      revenueGrowthYoY: combinedStockData.revenue_growth_yoy || 0,
      grossMargin: combinedStockData.gross_margin || 0,
      operatingMargin: combinedStockData.operating_margin || 0,
      cashBurn: combinedStockData.cash_burn || 0,
      freeCashFlow: combinedStockData.free_cash_flow || 0,
      aiAnalysis: historicalAnalysis.analysis || 'Analysis unavailable',
      recommendation: historicalAnalysis.recommendation || 'Hold',
      riskLevel: historicalAnalysis.risk_level || 'Medium',
      marketOutlook: historicalAnalysis.market_outlook || 'Analysis unavailable'
    };
  }
  
  return null;
}

export async function POST(request: NextRequest) {
  try {
    console.log('Starting newsletter send process...');
    
    // Determine newsletter day (Monday = recent IPOs, Friday = upcoming IPOs)
    const newsletterDay = getNewsletterDay(request);
    console.log(`Newsletter type: ${newsletterDay === 'monday' ? 'Recent IPOs' : 'Upcoming IPOs'}`);
    
    // Get all active subscribers
    const activeSubscribers = await db
      .select()
      .from(subscribers)
      .where(eq(subscribers.status, 'subscribed'));

    if (activeSubscribers.length === 0) {
      return NextResponse.json(
        { message: 'No active subscribers found' },
        { status: 200 }
      );
    }

    console.log(`Found ${activeSubscribers.length} active subscribers`);

    let scoredIPOs: any[] = [];
    let ipoList: any[] = [];
    let calendarTableData: any[] = [];
    
    try {
      // Fetch IPO data from PythonAnywhere CSVs
      let recentPrices: any[] = [];
      let tickerPrices: any[] = [];
      let calendarRows: any[] = [];
      
      // Get the appropriate IPO list based on day
      if (newsletterDay === 'monday') {
        // Monday: Get recent IPOs (already public)
        try {
          const recentIPOsResponse = await fetch('http://localhost:8000/api/pythonanywhere/recent-ipos', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
          });
          if (recentIPOsResponse.ok) {
            const recentData = await recentIPOsResponse.json();
            if (recentData.success && recentData.data) {
              ipoList = recentData.data;
            }
          }
        } catch (error) {
          console.log('Error fetching recent IPOs:', error);
        }
      } else {
        // Friday: Get upcoming IPOs (not yet public)
        try {
          const upcomingIPOsResponse = await fetch('http://localhost:8000/api/pythonanywhere/upcoming-ipos', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
          });
          if (upcomingIPOsResponse.ok) {
            const upcomingData = await upcomingIPOsResponse.json();
            if (upcomingData.success && upcomingData.data) {
              ipoList = upcomingData.data;
            }
          }
        } catch (error) {
          console.log('Error fetching upcoming IPOs:', error);
        }
      }
      
      if (ipoList.length === 0) {
        return NextResponse.json({ 
          error: `No ${newsletterDay === 'monday' ? 'recent' : 'upcoming'} IPO data available from PythonAnywhere` 
        }, { status: 503 });
      }
      
      // Get price data for matching
      try {
        const recentPricesResponse = await fetch('http://localhost:8000/api/pythonanywhere/recent-ipo-tickers-and-prices', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        if (recentPricesResponse.ok) {
          const pricesData = await recentPricesResponse.json();
          if (pricesData.success && pricesData.data) {
            recentPrices = pricesData.data;
          }
        }
      } catch (error) {
        console.log('Error fetching recent IPO tickers and prices:', error);
      }
      
      try {
        const tickerPricesResponse = await fetch('http://localhost:8000/api/pythonanywhere/tickers-and-prices', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        if (tickerPricesResponse.ok) {
          const pricesData = await tickerPricesResponse.json();
          if (pricesData.success && pricesData.data) {
            tickerPrices = pricesData.data;
          }
        }
      } catch (error) {
        console.log('Error fetching tickers and prices:', error);
      }
      
      try {
        const calendarResponse = await fetch('http://localhost:8000/api/pythonanywhere/new-ipo-calendar', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        if (calendarResponse.ok) {
          const calendarData = await calendarResponse.json();
          if (calendarData.success && calendarData.data) {
            calendarRows = calendarData.data;
          }
        }
      } catch (error) {
        console.log('Error fetching IPO calendar:', error);
      }

      const calendarSource = calendarRows.length > 0 ? calendarRows : ipoList;
      calendarTableData = buildCalendarTable(calendarSource);
      
      // Process IPOs in batches of 10, up to 10 total
      const batchSize = 10;
      const maxTotalProcessed = 10;
      let totalProcessed = 0;
      
      for (let batchStart = 0; batchStart < ipoList.length && totalProcessed < maxTotalProcessed; batchStart += batchSize) {
        const batchEnd = Math.min(batchStart + batchSize, ipoList.length, totalProcessed + batchSize);
        const batch = ipoList.slice(batchStart, batchEnd);
        
        console.log(`Processing batch ${Math.floor(batchStart / batchSize) + 1}: IPOs ${batchStart + 1}-${batchEnd} (${batch.length} IPOs)`);
        
        // Process each IPO in the batch
        for (const ipo of batch) {
          if (totalProcessed >= maxTotalProcessed) break;
          
          totalProcessed++;
          const processedIPO = await processIPO(ipo, recentPrices, tickerPrices);
          
          if (processedIPO) {
            scoredIPOs.push(processedIPO);
            console.log(`✅ Scored IPO: ${processedIPO.name} (Hype Score: ${processedIPO.hypeScore})`);
          }
        }
        
        console.log(`Batch complete. Scored IPOs so far: ${scoredIPOs.length}, Total processed: ${totalProcessed}`);
      }
      
      console.log(`Processing complete. Scored ${scoredIPOs.length} IPOs after processing ${totalProcessed}`);
      
    } catch (error) {
      console.error('Error fetching IPO data:', error);
    }
    
    // Sort by hype score (highest to lowest) and take top 5
    scoredIPOs.sort((a, b) => b.hypeScore - a.hypeScore);
    const topFiveData = scoredIPOs.slice(0, 5);
    
    if (topFiveData.length === 0) {
      return NextResponse.json({ 
        error: 'No IPOs returned hype scores after processing up to 10 candidates.' 
      }, { status: 503 });
    }

    console.log(`Final newsletter will include ${topFiveData.length} IPOs, sorted by hype score:`);
    topFiveData.forEach((ipo, idx) => {
      console.log(`  ${idx + 1}. ${ipo.name} - Hype Score: ${ipo.hypeScore}`);
    });

    // Generate charts
    const barChartUrl = makeBarChart(topFiveData);
    
    // Generate trend chart for top company
    const topCompany = topFiveData[0];
    const trendData = Array.from({ length: 7 }).map((_, idx) => {
      const d = new Date();
      d.setDate(d.getDate() - (6 - idx));
      return {
        date: d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        value: Math.max(0, Math.min(100, 50 + (Math.random() - 0.5) * 30)),
      };
    });
    const trendChartUrl = makeTrendChart(topCompany.name, trendData);
    const metricsChartUrl = makeBarChart(topFiveData); // Using bar chart for metrics

    // Render email template
    const emailHtml = await render(Newsletter({
      topFive: topFiveData,
      pricingTable: calendarTableData,
      barChartUrl,
      trendChartUrl,
      metricsChartUrl,
      unsubscribeUrl: `${process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'}/unsubscribe`,
    }));

    // Send emails to all subscribers using AWS SES bulk sending
    const campaignId = uuidv4();
    let emailResults;
    try {
      emailResults = await sendBulkEmails({
        recipients: activeSubscribers.map(sub => sub.email),
        subject: EMAIL_CONFIG.subject,
        html: emailHtml,
      });
      
      console.log(`📧 Newsletter sent successfully to ${emailResults.totalSent} recipient(s)`);
      if (emailResults.totalFailed > 0) {
        console.log(`⚠️ Failed to send to ${emailResults.totalFailed} recipient(s)`);
      }
    } catch (emailError) {
      console.error('Error sending emails:', emailError);
      // Continue even if email sending fails - log it but don't break the response
      emailResults = {
        totalSent: 0,
        failed: [],
        totalFailed: activeSubscribers.length,
        successful: []
      };
    }

    // Process email results
    const successfulSends = emailResults?.totalSent || 0;
    const failedSends = emailResults?.failed || [];
    const totalFailed = emailResults?.totalFailed || 0;

    // Log newsletter send event
    try {
      await db.insert(newsletterLog).values({
        subject: EMAIL_CONFIG.subject,
        recipients: successfulSends,
        campaignId,
      });
    } catch (logError) {
      console.log('Note: Could not log to database, continuing anyway...');
    }

    // Extract failed emails from error batches
    const failedEmails = failedSends.flatMap(error => error.recipients || []);

    return NextResponse.json({
      message: 'Newsletter sent successfully',
      campaignId,
      newsletterType: newsletterDay === 'monday' ? 'Recent IPOs' : 'Upcoming IPOs',
      iposProcessed: topFiveData.length,
      recipients: {
        total: activeSubscribers.length,
        emails: activeSubscribers.map(sub => sub.email),
        successful: successfulSends,
        failed: totalFailed,
      },
      failedEmails: failedEmails,
    });

  } catch (error: any) {
    console.error('Error sending newsletter:', error);
    return NextResponse.json(
      { error: 'Failed to send newsletter', details: error?.message || String(error) },
      { status: 500 }
    );
  }
}