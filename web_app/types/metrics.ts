// types/metrics.ts
export type Metric = {
    label: string;
    name: string;
    value: string;
    percentile: number | null;
    description: string;
    inverse: boolean | null;
    displayByDefault: boolean;
};

export type MetricList = {
    category: string;
    tic: string;
    score: number | null;
    metrics: Metric[];
    defaultVisibleCount: number;
};

export type StockScores = {
    tic: string;
    valuation_score: number | null;
    profitability_score: number | null;
    growth_score: number | null;
    efficiency_score: number | null;
    financial_health_score: number | null;
    total_score: number | null;
};