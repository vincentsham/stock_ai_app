# 📈 Stock AI Frontend Architecture

## 🌟 Project Overview

The Stock AI Web Application is a high-performance, data-dense financial dashboard built with **Next.js 16 (React 19)**. It visualizes complex financial data—including AI-generated insights, analyst ratings, earnings transcripts, and catalysts—through a modular, server-rendered architecture.

---

## 🛠️ Technology Stack

| Category | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Framework** | **Next.js** | v16 | App Router, Server Components, Server Actions. |
| **UI Library** | **React** | v19 | Component-based UI logic. |
| **Styling** | **Tailwind CSS** | v4 | Utility-first styling engine. |
| **Icons** | **Lucide React** | Latest | Consistent icon set. |
| **Visualization** | **Recharts** | v3.5 | Composable charting library for metrics/earnings. |
| **Widget** | **TradingView** | External | Uses embed for interactive price charts. |
| **Database** | **node-postgres** | v8 | Direct SQL access to the analytical database. |
| **External APIs** | **yahoo-finance2** | v3 | Real-time price data fetching. |

---

## 🏗️ Application Architecture

### routing Structure (`app/`)
The application utilizes Next.js App Router for intuitive navigation and SEO optimization.

*   `app/(root)/page.tsx` (**Dashboard**): Landing page displaying popular stocks and market overviews. fetches top stocks using `searchTopStocks`.
*   `app/(root)/stocks/[ticker]/page.tsx` (**Stock Analysis**): Dynamic route for individual stock reports. Aggregates data from multiple pillars (Profile, Earnings, Analysts, Metrics).
*   `app/(root)/compare/page.tsx` (**Comparison**): Tool for side-by-side analysis of multiple stocks using radar charts and metric tables.
*   `app/api/`: API endpoints for client-side data fetching where necessary.

### Data Fetching Strategy
The app employs a **hybrid data fetching strategy** to maximize performance and data freshness:

1.  **Server Components (Direct DB)**: Core analytical data (Profiles, Scores, Earnings History) is fetched directly from the PostgreSQL database inside Server Components.
    *   *Path:* `lib/db/*.ts` (e.g., `stockQueries.ts`, `metricsQueries.ts`).
2.  **Server Actions**: Operations requiring external API interactions or form submissions.
    *   *Path:* `lib/actions/*.ts` (e.g., `yfinance.actions.ts` for live pricing).

---

## 🧩 Component Breakdown

The UI is built using independent, self-contained components organized by domain.

### 1. Core Stock Identity
*   `StockMain`: The orchestration component for the single stock view.
*   `StockProfileCard`: Displays company metadata (Sector, Industry), description, and live pricing.
*   `StockLivePrice`: Real-time price updates.
*   `StockRadarChart`: Visualizes the 6-pillar score (Valuation, Growth, Profitability, etc.) for a single stock.

### 2. Analytical Modules
*   **Metrics Pillar**:
    *   `MetricsSection`: Grid of key financial ratios.
    *   `MetricCard` / `MetricItem`: Individual metric display with tooltips.
    *   `StockScores`: Aggregate score visualization.
*   **Earnings Pillar**:
    *   `EarningsSection`: Container for earnings analysis.
    *   `EarningsGraph` / `EarningsGrowthGraph`: Visualization of revenue/EPS trends.
    *   `EarningsCallCard`: Summary and sentiment analysis of earnings transcripts.
*   **Analyst Pillar**:
    *   `AnalystsSection`: Consolidation of Wall St. opinions.
    *   `AnalystGradeCard`: Upgrades/Downgrades list.
    *   `AnalystPTGraph`: Price target vs. Actual price visualization.
*   **Catalyst Pillar**:
    *   `CatalystsSection`: Timeline of key events.
    *   `CatalystCard`: Individual event details.

### 3. Comparison & Discovery
*   `CompareMain`: Orchestrates the multi-stock comparison view.
*   `MultiStockRadarChart`: Overlays scores of different stocks for gap analysis.
*   `SearchBar`: Global command-center style search input.

---

## 📦 Data Models (`types/`)

The application enforces strict typing across the full stack to ensure data integrity.

*   **Stock**: Basic profile info (`tic`, `market_cap`, `sector`).
*   **Metrics**: Financial ratios (`pe_ttm`, `revenue_growth`) and computed scores.
*   **Earnings**: Historical and estimated EPS/Revenue data.
*   **Analyst**: Ratings, price targets, and consensus data.
*   **Catalyst**: Structured event data with sentiment and impact scores.

---

## 🚀 Deployment & CI/CD

*   **Build**: `npm run build` generates optimized static and serverless assets.
*   **Lint**: `eslint` configuration ensures code quality.
*   **Environment**: Managed via `.env` files loaded through `lib/loadEnv.ts`.
