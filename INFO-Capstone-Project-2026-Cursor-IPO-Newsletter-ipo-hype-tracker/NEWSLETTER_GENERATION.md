# Newsletter Generation with IPO Table

This document explains how to generate a newsletter with custom IPO table data.

## Overview

The newsletter generation system has been enhanced to support a comprehensive IPO calendar table at the bottom of the newsletter. This table displays detailed information about upcoming and recent IPOs.

## API Endpoint

### POST `/api/newsletter/generate`

Generates a newsletter HTML with the provided IPO table data.

#### Request Body

```json
{
  "ipoTableData": [
    {
      "Company": "Company Name",
      "Symbol proposed": "SYMBOL",
      "Lead Managers": "Manager Name",
      "Shares (Millions)": 10.0,
      "Price Low": 10.00,
      "Price High": 12.00,
      "Est. $ Volume": "$ 100.0 mil",
      "Expected to Trade": "11/13/2025 Priced",
      "SCOOP Rating": "S/O",
      "Rating Change": "S/O"
    }
  ]
}
```

#### Response

```json
{
  "success": true,
  "html": "<html>...</html>",
  "message": "Newsletter generated successfully",
  "ipoCount": 17
}
```

## Usage Examples

### Using cURL

```bash
curl -X POST http://localhost:3000/api/newsletter/generate \
  -H "Content-Type: application/json" \
  -d @ipo-data.json
```

### Using Node.js Script

A pre-configured script is available at `scripts/generate-newsletter-with-data.js`:

```bash
node scripts/generate-newsletter-with-data.js
```

This script:
- Uses the IPO data provided in the file
- Calls the API endpoint
- Saves the generated HTML to `newsletter-output.html`

### Using JavaScript/TypeScript

```typescript
const response = await fetch('http://localhost:3000/api/newsletter/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    ipoTableData: [
      {
        Company: "Example Corp",
        "Symbol proposed": "EXMP",
        "Lead Managers": "Example Bank",
        "Shares (Millions)": 5.0,
        "Price Low": 10.00,
        "Price High": 12.00,
        "Est. $ Volume": "$ 55.0 mil",
        "Expected to Trade": "11/20/2025",
        "SCOOP Rating": "S/O",
        "Rating Change": "S/O"
      }
    ]
  }),
});

const result = await response.json();
console.log(result.html); // Newsletter HTML
```

## Newsletter Structure

The generated newsletter includes:

1. **Header** - Newsletter title and date
2. **Market Overview** - Summary of IPO market conditions
3. **Top 5 IPO Leaderboard** - Featured IPOs with hype scores
4. **Market Interest Distribution** - Bar chart visualization
5. **7-Day Trend Analysis** - Trend chart visualization
6. **IPO Calendar Table** - Complete listing with:
   - Company name
   - Symbol
   - Lead Managers
   - Shares (Millions)
   - Price Low/High
   - Estimated Volume
   - Expected Trading Date
   - SCOOP Rating
   - Rating Change
7. **Footer** - Unsubscribe and website links

## Table Format

The IPO table supports the following field mappings:

| Input Field | Mapped To |
|------------|-----------|
| `Company` or `company` | Company name |
| `Symbol proposed` or `symbol` | Stock symbol |
| `Lead Managers` or `leadManagers` | Lead underwriters |
| `Shares (Millions)` or `sharesMillions` | Number of shares (millions) |
| `Price Low` or `priceLow` | Minimum price |
| `Price High` or `priceHigh` | Maximum price |
| `Est. $ Volume` or `estVolume` | Estimated dollar volume |
| `Expected to Trade` or `expectedToTrade` | Trading date |
| `SCOOP Rating` or `scoopRating` | Rating |
| `Rating Change` or `ratingChange` | Rating change |

## Notes

- The table is responsive and will scroll horizontally on smaller screens
- All numeric values are automatically formatted
- The table uses alternating row colors for better readability
- The newsletter HTML is optimized for email clients

