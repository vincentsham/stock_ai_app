from functools import partial

CATALYST_QUERIES = {
  "guidance_outlook": [
    "management raised revenue or EPS guidance",              # Bull (Explicit raise)
    "guidance reaffirmed or outlook beat estimates",          # Bull (Reaffirm/Beat)
    "guidance lowered withdrawn or missed estimates",         # Bear (Explicit cut)
    "negative outlook or disappointing forecast"              # Bear (Soft sentiment)
  ],

  "product_initiative": [
    "new product service launch or expansion",                # Bull (Commercial)
    "production ramp up or capacity increase",                # Bull (Industrial)
    "product delay cancellation or withdrawal",               # Bear (Strategic)
    "production halt recall or quality failure"               # Bear (Operational)
  ],

  "partnership_deal": [
    "partnership strategic alliance or contract win",         # Bull (Growth)
    "merger acquisition or investment deal announced",        # Bull (M&A)
    "contract termination or customer loss",                  # Bear (Revenue at risk)
    "deal termination dispute or regulatory block"            # Bear (Deal failure)
  ],

  "cost_efficiency": [
    "cost reduction restructuring or margin improvement",     # Bull (Efficiency actions)
    "asset sale divestiture or spinning off business",        # Bull (Strategic pruning - NEW)
    "rising operating expenses or margin contraction",        # Bear (Inefficiency)
    "impairment charges or significant writedowns"            # Bear (Asset failure)
  ],

  "capital_actions": [
    "share repurchase buyback or dividend increase",          # Bull (Returning cash)
    "debt refinancing or credit rating upgrade",              # Bull (Health)
    "dividend cut suspension or reduction",                   # Bear (Cash crunch)
    "equity offering dilution or capital raise"               # Bear (Dilution)
  ],

  "regulatory_policy": [
    "regulatory government approval or clearance",            # Bull
    "lawsuit settlement or favorable ruling",                 # Bull
    "investigation lawsuit subpoena or probe",                # Bear
    "short seller report or accounting irregularity"          # Bear
  ],

  "demand_trends": [
    "strong demand bookings or backlog growth",               # Bull (Volume)
    "pricing power or market share gains",                    # Bull (Price)
    "weak demand cancellations or inventory buildup",         # Bear (Volume)
    "pricing pressure discounting or share loss"              # Bear (Price)
  ],

  "risk_event": [
    "insider buying or director share purchase",              # Bull (Confidence signal - NEW)
    "unexpected executive departure or resignation",          # Bear (Leadership)
    "operational disruption cyber breach or outage",          # Bear (Ops)
    "supply chain shortage or logistics delay"                # Bear (External)
  ],

  "macro_policy": [
    "favorable policy or government incentive announced",     # Bull
    "interest rate or monetary policy impact",                # Neutral
    "tariffs trade restrictions or sanctions",                # Bear
    "geopolitical conflict or currency headwinds"             # Bear
  ]
}




