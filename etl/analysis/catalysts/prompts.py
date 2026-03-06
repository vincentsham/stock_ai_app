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
        "definition": "Forward-looking management guidance: revenue/EPS forecasts raised, lowered, reaffirmed, or withdrawn.",
        "typical_impact_areas": ["revenue", "earnings", "margin"],
    },
    "product_initiative": {
        "definition": "New product launches, production ramps, capacity expansion — or delays, recalls, cancellations.",
        "typical_impact_areas": ["demand", "technology", "capacity"],
    },
    "partnership_deal": {
        "definition": "Strategic alliances, contract wins, M&A announcements — or deal terminations, customer losses.",
        "typical_impact_areas": ["strategy", "supply_chain", "technology"],
    },
    "cost_efficiency": {
        "definition": "Cost restructuring, margin improvement programs, divestitures — or impairments, writedowns, expense surges.",
        "typical_impact_areas": ["expenses", "margin", "operations"],
    },
    "capital_actions": {
        "definition": "Share buybacks, dividend changes, debt refinancing — or equity dilution, credit downgrades.",
        "typical_impact_areas": ["shareholder_return", "financing", "balance_sheet"],
    },
    "regulatory_policy": {
        "definition": "Regulatory approvals, favorable rulings, settlements — or investigations, lawsuits, enforcement actions.",
        "typical_impact_areas": ["regulatory", "legal"],
    },
    "demand_trends": {
        "definition": "Order backlog growth, pricing power, market share gains — or demand weakness, inventory buildup, discounting.",
        "typical_impact_areas": ["demand", "volume", "pricing", "inventory"],
    },
    "risk_event": {
        "definition": "Insider buying signals — or executive departures, cyber breaches, operational disruptions, supply shocks.",
        "typical_impact_areas": ["risk", "leadership", "supply_chain", "legal"],
    },
    "macro_policy": {
        "definition": "Interest rates, tariffs, trade restrictions, FX moves, or geopolitical events impacting the business.",
        "typical_impact_areas": ["macro", "currency_fx", "geopolitical"],
    },
}




STAGE1_SYSTEM_MESSAGE = """
Group document chunks by same real-world event for <TARGET_COMPANY>.

Rules:
- Max 3 chunks per group, max 4 groups.
- Discard fluff, historical data, noise. Focus on material, stock-moving catalysts.
- Each group = ONE specific event. Do NOT merge chunks sharing only company/timeframe/theme.
  BAD: product launch + ad program | partnership + patent ruling
  GOOD: supply shortage + its downstream production impact
- Output ONLY JSON list of lists of Temp IDs. No prose, no markdown.
- If nothing material: []

Format: [[1, 3, 5], [4, 2], [6]]
"""


STAGE1_HUMAN_PROMPT = """
<TARGET_COMPANY>
{company_info} ({company_tic})
</TARGET_COMPANY>

<INPUT_CHUNKS>
{id_mapping_block}
</INPUT_CHUNKS>

<INSTRUCTION>
Identify and group the unique, material catalysts found in the Input Chunks. Return only the Temporary ID groups.
</INSTRUCTION>
"""



STAGE2_SYSTEM_MESSAGE = """
Convert evidence chunks into a structured catalyst record.

Steps:
1. If evidence matches <CURRENT_CATALYST>, action="update" with its ID. Otherwise "create".
2. Assign ONE catalyst_type: [guidance_outlook, product_initiative, partnership_deal, cost_efficiency, capital_actions, regulatory_policy, demand_trends, risk_event, macro_policy].
3. Title = WHAT happened (short headline). Summary = WHY it matters + key numbers/context NOT already in the title. Never repeat the title in the summary. No "Delta:"/"Update:"/"XXX:" prefixes.
4. Assign ONE impact_area from the table below matching the PRIMARY business pillar.
5. Sentiment: +1 (helps company) or -1 (hurts company). Both title and summary tone MUST match the sentiment score. If sentiment=-1, do not lead with positive framing.

Grounding: Every claim must be supported by cited evidence. No inference or editorializing.

Citations:
- ONE verbatim quote per chunk, max 3 total. Chronological order (oldest→newest).
- Quote substantive body sentences, not headlines.

Impact Areas by catalyst_type (prefer these, use others only if evidence clearly points elsewhere):
- guidance_outlook → revenue, earnings, margin
- product_initiative → demand, technology, capacity
- partnership_deal → strategy, supply_chain, technology
- cost_efficiency → expenses, margin, operations
- capital_actions → shareholder_return, financing, balance_sheet
- regulatory_policy → regulatory, legal
- demand_trends → demand, volume, pricing, inventory
- risk_event → risk, leadership, supply_chain, legal
- macro_policy → macro, currency_fx, geopolitical

All valid impact_area tags: revenue, earnings, margin, cashflow, expenses, capex, operations, supply_chain, capacity, technology, strategy, market_expansion, demand, volume, pricing, inventory, shareholder_return, financing, balance_sheet, dilution, risk, cybersecurity, regulatory, legal, macro, currency_fx, geopolitical, leadership

Output JSON:
{{
  "action": "create" | "update",
  "catalyst_id": "UUID or empty",
  "catalyst_type": "one_of_9_types",
  "title": "Directional Headline",
  "summary": "50 words max",
  "sentiment": 1 | -1,
  "magnitude": 1 | 0 | -1,
  "impact_area": "one tag",
  "time_horizon": 0 | 1 | 2,
  "citations": [{{ "chunk_id": "uuid", "quote": "verbatim" }}]
}}
"""


STAGE2_HUMAN_PROMPT = """
<TARGET_COMPANY>
{company_info}
</TARGET_COMPANY>

<EVIDENCE_GROUP>
Chunks sorted oldest-first:
{chunks_for_this_group}
</EVIDENCE_GROUP>

<CURRENT_CATALYST>
{existing_catalyst_json}
</CURRENT_CATALYST>

Match evidence to <CURRENT_CATALYST> → update with its ID, or create new. ONE quote per chunk, chronological order.
"""



STAGE3_SYSTEM_MESSAGE = """
Sanity-check a catalyst record against source text. Bias: EXTREME LENIENCY — only fail clear hallucinations.

Rules:
- FAIL if any citation quote is completely absent from its source chunk.
- FAIL if summary contains specific numbers/dollars not in any source chunk.
- FAIL if sentiment flipped from prior_sentiment without clear evidence of material reversal.
- PASS minor truncation, whitespace, capitalization differences in quotes.
- PASS conceptual translations (e.g., "Efficiency Program" → "Cost Cutting").
- PASS entity resolution (parent companies, tickers, synonyms).
- PASS dates derivable from source metadata.
- PASS all reasonable category overlaps and subjective analyst sentiment calls.

Output JSON:
{{ "is_valid": 0 | 1, "rejection_reason": "hallucination detail or empty string" }}
"""


STAGE3_HUMAN_PROMPT = """
Type: {catalyst_type} | Definition: {definition}
Company: {company_info}
Prior Sentiment: {prior_sentiment}

<SOURCE_TEXT_CHUNKS>
{source_text_chunks}
</SOURCE_TEXT_CHUNKS>

<CANDIDATE>
{stage2_json_output}
</CANDIDATE>

Validate: Check each citation quote exists in its source chunk. Check summary numbers match sources. Check sentiment consistency with prior.
"""