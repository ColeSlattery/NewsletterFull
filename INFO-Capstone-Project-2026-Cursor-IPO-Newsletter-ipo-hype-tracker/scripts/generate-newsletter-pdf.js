/**
 * Script to generate a newsletter PDF with IPO table data
 * Usage: node scripts/generate-newsletter-pdf.js
 * 
 * Requires: npm install puppeteer
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

async function generateNewsletterPDF() {
  try {
    // Check if puppeteer is available
    let puppeteer;
    try {
      puppeteer = require('puppeteer');
    } catch (e) {
      console.error('❌ Puppeteer is not installed. Installing...');
      console.log('Please run: npm install puppeteer');
      console.log('Or: npm install puppeteer --save-dev');
      process.exit(1);
    }

    const apiUrl = process.env.NEXT_PUBLIC_BASE_URL 
      ? `${process.env.NEXT_PUBLIC_BASE_URL}/api/newsletter/generate`
      : 'http://localhost:3000/api/newsletter/generate';

    console.log('📄 Generating newsletter HTML...');
    console.log(`Sending request to: ${apiUrl}`);
    console.log(`Number of IPOs: ${IPO_DATA.length}`);

    // First, get the HTML from the API
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ipoTableData: IPO_DATA,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
    }

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.error || 'Unknown error');
    }

    console.log('✅ Newsletter HTML generated!');
    console.log(`📊 IPO Count: ${result.ipoCount}`);
    console.log(`📧 HTML length: ${result.html.length} characters`);

    // Save HTML for reference
    const htmlPath = path.join(process.cwd(), 'newsletter-output.html');
    fs.writeFileSync(htmlPath, result.html);
    console.log(`💾 HTML saved to: ${htmlPath}`);

    // Convert HTML to PDF using Puppeteer
    console.log('🖨️  Converting HTML to PDF...');
    const browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    // Set content with proper encoding
    await page.setContent(result.html, {
      waitUntil: 'networkidle0',
    });

    // Generate PDF
    const pdfPath = path.join(process.cwd(), 'newsletter-output.pdf');
    await page.pdf({
      path: pdfPath,
      format: 'A4',
      printBackground: true,
      margin: {
        top: '20px',
        right: '20px',
        bottom: '20px',
        left: '20px',
      },
    });

    await browser.close();

    console.log('✅ PDF generated successfully!');
    console.log(`📄 PDF saved to: ${pdfPath}`);
    console.log(`\nYou can now open: ${pdfPath}`);

    return { htmlPath, pdfPath };

  } catch (error) {
    console.error('❌ Error generating newsletter PDF:', error);
    throw error;
  }
}

// Run if called directly
if (require.main === module) {
  generateNewsletterPDF()
    .then(() => {
      console.log('\n✨ Done!');
      process.exit(0);
    })
    .catch((error) => {
      console.error('\n💥 Failed:', error.message);
      process.exit(1);
    });
}

module.exports = { generateNewsletterPDF, IPO_DATA };

