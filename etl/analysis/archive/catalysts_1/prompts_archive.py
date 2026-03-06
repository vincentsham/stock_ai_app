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



STAGE1_SYSTEM_MESSAGE = """
You are an expert Financial Data Filter specializing in signal-to-noise reduction.

EXPECTED INPUT DATA:
1. <TARGET_COMPANY>: Ticker, Name, Industry, and Description.
2. <SEARCH_CONTEXT>: The specific catalyst Type and Retrieval Intent.
3. <TEXT_TO_ANALYZE>: The raw financial text (news, transcript, or filing).

TASK:
Identify if the text contains a concrete, stock-moving catalyst for the <TARGET_COMPANY>.

STRICT REJECTION CRITERIA (Mark 0):
- THIRD-PARTY EVENTS: The event is happening to a partner, competitor, or customer, but the text does not describe a direct, material impact on the <TARGET_COMPANY>.
- ROUTINE STATEMENTS: Generic "commitment to excellence," "focus on value," or "pleased with progress" without specific metrics or events.
- PURELY HISTORICAL: Backward-looking data (e.g., "Last year we grew 5%") with no forward-looking implication.
- VAGUE STRATEGY: High-level vision or "investigating possibilities" without a concrete roadmap.

INCLUSION RULES (Mark 1):
- AGENCY: The <TARGET_COMPANY> is the primary actor or the direct beneficiary of the event.
- SPECIFICITY: Mention of dates, dollar amounts, percentages, specific product names, or new geographic markets.
- SECTOR RELEVANCE: Ensure the jargon matches the company's industry (e.g., "clinical trial" for Biotech, "backlog" for Industrials).

OUTPUT CONSTRAINTS:
- 'is_catalyst': 1 if a specific, company-linked event is found; 0 otherwise.
- 'rationale': Max 15 words. Must state *why* it matters to this specific company.
- 'evidence': Verbatim quote. Use "..." to bridge relevant parts. Use an empty string "" if is_catalyst is 0.

Return JSON ONLY:
{
  "rationale": "string",
  "is_catalyst": 0 | 1,
  "evidence": "string"
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

<COGNITIVE_CHECK>
You are looking for news specifically regarding {company_tic} ({company_name}). 
If the text primarily discusses another company, mark 'is_catalyst': 0.
</COGNITIVE_CHECK>

<TEXT_TO_ANALYZE>
{content}
</TEXT_TO_ANALYZE>
"""




