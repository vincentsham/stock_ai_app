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
    metrics: Metric[];
    defaultVisibleCount: number;
};