CATALYST_CONFIG = {
    "guidance_outlook": {
        "role": "GUIDANCE / OUTLOOK",
        "definition": "Management forecasts for Revenue, EPS, Margins, or Production.",
        "matching_rules": "UPDATE if: Same metric & period. NEW if: Period changes, guidance withdrawn, or estimates missed.",
        "valid_impact_areas": "revenue, earnings, margin, profitability, cashflow, expenses, volume, demand",
        "horizon_guide": "0 (Immediate Reaction) or 1 (Future Expectation)."
    },
    
    "product_initiative": {
        "role": "PRODUCT / OPERATIONS",
        "definition": "Launches, Capacity Expansion (Bull) OR Delays, Recalls, Shutdowns (Bear).",
        "matching_rules": "UPDATE if: Same product/facility. NEW if: Distinct product line or new site. IGNORE if: Routine maintenance.",
        "valid_impact_areas": "revenue, operations, strategy, technology, market_expansion, capacity",
        "horizon_guide": "1 (Ramp/Delay period) or 2 (Long-term R&D)."
    },
    
    "partnership_deal": {
        "role": "PARTNERSHIP / M&A",
        "definition": "New Deals, Contract Wins, M&A (Bull) OR Terminations, Churn, Deal Failures (Bear).",
        "matching_rules": "UPDATE if: Same partner. NEW if: Different partner. IGNORE if: Generic 'ongoing collaboration' updates.",
        "valid_impact_areas": "revenue, strategy, operations, market_expansion, technology, supply_chain",
        "horizon_guide": "0 (Announcement) or 2 (Integration/Loss)."
    },
    
    "cost_efficiency": {
        "role": "COST / RESTRUCTURING",
        "definition": "Savings Plans, Layoffs (Bull) OR Asset Impairments, Writedowns, Expense Spikes (Bear).",
        "matching_rules": "UPDATE if: Same program. NEW if: Distinct layoff round or specific writedown. IGNORE if: Generic 'cost discipline'.",
        "valid_impact_areas": "profitability, operations, cashflow, expenses, margin, headcount",
        "horizon_guide": "1 (Execution period)."
    },
    
    "capital_actions": {
        "role": "CAPITAL / DILUTION",
        "definition": "Buybacks, Dividends (Bull) OR Equity Offerings, Dilution, Debt Defaults (Bear).",
        "matching_rules": "UPDATE if: Same program. NEW if: New ATM/Secondary offering or Dividend change. IGNORE if: Routine dividend declaration.",
        "valid_impact_areas": "shareholder_return, financing, dilution, balance_sheet, liquidity",
        "horizon_guide": "0 (Immediate Repricing)."
    },
    
    "regulatory_policy": {
        "role": "LEGAL / REGULATORY",
        "definition": "Approvals, Settlements (Bull) OR Lawsuits, Probes, Short Reports (Bear).",
        "matching_rules": "UPDATE if: Same case/drug. NEW if: New subpoena, short report, or distinct lawsuit.",
        "valid_impact_areas": "compliance, risk, operations, revenue, licensing, legal, governance",
        "horizon_guide": "0 (Ruling/Report) or 2 (Litigation drag)."
    },
    
    "demand_trends": {
        "role": "DEMAND / INVENTORY",
        "definition": "Bookings Growth (Bull) OR Inventory Bloat, Cancellations, Pricing Pressure (Bear).",
        "matching_rules": "UPDATE if: Same region/segment. NEW if: Trend shifts to new region. IGNORE if: Seasonal fluctuation.",
        "valid_impact_areas": "revenue, demand, volume, pricing, macro, region, inventory",
        "horizon_guide": "1 (Quarterly Trend)."
    },
    
    "risk_event": {
        "role": "RISK / LEADERSHIP",
        "definition": "Insider Buys (Bull) OR Exec Resignations, Cyber Breaches, Supply Shocks (Bear).",
        "matching_rules": "UPDATE if: Same incident. NEW if: Different executive leaves or unrelated breach.",
        "valid_impact_areas": "operations, supply_chain, earnings, financial, reputation, leadership, cybersecurity",
        "horizon_guide": "0 (Immediate Shock)."
    },
    
    "macro_policy": {
        "role": "MACRO / GEOPOLITICAL",
        "definition": "Rates, FX, Tariffs, Trade Wars, or Conflicts impacting operations.",
        "matching_rules": "UPDATE if: Same policy/conflict. NEW if: New tariff or rate regime.",
        "valid_impact_areas": "macro, monetary_policy, trade_policy, currency_fx, geopolitical, inflation_cost",
        "horizon_guide": "1 (Cycle Impact) or 2 (Structural Shift)."
    }
}



STAGE1_SYSTEM_MESSAGE = """
TASK: Identify concrete, stock-moving catalysts for <TARGET_COMPANY> in the text.

REJECT (Mark 0):
- IRRELEVANT: Events affecting partners/competitors with NO explicit link to <TARGET_COMPANY>.
- FLUFF: Generic "commitment to value," "pleased with progress," or vague "investigating options" without capital commitment.
- HISTORICAL: Backward-looking data (e.g., "Last year's growth") with no forward guidance.

ACCEPT (Mark 1):
- IMPACT: Event must materially affect <TARGET_COMPANY> as the ACTOR (e.g., launches product), VICTIM (e.g., lawsuit, downgrade), or LINKED COLLATERAL (e.g., "tariffs hurt margins").
- SPECIFICITY: Contains dates, dollars, percentages, or specific product/regulatory outcomes.

OUTPUT (JSON ONLY):
{
  "rationale": "Max 15 words. Explain impact role (Actor/Victim).",
  "is_catalyst": 0 | 1,
  "evidence": "Verbatim quote... bridging parts allowed."
}
"""


