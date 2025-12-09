// types/analyst.ts
export type AnalystAnalysis = {
    tic: string;
    date: string;
    close: number;
    pt_count: number | null;
    pt_high: number | null;
    pt_low: number | null;
    pt_p25: number | null;
    pt_median: number | null;
    pt_p75: number | null; 
    pt_upgrade_n: number | null;
    pt_downgrade_n: number | null;
    pt_reiterate_n: number | null;
    pt_init_n: number | null;
    grade_count: number | null;
    grade_buy_n: number | null;
    grade_hold_n: number | null;
    grade_sell_n: number | null;
    grade_upgrade_n: number | null;
    grade_downgrade_n: number | null;
    grade_reiterate_n: number | null;
    grade_init_n: number | null;
};





