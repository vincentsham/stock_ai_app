// types/metrics.ts
export type Metric = {
    label: string;
    name: string;
    value: string;
    percentile: number | null;
    description: string;
    inverse: boolean | null;
    displayByDefault: boolean;
    highlight?: boolean | null;
};

export type MetricList = {
    category: string;
    tic: string;
    score: number | null;
    metrics: Metric[];
    defaultVisibleCount: number;
    highlight?: boolean | null;
};

export type AllMetrics = {
    valuation: MetricList | null;
    profitability: MetricList | null;
    growth: MetricList | null;
    efficiency: MetricList | null;
    financialHealth: MetricList | null;
}

export type StockScores = {
    tic: string;
    valuation_score: number | null;
    profitability_score: number | null;
    growth_score: number | null;
    efficiency_score: number | null;
    financial_health_score: number | null;
    total_score: number | null;
};

export type AllMetricsWithExpandedStates = {
    valuation: {metrics: MetricList | null} & { expandedState: [boolean, () => void] };
    profitability: {metrics: MetricList | null} & { expandedState: [boolean, () => void] };
    growth: {metrics: MetricList | null} & { expandedState: [boolean, () => void] };
    efficiency: {metrics: MetricList | null} & { expandedState: [boolean, () => void] };
    financialHealth: {metrics: MetricList | null} & { expandedState: [boolean, () => void] };
}