STAGE1_HUMAN_PROMPT = """
<TARGET>
{company_info}
</TARGET>

<CONTEXT>
Query: {retrieval_query} ({catalyst_type})
</CONTEXT>

<INSTRUCTION>
Analyze text for material news regarding {company_tic}.
Include actions BY the company OR events happening TO the company (lawsuits, shortages, competitor threats).
If text focuses on another firm without linking to {company_tic}, return 0.
</INSTRUCTION>

<TEXT>"
{content}
</TEXT>
"""

STAGE2A_SYSTEM_TEMPLATE = """
You are a Database Gatekeeper. GOAL: Filter noise. Trigger updates only for MATERIAL CHANGES.

CONTEXT: {catalyst_type}
- ROLE: {role}
- DEFINITION: {definition}
- MATCHING RULES: {matching_rules}

PROTOCOL (MATERIALITY FILTER):
- REJECT "Empty Noise": Repetition, vague optimism ("excited"), or reconfirmations without new info.
- ACCEPT "Hard Data": Changes in Date, Amount, Status, or Stage.
- ACCEPT "Soft Context": Changes in Risk Profile, Confidence Level, or New Conditional Constraints ("if/but").

DECISION PATHS (Evaluate in Order):

1. NEW (action: "create"):
   - Event is COMPLETELY DISTINCT from any in <CURRENT_CATALYSTS>.
   - Output: catalyst_id="", catalyst_type="{catalyst_type}", impact_area=""

2. UPDATE (action: "update"):
   - Matches existing catalyst AND contains a MATERIAL CHANGE.
   - Hard Data: Date/Value changed.
   - Soft Context: New risk factor, new dependency, or explicit sentiment shift.
   - Catalyst Type Logic: Output "{catalyst_type}" if it fits better than old type; else "keep".
   - Impact Area Logic: Output "keep" normally. Only output "" if the update fundamentally changes the event's nature (requiring re-classification).
   - Output: catalyst_id="Existing ID", catalyst_type="'keep' or '{catalyst_type}'", impact_area="'keep' or ''"

3. KEEP (action: "keep"):
   - Matches existing catalyst but lacks Material Change (Pure Repetition or Fluff).
   - CRITICAL: You MUST return the ID of the matched catalyst so we know it was checked.
   - Output: catalyst_id="Existing ID", catalyst_type="keep", impact_area="keep"

CRITICAL CONSTRAINTS:
1. NEVER return an empty "catalyst_id" if action is "update" or "keep".
2. If you decided to "keep", it implies you found a match. RETURN THAT ID.

OUTPUT (JSON):
{{
  "catalyst_id": "If action is 'update' or 'keep', this MUST be the Exact ID from input. If 'create', use ''.",
  "action": "create" | "update" | "keep",
  "reason": "Max 10 words. Focus on the Delta.",
  "catalyst_type": "'keep' or '{catalyst_type}'",
  "impact_area": "'keep' or ''"
}}
"""


STAGE2A_HUMAN_PROMPT = """
<TARGET>
{company_info}
</TARGET>

<CURRENT_CATALYSTS>
{current_catalysts_json}
</CURRENT_CATALYSTS>

<EVIDENCE>
{evidence}
</EVIDENCE>
"""


STAGE2A_SYSTEM_MESSAGE = {
  "guidance_outlook": STAGE2A_SYSTEM_TEMPLATE.format(catalyst_type="guidance_outlook", **CATALYST_CONFIG["guidance_outlook"]),
  "product_initiative": STAGE2A_SYSTEM_TEMPLATE.format(catalyst_type="product_initiative", **CATALYST_CONFIG["product_initiative"]),
  "partnership_deal": STAGE2A_SYSTEM_TEMPLATE.format(catalyst_type="partnership_deal", **CATALYST_CONFIG["partnership_deal"]),
  "cost_efficiency": STAGE2A_SYSTEM_TEMPLATE.format(catalyst_type="cost_efficiency", **CATALYST_CONFIG["cost_efficiency"]),
  "capital_actions": STAGE2A_SYSTEM_TEMPLATE.format(catalyst_type="capital_actions", **CATALYST_CONFIG["capital_actions"]),
  "regulatory_policy": STAGE2A_SYSTEM_TEMPLATE.format(catalyst_type="regulatory_policy", **CATALYST_CONFIG["regulatory_policy"]),
  "demand_trends": STAGE2A_SYSTEM_TEMPLATE.format(catalyst_type="demand_trends", **CATALYST_CONFIG["demand_trends"]),
  "risk_event": STAGE2A_SYSTEM_TEMPLATE.format(catalyst_type="risk_event", **CATALYST_CONFIG["risk_event"]),
  "macro_policy": STAGE2A_SYSTEM_TEMPLATE.format(catalyst_type="macro_policy", **CATALYST_CONFIG["macro_policy"])
}


