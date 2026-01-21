import {
  Html,
  Head,
  Body,
  Container,
  Section,
  Text,
  Heading,
  Link,
  Img,
} from '@react-email/components';

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

interface NewsletterProps {
  topFive: Array<{
    name: string;
    ticker: string;
    trendScore: number;
    sentimentScore: number;
    hypeScore: number;
    proposedPriceLow?: number;
    proposedPriceHigh?: number;
    sharesOffered?: number;
    impliedMarketCap?: number;
    enterpriseValue?: number;
    revenue?: number;
    netIncome?: number;
    revenueGrowthYoY?: number;
    grossMargin?: number;
    operatingMargin?: number;
    cashBurn?: number;
    freeCashFlow?: number;
    aiAnalysis?: string;
    recommendation?: string;
    riskLevel?: string;
    marketOutlook?: string;
  }>;
  pricingTable?: Array<{
    company: string;
    symbol: string;
    leadManagers: string;
    sharesMillions: string;
    priceLow: string;
    priceHigh: string;
    estVolume: string;
    expectedToTrade: string;
    scoopRating: string;
    ratingChange: string;
  }>;
  barChartUrl: string;
  trendChartUrl: string;
  metricsChartUrl: string;
  unsubscribeUrl: string;
  newsletterSummary?: string;
  ipoTable?: IPOTableRow[];
}