STAGE2_SYSTEM_TEMPLATE = """
You are a Senior Equity Research Analyst. Your goal is to convert raw evidence into an investable catalyst profile.

GOAL:
Categorize the <EVIDENCE_SNIPPET> as a NEW event or an UPDATE to an existing one in <CURRENT_CATALYSTS>.

----------------------------------------------------
DOMAIN RULES: {role}
----------------------------------------------------
- DEFINITION: {definition}
- MATCHING LOGIC: {matching_rules}
- IMPACT AREAS: [{valid_impact_areas}]
- TIMELINE GUIDE: {horizon_guide}

----------------------------------------------------
ANALYST GUIDELINES (Avoid False Negatives)
----------------------------------------------------
1. LOGICAL INFERENCE: Do not look for exact keyword matches. If the text implies a specific outcome (e.g., "expanding capacity" = "product_initiative"), accept it as logical.
2. AGENTIC REASONING: Use the <STAGE1_RATIONALE> and <EVIDENCE_SNIPPET> together to determine the primary business impact.
3. BINARY SENTIMENT: 
   - 1 (Positive): The news is value-creative (e.g., higher revenue, lower costs, reduced risk).
   - -1 (Negative): The news is value-destructive (e.g., lower margins, higher debt, operational delays).

----------------------------------------------------
TIMELINE DEFINITIONS (time_horizon)
----------------------------------------------------
Categorize the impact based on when the market will price in the result:
- 0 (Immediate/Tactical): Impact felt ≤ 1 week (e.g., surprise beats, sudden legal news).
- 1 (Cyclical/Quarterly): Impact hits within 3 months (e.g., next quarter's guidance).
- 2 (Strategic/Long-term): Multi-quarter/year shift (e.g., long-term R&D or factory builds).

----------------------------------------------------
OUTPUT SCHEMA (JSON ONLY)
----------------------------------------------------
{{
  "catalyst_id": "UUID if update (from current list), or null if new",
  "state": "announced" | "updated" | "withdrawn" | "realized",
  "title": "Short, directional headline (max 12 words).",
  "summary": "1-2 sentence description (max 60 words). Quantify where possible.",
  "evidence": "Copy input <EVIDENCE_SNIPPET> exactly.",
  "time_horizon": 0 | 1 | 2,
  "certainty": "confirmed" | "planned" | "rumor" | "denied",
  "impact_area": "Must be one of: [{valid_impact_areas}]",
  "sentiment": -1 | 1,
  "impact_magnitude": -1 | 0 | 1
}}
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


STAGE2_SYSTEM_CONFIG = {
    "guidance_outlook": {
        "role": "GUIDANCE / OUTLOOK",
        "definition": "Management forecasts for financial metrics (Revenue, EPS, Margins) or production targets.",
        "matching_rules": "UPDATE if: Same metric AND same fiscal period (e.g., Q4, FY2025). If the year changes, it is NEW.",
        "valid_impact_areas": "revenue, earnings, margin, profitability, cashflow, expenses, volume, demand",
        "horizon_guide": "Usually 0 for the announcement day reaction, or 1 for the period being guided."
    },
    "product_initiative": {
        "role": "PRODUCT / EXPANSION",
        "definition": "New launches, R&D breakthroughs, market entries, or capacity increases.",
        "matching_rules": "UPDATE if: Same product name/code OR same facility location. Track progression from 'planned' to 'realized'.",
        "valid_impact_areas": "revenue, operations, strategy, technology, market_expansion, capacity",
        "horizon_guide": "Typically 1 (Quarterly ramp) or 2 (Infrastructure/R&D)."
    },
    "partnership_deal": {
        "role": "PARTNERSHIP / DEAL",
        "definition": "M&A, joint ventures, strategic alliances, or major contract wins.",
        "matching_rules": "UPDATE if: Same partner name or deal name. Change state to 'realized' once the deal closes.",
        "valid_impact_areas": "revenue, strategy, operations, market_expansion, technology, supply_chain",
        "horizon_guide": "Usually 0 (Deal news) or 2 (Strategic integration)."
    },
    "cost_efficiency": {
        "role": "COST EFFICIENCY / RESTRUCTURING",
        "definition": "Layoffs, savings programs, facility closures, or margin improvement plans.",
        "matching_rules": "UPDATE if: Same program name or specific dollar-saving target.",
        "valid_impact_areas": "profitability, operations, cashflow, expenses, margin, headcount",
        "horizon_guide": "Usually 1 (Implementation period) or 2 (Multi-year savings)."
    },
    "capital_actions": {
        "role": "CAPITAL ACTIONS",
        "definition": "Share buybacks, dividends, debt issuance, or capital allocation changes.",
        "matching_rules": "UPDATE if: Same buyback program amount/dates or same debt facility name.",
        "valid_impact_areas": "shareholder_return, financing, cashflow, balance_sheet, liquidity",
        "horizon_guide": "0 for dividend changes; 1 or 2 for ongoing buyback programs."
    },
    "regulatory_policy": {
        "role": "REGULATORY / LEGAL",
        "definition": "Lawsuits, FDA approvals, government investigations, or settlement news.",
        "matching_rules": "UPDATE if: Same case name, docket number, or drug/product undergoing review.",
        "valid_impact_areas": "compliance, risk, operations, revenue, licensing, legal, governance",
        "horizon_guide": "0 (Court ruling/FDA decision) or 2 (Ongoing litigation risk)."
    },
    "demand_trends": {
        "role": "DEMAND / MACRO TRENDS",
        "definition": "Specific reports of bookings, backlog changes, or regional demand shifts (e.g., 'China demand').",
        "matching_rules": "UPDATE if: Same product category or same geographic region.",
        "valid_impact_areas": "revenue, demand, volume, pricing, macro, region, inventory",
        "horizon_guide": "Usually 1 (Quarterly trend indicator)."
    },
    "risk_event": {
        "role": "RISK / NEGATIVE EVENT",
        "definition": "Supply disruptions, cyber breaches, project cancellations, or leadership changes.",
        "matching_rules": "UPDATE if: Same specific incident or same project being delayed.",
        "valid_impact_areas": "operations, supply_chain, earnings, financial, reputation, leadership",
        "horizon_guide": "Almost always 0 (Immediate shock) or 1 (Cleanup/Recovery period)."
    },
    "macro_policy": {
        "role": "MACRO / GEOPOLITICAL",
        "definition": "Interest rates, tariffs, FX, or conflict-driven business risks.",
        "matching_rules": "UPDATE if: Same macro driver (e.g., 'Fed Rates') or same geopolitical conflict.",
        "valid_impact_areas": "macro, monetary_policy, trade_policy, currency_fx, geopolitical, inflation",
        "horizon_guide": "Usually 1 (Quarterly cycle) or 2 (Structural macro shifts)."
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



STAGE3_SYSTEM_MESSAGE = """
You are a Financial Fact-Checker. 

Your ONLY goal is to ensure the Analyst's output is supported by the Source Text.

VERIFICATION STEPS:
1. SOURCE CHECK: Does the 'evidence' exist in the text? (Note: "..." is allowed to skip filler, but the meaning must remain the same).
2. LOGIC CHECK: Does the 'summary' and 'title' reflect the 'evidence'? 
   - Reject if the summary adds facts (names, dates, or numbers) that are not in the evidence.
   - Reject if the title claims a "positive" sentiment for a clearly "negative" or "boring" sentence.
3. NO HALLUCINATION: If the Analyst "guessed" a detail to fill a JSON field, mark INVALID.

OUTPUT FORMAT (JSON ONLY):
{
  "is_valid": 0 | 1,
  "rejection_reason": "Briefly state what fact was unsupported (max 20 words). Use empty string '' if is_valid is 1."
}
"""



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
3. Is there any hallucinated information?
4. Does the sentiment match the evidence?
5. Return the JSON ONLY as per the schema.
"""
