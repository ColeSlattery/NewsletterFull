/**
 * Standalone script to create newsletter HTML file
 * This doesn't require the API to be running
 * Usage: node scripts/create-newsletter-html-standalone.js
 */

const fs = require('fs');
const path = require('path');

// IPO Data
const IPO_DATA = [
  {
    Company: "Alussa Energy Acquisition Corp. II",
    "Symbol proposed": "ALUB.U",
    "Lead Managers": "Santander",
    "Shares (Millions)": 25.0,
    "Price Low": 10.00,
    "Price High": 10.00,
    "Est. $ Volume": "$ 250.0 mil",
    "Expected to Trade": "11/13/2025 Priced",
    "SCOOP Rating": "S/O",
    "Rating Change": "S/O"
  },
  {
    Company: "Caring Brands, Inc. (Uplisting)",
    "Symbol proposed": "CABR",
    "Lead Managers": "D. Boral Capital (ex-EF Hutton)",
    "Shares (Millions)": 1.0,
    "Price Low": 4.00,
    "Price High": 4.00,
    "Est. $ Volume": "$ 4.0 mil",
    "Expected to Trade": "11/13/2025 Priced",
    "SCOOP Rating": "S/O",
    "Rating Change": "S/O"
  },
  {
    Company: "Off the Hook YS",
    "Symbol proposed": "OTH",
    "Lead Managers": "ThinkEquity",
    "Shares (Millions)": 3.8,
    "Price Low": 4.00,
    "Price High": 4.00,
    "Est. $ Volume": "$ 15.0 mil",
    "Expected to Trade": "11/13/2025 Priced",
    "SCOOP Rating": "S/O",
    "Rating Change": "S/O"
  },
  {
    Company: "Phaos Technology (Cayman) Holdings Ltd.",
    "Symbol proposed": "POAS",
    "Lead Managers": "Network 1 Financial Securities",
    "Shares (Millions)": 3.6,
    "Price Low": 4.00,
    "Price High": 4.00,
    "Est. $ Volume": "$ 14.4 mil",
    "Expected to Trade": "11/13/2025 Priced",
    "SCOOP Rating": "S/O",
    "Rating Change": "S/O"
  },
  {
    Company: "Regentis Biomaterials, Ltd.",
    "Symbol proposed": "RGNT",
    "Lead Managers": "ThinkEquity",
    "Shares (Millions)": 1.0,
    "Price Low": 10.00,
    "Price High": 12.00,
    "Est. $ Volume": "$ 11.0 mil",
    "Expected to Trade": "11/14/2025 Friday",
    "SCOOP Rating": "S/O",
    "Rating Change": "S/O"
  },
  {
    Company: "DT House Ltd.",
    "Symbol proposed": "DTDT",
    "Lead Managers": "American Trust Investment Services",
    "Shares (Millions)": 2.0,
    "Price Low": 4.00,
    "Price High": 5.00,
    "Est. $ Volume": "$ 9.0 mil",
    "Expected to Trade": "11/17/2025 Week of",
    "SCOOP Rating": "S/O",
    "Rating Change": "S/O"
  },
  {
    Company: "ELC Group Holdings Ltd.",
    "Symbol proposed": "ELCG",
    "Lead Managers": "D. Boral Capital (ex-EF Hutton)",
    "Shares (Millions)": 1.9,
    "Price Low": 4.00,
    "Price High": 6.00,
    "Est. $ Volume": "$ 9.4 mil",
    "Expected to Trade": "11/17/2025 Week of",
    "SCOOP Rating": "S/O",
    "Rating Change": "S/O"
  },
  {
    Company: "Gloo Holdings, Inc.",
    "Symbol proposed": "GLOO",
    "Lead Managers": "Roth Capital Partners",
    "Shares (Millions)": 9.1,
    "Price Low": 10.00,
    "Price High": 12.00,
    "Est. $ Volume": "$ 100.1 mil",
    "Expected to Trade": "11/19/2025 Wednesday",
    "SCOOP Rating": "S/O",
    "Rating Change": "S/O"
  },
  {
    Company: "Central Bancompany (Uplisting)",
    "Symbol proposed": "CBC",
    "Lead Managers": "Morgan Stanley/Keefe, Bruyette & Woods (Stifel)/BofA Securities/Piper Sandler/Stephens Inc.",
    "Shares (Millions)": 17.8,
    "Price Low": 21.00,
    "Price High": 24.00,
    "Est. $ Volume": "$ 399.4 mil",
    "Expected to Trade": "11/20/2025 Thursday",
    "SCOOP Rating": "S/O",
    "Rating Change": "S/O"
  },
  {
    Company: "ALE Group Holding Limited",
    "Symbol proposed": "ALEH",
    "Lead Managers": "D. Boral Capital (ex-EF Hutton)",
    "Shares (Millions)": 1.5,
    "Price Low": 4.00,
    "Price High": 6.00,
    "Est. $ Volume": "$ 7.5 mil",
    "Expected to Trade": "11/21/2025 Week of",
    "SCOOP Rating": "S/O",
    "Rating Change": "S/O"
  },
  {
    Company: "Anew Health Ltd.",
    "Symbol proposed": "AVG",
    "Lead Managers": "D. Boral Capital (ex-EF Hutton)",
    "Shares (Millions)": 1.8,
    "Price Low": 4.00,
    "Price High": 6.00,
    "Est. $ Volume": "$ 9.0 mil",
    "Expected to Trade": "11/21/2025 Week of",
    "SCOOP Rating": "S/O",
    "Rating Change": "S/O"
  },
  {
    Company: "Libera Gaming Operations",
    "Symbol proposed": "LBRJ",
    "Lead Managers": "D. Boral Capital (ex-EF Hutton)/Sutter Securities",
    "Shares (Millions)": 1.3,
    "Price Low": 4.00,
    "Price High": 4.00,
    "Est. $ Volume": "$ 5.0 mil",
    "Expected to Trade": "11/21/2025 Week of",
    "SCOOP Rating": "S/O",
    "Rating Change": "S/O"
  },
  {
    Company: "Monkey Tree Investment Ltd.",
    "Symbol proposed": "MKTR",
    "Lead Managers": "Craft Capital Management/Revere Securities",
    "Shares (Millions)": 1.6,
    "Price Low": 4.00,
    "Price High": 5.00,
    "Est. $ Volume": "$ 7.0 mil",
    "Expected to Trade": "11/24/2025 Week of",
    "SCOOP Rating": "S/O",
    "Rating Change": "S/O"
  },
  {
    Company: "AIGO Holding Ltd.",
    "Symbol proposed": "AIGO",
    "Lead Managers": "Eddid Securities USA",
    "Shares (Millions)": 2.0,
    "Price Low": 4.00,
    "Price High": 6.00,
    "Est. $ Volume": "$ 10.0 mil",
    "Expected to Trade": "12/1/2025 Week of",
    "SCOOP Rating": "S/O",
    "Rating Change": "S/O"
  },
  {
    Company: "HW Electro Co., Ltd. (NASDAQ-New Filing)",
    "Symbol proposed": "HWEP",
    "Lead Managers": "American Trust Investment Services/WestPark Capital",
    "Shares (Millions)": 4.2,
    "Price Low": 4.00,
    "Price High": 4.00,
    "Est. $ Volume": "$ 16.6 mil",
    "Expected to Trade": "12/1/2025 Week of",
    "SCOOP Rating": "S/O",
    "Rating Change": "S/O"
  },
  {
    Company: "PressLogic",
    "Symbol proposed": "PLAI",
    "Lead Managers": "American Trust Investment Services",
    "Shares (Millions)": 1.8,
    "Price Low": 4.00,
    "Price High": 6.00,
    "Est. $ Volume": "$ 9.0 mil",
    "Expected to Trade": "12/1/2025 Week of",
    "SCOOP Rating": "S/O",
    "Rating Change": "S/O"
  },
  {
    Company: "Public Policy Holding Co. (NASDAQ Uplisting)",
    "Symbol proposed": "PPHC",
    "Lead Managers": "Oppenheimer & Co./Canaccord Genuity/Texas Capital Securities",
    "Shares (Millions)": 4.1,
    "Price Low": 14.64,
    "Price High": 14.64,
    "Est. $ Volume": "$ 60.0 mil",
    "Expected to Trade": "12/1/2025 Week of",
    "SCOOP Rating": "S/O",
    "Rating Change": "S/O"
  }
];