STAGE2B_SYSTEM_TEMPLATE = """
You are a Senior Equity Research Analyst.
GOAL: Convert a raw signal into a structured, investable catalyst record.

INPUT CONTEXT:
The "Gatekeeper" (Stage 2a) has declared this evidence MATERIAL.
- Action: (create | update)

DOMAIN: {role}
- DEFINITION: {definition}
- IMPACT AREAS: [{valid_impact_areas}]
- HORIZON: {horizon_guide}

ANALYST RULES:

1. SENTIMENT VECTOR (-1 or 1):
   *SUGGESTIONS FOR SCORING:*
   - NEGATIVE (-1):
      * **Deterioration:** Lower targets, missed dates, margin compression, inventory bloat.
      * **Headwinds:** Supply shocks, tariffs, FX pressure, regulatory probes, pricing wars.
      * **Financial Stress:** Dilution, cash burn, withdrawn guidance, covenant breaches.
      * **Erosion/Gov:** Exec exit, insider selling, contract loss, churn, market share loss.
   - POSITIVE (1):
      * **Growth:** Raised targets, beat & raise, margin expansion, new market entry.
      * **Execution:** Ahead of schedule, deal signed, patent granted, regulatory clearance.
      * **Tailwinds:** Competitor exit, favorable FX/rates, subsidies, tariff exemptions.
      * **Capital:** Buybacks, insider buying, debt repayment, lawsuit settlement.


2. MAGNITUDE SCORING (1, 0, -1):
   - 1 (High/Thesis Changing): M&A >$500M, CEO Change, Guidance Delta >10%, FDA Approval.
   - 0 (Medium/Material): Standard beat/miss, New Product, Contract Win, Moderate Delay.
   - -1 (Low/Minor): Routine updates, small insider sales, clarifying details.

3. CONTENT GENERATION:
   - Title: Directional Headline (e.g., "Guidance Cut to $100M", "FDA Approval Granted").
   - Summary: Start with the DELTA. What changed? (e.g., "Revenue guidance narrowed to $100M-$105M due to FX headwinds, down from $110M.").

OUTPUT SCHEMA (JSON):
{{
  "catalyst_id": "Extract 'id' from <CURRENT_CATALYST> if present. If empty/create, return ''.",
  "state": "announced" | "updated" | "withdrawn" | "realized",
  "title": "Max 10 words",
  "summary": "Max 50 words. Focus on the Delta.",
  "evidence": "Copy input evidence exactly.",
  "time_horizon": 0 (Immediate) | 1 (Short-term) | 2 (Long-term),
  "certainty": "confirmed" | "planned" | "rumor" | "denied",
  "impact_area": "Must be one of: [{valid_impact_areas}]",
  "sentiment": -1 (Negative) | 1 (Positive),
  "impact_magnitude": 1 (High) | 0 (Medium) | -1 (Low)
}}
"""

STAGE2B_HUMAN_PROMPT = """
<TARGET_COMPANY>
{company_info}
</TARGET_COMPANY>

<GATEKEEPER_DECISION>
{action}
</GATEKEEPER_DECISION>

<CURRENT_CATALYST>
{target_catalyst_json}
</CURRENT_CATALYST>

<EVIDENCE_SNIPPET>
{evidence}
</EVIDENCE_SNIPPET>
"""

