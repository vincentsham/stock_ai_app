HUMAN_PROMPT_TEMPLATE = """
Company: {company_name} ({tic}) | {industry} / {sector}
Quarter: Q{calendar_quarter} {calendar_year}

Analyze these earnings call excerpts. Follow system instructions exactly.

Excerpts:
{context}

Return strict JSON only. No commentary.
"""


PAST_PERFORMANCE_SYSTEM_MESSAGE = """
Analyze ONLY backward-looking statements from an earnings transcript.

Output JSON:
{{
  "sentiment": +1 positive | 0 neutral | -1 negative,
  "durability": 2 sustainable | 1 unclear | 0 one-time,
  "performance_factors": ["<2-5 word phrase>", ...],  // 3-6 items
  "past_summary": "<2-3 sentences, max 80 words, with 1-2 verbatim quotes>"
}}

Example:
{{
  "sentiment": 1,
  "durability": 2,
  "performance_factors": ["record iPhone revenue", "services growth 18%", "supply chain recovery"],
  "past_summary": "Strong quarter with record results. CEO noted \\"record revenue in our services business.\\" Margins expanded on cost discipline."
}}

Rules:
1. Ignore all guidance/forecasts.
2. Include verbatim quotes as evidence.
3. If mixed, use dominant polarity.
"""

FUTURE_OUTLOOK_SYSTEM_MESSAGE = """
Analyze ONLY forward-looking statements (guidance, forecasts, plans) from an earnings transcript.

Output JSON:
{{
  "guidance_direction": +1 raised | 0 reaffirmed/mixed | -1 lowered,
  "revenue_outlook": +1 growth | 0 stable | -1 decline,
  "earnings_outlook": +1 growth | 0 stable | -1 decline,
  "margin_outlook": +1 expansion | 0 stable | -1 contraction,
  "cashflow_outlook": +1 growth | 0 stable | -1 decline,
  "growth_acceleration": +1 accelerating | 0 stable | -1 decelerating,
  "future_outlook_sentiment": +1 optimistic | 0 neutral | -1 cautious,
  "growth_drivers": ["<2-5 word phrase>", ...],  // 3-6 forward-looking items
  "future_summary": "<2-3 sentences, max 80 words, with 1-2 verbatim quotes>"
}}

guidance_direction — assess from the RAW guidance language, not from your other outlook fields:
- +1 if management frames guidance as year-over-year growth or acceleration AND margins not guided lower
- -1 if guidance explicitly lowered or withdrawn
- 0 if guidance reaffirmed at similar levels or mixed signals (revenue up but margins declining)
Sequential seasonal decline (e.g. Q4→Q1 holiday effect) does NOT mean guidance was lowered.

Other rules:
1. margin_outlook: +1 only if next-quarter guidance range is entirely above the completed quarter's actual margin. Range overlapping prior actual = 0. Ignore long-term "hold" language.
2. CapEx increases reduce cashflow_outlook.
3. 0 for any metric not mentioned.
"""


RISK_FACTORS_SYSTEM_MESSAGE = """
Identify explicit risks, headwinds, or uncertainties stated by management.

Output JSON:
{{
  "risk_mentioned": 1 if risks stated | 0 if none,
  "risk_impact": -1 minor | 0 moderate | 1 major,
  "risk_time_horizon": 0 short-term (1-2 qtrs) | 1 mid-term (6-12 mo) | 2 long-term (>1 yr),
  "risk_factors": ["<2-5 word phrase>", ...],  // 3-6 items
  "risk_summary": "<2-3 sentences, max 80 words, with 1-2 verbatim quotes>"
}}

Rules:
1. A risk must be an external or internal factor that THREATENS earnings, revenue, or operations. If a factor does not threaten business performance, it is not a risk.
2. Management being selective or disciplined is NOT a risk — it is a positive signal.
3. If no explicit risks stated, return: {{"risk_mentioned": 0, "risk_impact": -1, "risk_time_horizon": 0, "risk_factors": [], "risk_summary": ""}}
4. Do NOT stretch to find risks. Empty is correct when transcript is purely positive.
"""

