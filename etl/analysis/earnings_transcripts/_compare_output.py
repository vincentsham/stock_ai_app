"""Compare old DB output vs new agent output for a given ticker/quarter."""
import sys
import os
import json

# Ensure project root is on PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from database.utils import execute_query
from states import merged_state_factory
from graph import create_graph

# ─── PARAMETERS (change these to test other records) ──────────────
TIC = "SOFI"
CALENDAR_YEAR = 2025
CALENDAR_QUARTER = 4
# ──────────────────────────────────────────────────────────────────

# ─── Fetch company info from DB ──────────────────────────────────
company_df = execute_query("""
SELECT et.tic, sm.name, sm.sector, sm.industry, sm.short_summary,
       et.calendar_year, et.calendar_quarter, et.earnings_date
FROM core.earnings_transcripts et
JOIN core.stock_profiles sm ON et.tic = sm.tic
WHERE et.tic = %s AND et.calendar_year = %s AND et.calendar_quarter = %s
LIMIT 1;
""", (TIC, CALENDAR_YEAR, CALENDAR_QUARTER))

if company_df.empty:
    print(f"No transcript found for {TIC} Q{CALENDAR_QUARTER} {CALENDAR_YEAR}")
    sys.exit(1)

row = company_df.iloc[0]
print(f"\nCompany: {row['name']} ({row['tic']}) | {row['industry']} / {row['sector']}")
print(f"Quarter: Q{row['calendar_quarter']} {row['calendar_year']} | Earnings Date: {row['earnings_date']}")

# ─── 0) REFERENCE: Full Transcript ────────────────────────────────
print("\n" + "=" * 80)
print("REFERENCE INPUT (transcript from core.earnings_transcripts)")
print("=" * 80)

transcript_df = execute_query("""
SELECT transcript FROM core.earnings_transcripts
WHERE tic = %s AND calendar_year = %s AND calendar_quarter = %s
LIMIT 1;
""", (TIC, CALENDAR_YEAR, CALENDAR_QUARTER))

if transcript_df.empty:
    print("No transcript found.")
else:
    transcript_text = transcript_df.iloc[0]['transcript']
    print(transcript_text)

# ─── 1) OLD output from DB ────────────────────────────────────────
print("\n" + "=" * 80)
print("OLD OUTPUT (from core.earnings_transcript_analysis)")
print("=" * 80)

df = execute_query("""
SELECT sentiment, durability, performance_factors, past_summary,
       guidance_direction, revenue_outlook, margin_outlook, earnings_outlook,
       cashflow_outlook, growth_acceleration, future_outlook_sentiment, growth_drivers, future_summary,
       risk_mentioned, risk_impact, risk_time_horizon, risk_factors, risk_summary,
       mitigation_mentioned, mitigation_effectiveness, mitigation_time_horizon, mitigation_actions, mitigation_summary
FROM core.earnings_transcript_analysis
WHERE tic = %s AND calendar_year = %s AND calendar_quarter = %s;
""", (TIC, CALENDAR_YEAR, CALENDAR_QUARTER))

if df.empty:
    print("No old records found for AAPL Q4 2025")
    old_data = None
