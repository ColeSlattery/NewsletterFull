import { NextRequest, NextResponse } from 'next/server';
import { render } from '@react-email/render';
import Newsletter from '@/emails/Newsletter';
import { makeBarChart, makeTrendChart } from '@/lib/charts';

interface IPOTableRow {
  company: string;
  symbol: string;
  leadManagers: string;
  sharesMillions: number;
  priceLow: number;
  priceHigh: number;
  estVolume: string;
  expectedToTrade: string;
  scoopRating: string;
  ratingChange: string;
}

export async function POST(request: NextRequest) {
  try {
    const { ipoTableData } = await request.json();

    if (!ipoTableData || !Array.isArray(ipoTableData)) {
      return NextResponse.json(
        { error: 'ipoTableData array is required' },
        { status: 400 }
      );
    }

    // Parse the IPO table data
    const ipoTable: IPOTableRow[] = ipoTableData.map((row: any) => ({
      company: row.Company || row.company || '',
      symbol: row.Symbol || row.symbol || row['Symbol proposed'] || '',
      leadManagers: row['Lead Managers'] || row.leadManagers || row.LeadManagers || '',
      sharesMillions: parseFloat(row['Shares (Millions)'] || row.sharesMillions || row.shares || 0),
      priceLow: parseFloat(row['Price Low'] || row.priceLow || row.price_low || 0),
      priceHigh: parseFloat(row['Price High'] || row.priceHigh || row.price_high || 0),
      estVolume: row['Est. $ Volume'] || row.estVolume || row.est_volume || '',
      expectedToTrade: row['Expected to Trade'] || row.expectedToTrade || row.expected_to_trade || '',
      scoopRating: row['SCOOP Rating'] || row.scoopRating || row.scoop_rating || '',
      ratingChange: row['Rating Change'] || row.ratingChange || row.rating_change || '',
    }));

    // Create dummy top 5 data (can be empty or minimal)
    const topFive = ipoTable.slice(0, 5).map((row, index) => ({
      name: row.company,
      ticker: row.symbol,
      trendScore: 50,
      sentimentScore: 0,
      hypeScore: 50,
      proposedPriceLow: row.priceLow,
      proposedPriceHigh: row.priceHigh,
      sharesOffered: row.sharesMillions * 1000000,
      recommendation: 'Hold',
      riskLevel: 'Medium',
    }));

    // Generate charts (using dummy data if needed)
    const barChartUrl = topFive.length > 0 
      ? makeBarChart(topFive)
      : 'https://via.placeholder.com/600x300?text=No+Data';
    
    const trendData = Array.from({ length: 7 }).map((_, idx) => {
      const d = new Date();
      d.setDate(d.getDate() - (6 - idx));
      return {
        date: d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        value: 50,
      };
    });
    const trendChartUrl = topFive.length > 0
      ? makeTrendChart(topFive[0]?.name || 'IPO Market', trendData)
      : 'https://via.placeholder.com/600x300?text=No+Data';
    const metricsChartUrl = barChartUrl;

    // Generate newsletter summary
    const totalIPOs = ipoTable.length;
    const totalVolume = ipoTable.reduce((sum, row) => {
      const volumeStr = row.estVolume.replace(/[^0-9.]/g, '');
      return sum + parseFloat(volumeStr || '0');
    }, 0);
    const newsletterSummary = `This week's IPO calendar features ${totalIPOs} companies preparing to go public, with an estimated total volume of $${(totalVolume / 1000).toFixed(1)}B. The market shows diverse opportunities across various sectors, with companies ranging from small-cap offerings to major institutional deals.`;

    // Unsubscribe URL
    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';
    const unsubscribeUrl = `${baseUrl}/unsubscribe`;

    // Render email template
    const emailHtml = await render(
      Newsletter({
        topFive,
        barChartUrl,
        trendChartUrl,
        metricsChartUrl,
        unsubscribeUrl,
        newsletterSummary,
        ipoTable,
      })
    );

    // Return HTML that can be printed to PDF
    // The client can use browser's print to PDF functionality
    return new NextResponse(emailHtml, {
      headers: {
        'Content-Type': 'text/html',
        'Content-Disposition': 'inline; filename="newsletter.html"',
      },
    });

  } catch (error: any) {
    console.error('Error generating newsletter:', error);
    return NextResponse.json(
      { error: 'Failed to generate newsletter', details: error?.message || String(error) },
      { status: 500 }
    );
  }
}