const formatCurrency = (value?: number | null) => {
  if (value === undefined || value === null || Number.isNaN(value)) {
    return 'N/A';
  }
  return `$${Number(value).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
};

const formatPercent = (value?: number | null) => {
  if (value === undefined || value === null || Number.isNaN(value)) {
    return 'N/A';
  }
  return `${(value * 100).toFixed(1)}%`;
};

const formatPriceRange = (low?: number | null, high?: number | null) => {
  if (low && high) {
    return `${formatCurrency(low)} – ${formatCurrency(high)}`;
  }
  if (low) return formatCurrency(low);
  if (high) return formatCurrency(high);
  return 'N/A';
};

const parseNumberFromString = (value?: string | number | null) => {
  if (value === undefined || value === null) return null;
  if (typeof value === 'number') return Number.isFinite(value) ? value : null;
  const match = String(value).replace(/[,\s]/g, '').match(/-?\d+(\.\d+)?/);
  return match ? Number(match[0]) : null;
};

const parseVolumeToMillions = (value?: string | null) => {
  if (!value) return 0;
  const cleaned = value.trim().toLowerCase();
  const number = parseNumberFromString(cleaned) || 0;
  if (cleaned.includes('bil')) {
    return number * 1000;
  }
  if (cleaned.includes('mil') || cleaned.includes('mm')) {
    return number;
  }
  if (cleaned.includes('k')) {
    return number / 1000;
  }
  return number / 1_000_000;
};

const parsePrice = (value?: string | null) => {
  const parsed = parseNumberFromString(value);
  return parsed !== null && parsed > 0 ? parsed : null;
};

const formatMillions = (value: number) => {
  if (value >= 1000) {
    return `$${(value / 1000).toFixed(1)}B`;
  }
  if (value > 0) {
    return `$${value.toFixed(1)}M`;
  }
  return 'N/A';
};

export default function Newsletter({
  topFive,
  pricingTable = [],
  barChartUrl,
  trendChartUrl,
  metricsChartUrl,
  unsubscribeUrl,
  newsletterSummary,
  ipoTable,
}: NewsletterProps) {
  const today = new Date();
  const formattedDate = today.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  });

  const totalIpos = pricingTable.length;
  const totalVolumeMillions = pricingTable.reduce(
    (sum, row) => sum + parseVolumeToMillions(row.estVolume),
    0
  );
  const lowestPrice = Math.min(
    ...pricingTable
      .map((row) => parsePrice(row.priceLow))
      .filter((price): price is number => price !== null),
  );
  const highestPrice = Math.max(
    ...pricingTable
      .map((row) => parsePrice(row.priceHigh))
      .filter((price): price is number => price !== null),
  );
  const uplistings = pricingTable.filter((row) =>
    row.company?.toLowerCase().includes('uplisting')
  ).length;

  const averageHype =
    topFive.length > 0
      ? topFive.reduce((sum, ipo) => sum + ipo.hypeScore, 0) / topFive.length
      : 0;
  const averageTrend =
    topFive.length > 0
      ? topFive.reduce((sum, ipo) => sum + ipo.trendScore, 0) / topFive.length
      : 0;
  const averageSentiment =
    topFive.length > 0
      ? topFive.reduce((sum, ipo) => sum + (ipo.sentimentScore ?? 0), 0) /
        topFive.length
      : 0;
  const buyRecommendations = topFive.filter((ipo) =>
    (ipo.recommendation || '').toLowerCase().includes('buy')
  ).length;
  const topPick = topFive[0];
  const [largestVolume] = [...pricingTable]
    .map((row) => ({
      row,
      volume: parseVolumeToMillions(row.estVolume),
    }))
    .sort((a, b) => b.volume - a.volume);

  const priceWindowLabel =
    Number.isFinite(lowestPrice) && Number.isFinite(highestPrice)
      ? `${formatCurrency(lowestPrice)} – ${formatCurrency(highestPrice)}`
      : 'N/A';

  const barsData = [
    {
      label: 'Average Hype Score',
      display: averageHype.toFixed(1),
      percent: Math.min(100, Math.round(averageHype)),
    },
    {
      label: 'Average Trend Momentum',
      display: averageTrend.toFixed(0),
      percent: Math.min(100, Math.round(averageTrend)),
    },
    {
      label: 'Average Sentiment',
      display: formatPercent(averageSentiment),
      percent: Math.min(100, Math.round(averageSentiment * 100)),
    },
    {
      label: 'Buy / Strong Buy Signals',
      display: `${buyRecommendations}`,
      percent:
        topFive.length > 0
          ? Math.min(100, Math.round((buyRecommendations / topFive.length) * 100))
          : 0,
    },
  ];

  const insights: string[] = [];
  if (topPick) {
    insights.push(
      `${topPick.name} (${topPick.ticker}) tops the hype board at ${topPick.hypeScore.toFixed(
        1,
      )}, with sentiment running ${formatPercent(topPick.sentimentScore)}.`
    );
  }
  if (largestVolume?.row) {
    insights.push(
      `${largestVolume.row.company} leads deal size at ${formatMillions(
        largestVolume.volume,
      )}.`
    );
  }
  if (totalIpos > 0) {
    insights.push(
      `We are tracking ${totalIpos} offerings with an aggregate projected volume of ${formatMillions(
        totalVolumeMillions,
      )}.`
    );
  }
  insights.push(`Current price window spans ${priceWindowLabel}.`);

  const upcomingRows = pricingTable
    .filter((row) => !/priced/i.test(row.expectedToTrade || ''))
    .slice(0, 12);
  const pricedRows = pricingTable
    .filter((row) => /priced/i.test(row.expectedToTrade || ''))
    .slice(0, 12);
  let filingsRows = pricingTable
    .filter((row) => /filing/i.test(row.expectedToTrade || ''))
    .slice(0, 8);
  if (filingsRows.length === 0 && pricingTable.length > 0) {
    filingsRows = pricingTable.slice(0, Math.min(6, pricingTable.length));
  }

  return (
    <Html>
      <Head />
      <Body style={mainStyle}>
        <Container style={containerStyle}>
          <Section style={headerSection}>
            <Text style={volBadge}>VOL. 01</Text>
            <Heading style={headerTitle}>
              <span style={headerTitleLine}>WEEKLY</span>
              <span style={headerTitleLine}>NEWSLETTER</span>
            </Heading>
            <div style={headerDivider} />
            <Text style={headerIntro}>
              {`Fresh off the wire for ${formattedDate}. We blend live market data, historical comps, and GPT-4 mini commentary so you know which listings are primed to move.`}
            </Text>
          </Section>

          <Section style={marketSection}>
            <Heading style={sectionTitle}>
              <span style={sectionTitleLine}>MARKET</span>
              <span style={sectionTitleLine}>OVERVIEW</span>
            </Heading>
            <Text style={sectionDescription}>
              {newsletterSummary ||
                `Average hype score across the cohort lands at ${averageHype.toFixed(
                  1,
                )}. ${buyRecommendations} listings hold buy-or-better status, with ${totalVolumeMillions > 0 ? formatMillions(totalVolumeMillions) : 'N/A'} in projected proceeds on the docket.`}
            </Text>

            <table style={statsTable} cellPadding={0} cellSpacing={0}>
              <tbody>
                <tr>
                  <td style={statCell}>
                    <Text style={statNumber}>{totalIpos}</Text>
                    <Text style={statLabel}>Total IPOs</Text>
                  </td>
                  <td style={statCell}>
                    <Text style={statNumber}>{formatMillions(totalVolumeMillions)}</Text>
                    <Text style={statLabel}>Total Volume</Text>
                  </td>
                  <td style={statCell}>
                    <Text style={statNumber}>{priceWindowLabel}</Text>
                    <Text style={statLabel}>Price Window</Text>
                  </td>
                  <td style={statCell}>
                    <Text style={statNumber}>{uplistings}</Text>
                    <Text style={statLabel}>Uplistings</Text>
                  </td>
                </tr>
              </tbody>
            </table>

            <div style={barChartSection}>
              {barsData.map((bar) => (
                <div key={bar.label} style={barItem}>
                  <Text style={barLabel}>{bar.label}</Text>
                  <div style={barWrapper}>
                    <div
                      style={{
                        ...barFill,
                        width: `${Math.max(10, bar.percent)}%`,
                      }}
                    >
                      <Text style={barValue}>{bar.display}</Text>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {insights.length > 0 && (
              <div style={insightsSection}>
                <Text style={insightsTitle}>Key Insights</Text>
                <ul style={insightsList}>
                  {insights.map((item, idx) => (
                    <li key={idx} style={insightRow}>
                      <span style={insightBullet}>→</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </Section>

          {topFive.length > 0 && (
            <Section style={stocksSection}>
              <Heading style={sectionTitle}>
                <span style={sectionTitleLine}>TOP 5</span>
                <span style={sectionTitleLine}>SIGNALS</span>
              </Heading>
              <Text style={sectionDescription}>
                The highest conviction listings ranked by hype score with GPT-4 mini analysis layered on top of live metrics.
              </Text>
              {topFive.map((ipo, idx) => (
                <table key={ipo.ticker} style={stockCard} cellPadding={0} cellSpacing={0}>
                  <tbody>
                    <tr>
                      <td style={stockRankCell}>#{idx + 1}</td>
                      <td style={stockContentCell}>
                        <Text style={stockName}>{ipo.name}</Text>
                        <Text style={stockSymbol}>{
                          ipo.ticker
                        }</Text>
                        <Text style={stockDescription}>
                          {ipo.aiAnalysis || 'AI analysis is still generating for this listing.'}
                        </Text>
                        <table style={stockMetricsTable} cellPadding={0} cellSpacing={0}>
                          <tbody>
                            <tr>
                              <td style={stockMetricLabel}>Hype</td>
                              <td style={stockMetricValue}>{ipo.hypeScore.toFixed(1)}</td>
                              <td style={stockMetricLabel}>Trend</td>
                              <td style={stockMetricValue}>{ipo.trendScore.toFixed(0)}</td>
                              <td style={stockMetricLabel}>Sentiment</td>
                              <td style={stockMetricValue}>{formatPercent(ipo.sentimentScore)}</td>
                            </tr>
                            <tr>
                              <td style={stockMetricLabel}>Price Range</td>
                              <td style={stockMetricValue} colSpan={3}>
                                {formatPriceRange(ipo.proposedPriceLow, ipo.proposedPriceHigh)}
                              </td>
                              <td style={stockMetricLabel}>Recommendation</td>
                              <td style={stockMetricValue}>{ipo.recommendation || '—'}</td>
                            </tr>
                          </tbody>
                        </table>
                        <Text style={stockDetails}>
                          <strong>Risk:</strong> {ipo.riskLevel || '—'} · <strong>Market Outlook:</strong> {ipo.marketOutlook || '—'}
                        </Text>
                      </td>
                    </tr>
                  </tbody>
                </table>
              ))}
            </Section>
          )}

          {upcomingRows.length > 0 && (
            <Section style={tableSection}>
              <Heading style={sectionTitle}>
                <span style={sectionTitleLine}>UPCOMING</span>
              </Heading>
              <Text style={sectionDescription}>Listings scheduled to price or open soon.</Text>
              <div style={tableContainer}>
                <table style={dataTable} cellPadding={0} cellSpacing={0}>
                  <thead>
                    <tr>
                      <th style={tableHeader}>Company</th>
                      <th style={tableHeader}>Symbol</th>
                      <th style={tableHeader}>Lead Managers</th>
                      <th style={tableHeader}>Shares (M)</th>
                      <th style={tableHeader}>Price Low</th>
                      <th style={tableHeader}>Price High</th>
                      <th style={tableHeader}>Est. $ Volume</th>
                      <th style={tableHeader}>Expected</th>
                      <th style={tableHeader}>SCOOP</th>
                      <th style={tableHeader}>Rating Δ</th>
                    </tr>
                  </thead>
                  <tbody>
                    {upcomingRows.map((row, idx) => (
                      <tr
                        key={`${row.symbol}-${idx}`}
                        style={idx % 2 === 0 ? tableRowEven : tableRowOdd}
                      >
                        <td style={tableCell}>{row.company}</td>
                        <td style={tableCellStrong}>{row.symbol}</td>
                        <td style={tableCell}>{row.leadManagers}</td>
                        <td style={tableCellNumeric}>{row.sharesMillions}</td>
                        <td style={tableCellNumeric}>{row.priceLow}</td>
                        <td style={tableCellNumeric}>{row.priceHigh}</td>
                        <td style={tableCellNumeric}>{row.estVolume}</td>
                        <td style={tableCell}>{row.expectedToTrade}</td>
                        <td style={tableCell}>{row.scoopRating}</td>
                        <td style={tableCell}>{row.ratingChange}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Section>
          )}

          {pricedRows.length > 0 && (
            <Section style={tableSection}>
              <Heading style={sectionTitle}>
                <span style={sectionTitleLine}>PRICED</span>
              </Heading>
              <Text style={sectionDescription}>Deals already priced and ready to trade.</Text>
              <div style={tableContainer}>
                <table style={dataTable} cellPadding={0} cellSpacing={0}>
                  <thead>
                    <tr>
                      <th style={tableHeader}>Company</th>
                      <th style={tableHeader}>Symbol</th>
                      <th style={tableHeader}>Lead Managers</th>
                      <th style={tableHeader}>Price</th>
                      <th style={tableHeader}>Shares (M)</th>
                      <th style={tableHeader}>Est. $ Volume</th>
                      <th style={tableHeader}>Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pricedRows.map((row, idx) => (
                      <tr
                        key={`${row.symbol}-priced-${idx}`}
                        style={idx % 2 === 0 ? tableRowEven : tableRowOdd}
                      >
                        <td style={tableCell}>{row.company}</td>
                        <td style={tableCellStrong}>{row.symbol}</td>
                        <td style={tableCell}>{row.leadManagers}</td>
                        <td style={tableCellNumeric}>{`${row.priceLow} - ${row.priceHigh}`}</td>
                        <td style={tableCellNumeric}>{row.sharesMillions}</td>
                        <td style={tableCellNumeric}>{row.estVolume}</td>
                        <td style={tableCell}>{row.expectedToTrade}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Section>
          )}

          {filingsRows.length > 0 && (
            <Section style={tableSection}>
              <Heading style={sectionTitle}>
                <span style={sectionTitleLine}>FILINGS</span>
              </Heading>
              <Text style={sectionDescription}>Fresh filings and first-time entrants to watch.</Text>
              <div style={tableContainer}>
                <table style={dataTable} cellPadding={0} cellSpacing={0}>
                  <thead>
                    <tr>
                      <th style={tableHeader}>Company</th>
                      <th style={tableHeader}>Symbol</th>
                      <th style={tableHeader}>Lead Managers</th>
                      <th style={tableHeader}>Price</th>
                      <th style={tableHeader}>Shares (M)</th>
                      <th style={tableHeader}>Est. $ Volume</th>
                      <th style={tableHeader}>Expected</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filingsRows.map((row, idx) => (
                      <tr
                        key={`${row.symbol}-filing-${idx}`}
                        style={idx % 2 === 0 ? tableRowEven : tableRowOdd}
                      >
                        <td style={tableCell}>{row.company}</td>
                        <td style={tableCellStrong}>{row.symbol}</td>
                        <td style={tableCell}>{row.leadManagers}</td>
                        <td style={tableCellNumeric}>{`${row.priceLow} - ${row.priceHigh}`}</td>
                        <td style={tableCellNumeric}>{row.sharesMillions}</td>
                        <td style={tableCellNumeric}>{row.estVolume}</td>
                        <td style={tableCell}>{row.expectedToTrade}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Section>
          )}

          {(barChartUrl || trendChartUrl || metricsChartUrl) && (
            <Section style={chartSection}>
              <Heading style={sectionTitle}>
                <span style={sectionTitleLine}>DATA</span>
                <span style={sectionTitleLine}>SNAPSHOTS</span>
              </Heading>
              <Text style={sectionDescription}>
                Visual scorecards rendered at send time so you can audit the signals backing each ranking.
              </Text>
              <div style={chartGrid}>
                {barChartUrl && (
                  <div style={chartCard}>
                    <Text style={chartLabel}>Market Interest</Text>
                    <Img src={barChartUrl} alt="Market Interest" style={chartImage} />
                  </div>
                )}
                {trendChartUrl && (
                  <div style={chartCard}>
                    <Text style={chartLabel}>7-Day Trendline</Text>
                    <Img src={trendChartUrl} alt="Trend Chart" style={chartImage} />
                  </div>
                )}
                {metricsChartUrl && (
                  <div style={chartCardWide}>
                    <Text style={chartLabel}>Component Breakdown</Text>
                    <Img src={metricsChartUrl} alt="Component Breakdown" style={chartImage} />
                  </div>
                )}
              </div>
            </Section>
          )}

          <Section style={footerSection}>
            <Text style={footerBrand}>IPO HYPE TRACKER</Text>
            <Text style={footerCopy}>
              Twice-weekly coverage built from live APIs, historical benchmarking, and GPT-4 mini insights.
            </Text>
            <Text style={footerLinks}>
              <Link href={process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'} style={footerLink}>
                IPOHypeTracker.com
              </Link>
              {' · '}
              <Link href={unsubscribeUrl} style={footerLink}>
                Unsubscribe
              </Link>
            </Text>
            <Text style={footerMeta}>© {today.getFullYear()} IPO Hype Tracker. All rights reserved.</Text>
          </Section>
        </Container>
      </Body>
    </Html>
  );
}

const mainStyle = {
  margin: 0,
  padding: '0 16px',
  backgroundColor: '#1f2937',
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
};

const containerStyle = {
  maxWidth: '720px',
  margin: '0 auto',
  backgroundColor: '#1f2937',
};

const headerSection = {
  padding: '48px 32px 40px',
  backgroundColor: '#1f2937',
};

const volBadge = {
  color: '#ffffff',
  fontSize: '14px',
  fontWeight: 500,
  letterSpacing: '1px',
  textAlign: 'right' as const,
};

const headerTitle = {
  color: '#ff6b35',
  fontSize: '68px',
  fontWeight: 900,
  lineHeight: '0.9',
  margin: '24px 0 0',
  letterSpacing: '-2px',
};

const headerTitleLine = {
  display: 'block',
};

const headerDivider = {
  width: '100%',
  height: '1px',
  backgroundColor: 'rgba(255,255,255,0.3)',
  margin: '28px 0',
};

const headerIntro = {
  color: '#ffffff',
  fontSize: '16px',
  lineHeight: '1.6',
  maxWidth: '780px',
  margin: 0,
};

const sectionTitle = {
  color: '#ffffff',
  fontSize: '48px',
  fontWeight: 900,
  margin: '0 0 12px',
  letterSpacing: '-1px',
};

const sectionTitleLine = {
  display: 'block',
};

const sectionDescription = {
  color: '#ffffff',
  fontSize: '16px',
  lineHeight: '1.6',
  margin: '0 0 28px',
  opacity: 0.9,
};

const marketSection = {
  padding: '48px 32px',
  backgroundColor: '#374151',
};

const statsTable = {
  width: '100%',
  borderCollapse: 'collapse' as const,
  marginBottom: '28px',
};

const statCell = {
  padding: '18px 12px',
  border: '1px solid rgba(255,255,255,0.12)',
  textAlign: 'center' as const,
  backgroundColor: 'rgba(17,24,39,0.4)',
};

const statNumber = {
  color: '#ff6b35',
  fontSize: '28px',
  fontWeight: 900,
  margin: '0 0 6px',
};

const statLabel = {
  color: '#ffffff',
  fontSize: '12px',
  letterSpacing: '1px',
  textTransform: 'uppercase' as const,
  margin: 0,
};

const barChartSection = {
  marginBottom: '32px',
};

const barItem = {
  marginBottom: '16px',
};

const barLabel = {
  color: '#ffffff',
  fontSize: '13px',
  fontWeight: 600,
  margin: '0 0 6px',
};

const barWrapper = {
  backgroundColor: 'rgba(255,255,255,0.12)',
  height: '28px',
  borderRadius: '4px',
  overflow: 'hidden',
};

const barFill = {
  background: 'linear-gradient(90deg, #ff6b35 0%, #ff8c5a 100%)',
  height: '28px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'flex-end' as const,
  paddingRight: '10px',
};

const barValue = {
  color: '#ffffff',
  fontSize: '12px',
  fontWeight: 700,
  margin: 0,
};

const insightsSection = {
  borderTop: '1px solid rgba(255,255,255,0.12)',
  paddingTop: '24px',
};

const insightsTitle = {
  color: '#ffffff',
  fontSize: '20px',
  fontWeight: 700,
  margin: '0 0 12px',
  letterSpacing: '1px',
};

const insightsList = {
  listStyle: 'none',
  margin: 0,
  padding: 0,
};

const insightRow = {
  color: '#ffffff',
  fontSize: '14px',
  lineHeight: '1.7',
  marginBottom: '12px',
  display: 'flex',
  gap: '8px',
  alignItems: 'flex-start',
};

const insightBullet = {
  color: '#ff6b35',
  fontWeight: 700,
};

const stocksSection = {
  padding: '48px 32px',
  backgroundColor: '#1f2937',
};

const stockCard = {
  width: '100%',
  borderCollapse: 'collapse' as const,
  marginBottom: '24px',
  border: '1px solid rgba(255,255,255,0.1)',
  backgroundColor: 'rgba(255,255,255,0.05)',
  borderRadius: '8px',
  overflow: 'hidden',
};

const stockRankCell = {
  width: '64px',
  padding: '24px 16px',
  backgroundColor: 'rgba(255,107,53,0.15)',
  color: '#ff6b35',
  fontSize: '40px',
  fontWeight: 900,
  textAlign: 'center' as const,
  verticalAlign: 'top' as const,
};

const stockContentCell = {
  padding: '24px',
  verticalAlign: 'top' as const,
  backgroundColor: 'rgba(0,0,0,0)',
};

const stockName = {
  color: '#ffffff',
  fontSize: '24px',
  fontWeight: 700,
  margin: '0 0 6px',
};

const stockSymbol = {
  color: '#ff6b35',
  fontSize: '16px',
  fontWeight: 600,
  letterSpacing: '2px',
  textTransform: 'uppercase' as const,
  margin: '0 0 12px',
};

const stockDescription = {
  color: '#ffffff',
  fontSize: '14px',
  lineHeight: '1.7',
  margin: '0 0 16px',
  opacity: 0.9,
};

const stockMetricsTable = {
  width: '100%',
  borderCollapse: 'collapse' as const,
  marginBottom: '16px',
};

const stockMetricLabel = {
  color: '#9ca3af',
  fontSize: '12px',
  padding: '4px 6px',
  textTransform: 'uppercase' as const,
  letterSpacing: '1px',
};

const stockMetricValue = {
  color: '#ffffff',
  fontSize: '13px',
  padding: '4px 6px',
  fontWeight: 600,
};

const stockDetails = {
  color: '#d1d5db',
  fontSize: '12px',
  margin: 0,
  borderTop: '1px solid rgba(255,255,255,0.1)',
  paddingTop: '12px',
};

const tableSection = {
  padding: '48px 32px',
  backgroundColor: '#4b5563',
};

const tableContainer = {
  border: '1px solid rgba(255,255,255,0.1)',
  borderRadius: '4px',
  overflow: 'hidden',
};

const dataTable = {
  width: '100%',
  borderCollapse: 'collapse' as const,
  fontSize: '12px',
  backgroundColor: '#374151',
};

const tableHeader = {
  padding: '14px 12px',
  textAlign: 'left' as const,
  fontWeight: 700,
  fontSize: '11px',
  textTransform: 'uppercase' as const,
  letterSpacing: '1px',
  color: '#ffffff',
  backgroundColor: '#1f2937',
  borderBottom: '2px solid #ff6b35',
  whiteSpace: 'nowrap' as const,
};

const tableRowEven = {
  backgroundColor: 'rgba(255,255,255,0.05)',
};

const tableRowOdd = {
  backgroundColor: 'rgba(255,255,255,0.08)',
};

const tableCell = {
  padding: '12px 10px',
  color: '#ffffff',
  borderBottom: '1px solid rgba(255,255,255,0.08)',
  fontSize: '12px',
  verticalAlign: 'top' as const,
};

const tableCellStrong = {
  ...tableCell,
  color: '#ffba70',
  letterSpacing: '1px',
  textTransform: 'uppercase' as const,
};

const tableCellNumeric = {
  ...tableCell,
  textAlign: 'right' as const,
};

const chartSection = {
  padding: '48px 32px',
  backgroundColor: '#1f2937',
};

const chartGrid = {
  display: 'flex',
  flexWrap: 'wrap' as const,
  gap: '16px',
};

const chartCard = {
  flex: '1 1 220px',
  backgroundColor: 'rgba(255,255,255,0.05)',
  border: '1px solid rgba(255,255,255,0.1)',
  borderRadius: '8px',
  padding: '16px',
};

const chartCardWide = {
  ...chartCard,
  flex: '1 1 100%',
};

const chartLabel = {
  color: '#ffffff',
  fontSize: '13px',
  fontWeight: 600,
  margin: '0 0 12px',
  textTransform: 'uppercase' as const,
  letterSpacing: '1px',
};

const chartImage = {
  width: '100%',
  borderRadius: '6px',
  border: '1px solid rgba(255,255,255,0.1)',
};

const footerSection = {
  padding: '36px 32px 48px',
  backgroundColor: '#1f2937',
  borderTop: '1px solid rgba(255,255,255,0.12)',
};

const footerBrand = {
  color: '#ffffff',
  fontSize: '18px',
  letterSpacing: '2px',
  textTransform: 'uppercase' as const,
  margin: '0 0 12px',
};

const footerCopy = {
  color: '#d1d5db',
  fontSize: '14px',
  lineHeight: '1.6',
  margin: '0 0 16px',
};

const footerLinks = {
  color: '#fbbf24',
  fontSize: '13px',
  margin: '0 0 12px',
};

const footerLink = {
  color: '#fbbf24',
  textDecoration: 'none',
};

const footerMeta = {
  color: '#94a3b8',
  fontSize: '12px',
  margin: 0,
};

// Styles for IPO table
const tableContainer = {
  overflowX: 'auto' as const,
  marginTop: '16px',
  border: '1px solid #e5e7eb',
  borderRadius: '8px',
};

const dataTable = {
  width: '100%',
  borderCollapse: 'collapse' as const,
  fontSize: '12px',
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  backgroundColor: '#ffffff',
};

const tableHeaderRow = {
  backgroundColor: '#1f2937',
  color: '#ffffff',
};

const tableHeaderCell = {
  padding: '12px 8px',
  textAlign: 'left' as const,
  fontWeight: '600',
  fontSize: '11px',
  textTransform: 'uppercase' as const,
  borderBottom: '2px solid #374151',
  whiteSpace: 'nowrap' as const,
  color: '#ffffff',
};

const tableRowEven = {
  backgroundColor: '#ffffff',
};

const tableRowOdd = {
  backgroundColor: '#f9fafb',
};

const tableCell = {
  padding: '10px 8px',
  borderBottom: '1px solid #e5e7eb',
  color: '#374151',
  fontSize: '12px',
  whiteSpace: 'nowrap' as const,
  verticalAlign: 'top' as const,
};
