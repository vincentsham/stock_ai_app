CATALYST_QUERIES = {
  "guidance_outlook": [
    "management updated revenue or EPS guidance",
    "guidance raised or lowered for next quarter or fiscal year",
    "guidance reaffirmed or withdrawn",
    "forward financial outlook discussed"
  ],

  "product_initiative": [
    "new product or service launch announced",
    "capacity expansion or production ramp",
    "entry into a new market or category"
  ],

  "partnership_deal": [
    "partnership or strategic alliance announced",
    "major customer or supplier contract win",
    "merger acquisition or investment deal disclosed"
  ],

  "cost_efficiency": [
    "restructuring plan with layoffs announced",
    "cost reduction initiative to improve margins",
    "operational or margin improvement program"
  ],

  "capital_actions": [
    "share repurchase or dividend change announced",
    "debt issuance refinancing or new credit facility",
    "equity offering or capital raise disclosed"
  ],

  "regulatory_policy": [
    "regulatory or government approval granted or filed",
    "investigation lawsuit settlement or fine announced",
    "antitrust or agency probe affecting the company"
  ],

  "demand_trends": [
    "company reported stronger or weaker demand",
    "orders bookings or backlog changed materially",
    "pricing or inventory conditions affecting sales"
  ],

  "risk_event": [
    "unexpected project delay cancellation or withdrawal",
    "profit warning or negative earnings impact",
    "production halt recall outage or supply shortage"
  ],

  "macro_policy": [
    "interest rate or monetary policy shift affecting company",
    "tariffs trade restrictions or sanctions impacting operations",
    "fiscal or government policy influencing demand or investment",
    "geopolitical conflict creating business or supply risk"
  ]
}


STAGE1_HUMAN_PROMPT = """
<TARGET_COMPANY>
{company_info}
</TARGET_COMPANY>

<SEARCH_CONTEXT>
Type: {catalyst_type}
Query: {retrieval_query}
</SEARCH_CONTEXT>

<TEXT_TO_ANALYZE>
{content}
</TEXT_TO_ANALYZE>
"""

STAGE1_SYSTEM_MESSAGE = """
You are a Financial Data Filter.

EXPECTED INPUT DATA:
1. <TARGET_COMPANY>: A JSON object containing:
   - "tic": Stock ticker symbol (e.g., AAPL).
   - "company_name": Full entity name.
   - "industry" & "sector": Classification context.
   - "company_description": Short description of operations.
2. <SEARCH_CONTEXT>:
   - "Type": The target catalyst category (e.g., "guidance_outlook").
   - "Query": The specific retrieval intent.
3. <TEXT_TO_ANALYZE>: The raw text chunk.

TASK:
Analyze <TEXT_TO_ANALYZE> to determine if it contains a stock catalyst matching the <SEARCH_CONTEXT> for the specific <TARGET_COMPANY>.

RULES:
1. **Relevance:** Ignore competitor news, general industry trends, or old data (>1 year).
2. **Identity Check:** Use 'tic' and 'company_name' to ensure the event belongs to this specific entity, not a peer.
3. **Sector Check:** Use 'industry'/'sector' to filter out irrelevant jargon (e.g., don't flag "oil prices" for a software firm unless explicitly linked).
4. **Smart Snipping:** Extract ONLY the core subject and action. Use "..." to remove filler words.

JSON OUTPUT FORMAT:
{
  "rationale": "Max 15 words on why this matches the Search Context for THIS company.",
  "is_catalyst": 0 | 1,
  "evidence": "Verbatim quote using '...' for compression. MAX 40 WORDS. Returns null if 0."
}
"""


STAGE1_HUMAN_PROMPT = """
<TARGET_COMPANY>
{company_info}
</TARGET_COMPANY>

<SEARCH_CONTEXT>
Type: {catalyst_type}
Query: {retrieval_query}
</SEARCH_CONTEXT>

<TEXT_TO_ANALYZE>
{content}
</TEXT_TO_ANALYZE>
"""



