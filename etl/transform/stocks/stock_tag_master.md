# 📘 Stock Tag Master Table with Examples

This document defines the **Layer-3 contextual tags (L3)** that complement the core Archetype (L1) and Subtype (L2) layers.  
Tags are multi-label descriptors that represent **situational, thematic, or risk contexts** derived from news, catalysts, transcripts, and financial signals.

---

## 🧩 Tag Reference Table with Examples

| **Category** | **Tag Name** | **Meaning / Trigger** | **Example Scenarios / Companies** |
|:--|:--|:--|:--|
| **Structural / Ownership** | `Founder_Led` | Founder still runs or chairs the company. | Meta (Mark Zuckerberg), Tesla (Elon Musk), Snowflake (Frank Slootman). |
|  | `Family_Controlled` | Controlled by founding family or descendants. | Walmart, Ford, L’Oréal. |
|  | `State_Owned` | Majority owned by government or SOE. | PetroChina, Gazprom. |
|  | `Private_Equity_Backed` | Previously owned or influenced by PE firm. | Hilton (Blackstone legacy), Dell (Silver Lake). |
|  | `Conglomerate_Structure` | Multi-segment business spanning industries. | Berkshire Hathaway, GE. |
|  | `Spin_Off_Pending` | Division expected to separate or IPO. | GE → GE Vernova/GE Aerospace, Kenvue (J&J). |
|  | `IPO_Recent` | Listed within 18 months. | ARM Holdings (2023), Reddit (2024). |
|  | `Dual_Class_Shares` | Unequal voting rights benefiting founders. | Alphabet, Meta, Rivian. |
| **Strategic / Corporate Action** | `Buyback_Program` | Announced or ongoing share repurchase plan. | Apple, Meta, Oracle. |
|  | `Dividend_Initiation` | Introduced or raised a dividend. | Alphabet (2024), Meta (2024). |
|  | `Restructuring_Initiative` | Cost-cutting, layoffs, or operational reorg. | Disney (2023), Intel (2024). |
|  | `Leadership_Change` | CEO/CFO or board turnover. | Boeing (CEO change 2024), PayPal (new CEO 2023). |
|  | `M&A_Activity` | Acquisition, merger, or major investment. | Broadcom–VMware, Microsoft–Activision. |
|  | `Divestiture` | Selling or spinning off a division. | IBM → Kyndryl, J&J → Kenvue. |
|  | `Share_Split` | Stock split or reverse split. | Nvidia 4:1 split (2021), Tesla (2022). |
|  | `Debt_Refinancing` | Issued new bonds or refinanced loans. | AT&T, American Airlines. |
| **Innovation / Technology** | `AI_Beneficiary` | Exposure to or use of AI in operations or products. | Nvidia (GPU), Microsoft (Copilot), Adobe (Firefly). |
|  | `Cloud_Transition` | Migrating legacy products to cloud. | SAP, Oracle. |
|  | `Digital_Transformation` | Adopting digital-first strategy. | JPMorgan (AI + automation). |
|  | `Automation_Adoption` | Investing in robotics or process automation. | Amazon warehouses, Foxconn factories. |
|  | `Green_Tech` | ESG or clean energy focus. | Tesla, Plug Power, Enphase. |
|  | `New_Product_Line` | Launching a new flagship product. | Apple Vision Pro, Rivian R3, Meta Ray-Ban smart glasses. |
|  | `Patent_Activity` | Filing or defending major IP claims. | Qualcomm, Moderna, ARM. |
|  | `R&D_Intensive` | Large portion of revenue allocated to R&D. | ASML, Snowflake, Moderna. |
| **Market / Positioning** | `Sector_Leader` | Market share leader in primary industry. | Nvidia (AI chips), Visa (payments). |
|  | `Market_Share_Gaining` | Taking share from peers. | AMD vs. Intel, Costco vs. Walmart. |
|  | `Pricing_Power` | Can raise prices without demand loss. | Apple, Procter & Gamble. |
|  | `New_Market_Entry` | Expanding into new product category. | Tesla (energy storage), Netflix (gaming). |
|  | `International_Expansion` | Entering or scaling in foreign markets. | Starbucks China expansion. |
|  | `Rebranding` | Corporate identity refresh or repositioning. | Facebook → Meta, Google → Alphabet. |
| **Financial / Performance** | `Guidance_Raised` | Upward revision to revenue or EPS outlook. | Microsoft (2024), AMD (AI cycle). |
|  | `Guidance_Reaffirmed` | Maintained prior quarter’s guidance. | Apple (FY2025). |
|  | `Guidance_Lowered` | Reduced or withdrawn outlook. | Tesla (2024 Q2). |
|  | `Margin_Expansion` | Sequential improvement in margins. | Meta (2023–2024 efficiency). |
|  | `Margin_Compression` | Shrinking margins due to cost or price pressure. | PepsiCo (input costs 2022). |
|  | `FCF_Positive` | Turned positive on free cash flow. | Palantir (2023), Lucid (target 2025). |
|  | `High_Leverage` | Debt/EBITDA > 3×. | AT&T, Carnival Corp. |
|  | `Strong_Balance_Sheet` | Net cash or low leverage. | Alphabet, Microsoft. |
|  | `Earnings_Beat` | EPS > consensus by >5%. | Nvidia (Q1 2024 blowout). |
|  | `Earnings_Miss` | EPS < consensus by >5%. | Disney (Q2 2023 miss). |
|  | `Revenue_Beat` | Revenue > consensus. | AMD (Q3 2024). |
|  | `Revenue_Miss` | Revenue below expectations. | Netflix (2022). |
|  | `FX_Headwind` | FX movements reducing earnings. | LVMH, Unilever. |
|  | `FX_Tailwind` | FX movements boosting results. | Toyota, Siemens. |
| **Macro / Thematic Exposure** | `Rate_Sensitive` | Impacted by rate moves (banks, REITs, utilities). | JPMorgan, Realty Income. |
|  | `Inflation_Beneficiary` | Benefits from higher prices. | ExxonMobil, Archer-Daniels-Midland. |
|  | `Inflation_Pressure` | Margins hurt by cost inflation. | PepsiCo, Delta Airlines. |
|  | `Geopolitical_Exposure` | Risk from conflicts or sanctions. | TSMC (Taiwan), BP (Russia exit). |
|  | `China_Exposure` | High China revenue share. | Apple, Starbucks, Nike. |
|  | `US_Focused` | Domestic-driven business. | Kroger, AT&T. |
|  | `Europe_Exposure` | Major EU exposure. | LVMH, Volkswagen. |
| **Catalyst / Event** | `Earnings_Event` | Quarterly earnings release imminent or recent. | Apple (Q4 earnings week). |
|  | `Product_Launch` | New product introduced to market. | Nvidia (Blackwell GPU), Tesla (Cybertruck). |
|  | `Regulatory_Approval` | License or FDA approval received. | Eli Lilly (Zepbound), Moderna (vaccine). |
|  | `Regulatory_Risk` | Antitrust or policy headwind. | Apple (EU App Store case). |
|  | `Litigation_Risk` | Facing lawsuits or settlements. | Johnson & Johnson (talc case). |
|  | `ESG_Issue` | Environmental or labor controversy. | BP (oil spills), Amazon (labor rights). |
|  | `Cybersecurity_Incident` | Data breach or hack. | MGM Resorts (2023 breach). |
|  | `Activist_Pressure` | Activist investor pushing for change. | Disney (Nelson Peltz), Salesforce (Elliott Mgmt). |
|  | `Short_Squeeze` | Rapid short-covering rally. | GameStop, AMC. |
| **Investor Sentiment / Market Dynamics** | `Analyst_Upgrade` | Analyst rating or PT upgrade. | Nvidia (2023–2024 cycle). |
|  | `Analyst_Downgrade` | Rating downgrade. | Tesla (2024 Q2). |
|  | `High_Short_Interest` | Short interest > 10% of float. | Beyond Meat, Upstart. |
|  | `Insider_Buying` | Executives purchasing shares. | Palantir (Alex Karp 2024). |
|  | `Insider_Selling` | Insider share sales. | Nvidia execs trimming (2024). |
|  | `ETF_Inclusion` | Added to or removed from major ETF. | ARM added to NASDAQ-100 (2024). |
| **Sustainability / ESG** | `ESG_Leader` | High sustainability ranking. | Microsoft, Ørsted, Unilever. |
|  | `ESG_Laggard` | Low ESG or controversy exposure. | ExxonMobil, Meta (privacy). |
|  | `Carbon_Neutral_Goal` | Public target for net-zero emissions. | Apple, Amazon, Shell (2050 goal). |
|  | `Renewable_Exposure` | Revenue from clean energy operations. | NextEra, Enphase, First Solar. |
| **Risk / Warning Signals** | `Earnings_Warning` | Pre-announced weaker earnings. | Boeing (2023 Q4). |
|  | `Revenue_Decline` | Sustained top-line contraction. | IBM (legacy years), Intel (2023). |
|  | `Cash_Burn_Risk` | High burn, limited cash runway. | Lucid, Rivian (early stage). |
|  | `Liquidity_Risk` | Tight liquidity or refinancing concern. | WeWork, Bed Bath & Beyond. |
|  | `Accounting_Flag` | Restatement, auditor issue, or delay. | Nikola, Luckin Coffee. |
|  | `Delisting_Risk` | Below listing thresholds or noncompliance. | Faraday Future, small-cap ADRs. |

