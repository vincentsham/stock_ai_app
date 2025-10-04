# 📑 Stock News Classification Guide

This guide defines the categories used to classify stock-related news into a small, consistent set. It also provides a decision tree and examples for clarity.

---

## Categories

### 1. Fundamental
**Definition:**  
News that reports **hard business facts or events** that directly affect a company’s financials, operations, or long-term valuation. Includes official filings, earnings, guidance, corporate actions, regulatory/legal updates, leadership changes, and operational events. Also includes *alternative data* if it provides measurable evidence of business activity.  

**Examples:**  
- “Tesla reports record Q3 deliveries of 435,000 vehicles, beating analyst expectations.”  
- “Nvidia announces acquisition of startup X for $1.2 billion.”  
- “Apple CFO resigns amid SEC investigation.”  
- “Pfizer receives FDA approval for new cancer drug.”  
- “Amazon to lay off 10,000 employees in cost-cutting move.”  
- “Satellite data shows Nike factory output down 15% year-over-year.” *(alternative data)*  

---

### 2. Market Perception  
**Definition:**  
News that conveys **opinions, interpretations, or evaluations** about a company or its stock without introducing new fundamental facts. Often reflects how investors, analysts, or media *perceive* the company. May influence short-term price moves but does not change intrinsic value directly.  

**Examples:**  
- “Goldman Sachs downgrades Tesla to Neutral, lowers price target from $320 to $250.”  
- “CNBC panel debates whether Nvidia’s valuation is in bubble territory.”  
- “Investor letter from Hedge Fund X calls Apple ‘overhyped’ and trims holdings.”  
- “Social media buzz spikes around Tesla’s Cybertruck after viral video.”  
- “Bloomberg op-ed: ‘Tesla’s dominance in EVs may not last another decade.’”  

---

### 3. Technical  
**Definition:**  
News or commentary focused on **market structure, price patterns, or trading activity**, not on the company’s business itself. Includes technical analysis, unusual options flow, or commentary about stock movement unrelated to fundamentals.  

**Examples:**  
- “Tesla stock breaks above its 200-day moving average.”  
- “Unusual options activity: Nvidia call volume surges 3x daily average.”  
- “Apple shares down 5% on high trading volume, triggering circuit breaker.”  
- “ARK ETF trims Tesla holdings after RSI signals overbought conditions.”  

---

### 4. Noise  
**Definition:**  
News that is **low-value, irrelevant, repetitive, or purely speculative**, adding no meaningful insight for investors. Typically generic commentary, duplicate wire stories, lifestyle PR, or clickbait headlines. Should be archived but not surfaced as important.  

**Examples:**  
- “Tesla opens a new store in Dubai Mall.” *(irrelevant PR)*  
- “Should you buy Nvidia stock today? 3 reasons yes, 3 reasons no.” *(SEO clickbait)*  
- “Apple shares close at $175 on Tuesday.” *(pure price recap with no context)*  
- “Tesla stock is trending on Twitter.” *(social mention without analysis)*  
- “Report: Amazon might consider acquiring Netflix, according to unverified sources.” *(unconfirmed rumor)*  

---

## 🪢 Decision Tree for Classification

1. **Does the news report a verifiable fact/event about the company’s business (earnings, operations, regulation, leadership, M&A, filings, alt data)?**  
   - ✅ Yes → **Fundamental**  
   - ❌ No → go to Step 2  

2. **Does the news primarily express an opinion, evaluation, or perception (analyst calls, hedge fund letters, media narratives, PR controversies, social buzz) without new business facts?**  
   - ✅ Yes → **Market Perception**  
   - ❌ No → go to Step 3  

3. **Does the news focus on market structure, price action, flows, or trading signals (charts, volume, options, ETFs)?**  
   - ✅ Yes → **Technical**  
   - ❌ No → go to Step 4  

4. **Is the news low-value, irrelevant, duplicate, or clickbait (no new insights, generic PR, price recaps, unverified rumors)?**  
   - ✅ Yes → **Noise**  
   - ❌ If none apply, default to **Noise**  

---

## 📝 Example LLM Prompt

**Instruction:** Classify the following news headline/article into one of four categories: **Fundamental, Market Perception, Technical, or Noise.**  

**Decision Tree:**  
1. If the news contains **hard business facts/events** (earnings, M&A, regulation, filings, operations, alternative data), → **Fundamental**.  
2. Else if the news is **opinion, interpretation, or analyst/media narrative** without new facts, → **Market Perception**.  
3. Else if the news is **about price/volume/flows or technical analysis**, → **Technical**.  
4. Else → **Noise** (irrelevant, duplicate, clickbait, unconfirmed rumors).  

**Return JSON in this format:**  
```json
{
  "category": "...",
  "rationale": "short explanation of why this category applies"
}