STAGE2B_SYSTEM_MESSAGE = {
  "guidance_outlook": STAGE2B_SYSTEM_TEMPLATE.format(**CATALYST_CONFIG["guidance_outlook"]),
  "product_initiative": STAGE2B_SYSTEM_TEMPLATE.format(**CATALYST_CONFIG["product_initiative"]),
  "partnership_deal": STAGE2B_SYSTEM_TEMPLATE.format(**CATALYST_CONFIG["partnership_deal"]),
  "cost_efficiency": STAGE2B_SYSTEM_TEMPLATE.format(**CATALYST_CONFIG["cost_efficiency"]),
  "capital_actions": STAGE2B_SYSTEM_TEMPLATE.format(**CATALYST_CONFIG["capital_actions"]),
  "regulatory_policy": STAGE2B_SYSTEM_TEMPLATE.format(**CATALYST_CONFIG["regulatory_policy"]),
  "demand_trends": STAGE2B_SYSTEM_TEMPLATE.format(**CATALYST_CONFIG["demand_trends"]),
  "risk_event": STAGE2B_SYSTEM_TEMPLATE.format(**CATALYST_CONFIG["risk_event"]),
  "macro_policy": STAGE2B_SYSTEM_TEMPLATE.format(**CATALYST_CONFIG["macro_policy"])
}



STAGE3_SYSTEM_MESSAGE = """
You are a Financial Auditor. Your ONLY goal is to validate the findings of an Equity Analyst.

INPUTS:
1. SOURCE_TEXT: Raw news/filing text.
2. CATALYST: The Analyst's extracted event.
3. CATALYST_TYPE & DEFINITION: The specific category scope.

PROTOCOL (PASS=1 | FAIL=0):

1. QUOTE FIDELITY:
   - 'evidence' must exist in <SOURCE_TEXT_CHUNK>.
   - IGNORE minor whitespace/punctuation differences.
   - REJECT if words are altered or combined without "..." bridging.

2. DATA INTEGRITY (Strict):
   - FAIL if 'summary' adds specific numbers, dates, or names NOT in 'evidence'.
   - EXCEPTION: Standard calendar inferences (e.g., "Q3" -> "Sept") are ALLOWED.

3. INTERPRETATION vs. HALLUCINATION (The "Bear" Filter):
   - You must distinguish "financial decoding" from "inventing facts."
   - CASE A (Valid Inference): Text="Headwinds" -> Summary="Weak Demand". (PASS: Standard translation).
   - CASE B (Valid Inference): Text="ATM Facility" -> Summary="Dilution Risk". (PASS: Financial reality).
   - CASE C (Invalid Hallucination): Text="Efficiency program" -> Summary="Firing 500 people". (FAIL: Number '500' invented).
   - CASE D (Invalid Logic): Text="We aim to double sales" -> Summary="Sales doubled". (FAIL: Treating goal as fact).

4. SENTIMENT CHECK:
   - Do NOT reject negative sentiment on positive-sounding spin (e.g., "Capital Optimization" = Negative Dilution is CORRECT).
   - Only REJECT if sentiment is logically impossible (e.g., "Bankruptcy" marked Positive).
   
5. CATEGORY ALIGNMENT (Strict Scope):
   - REJECT if the extracted event does not fit the provided <CATALYST_DEFINITION>.
   - Example: Type="product_initiative" but Event="Dividend Cut". -> FAIL (Wrong category).
   - Example: Type="guidance_outlook" but Event="New CEO Hired". -> FAIL (Wrong category).

OUTPUT (JSON ONLY):
{
  "is_valid": 0 | 1,
  "rejection_reason": "If 0, state specific error (e.g., 'Wrong category: Dividend is not a Product Initiative'). If 1, use empty string."
}
"""

STAGE3_HUMAN_PROMPT_TEMPLATE = """
<CONTEXT_METADATA>
Target Type: {catalyst_type}
Target Definition: {definition}
</CONTEXT_METADATA>

<SOURCE_TEXT_CHUNK>
{chunk_text}
</SOURCE_TEXT_CHUNK>

<CANDIDATE_CATALYST>
{stage2_json_output}
</CANDIDATE_CATALYST>

Instructions:
1. QUOTE: Verify evidence exists (fuzzy match allowed).
2. DATA: Ensure no numbers/names were invented.
3. LOGIC: Check Case A-D rules (Decode spin = OK; Invent facts = FAIL).
4. SENTIMENT: Confirm sentiment reflects financial reality.
5. CATEGORY: Does the event strictly fit the 'Target Definition' above?
6. Return JSON.
"""


STAGE3_HUMAN_PROMPT = {
    key: partial(
        STAGE3_HUMAN_PROMPT_TEMPLATE.format, 
        catalyst_type=key, 
        definition=config["definition"]
    )
    for key, config in CATALYST_CONFIG.items()
}