STAGE1_SYSTEM_MESSAGE = """
You are an AI classifier for financial text.

EXPECTED INPUT DATA:
1. <TARGET_COMPANY>: A JSON object containing:
   - "tic": Stock ticker symbol (e.g., AAPL).
   - "company_name": Full entity name.
   - "industry" & "sector": Classification context.
   - "company_description": Short description of operations.
2. <SEARCH_CONTEXT>:
   - "Type": The target catalyst category (e.g., "guidance_outlook").
   - "Query": The specific retrieval intent.
3. <TEXT_TO_ANALYZE>: The raw text chunk.


Use the query as context for what kind of event the system expects.
Your job is to decide if this chunk truly describes that kind of catalyst event **for this company**.

TASK:
1. Determine whether the chunk expresses a concrete, forward-looking, event-like statement
matching the intended catalyst type and relevant to the company’s operations.
2. Explain your reasoning in a brief rationale (max 15 words).
3. Extract a quote snippet from the chunk that best supports your decision.

IGNORE:
- generic strategy or vision statements
- historical results with no forward implication
- macro or competitor commentary unrelated to this company
- filler, greetings, or Q&A context

RULES:
- Consider both the chunk text and the retrieval query when judging relevance.
- Be slightly liberal: if the chunk clearly implies an actionable development, mark 1.
- If it only mentions routine context or vague sentiment, mark 0.
- Use company context only to assess whether the event affects this business or industry.

Return JSON ONLY, following this structure:
{
  "rationale": "Max 15 words on why this matches the Search Context for THIS company.",
  "is_catalyst": 0 | 1,
  "evidence": "Verbatim quote using "..." for compression. MAX 40 WORDS. Returns empty string "" if 0."
}
"""


STAGE2_HUMAN_PROMPT = """
<TARGET_COMPANY>
{company_info}
</TARGET_COMPANY>

<CONTEXT_METADATA>
Type: {catalyst_type}
Query: {retrieval_query}
Stage1_Rationale: {rationale}
</CONTEXT_METADATA>

<CURRENT_CATALYSTS>
{current_catalysts_json}
</CURRENT_CATALYSTS>

<EVIDENCE_SNIPPET>
{evidence}
</EVIDENCE_SNIPPET>
"""


STAGE2_SYSTEM_TEMPLATE = """
You are an expert Financial Analyst specializing in {role} catalysts.

Your Goal:
Analyze the provided <EVIDENCE_SNIPPET> (extracted from a larger text) to determine if it represents a **NEW** catalyst or an **UPDATE** to an existing one.

----------------------------------------------------
DOMAIN RULES: {role}
----------------------------------------------------
**Valid Definition:**
{definition}

**Matching Logic (New vs Update):**
{matching_rules}

**Allowed Impact Areas:**
[{valid_impact_areas}]

----------------------------------------------------
DECISION LOGIC
----------------------------------------------------
Step 1: Read the <EVIDENCE_SNIPPET> and <STAGE1_RATIONALE>.
Step 2: Compare against <CURRENT_CATALYSTS> to check for duplicates/updates.
Step 3: Apply the **Matching Logic** defined above.
   - If match found → It is an UPDATE.
   - If no match → It is NEW.
Step 4: Generate the JSON output. 
   - If it is UPDATE, adjust the state to "updated"; keep the same catalyst_id; update all the fields according to the new snippet.
   - If NEW, set `catalyst_id` to null.

----------------------------------------------------
OUTPUT SCHEMA (JSON ONLY)
----------------------------------------------------
Return a single JSON object:
{{
  "catalyst_id": "UUID string if update (copy from current list), or null if new",
  "state": "announced" | "updated" | "withdrawn" | "realized",
  "title": "Short, punchy headline (max 12 words). Directional.",
  "summary": "1-2 sentence description (max 60 words). Synthesize the snippet's meaning.",
  "evidence": "Copy the input <EVIDENCE_SNIPPET> exactly.",
  "time_horizon": 0 | 1 | 2 | null,   // 0=Short(≤1wk), 1=Mid(≤3mo), 2=Long(>3mo)
  "certainty": "confirmed" | "planned" | "rumor" | "denied" | null,
  "impact_area": "Must be one of: [{valid_impact_areas}]",
  "sentiment": -1 | 0 | 1,   // -1=Negative, 0=Neutral, 1=Positive
  "impact_magnitude": -1 | 0 | 1   // -1=Minor, 0=Moderate, 1=Major
}}
"""