else:
    old_data = df.iloc[0].to_dict()
    print("\n--- Past Performance ---")
    print(f"  sentiment: {old_data['sentiment']}")
    print(f"  durability: {old_data['durability']}")
    print(f"  performance_factors: {old_data['performance_factors']}")
    print(f"  past_summary: {old_data['past_summary']}")
    
    print("\n--- Future Outlook ---")
    print(f"  guidance_direction: {old_data['guidance_direction']}")
    print(f"  revenue_outlook: {old_data['revenue_outlook']}")
    print(f"  margin_outlook: {old_data['margin_outlook']}")
    print(f"  earnings_outlook: {old_data['earnings_outlook']}")
    print(f"  cashflow_outlook: {old_data['cashflow_outlook']}")
    print(f"  growth_acceleration: {old_data['growth_acceleration']}")
    print(f"  future_outlook_sentiment: {old_data['future_outlook_sentiment']}")
    print(f"  growth_drivers: {old_data['growth_drivers']}")
    print(f"  future_summary: {old_data['future_summary']}")
    
    print("\n--- Risk Factors ---")
    print(f"  risk_mentioned: {old_data['risk_mentioned']}")
    print(f"  risk_impact: {old_data['risk_impact']}")
    print(f"  risk_time_horizon: {old_data['risk_time_horizon']}")
    print(f"  risk_factors: {old_data['risk_factors']}")
    print(f"  risk_summary: {old_data['risk_summary']}")
    
    print("\n--- Risk Response ---")
    print(f"  mitigation_mentioned: {old_data['mitigation_mentioned']}")
    print(f"  mitigation_effectiveness: {old_data['mitigation_effectiveness']}")
    print(f"  mitigation_time_horizon: {old_data['mitigation_time_horizon']}")
    print(f"  mitigation_actions: {old_data['mitigation_actions']}")
    print(f"  mitigation_summary: {old_data['mitigation_summary']}")


# ─── 2) NEW output from agent ─────────────────────────────────────
print("\n\n" + "=" * 80)
print("NEW OUTPUT (from current agent)")
print("=" * 80)

graph = create_graph()
app = graph.compile()

state = merged_state_factory(
    tic=row['tic'],
    company_name=row['name'],
    industry=row['industry'],
    sector=row['sector'],
    company_description=row['short_summary'],
    calendar_year=int(row['calendar_year']),
    calendar_quarter=int(row['calendar_quarter']),
    earnings_date=row['earnings_date'].isoformat() if hasattr(row['earnings_date'], 'isoformat') else str(row['earnings_date'])
)

result = app.invoke(state)

new_past = result.get('past_analysis', {})
new_future = result.get('future_analysis', {})
new_risk = result.get('risk_analysis', {})
new_risk_resp = result.get('risk_response_analysis', {})

print("\n--- Past Performance ---")
print(f"  sentiment: {new_past.get('sentiment')}")
print(f"  durability: {new_past.get('durability')}")
print(f"  performance_factors: {new_past.get('performance_factors')}")
print(f"  past_summary: {new_past.get('past_summary')}")

print("\n--- Future Outlook ---")
print(f"  guidance_direction: {new_future.get('guidance_direction')}")
print(f"  revenue_outlook: {new_future.get('revenue_outlook')}")
print(f"  margin_outlook: {new_future.get('margin_outlook')}")
print(f"  earnings_outlook: {new_future.get('earnings_outlook')}")
print(f"  cashflow_outlook: {new_future.get('cashflow_outlook')}")
print(f"  growth_acceleration: {new_future.get('growth_acceleration')}")
print(f"  future_outlook_sentiment: {new_future.get('future_outlook_sentiment')}")
print(f"  growth_drivers: {new_future.get('growth_drivers')}")
print(f"  future_summary: {new_future.get('future_summary')}")

print("\n--- Risk Factors ---")
print(f"  risk_mentioned: {new_risk.get('risk_mentioned')}")
print(f"  risk_impact: {new_risk.get('risk_impact')}")
print(f"  risk_time_horizon: {new_risk.get('risk_time_horizon')}")
print(f"  risk_factors: {new_risk.get('risk_factors')}")
print(f"  risk_summary: {new_risk.get('risk_summary')}")

print("\n--- Risk Response ---")
print(f"  mitigation_mentioned: {new_risk_resp.get('mitigation_mentioned')}")
print(f"  mitigation_effectiveness: {new_risk_resp.get('mitigation_effectiveness')}")
print(f"  mitigation_time_horizon: {new_risk_resp.get('mitigation_time_horizon')}")
print(f"  mitigation_actions: {new_risk_resp.get('mitigation_actions')}")
print(f"  mitigation_summary: {new_risk_resp.get('mitigation_summary')}")
