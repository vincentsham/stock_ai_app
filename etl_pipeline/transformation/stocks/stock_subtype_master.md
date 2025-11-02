# 📘 Stock Subtype Master Table

This document defines the **Layer-2 subtypes** that extend the core Archetypes (L1).  
Subtypes provide more granular distinctions for how a company behaves within its archetype — based on business model, growth stage, or strategic positioning.

---

## 🧩 Subtype Reference Table

| **Archetype (L1)** | **Subtype (L2)** | **Definition / Distinguishing Features** | **Primary Signals** | **Example Companies** |
|:--|:--|:--|:--|:--|
| **Pre-Profit** | **Pre-Revenue** | Product in R&D or prototype stage, little to no revenue yet. | Revenue_TTM < $5M; R&D/Revenue undefined or extreme; high cash burn. | Neuralink, QuantumScape, early biotech IPOs. |
|  | **R&D-Led** | Research-driven model focused on innovation and IP creation. | R&D/Revenue ≥ 50%; catalysts around trials or patents. | Moderna (early stage), CRISPR Therapeutics. |
|  | **Scale-Up** | Rapid revenue growth but still loss-making; expanding infrastructure. | Revenue_YoY ≥ 30%; margins negative; strong catalyst activity. | Rivian, Snowflake, Unity. |
|  | **Venture-Stage Platform** | Network-effect or marketplace early scaling; not yet monetized efficiently. | Rapid user growth; CAC/LTV ratio improving; high narrative tone. | Reddit (pre-IPO), Discord, early-stage SaaS. |
| **Emerging Growth** | **Breakeven Transition** | Nearing profitability with expanding margins and OCF turning positive. | EPS_TTM ≈ 0; Margin_Trend_4Q > 0; OCF > 0 for 2+ quarters. | Palantir, ZoomInfo, Pinterest. |
|  | **Operational Leverage** | Revenue growth outpacing cost growth; operating leverage emerging. | Revenue ↑; SG&A/Revenue ↓; EPS accelerating. | Shopify (2024), Datadog. |
|  | **Early Profit Expansion** | First stage of sustainable profit generation with reinvestment. | EPS > 0; FCF near 0; CapEx ↑; ROIC rising. | Roku, Toast, Coupang. |
| **Sustainable Growth** | **Sustained Compounder** | Consistent double-digit growth and high returns on capital. | Revenue_CAGR_3Y ≥ 15%; ROIC ≥ 15%; low EPS volatility. | Microsoft, ServiceNow, Adobe. |
|  | **Reinvestment-Heavy Growth** | Reinvesting aggressively for long-term TAM expansion. | Reinvestment_Rate ≥ 0.4; CapEx/R&D ↑; FCF low. | Amazon (AWS cycle), Tesla. |
|  | **Platform Expansion** | Extending core platform into adjacent verticals. | New segments contributing >20% incremental revenue. | Salesforce (Data Cloud), Nvidia (AI compute). |
| **Mature / Quality Compounder** | **High-Margin Compounder** | Margin leader with consistent FCF conversion and low volatility. | Gross_Margin ≥ 50%; FCF_Margin ≥ 20%; ROIC ≥ 15%. | Visa, Apple, L’Oréal. |
|  | **Steady Performer** | Predictable earnings and moderate capital return. | EPS_Volatility ≤ 10%; Dividend_Yield 1–3%. | PepsiCo, Nestlé. |
|  | **Capital Return Leader** | Prioritizing buybacks over growth investment. | Share count ↓ ≥ 2% YoY; FCF_Payout ≥ 0.7. | Home Depot, Oracle. |
| **Re-Growth / Re-Acceleration** | **Product Cycle Revival** | New product line or refresh drives revenue/EPS acceleration. | Revenue_Accel_4Q ≥ 2; positive guidance. | AMD (AI GPU cycle), Apple (Vision Pro). |
|  | **Strategic Pivot** | Business model transformation or tech adoption boosts growth. | New keywords: “AI,” “Cloud,” “Subscription.” | Microsoft (Copilot), Meta (AI ads). |
|  | **Efficiency-Driven Growth** | Margin and EPS expansion via cost optimization. | Margin_Trend_4Q ↑; EPS_Accel_4Q ≥ 2; OCF ↑. | Meta (2023), Intel (2025 pivot). |
| **Turnaround / Recovery** | **Restructuring Phase** | Cost cutting, divestitures, or leadership overhaul. | Opex ↓; “restructuring” catalysts; new CEO. | Disney, Boeing, Peloton. |
|  | **Operational Recovery** | Stabilizing operations and restoring profitability. | EPS_YoY ↑; OCF ↑; Margin_Trend > 0. | Intel (2024–2025), Ford (EV refocus). |
|  | **Sentiment Recovery** | Market perception improving ahead of fundamentals. | Analyst_PT_Upgrades ↑; news sentiment ↑. | PayPal, AT&T. |
| **Value / Reassessment** | **Deep Value** | Severely undervalued relative to fundamentals. | P/E < 10; EV/EBITDA < 6; strong balance sheet. | Citi, BP, Alibaba. |
|  | **Quality Value** | Strong profitability but low valuation multiples. | ROIC ≥ 15%; P/E < sector median. | Intel, Oracle. |
|  | **Income-Value Hybrid** | Combines dividend yield with undervaluation potential. | Dividend_Yield 3–5%; stable EPS. | Verizon, IBM. |
|  | **Re-Rating Candidate** | Market-driven multiple expansion ahead of EPS growth. | P/E expanding; analyst upgrades; mild EPS ↑. | Pfizer, Alibaba (2024). |
| **Income / Dividend** | **Dividend Aristocrat** | 10+ years of consecutive dividend increases. | Dividend_Streak ≥ 10 years; low volatility. | Johnson & Johnson, Coca-Cola. |
|  | **High-Yield Stable** | High dividend yield with strong FCF coverage. | Dividend_Yield ≥ 5%; FCF_Coverage ≥ 1.5×. | Altria, Realty Income. |
|  | **Buyback-Focused** | Prioritizes repurchases over dividends. | Share count ↓ ≥ 3% YoY; low payout ratio. | Apple, Oracle. |
| **Cyclical / Capital-Intensive** | **Commodity-Linked** | Performance driven by commodity prices. | Sector: Energy/Materials; EBITDA–price correlation > 0.8. | ExxonMobil, Rio Tinto. |
|  | **Industrial Cycle** | CapEx-driven business with inventory cycles. | CapEx/Revenue cyclical; WorkingCapital swings. | Caterpillar, 3M. |
|  | **Financial / Rate-Sensitive** | Dependent on interest rate or credit spreads. | Sector: Banks, REITs; NIM correlated with Fed Funds. | JPMorgan, Blackstone, Schwab. |
| **Event-Driven / Special Situation** | **M&A Target** | Potential acquisition or merger activity. | “acquisition,” “merger,” “offer” keywords. | Activision Blizzard, Splunk. |
|  | **Spin-Off / Split** | Unlocking value via divestiture or separation. | “spinoff,” “split,” “IPO” catalysts. | GE (GE Vernova/GE Aerospace), Kenvue. |
|  | **Regulatory / Legal Resolution** | Driven by policy change or litigation outcome. | “settlement,” “approval,” “ban.” | Meta (FTC), Illumina. |
| **Defensive / Low-Beta** | **Staple Defensive** | Essential consumer demand with low cyclicality. | Beta ≤ 0.7; Revenue_YoY < 5%. | P&G, PepsiCo, Costco. |
|  | **Utility Defensive** | Regulated, predictable cash flows. | Sector: Utilities; EPS growth 2–4%. | Duke Energy, NextEra. |
|  | **Healthcare Defensive** | Stable long-term demand across cycles. | Sector: Healthcare; low earnings volatility. | Abbott, Johnson & Johnson. |
| **Speculative / Story-Driven** | **Thematic Momentum** | Narrative-based sectors (AI, EVs, green energy, etc.). | News/topic ratio ≥ 0.4; catalysts frequent. | C3.ai, Plug Power, DraftKings. |
|  | **Early-Tech Explorer** | Commercializing unproven technology. | R&D/Revenue ≥ 40%; EPS < 0. | QuantumScape, Rigetti, IonQ. |
|  | **Hype-Cycle Peak** | Valuation extreme, sentiment overheated. | P/S > 30; negative FCF; news volume spike. | Nikola, Beyond Meat. |
| **Crisis / Distressed** | **Liquidity Crisis** | Insufficient cash runway or refinancing risk. | Cash/OCF < 1 year; short-term debt ↑. | WeWork, Bed Bath & Beyond. |
|  | **Operational Collapse** | Core operations deteriorating sharply. | Revenue ↓ > 20%; OCF/FCF deeply negative. | Lordstown Motors, Peloton (2022). |
|  | **Balance Sheet Distress** | Debt burden unsustainable; solvency risk. | Interest_Coverage < 1.0; Leverage > 5×. | Evergrande, Rite Aid. |

---

### 🧠 Design Notes

- Each archetype has **2–4 subtypes** capturing strategic or structural variation.  
- Subtypes refine **analysis weighting and peer benchmarking**.  
- Transitions can be tracked longitudinally, e.g.  
  ```
  R&D-Led → Scale-Up → Breakeven Transition → Sustainable Compounder
  ```  
- Suggested schema columns:
  ```sql
  subtype_code TEXT,
  subtype_name TEXT,
  subtype_confidence NUMERIC(4,3)
  ```
- Subtype inference combines **quantitative metrics** and **qualitative language signals** (e.g., “AI pivot,” “restructuring,” “spinoff,” etc.).

---
