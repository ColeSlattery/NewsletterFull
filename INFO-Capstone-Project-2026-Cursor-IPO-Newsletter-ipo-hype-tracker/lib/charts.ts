/**
 * Chart generation using QuickChart API
 * Documentation: https://quickchart.io/documentation/
 */

interface TopFiveData {
  name: string;
  ticker: string;
  trendScore: number;
  sentimentScore: number;
}

interface TrendData {
  date: string;
  value: number;
}

/**
 * Generates a bar chart URL for top 5 IPO companies
 */
export function makeBarChart(topFive: TopFiveData[]): string {
  try {
    const labels = topFive.map(ipo => ipo.ticker);
    const data = topFive.map(ipo => ipo.trendScore);
    const colors = [
      '#dc2626', // red-600
      '#ea580c', // orange-600
      '#d97706', // amber-600
      '#ca8a04', // yellow-600
      '#65a30d', // lime-600
    ];

    const chartConfig = {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Trend Score',
            data,
            backgroundColor: colors,
            borderColor: colors.map(color => color + '80'), // Add transparency
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Top 5 IPO Companies - Market Interest',
            font: {
              size: 16,
              weight: 'bold',
            },
          },
          legend: {
            display: false,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            title: {
              display: true,
              text: 'Trend Score (0-100)',
            },
          },
          x: {
            title: {
              display: true,
              text: 'Company Ticker',
            },
          },
        },
      },
    };

    const encodedConfig = encodeURIComponent(JSON.stringify(chartConfig));
    const chartUrl = `https://quickchart.io/chart?c=${encodedConfig}&width=800&height=400&format=png&backgroundColor=white`;
    
    console.log('Generated bar chart URL for top 5 IPOs');
    return chartUrl;
  } catch (error) {
    console.error('Error generating bar chart:', error);
    return '';
  }
}

/**
 * Generates a line chart URL for 7-day trend data
 */
export function makeTrendChart(companyName: string, data: TrendData[]): string {
  try {
    const labels = data.map(d => d.date);
    const values = data.map(d => d.value);

    const chartConfig = {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Interest Trend',
            data: values,
            borderColor: '#2563eb', // blue-600
            backgroundColor: '#2563eb20', // blue-600 with transparency
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#2563eb',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            pointRadius: 5,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: `${companyName} - 7-Day Interest Trend`,
            font: {
              size: 16,
              weight: 'bold',
            },
          },
          legend: {
            display: false,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            max: Math.max(...values) * 1.1,
            title: {
              display: true,
              text: 'Interest Score',
            },
          },
          x: {
            title: {
              display: true,
              text: 'Date',
            },
          },
        },
        elements: {
          point: {
            hoverRadius: 8,
          },
        },
      },
    };

    const encodedConfig = encodeURIComponent(JSON.stringify(chartConfig));
    const chartUrl = `https://quickchart.io/chart?c=${encodedConfig}&width=800&height=400&format=png&backgroundColor=white`;
    
    console.log(`Generated trend chart URL for ${companyName}`);
    return chartUrl;
  } catch (error) {
    console.error('Error generating trend chart:', error);
    return '';
  }
}

/**
 * Generates a combined chart showing both trend scores and sentiment scores
 */
export function makeCombinedChart(topFive: TopFiveData[]): string {
  try {
    const labels = topFive.map(ipo => ipo.ticker);
    const trendData = topFive.map(ipo => ipo.trendScore);
    const sentimentData = topFive.map(ipo => ipo.sentimentScore * 100); // Convert to percentage

    const chartConfig = {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Trend Score',
            data: trendData,
            backgroundColor: '#3b82f6', // blue-500
            borderColor: '#1d4ed8', // blue-700
            borderWidth: 2,
            yAxisID: 'y',
          },
          {
            label: 'Sentiment Score (%)',
            data: sentimentData,
            backgroundColor: '#10b981', // emerald-500
            borderColor: '#059669', // emerald-600
            borderWidth: 2,
            yAxisID: 'y1',
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'IPO Companies - Trend vs Sentiment Analysis',
            font: {
              size: 16,
              weight: 'bold',
            },
          },
        },
        scales: {
          y: {
            type: 'linear',
            display: true,
            position: 'left',
            title: {
              display: true,
              text: 'Trend Score (0-100)',
            },
            max: 100,
          },
          y1: {
            type: 'linear',
            display: true,
            position: 'right',
            title: {
              display: true,
              text: 'Sentiment Score (%)',
            },
            max: 100,
            grid: {
              drawOnChartArea: false,
            },
          },
        },
      },
    };

    const encodedConfig = encodeURIComponent(JSON.stringify(chartConfig));
    const chartUrl = `https://quickchart.io/chart?c=${encodedConfig}&width=900&height=400&format=png&backgroundColor=white`;
    
    console.log('Generated combined chart URL');
    return chartUrl;
  } catch (error) {
    console.error('Error generating combined chart:', error);
    return '';
  }
}

/**
 * Generates a pie chart showing sentiment distribution
 */
export function makeSentimentPieChart(sentimentBreakdown: Record<string, number>): string {
  try {
    const labels = Object.keys(sentimentBreakdown);
    const data = Object.values(sentimentBreakdown);
    const colors = {
      positive: '#10b981', // emerald-500
      negative: '#ef4444', // red-500
      neutral: '#6b7280', // gray-500
    };

    const chartConfig = {
      type: 'pie',
      data: {
        labels,
        datasets: [
          {
            data,
            backgroundColor: labels.map(label => colors[label as keyof typeof colors] || '#6b7280'),
            borderColor: '#ffffff',
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Market Sentiment Distribution',
            font: {
              size: 16,
              weight: 'bold',
            },
          },
          legend: {
            position: 'bottom',
          },
        },
      },
    };

    const encodedConfig = encodeURIComponent(JSON.stringify(chartConfig));
    const chartUrl = `https://quickchart.io/chart?c=${encodedConfig}&width=600&height=400&format=png&backgroundColor=white`;
    
    console.log('Generated sentiment pie chart URL');
    return chartUrl;
  } catch (error) {
    console.error('Error generating sentiment pie chart:', error);
    return '';
  }
}

// TODO for Developer:
// 1. Consider upgrading to QuickChart Pro for higher resolution and custom branding
// 2. Add caching for generated chart URLs to reduce API calls
// 3. Implement fallback chart generation using local libraries (Chart.js, D3.js)
// 4. Add more chart types (candlestick, area charts, etc.)
// 5. Implement dynamic chart sizing based on email client requirements
