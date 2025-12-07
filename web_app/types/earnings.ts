// types/earnings.ts
export type Earnings = {
    tic: string;
    calendar_year: number;
    calendar_quarter: number;
    eps: number;
    eps_estimated: number;
    revenue: number;
    revenue_estimated: number;
};

export type EarningsRegime = {
    eps_surprise_regime: string;
    revenue_surprise_regime: string;
};

export type EPSRegime = {
    yoy_growth_regime: string;
    yoy_accel_regime: string;
};

export type RevenueRegime = {
    yoy_growth_regime: string;
    yoy_accel_regime: string;
};