# 📊 Stock News Pipeline Strategy

This document describes the end-to-end strategy for processing, classifying, scoring, and presenting stock-related news for the AI Agent project. It complements the `news_categories.md` taxonomy guide.

---

## 1. Pipeline Overview

1. **Ingest & Normalize**
   - Load raw news into database (`tic, published_at, source, url, headline, body, raw_json`).
   - Normalize timestamps, resolve aliases → ticker/CIK.

2. **Classify Category**
   - Use 4 top-level categories from `news_categories.md`.
   - Assign `event_type` (e.g., `earnings_guidance`, `mna`, `analyst_action`, `price`, `clickbait`).

3. **Score Importance**
   - Compute **ImpactScore (0–100)** based on event type, materiality, source credibility, relevance, novelty, catalyst proximity.
   - Thresholds:  
     - ≥ 80 → Important (alerts, highlights)  
     - 60–79 → Dashboard (context)  
     - < 60 → Archive (still searchable)  

4. **Classify Sentiment**
   - For each article: `polarity (positive/neutral/negative)`, `intensity (low/medium/high)`, and optional aspect-level sentiment.

5. **Dedup & Canonicalize**
   - Cluster near-duplicate stories (SimHash/TF-IDF).  
   - Keep one **canonical** (earliest, most credible), mark others with `cluster_id`.

6. **Timeline Assembly**
   - Return only canonical items.  
   - Timeline ordered by `published_at DESC`, grouped by day.

7. **Summarization / Highlights**
   - Select **top 3–5 important events** for a highlight feed.  
   - Create a **weekly 4-bullet digest** (short, factual, consistent format).  
   - Optionally add an **overall read** (net sentiment).

---

## 2. Highlight Presentation Strategy

- **Event Cards (Highlights)**  
  - Show only important items (ImpactScore ≥ 80).  
  - Card format: `Title + Key number + Sentiment tag`.  
  - Example:  
    - **Record Q3 Deliveries**: 435k vehicles (+9% YoY) ✅ Positive  
    - **Cybertruck Delay**: Launch pushed 2 months 🔽 Negative  

- **Color-coded Sentiment Tags**  
  - Green / 🔼 = Positive  
  - Red / 🔽 = Negative  
  - Grey / ➖ = Neutral  

- **Timeline View**  
  - Chronological vertical layout for clarity.  
  - Example:  
    - **Oct 3** – Tesla reports record deliveries (+9% YoY).  
    - **Oct 4** – Goldman downgrades Tesla, PT cut to $250.  
    - **Oct 6** – Cybertruck launch delayed 2 months.  

- **4-Point Digest (Weekly Summary)**  
  - Always 4 bullets, max 25 words each.  
  - Prioritize: Earnings/Guidance → M&A/Capital → Regulatory/Legal → Operations/Customer → Analyst Actions/PR.  
  - Example:  
    - Tesla delivers 435k vehicles, record quarter.  
    - Guidance raised 5% EPS outlook.  
    - Goldman Sachs downgrades Tesla, PT $250.  
    - Cybertruck launch delayed 2 months.  

---

## 3. Example Prompt for 4-Point Summary

**Instruction:**  
“Summarize the most important news into exactly 4 concise bullets (<25 words). Prioritize earnings, M&A/capital, regulation, operations, then analyst actions. Include numbers if possible. Avoid noise and technicals.”  

**Output Example:**  
- Tesla delivers 435k vehicles, record quarter (+9% YoY).  
- Guidance raised 5% EPS outlook.  
- Goldman Sachs downgrades Tesla, PT $250.  
- Cybertruck launch delayed 2 months.  

---

## 4. Missing Pieces to Consider (Future Enhancements)

Even with a strong pipeline, there are a few critical areas to add later for robustness:

1. **Source credibility tiers**  
   - Weight news based on trust level (filings > Tier-1 outlets > blogs).  

2. **Event lifecycle tracking**  
   - Handle rumor → unconfirmed → confirmed → denied transitions.  

3. **Market reaction validation**  
   - Add fields for `abnormal_return`, `volume_zscore`, `IV_jump` after news release.  

4. **Multi-ticker & aspect tagging**  
   - Support stories affecting multiple companies and specific aspects (demand, leadership, regulation).  

5. **Longer-term rollups**  
   - Monthly/quarterly narrative summaries: “Key themes for Tesla this quarter were demand growth, analyst downgrades, product delays.”  

6. **Smarter noise filtering & deduplication**  
   - Expand clustering rules to auto-collapse duplicate wires or SEO spam.  

7. **Cluster-level storage**  
   - Store at the **event level**, not just article level, for cleaner aggregation.  

8. **Evaluation loop**  
   - Track precision of “important” events vs. stock reactions, category coverage, and summary clarity.  

---

# ✅ Key Takeaways

- Keep only **4 categories** for clarity.  
- Use **ImpactScore** to highlight only important events.  
- Present information as **highlights and digests**, not long text.  
- Add **future enhancements** (credibility tiers, event lifecycle, market validation, rollups) to improve accuracy and trustworthiness.  