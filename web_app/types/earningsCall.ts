// types/earnings.ts
export type EarningsCallAnalysis = {
    inference_id: string;
    event_id: string;
    tic: string;
    calendar_year: number;
    calendar_quarter: number;
    earnings_date: string;
    sentiment: number;
    durability: number;
    performance_factors: string[];
    past_summary: string;
    guidance_direction: number;
    revenue_outlook: number;
    margin_outlook: number;
    earnings_outlook: number;
    cashflow_outlook: number;
    growth_acceleration: number;
    future_outlook_sentiment?: string | null;
    growth_drivers: string[];
    future_summary: string;
    risk_mentioned: number;
    risk_impact: number;
    risk_time_horizon: number;
    risk_factors: string[];
    risk_summary: string;
    mitigation_mentioned: number;
    mitigation_effectiveness: number;
    mitigation_time_horizon: number;
    mitigation_actions: string[];
    mitigation_summary: string;
    transcript_sha256: string;
    updated_at: string;
}