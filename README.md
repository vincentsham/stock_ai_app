# AI Stock Intelligence System (Work in Progress)
**Author:** Vincent Sham  
**Project:** Multi-Agent AI Framework for Comprehensive Stock Analysis  

---

## Table of Contents
- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Stock Type Classification](#stock-type-classification)
  - [Purpose](#1-purpose)
  - [Three-Layer Taxonomy](#2-three-layer-taxonomy)
  - [Benefits of Subtypes](#3-benefits-of-subtypes)
  - [Example Hierarchy](#4-example-hierarchy)
  - [Dynamic Labeling](#5-dynamic-labeling)
- [Multi-Pillar Scoring Framework](#multi-pillar-scoring-framework)
  - [Purpose](#1-purpose-1)
  - [Pillar → Sub-Pillar Hierarchy](#2-pillar--sub-pillar-hierarchy)
  - [Trend-Aware Scoring](#3-trend-aware-scoring)
  - [Peer Comparison Framework](#4-peer-comparison-framework)
  - [Interpretability](#5-interpretability)
- [AI-Generated Ratings & Price Targets](#ai-generated-ratings--price-targets)
- [Objective](#objective)
- [Future Development Roadmap](#future-development-roadmap)

---

## Project Overview  

This project is a **multi-agent AI system for comprehensive stock analysis**.  
The framework integrates structured financial data and unstructured textual insights to create an explainable, adaptive pipeline for evaluating publicly traded companies.  

The system combines data from earnings reports, financial statements, analyst estimates, news, and market trends.  
Its objective is to build an **AI-driven “analyst”** that can classify, score, and rate stocks in a consistent, data-grounded, and interpretable manner — providing quantitative scores, qualitative rationales, and AI-generated price targets.  

---

## System Architecture  

The system is composed of specialized **AI agents**, each focused on a distinct data domain:  

| Agent | Primary Function |
|--------|------------------|
| **News Agent** | Classifies financial headlines by event type and extracts sentiment and market perception. |
| **Earnings Transcript Agent** | Analyzes tone, confidence, and risk language in management commentary. |
| **Financial Report Agent** | Extracts quantitative fundamentals from income statements, balance sheets, and cash flow statements. |
| **Analyst Forecast Agent** | Aggregates analyst consensus, price-target revisions, and forecast trends. |
| **Market Trend Agent** | Evaluates recent price action, volatility, liquidity, and technical momentum indicators. |

Each agent outputs structured JSON data stored in the database (`core` and `mart` schemas).  
A **Feature Aggregation Layer** normalizes and merges these outputs into a unified feature space, which feeds into the **Stock Type Classifier** and **Multi-Pillar Scoring Engine**.  

---

## Stock Type Classification  

### 1. Purpose  
Stock type classification determines *how a company should be evaluated* by grouping it with peers that share similar structural and behavioral characteristics.  
Different types emphasize different aspects of performance (e.g., growth vs. stability), allowing **type-specific weights** and **contextual scoring**.

---

### 2. Three-Layer Taxonomy

| Layer | Definition | Examples |
|--------|-------------|-----------|
| **L1 — Archetype** | Broad classification based on financial structure and business model. | Growth, Value, Defensive, Cyclical, High-Margin, Mega-Cap, Pre-Profit, Turnaround |
| **L2 — Subtype** | Specialized subclass capturing unique strategic or financial behavior within the archetype. | Growth → Hypergrowth / Sustainable / Emerging<br>Pre-Profit → R&D-Led / Pre-Revenue / Scale-Up<br>Value → Deep / Quality / Income |
| **L3 — Tags** | Thematic or situational multi-labels for catalysts and qualitative context. | AI_Beneficiary, Founder_Led, Buyback_Program, Green_Transition, Regulatory_Risk, etc. |

---

### 3. Benefits of Subtypes

| Advantage | Explanation |
|------------|-------------|
| **Interpretability** | Clarifies a company’s identity within its archetype (e.g., *Sustainable Growth* vs. *Hypergrowth*). |
| **Scoring Precision** | Enables subtype-specific weightings (e.g., *Growth* → Growth/Momentum, *Value* → Valuation/Profitability). |
| **Peer Comparison** | Ensures fair benchmarking within relevant cohorts. |
| **Lifecycle Tracking** | Captures company evolution over time (*Pre-Profit → Growth → High-Margin*). |
| **Explainability** | Improves transparency for dashboards and textual rationales. |

---

### 4. Example Hierarchy

**Growth Archetype**
- **Hypergrowth:** Revenue CAGR ≥ 25% or Rule-of-40 ≥ 40  
- **Sustainable Growth:** Revenue CAGR 15–25% with positive FCF  
- **Emerging Growth:** Revenue CAGR 10–15% with high reinvestment  

**Pre-Profit Archetype**
- **Pre-Revenue:** Revenue TTM < $5M  
- **R&D-Led:** R&D / Revenue ≥ 50%  
- **Scale-Up:** Revenue growth ≥ 30% but still unprofitable  

**Value Archetype**
- **Deep Value:** P/E or P/S ≤ sector 20th percentile  
- **Quality Value:** Cheap but high ROIC and margin stability  
- **Income Value:** Dividend yield ≥ sector 75th percentile  

**Defensive Archetype**
- **Dividend Aristocrat:** 10+ years of dividend increases  
- **Utility Defensive:** Low-beta, stable cash-flow sectors  
- **Staple Defensive:** Predictable consumer demand patterns  

---

### 5. Dynamic Labeling  
- Supports **multi-labeling** (e.g., Apple = {Mega-Cap, High-Margin, Growth})  
- **Priority rules** determine primary label when overlaps occur  
- Label history allows tracking of **lifecycle transitions** across time  

---

## Multi-Pillar Scoring Framework  

### 1. Purpose  
After classification, each stock is evaluated across **six high-level investment pillars**, further decomposed into **sub-pillars**.  
This hierarchical design ensures interpretability, fine-grained weighting, and modular agent contributions.

---

### 2. Pillar → Sub-Pillar Hierarchy

| Pillar | Sub-Pillars | Focus |
|---------|--------------|--------|
| **Growth** | Revenue Growth, Earnings Growth, Reinvestment & Expansion, Market Share Gain | Measures business expansion pace and reinvestment efficiency. |
| **Profitability** | Margins, Return Metrics, Operational Efficiency | Captures ability to convert revenue into cash and returns. |
| **Quality & Risk** | Balance Sheet Strength, Earnings Stability, Financial Risk, Operational Risk | Assesses resilience and downside protection. |
| **Valuation** | Absolute Valuation, Relative Valuation, Sentiment Valuation | Compares pricing versus intrinsic and peer benchmarks. |
| **Momentum** | Price Momentum, Volume Flow, Sentiment Momentum, Catalyst Reaction | Tracks technical and behavioral market signals. |
| **Execution** | Earnings Surprise, Guidance Revisions, Transcript Tone, Operational Actions | Measures management delivery and forward execution. |

---

### 3. Trend-Aware Scoring  
The scoring engine incorporates **temporal trend analysis** to capture changes in company performance over time.  
Rather than relying solely on static snapshots, it evaluates whether each pillar is **improving, stable, or deteriorating**, integrating directionality into the scoring process.  
This trend component strengthens interpretability by identifying consistent growth trajectories or early signs of weakening fundamentals.

---

### 4. Peer Comparison Framework  
The scoring system applies **peer-based normalization** to ensure fair and context-specific evaluations.  
Each company’s pillar and sub-pillar results are compared against a relevant peer group — defined by **sector**, **market-cap range**, and **stock type or subtype**.  
This approach enables more meaningful benchmarking, allowing the system to measure performance relative to similar companies rather than the entire market.

---

### 5. Interpretability  
Each company’s final evaluation can be visualized as a hierarchical breakdown:  

> **Total Score → Pillars → Sub-Pillars → Features**  

This enables the system to generate **transparent textual rationales**, such as:  

> “Tesla scores high in *Growth* (89) driven by *Revenue Growth + EPS Expansion*,  
> but low in *Valuation* (42) due to elevated EV/EBITDA multiples.”  

---

## AI-Generated Ratings & Price Targets  

The top layer of the system produces **AI-generated investment ratings and price targets (PTs)** by synthesizing all quantitative and qualitative signals.  

- **Ratings:** Generated on a numerical or categorical scale (*Buy / Hold / Sell*)  
- **Price Targets:** Estimated using a blend of valuation modeling, peer comparison, and growth projections  
- **Rationale:** Each rating/PT includes an interpretable explanation detailing contributing pillars, sub-pillars, and risk factors  

This capability transforms the framework from an analytics engine into a fully autonomous, explainable **AI equity-research analyst**.

---

## Objective  

The project’s objective is to develop an **adaptive, multi-agent AI analyst** that can:  
1. Collect and normalize diverse financial signals.  
2. Classify companies into dynamic, explainable stock types.  
3. Evaluate them through a multi-pillar, sub-pillar, and trend-aware scoring hierarchy.  
4. Benchmark results using peer comparisons for contextual fairness.  
5. Produce transparent investment ratings and AI-derived price targets with rationale.  

By combining data engineering, financial modeling, and natural-language understanding, this system delivers a **coherent, interpretable, and context-aware stock intelligence layer** for both quantitative research and portfolio decision support.

---

## Future Development Roadmap  

| Focus Area | Description |
|-------------|--------------|
| **Narrative & Sentiment Expansion** | Extend beyond tone analysis to capture *narrative evolution* and *discourse alignment*. The system will measure how company messaging shifts across time, how analyst narratives align or diverge from management tone, and how social sentiment compares with institutional views. |
| **Catalyst & Event Awareness** | Incorporate detection of key market-moving events such as earnings surprises, M&A activity, product launches, and regulatory actions. This layer will enhance short-term interpretability and connect pillar scoring to event-driven insights. |

---