function formatDate() {
  const date = new Date();
  return date.toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
}

function generateTableRows() {
  return IPO_DATA.map((row, index) => {
    const bgColor = index % 2 === 0 ? '#ffffff' : '#f9fafb';
    return `
      <tr style="background-color: ${bgColor};">
        <td style="padding: 10px 8px; border-bottom: 1px solid #e5e7eb; color: #374151; font-size: 12px; white-space: nowrap; vertical-align: top;">${row.Company}</td>
        <td style="padding: 10px 8px; border-bottom: 1px solid #e5e7eb; color: #374151; font-size: 12px; white-space: nowrap; vertical-align: top;">${row['Symbol proposed']}</td>
        <td style="padding: 10px 8px; border-bottom: 1px solid #e5e7eb; color: #374151; font-size: 12px; white-space: nowrap; vertical-align: top;">${row['Lead Managers']}</td>
        <td style="padding: 10px 8px; border-bottom: 1px solid #e5e7eb; color: #374151; font-size: 12px; white-space: nowrap; vertical-align: top;">${row['Shares (Millions)'].toFixed(1)}</td>
        <td style="padding: 10px 8px; border-bottom: 1px solid #e5e7eb; color: #374151; font-size: 12px; white-space: nowrap; vertical-align: top;">$${row['Price Low'].toFixed(2)}</td>
        <td style="padding: 10px 8px; border-bottom: 1px solid #e5e7eb; color: #374151; font-size: 12px; white-space: nowrap; vertical-align: top;">$${row['Price High'].toFixed(2)}</td>
        <td style="padding: 10px 8px; border-bottom: 1px solid #e5e7eb; color: #374151; font-size: 12px; white-space: nowrap; vertical-align: top;">${row['Est. $ Volume']}</td>
        <td style="padding: 10px 8px; border-bottom: 1px solid #e5e7eb; color: #374151; font-size: 12px; white-space: nowrap; vertical-align: top;">${row['Expected to Trade']}</td>
        <td style="padding: 10px 8px; border-bottom: 1px solid #e5e7eb; color: #374151; font-size: 12px; white-space: nowrap; vertical-align: top;">${row['SCOOP Rating']}</td>
        <td style="padding: 10px 8px; border-bottom: 1px solid #e5e7eb; color: #374151; font-size: 12px; white-space: nowrap; vertical-align: top;">${row['Rating Change']}</td>
      </tr>
    `;
  }).join('');
}

