# Tech Stack  
**Project:** AI Stock Intelligence System  
**Author:** Vincent Sham  

---

## Overview  
The AI Stock Intelligence System integrates multi-agent AI, financial data processing, and a web-based interface for stock evaluation and scoring.  
The project combines backend intelligence (Python, FastAPI) with future web visualization (Node.js, React/Next.js).

---

## Core Stack  

| Layer | Technologies | Purpose |
|--------|---------------|----------|
| **Programming Languages** | Python, JavaScript (Node.js) | Data processing, backend API, and web integration. |
| **AI & NLP Frameworks** | LangGraph, LangChain, HuggingFace, OpenAI API | Multi-agent orchestration, text classification, and sentiment analysis. |
| **Model Families** | DeepSeek, Mistral, GPT, Llama (Groq) | Used for financial text reasoning and scoring. |
| **Backend Frameworks** | FastAPI (Python), Node.js / Express | RESTful APIs and backend service layer. |
| **Database** | PostgreSQL + pgvector | Stores structured data, embeddings, and analysis results. |
| **Data Tools** | Pandas, NumPy, SQLAlchemy | Data ingestion, normalization, and feature engineering. |
| **Frontend (Planned)** | React / Next.js | Interactive web dashboard for visualization and insights. |
| **Visualization** | Plotly, Chart.js, or Recharts | Displays score breakdowns, comparisons, and AI-generated metrics. |
| **Version Control & Environment** | Git, GitHub, Python venv, `.env` | Code versioning, dependency, and configuration management. |

---

## Data Sources  

| Source | Description |
|---------|--------------|
| **Yahoo Finance** | Stock prices, financial ratios, and market data. |
| **CoinCodex** | Cryptocurrency price and market trend data. |
| **FMP API (Financial Modeling Prep)** | Company fundamentals, earnings reports, and analyst data. |
| **Twelvedata API** | Real-time and historical stock/crypto price feeds. |
| **News API** | General financial and market news aggregation. |
| **Benzinga** | Premium financial headlines and sentiment data. |
| **Nasdaq** | Market data, filings, and official corporate actions. |

---

## Planned Integrations  
- **Web Dashboard:** Next.js + FastAPI interface for analysis and visualization.  
- **API Gateway:** Unified REST API for multi-agent results (scores, PTs, classifications).  
- **Containerization:** Docker setup for reproducible deployment.  
- **Authentication Layer:** Secure access for user or research accounts.