STAGE2_SYSTEM_CONFIG = {
    "guidance_outlook": {
        "role": "GUIDANCE / OUTLOOK",
        "definition": "Valid when management issues forecasts for revenue, EPS, margins, cash flow, or production numbers for a specific future period.",
        "matching_rules": "Treat as UPDATE if: Same fiscal period (e.g., Q4, FY25), same metric (revenue, EPS), or mentions 'reaffirming'/'lowering'/'raising' prior guidance.",
        "valid_impact_areas": "revenue, earnings, margin, profitability, cashflow, expenses, volume, demand"
    },
    "product_initiative": {
        "role": "PRODUCT / EXPANSION",
        "definition": "Valid for new product launches, feature rollouts, entering new markets/geographies, or capacity expansion (factories, lines).",
        "matching_rules": "Treat as UPDATE if: Same product name, same facility location, or explicitly mentions progress/ramp-up of a previously announced initiative.",
        "valid_impact_areas": "revenue, operations, strategy, technology, market_expansion, capacity"
    },
    "partnership_deal": {
        "role": "PARTNERSHIP / DEAL",
        "definition": "Valid for M&A, joint ventures, strategic alliances, major contract wins, or licensing agreements.",
        "matching_rules": "Treat as UPDATE if: Same partner/counterparty name, same deal structure, or mentions closing/completion of a previously announced deal.",
        "valid_impact_areas": "revenue, strategy, operations, market_expansion, technology, supply_chain, financial"
    },
    "cost_efficiency": {
        "role": "COST EFFICIENCY / RESTRUCTURING",
        "definition": "Valid for layoffs, hiring freezes, cost-saving programs, facility closures, or margin improvement initiatives.",
        "matching_rules": "Treat as UPDATE if: Same program name (e.g. 'Project X'), same savings target amount, or progress update on previously announced restructuring.",
        "valid_impact_areas": "profitability, operations, cashflow, expenses, margin, headcount, productivity"
    },
    "capital_actions": {
        "role": "CAPITAL ACTIONS",
        "definition": "Valid for share buybacks, dividends, debt issuance/repayment, credit facilities, or capital allocation changes.",
        "matching_rules": "Treat as UPDATE if: Refers to the same buyback program ($ amount/dates), dividend declaration, or financing facility.",
        "valid_impact_areas": "shareholder_return, financing, cashflow, balance_sheet, leverage, liquidity"
    },
    "regulatory_policy": {
        "role": "REGULATORY / LEGAL",
        "definition": "Valid for lawsuits, investigations, FDA/regulatory approvals, settlements, or compliance changes.",
        "matching_rules": "Treat as UPDATE if: Same lawsuit case, same regulatory application (e.g., specific drug), or resolution of a known investigation.",
        "valid_impact_areas": "compliance, risk, operations, revenue, licensing, legal, governance, policy"
    },
    "demand_trends": {
        "role": "DEMAND / MACRO TRENDS",
        "definition": "Valid for reports of strong/weak bookings, backlog changes, inventory destocking, or specific regional/sector demand shifts.",
        "matching_rules": "Treat as UPDATE if: Relates to the same specific product line, region (e.g., 'China demand'), or customer segment (e.g., 'Enterprise').",
        "valid_impact_areas": "revenue, demand, volume, pricing, macro, region, channel, inventory"
    },
    "risk_event": {
        "role": "RISK / NEGATIVE EVENT",
        "definition": "Valid for supply chain disruptions, delays, cancellations, accidents, cyber breaches, or executive departures.",
        "matching_rules": "Treat as UPDATE if: Same specific incident, same delayed project, or continuation of a previously reported outage/shortage.",
        "valid_impact_areas": "operations, supply_chain, earnings, demand, financial, regulatory, cybersecurity, reputation, leadership, environmental"
    },
    "macro_policy": {
        "role": "MACRO / POLICY / GEOPOLITICAL",
        "definition": "Valid for interest rates, inflation, FX, trade tariffs, fiscal stimulus, or war/geopolitical conflict affecting the company.",
        "matching_rules": "Treat as UPDATE if: Same macro factor (e.g. 'interest rates'), same specific policy (e.g. 'IRA Act'), or same geopolitical conflict.",
        "valid_impact_areas": "macro, monetary_policy, fiscal_policy, trade_policy, currency_fx, commodity_prices, geopolitical, inflation_cost, demand, risk"
    }
}