RISK_RESPONSE_SYSTEM_MESSAGE = """
The previous AI message has risk_factors JSON. Find management's concrete mitigation actions in the transcript excerpts.

Output JSON:
{{
  "mitigation_mentioned": 1 if actions stated | 0 if none,
  "mitigation_effectiveness": -1 weak | 0 moderate | 1 strong,
  "mitigation_time_horizon": 0 short-term | 1 mid-term | 2 long-term,
  "mitigation_actions": ["<2-5 word phrase>", ...],
  "mitigation_summary": "<2-3 sentences, max 80 words, with 1-2 verbatim quotes>"
}}

What counts:
  risk "FX volatility" -> action "natural hedging program" = GOOD
  risk "supply chain" -> action "dual-source components" = GOOD
  "scaling AI models", "launching new products" = BAD (growth, not mitigation)
  risk "regulatory pressure" -> action "diversify chip supply" = BAD (wrong risk category)

Rules:
1. Each action MUST counter a specific risk from risk_factors. Actions addressing a different risk category = exclude.
2. "Monitoring", "watching", "evaluating", "looking at options" = not an action. Exclude.
3. Growth initiatives or long-term strategic investments that don't directly address a near-term risk = exclude.
4. Fewer honest actions > padded list. Empty list is OK.
5. If management only states intent without naming a SPECIFIC action, return mitigation_mentioned=0.
6. If none: {{"mitigation_mentioned": 0, "mitigation_effectiveness": -1, "mitigation_time_horizon": 0, "mitigation_actions": [], "mitigation_summary": ""}}
"""


RISK_RESPONSE_QUERY_GEN_SYSTEM_MESSAGE = """
Generate 3 search queries to find transcript passages about management's response to identified risks.
Input: risk_factors JSON from previous message.
Each query max 20 words. Use risk_factors terms + synonyms.
Every query must reference at least one specific risk from risk_factors. No generic strategy queries.
Cover: (1) direct mitigation, (2) strategic response, (3) financial or contingency plans.
Output JSON: {{"queries": ["<q1>", "<q2>", "<q3>"]}}
"""

RISK_RESPONSE_QUERY_GEN_HUMAN_MESSAGE = """
Company: {tic} ({company_name}) | {industry} / {sector}
Quarter: Q{calendar_quarter} {calendar_year}

Using the risk_factors above, return JSON: {{"queries": ["<q1>", "<q2>", "<q3>"]}}
"""


def get_past_performance_queries(company_name="", industry="", sector="", **kwargs):
    name = company_name or "the company"
    return [
        f"{name} recent quarter financial performance and operational results",
        f"{name} management discussion of execution, demand, and margins in the last quarter",
        f"{name} {industry} commentary on quarterly performance drivers and results" if industry else f"{name} commentary on quarterly performance drivers and results"
    ]

def get_future_outlook_queries(company_name="", industry="", sector="", **kwargs):
    name = company_name or "the company"
    return [
        f"{name} management outlook guidance and forecast for upcoming quarters",
        f"{name} next quarter revenue guidance gross margin outlook and operating expense expectations",
        f"{name} expectations for revenue margins cash flow and capital allocation going forward"
    ]

def get_risk_factors_queries(company_name="", industry="", sector="", **kwargs):
    name = company_name or "the company"
    return [
        f"{name} management discussion of risks headwinds or uncertainties",
        f"{name} {industry} supply chain regulation macroeconomic or competitive risks" if industry else f"{name} supply chain regulation macroeconomic or competitive risks",
        f"{name} challenges volatility or adverse factors facing the business",
        f"{name} geopolitical risk supply chain constraint chip shortage or long-term strategic vulnerability"
    ]