---

## 🧠 Example in Context

### Example 1 — Re-Growth Company
```json
{
  "archetype": "Re-Growth / Re-Acceleration",
  "subtype": "Strategic Pivot",
  "tags": [
    "AI_Beneficiary",
    "Product_Launch",
    "Guidance_Raised",
    "Buyback_Program",
    "Analyst_Upgrade"
  ],
  "analysis_mode": "growth_heavy_v1",
  "confidence": 0.92
}
```

### Example 2 — Turnaround Value Stock
```json
{
  "archetype": "Turnaround / Recovery",
  "subtype": "Operational Recovery",
  "tags": [
    "Restructuring_Initiative",
    "Leadership_Change",
    "Guidance_Reaffirmed",
    "Activist_Pressure"
  ],
  "analysis_mode": "catalyst_driven_v1",
  "confidence": 0.86
}
```

---

### 💡 Implementation Notes

- Tags are **multi-label** and stored as a JSON array in the database:  
  ```sql
  tags JSONB DEFAULT '[]';
  ```
- Each tag can include a confidence score:  
  ```json
  [{"name": "AI_Beneficiary", "confidence": 0.91}, {"name": "Buyback_Program", "confidence": 0.83}]
  ```
- Sources:  
  - **Catalyst Agent** → events, corporate actions, regulation.  
  - **Transcript Agent** → sentiment, forward guidance, innovation.  
  - **News Agent** → thematic / macro exposure.  
  - **Metrics Agent** → quantitative trends (EPS, FCF, margins).

---