STAGE2_SYSTEM_MESSAGE = {
  "guidance_outlook": STAGE2_SYSTEM_TEMPLATE.format(**STAGE2_SYSTEM_CONFIG["guidance_outlook"]),
  "product_initiative": STAGE2_SYSTEM_TEMPLATE.format(**STAGE2_SYSTEM_CONFIG["product_initiative"]),
  "partnership_deal": STAGE2_SYSTEM_TEMPLATE.format(**STAGE2_SYSTEM_CONFIG["partnership_deal"]),
  "cost_efficiency": STAGE2_SYSTEM_TEMPLATE.format(**STAGE2_SYSTEM_CONFIG["cost_efficiency"]),
  "capital_actions": STAGE2_SYSTEM_TEMPLATE.format(**STAGE2_SYSTEM_CONFIG["capital_actions"]),
  "regulatory_policy": STAGE2_SYSTEM_TEMPLATE.format(**STAGE2_SYSTEM_CONFIG["regulatory_policy"]),
  "demand_trends": STAGE2_SYSTEM_TEMPLATE.format(**STAGE2_SYSTEM_CONFIG["demand_trends"]),
  "risk_event": STAGE2_SYSTEM_TEMPLATE.format(**STAGE2_SYSTEM_CONFIG["risk_event"]),
  "macro_policy": STAGE2_SYSTEM_TEMPLATE.format(**STAGE2_SYSTEM_CONFIG["macro_policy"])
}



STAGE3_HUMAN_PROMPT = """
<SOURCE_TEXT_CHUNK>
{chunk_text}
</SOURCE_TEXT_CHUNK>

<CANDIDATE_CATALYST>
{stage2_json_output}
</CANDIDATE_CATALYST>

Instructions:
1. Read the 'evidence' field.
2. Does this evidence support the 'title' and 'summary'?
"""


STAGE3_SYSTEM_MESSAGE = """
You are a Financial Fact-Checker.

Your task is to verify the **Internal Consistency** and **Source Integrity** of a "Candidate Catalyst".

INPUTS:
1. **Source Context:** The original text chunk.
2. **Candidate Catalyst:** A JSON object containing `evidence`, `title` and `summary`.

VERIFICATION STEPS (Pass only if ALL are true):

1. **Quote Integrity (Hallucination Check):**
   - The `evidence` text must exist within the **Source Context**.
   - *Tolerance:* Allow for minor differences in whitespace, newlines, or punctuation.
   - *Failure:* If the evidence is fabricated or combines two sentences that are not adjacent in the source, MARK INVALID.

2. **Logical Consistency (Support Check):**
   - The `evidence` is relevant to the `title` and `summary`.
   - *Failure:* If the Summary claims a fact (e.g., "Revenue up") that contradicts the Evidence (e.g., "Revenue down"), MARK INVALID.

OUTPUT FORMAT (JSON ONLY):
{
  "is_valid": 0, // or 1
  "rejection_reason": "Concise explanation of failure (max 20 words) or null if valid"
}
"""