function generateHTML() {
  const totalIPOs = IPO_DATA.length;
  const totalVolume = IPO_DATA.reduce((sum, row) => {
    const volumeStr = row['Est. $ Volume'].replace(/[^0-9.]/g, '');
    return sum + parseFloat(volumeStr || '0');
  }, 0);
  const newsletterSummary = `This week's IPO calendar features ${totalIPOs} companies preparing to go public, with an estimated total volume of $${(totalVolume / 1000).toFixed(1)}B. The market shows diverse opportunities across various sectors, with companies ranging from small-cap offerings to major institutional deals.`;

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>IPO Hype Tracker Newsletter</title>
  <style>
    @media print {
      @page {
        margin: 1cm;
      }
      body {
        margin: 0;
        padding: 0;
      }
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background-color: #f6f9fc;
      margin: 0;
      padding: 20px;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
      background-color: #ffffff;
      padding: 20px 0 48px;
    }
    .header {
      padding: 32px 24px;
      text-align: center;
    }
    .header-title {
      color: #1f2937;
      font-size: 32px;
      font-weight: 700;
      margin: 0 0 8px;
    }
    .header-subtitle {
      color: #6b7280;
      font-size: 16px;
      margin: 0;
    }
    hr {
      border: none;
      border-top: 1px solid #e5e7eb;
      margin: 20px 0;
    }
    .section {
      padding: 24px;
    }
    .section-title {
      color: #1f2937;
      font-size: 24px;
      font-weight: 600;
      margin: 0 0 8px;
    }
    .section-description {
      color: #6b7280;
      font-size: 14px;
      margin: 0 0 24px;
    }
    .table-container {
      overflow-x: auto;
      margin-top: 16px;
      border: 1px solid #e5e7eb;
      border-radius: 8px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
      background-color: #ffffff;
    }
    th {
      padding: 12px 8px;
      text-align: left;
      font-weight: 600;
      font-size: 11px;
      text-transform: uppercase;
      border-bottom: 2px solid #374151;
      white-space: nowrap;
      color: #ffffff;
      background-color: #1f2937;
    }
    td {
      padding: 10px 8px;
      border-bottom: 1px solid #e5e7eb;
      color: #374151;
      font-size: 12px;
      white-space: nowrap;
      vertical-align: top;
    }
    tr:nth-child(even) {
      background-color: #f9fafb;
    }
    .footer {
      padding: 24px;
      text-align: center;
      background-color: #f9fafb;
    }
    .footer-text {
      color: #6b7280;
      font-size: 14px;
      margin: 0 0 8px;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1 class="header-title">IPO Hype Tracker</h1>
      <p class="header-subtitle">Weekly Market Update - ${formatDate()}</p>
    </div>

    <hr>

    <div class="section">
      <h2 class="section-title">📈 Market Overview</h2>
      <p class="section-description">${newsletterSummary}</p>
    </div>

    <hr>

    <div class="section">
      <h2 class="section-title">📋 IPO Calendar</h2>
      <p class="section-description">Complete listing of upcoming and recent IPOs with key details.</p>
      <div class="table-container">
        <table cellpadding="8" cellspacing="0">
          <thead>
            <tr>
              <th>Company</th>
              <th>Symbol</th>
              <th>Lead Managers</th>
              <th>Shares (M)</th>
              <th>Price Low</th>
              <th>Price High</th>
              <th>Est. $ Volume</th>
              <th>Expected to Trade</th>
              <th>SCOOP Rating</th>
              <th>Rating Change</th>
            </tr>
          </thead>
          <tbody>
            ${generateTableRows()}
          </tbody>
        </table>
      </div>
    </div>

    <hr>

    <div class="footer">
      <p class="footer-text">Stay ahead of the IPO market with IPO Hype Tracker.</p>
      <p class="footer-text">IPO Hype Tracker Newsletter | Your trusted source for IPO market insights</p>
    </div>
  </div>
</body>
</html>`;
}

function createNewsletterFile() {
  try {
    const html = generateHTML();
    const outputPath = path.join(process.cwd(), 'newsletter-preview.html');
    fs.writeFileSync(outputPath, html, 'utf8');
    
    console.log('✅ Newsletter HTML file created successfully!');
    console.log(`📄 File saved to: ${outputPath}`);
    console.log(`\n📋 To convert to PDF:`);
    console.log('   1. Open newsletter-preview.html in your browser');
    console.log('   2. Press Ctrl+P (or Cmd+P on Mac)');
    console.log('   3. Select "Save as PDF" as the destination');
    console.log('   4. Click Save');
    console.log(`\n   Or double-click the file to open it in your default browser.`);
    
    return outputPath;
  } catch (error) {
    console.error('❌ Error creating newsletter file:', error);
    throw error;
  }
}

// Run if called directly
if (require.main === module) {
  try {
    createNewsletterFile();
    console.log('\n✨ Done!');
    process.exit(0);
  } catch (error) {
    console.error('\n💥 Failed:', error.message);
    process.exit(1);
  }
}

module.exports = { createNewsletterFile, IPO_DATA };

