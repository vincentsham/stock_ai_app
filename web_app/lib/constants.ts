import { formatCurrency, formatInteger, formatPercentage, formatRatio } from '@/lib/formatters';
import { format } from 'path';
import { coerceNumber } from './utils';

export const DISCLAIMER_TEXT = `This is for informational purposes only, not financial advice. 
      Be aware: The AI system may occasionally generate incorrect or incomplete information. 
      Invest responsibly and conduct your own due diligence.`;


export const EARNINGS_TAG_METADATA: Record<string, { label: string; description: string; className: string }> = {
      'consistent-outperform': {
            label: 'Consistent Outperform',
            description: 'Recorded Wall Street estimate beats in >=3 consecutive quarters.',
            className: 'bg-[#22c55e]/10 text-[#22c55e] border-[#22c55e]/20',
      },    
      'frequent-beat': {
            label: 'Frequent Beat',
            description: 'Recorded Wall Street estimate beats in 3 of the last 4 quarters.',
            className: 'bg-[#22c55e]/10 text-[#22c55e] border-[#22c55e]/20',
      },  
      'broken-beat-streak': {
            label: 'Broken Beat Streak',
            description: 'Recorded Wall Street estimate beats in 3 of the last 4 quarters but missed the latest result.',
            className: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      },    
      'emerging-beat': {
            label: 'Emerging Beat',
            description: 'Recorded Wall Street estimate beats in the last 2 quarters after earlier misses.',
            className: 'bg-[#22c55e]/10 text-[#22c55e] border-[#22c55e]/20',
      },
      'mixed-performance': {
            label: 'Mixed Performance',
            description: 'Recorded Wall Street estimate beats in 2 of the last 4 quarters without a recent streak.',
            // className: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
            className: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      },
      'consistent-miss': {
            label: 'Consistent Miss',
            description: 'Recorded Wall Street estimate misses in >=3 of the last 4 quarters.',
            className: 'bg-[#ef4444]/10 text-[#ef4444] border-[#ef4444]/20',
      },
      'sustained-expansion': {
            label: 'Sustained Expansion',
            description: 'Recorded positive YoY growth in >=3 consecutive quarters.',
            className: 'bg-[#22c55e]/10 text-[#22c55e] border-[#22c55e]/20',
      },    
      'developing-expansion': {
            label: 'Developing Expansion',
            description: 'Recorded positive YoY growth in 3 of the last 4 quarters.',
            className: 'bg-[#22c55e]/10 text-[#22c55e] border-[#22c55e]/20',
      },   
      'broken-growth-streak': {
            label: 'Broken Expansion Streak',
            description: 'Recorded positive YoY growth in 3 of the last 4 quarters but contracted most recently.',
            className: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      },   
      'emerging-growth': {
            label: 'Emerging Growth',
            description: 'Recorded positive YoY growth in the last 2 quarters after earlier contraction.',
            // className: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
            className: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      },
      'volatile-growth': {
            label: 'Volatile Growth',
            description: 'Recorded positive YoY growth in 2 of the last 4 quarters without a recent streak.',
            // className: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
            className: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      },
      'tentative-turnaround': {
            label: 'Tentative Turnaround',
            description: 'Recorded positive YoY growth after >=3 consecutive contraction quarters.',
            className: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      },
      'persistent-contraction': {
            label: 'Persistent Contraction',
            description: 'Recorded negative YoY growth in >=3 of the last 4 quarters.',
            className: 'bg-[#ef4444]/10 text-[#ef4444] border-[#ef4444]/20',
      },
      'sustained-acceleration': {
            label: 'Sustained Acceleration',
            description: 'Recorded YoY growth-rate acceleration in 3 of the last 4 quarters including a recent >=2-quarter streak.',
            className: 'bg-[#22c55e]/10 text-[#22c55e] border-[#22c55e]/20',
      }, 
      'choppy-acceleration': {
            label: 'Choppy Acceleration',
            description: 'Recorded YoY growth-rate acceleration in 3 of the last 4 quarters.',
            className: 'bg-[#22c55e]/10 text-[#22c55e] border-[#22c55e]/20',
      }, 
      'broken-acceleration-streak': {
            label: 'Broken Acceleration Streak',
            description: 'Recorded YoY growth-rate acceleration in 3 of the last 4 quarters but slowed most recently.',
            className: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      },
      'emerging-acceleration': {
            label: 'Emerging Acceleration',
            description: 'Recorded YoY growth-rate acceleration in the last 2 quarters after earlier stagnation.',
            className: 'bg-[#22c55e]/10 text-[#22c55e] border-[#22c55e]/20',
      },
      'unstable-momentum': {
            label: 'Unstable Momentum',
            description: 'Recorded YoY growth-rate acceleration in 2 of the last 4 quarters without a recent streak.',
            // className: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
            className: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      },
      'broken-deceleration-streak': {
            label: 'Broken Deceleration Streak',
            description: 'Recorded YoY growth-rate deceleration in 3 of the last 4 quarters but re-accelerated most recently.',
            className: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      },
      'persistent-deceleration': {
            label: 'Persistent Deceleration',
            description: 'Recorded YoY growth-rate deceleration in >=3 of the last 4 quarters.',
            className: 'bg-[#ef4444]/10 text-[#ef4444] border-[#ef4444]/20',
      },
      'unknown': {
            label: 'Unknown',
            description: 'Insufficient data to classify the trend.',
            className: 'hidden bg-purple-500/10 text-purple-400 border-purple-500/20',
      },
};

export const METRICS_METADATA: Record<string, { 
      name: string; 
      display_fn: (value: unknown) => string;
      inverse: boolean | null;
      displayByDefault: boolean;
      description: string }> = {   

      'market_cap': {
            name: 'Market Cap',
            display_fn: formatCurrency,
            inverse: null,
            displayByDefault: true,
            description: 'The total market value of a company\'s outstanding shares, indicating its size and investor perception.',
      },
      'pe_ttm': {
            name: 'P/E Ratio',
            display_fn: formatRatio,
            inverse: true,
            displayByDefault: true,
            description: 'Price-to-Earnings ratio, measuring stock price relative to earnings per share; lower values may indicate undervaluation.',
      },
      'pe_forward': {
            name: 'Forward P/E Ratio',
            display_fn: formatRatio,
            inverse: true,
            displayByDefault: true,
            description: 'Forward Price-to-Earnings ratio based on projected earnings; lower values may suggest undervaluation.',
      },
      'ev_to_ebitda_ttm': {
            name: 'EV/EBITDA',
            display_fn: (value: unknown) => {
                  const n = coerceNumber(value);
                  return n === null ? 'N/A' : n.toFixed(2);
            },
            inverse: true,
            displayByDefault: false,
            description: 'Enterprise Value to EBITDA ratio, assessing company value relative to earnings; lower values may indicate undervaluation.',
      },
      'fcf_yield_ttm': {
            name: 'FCF Yield',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: false,
            description: 'Free Cash Flow Yield, indicating cash flow generation relative to market value; higher values may suggest undervaluation.',
      },
      'ps_ttm': {
            name: 'P/S Ratio',
            display_fn: formatRatio,
            inverse: true,
            displayByDefault: true,
            description: 'Price-to-Sales ratio, measuring stock price relative to revenue; lower values may indicate undervaluation.',
      },
      'peg_ratio': {
            name: 'PEG Ratio',
            display_fn: formatRatio,
            inverse: true,
            displayByDefault: true,
            description: 'Price/Earnings to Growth ratio, evaluating valuation relative to earnings growth; lower values may suggest undervaluation.',
      },
      'peg_ratio_forward': {
            name: 'PEG Ratio',
            display_fn: formatRatio,
            inverse: true,
            displayByDefault: true,
            description: 'Forward Price/Earnings to Growth ratio, evaluating valuation relative to projected earnings growth; lower values may suggest undervaluation.',
      },
      'ev_to_revenue_ttm': {
            name: 'EV/Revenue',
            display_fn: (value: unknown) => {
                  const n = coerceNumber(value);
                  return n === null ? 'N/A' : n.toFixed(2);
            },
            inverse: true,
            displayByDefault: false,
            description: 'Enterprise Value to Revenue ratio, assessing company value relative to revenue; lower values may indicate undervaluation.',
      },
      'p_to_fcf_ttm': {
            name: 'P/FCF Ratio',
            display_fn: formatRatio,
            inverse: true,
            displayByDefault: true,
            description: 'Price-to-Free Cash Flow ratio, measuring stock price relative to free cash flow; lower values may indicate undervaluation.',
      },
      'price_to_book': {
            name: 'P/B Ratio',
            display_fn: formatRatio,
            inverse: true,
            displayByDefault: false,
            description: 'Price-to-Book ratio, comparing stock price to book value; lower values may indicate undervaluation.',
      },
      'ev_to_fcf_ttm': {
            name: 'EV/FCF',
            display_fn: (value: unknown) => {
                  const n = coerceNumber(value);
                  return n === null ? 'N/A' : n.toFixed(2);
            },
            inverse: true,
            displayByDefault: false,
            description: 'Enterprise Value to Free Cash Flow ratio, assessing company value relative to free cash flow; lower values may indicate undervaluation.',
      },
      'earnings_yield_ttm': {
            name: 'Earnings Yield',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: false,
            description: 'Earnings Yield, the inverse of the P/E ratio, indicating earnings relative to stock price; higher values may suggest undervaluation.',
      },
      'revenue_yield_ttm': {
            name: 'Revenue Yield',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: false,
            description: 'Revenue Yield, the inverse of the P/S ratio, indicating revenue relative to stock price; higher values may suggest undervaluation.',
      },
      'gross_margin': {
            name: 'Gross Margin',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: true,
            description: 'Gross Margin, indicating the percentage of revenue remaining after COGS; higher values suggest better efficiency.',
      },
      'operating_margin': {
            name: 'Operating Margin',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: true,
            description: 'Operating Margin, measuring profitability from core operations; higher values indicate better operational efficiency.',
      },
      'ebitda_margin': {
            name: 'EBITDA Margin',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: true,
            description: 'EBITDA Margin, indicating earnings before interest, taxes, depreciation, and amortization as a percentage of revenue; higher values suggest better profitability.',
      },
      'net_margin': {
            name: 'Net Margin',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: true,
            description: 'Net Margin, showing overall profitability after all expenses; higher values indicate better financial health.',
      },
      'roe': {
            name: 'Return on Equity',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: false,
            description: 'Return on Equity, measuring profitability relative to shareholder equity; higher values indicate efficient use of equity.',
      },
      'roa': {
            name: 'Return on Assets',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: false,
            description: 'Return on Assets, indicating how efficiently assets generate profit; higher values suggest better asset utilization.',
      },
      'ocf_margin': {
            name: 'Operating Cash Flow Margin',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: false,
            description: 'Operating Cash Flow Margin, showing cash generated from operations as a percentage of revenue; higher values indicate strong cash flow generation.',
      },
      'fcf_margin': {
            name: 'Free Cash Flow Margin',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: false,
            description: 'Free Cash Flow Margin, indicating free cash flow as a percentage of revenue; higher values suggest better financial flexibility.',
      },
      'revenue_growth_yoy': {
            name: 'Revenue Growth (YoY)',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: true,
            description: 'Year-over-Year Revenue Growth, measuring annual increase in revenue; higher values indicate strong sales performance.',
      },
      'revenue_cagr_3y': {
            name: 'Revenue CAGR (3Y)',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: true,
            description: '3-Year Compound Annual Growth Rate of Revenue, indicating long-term sales growth; higher values suggest sustained expansion.',
      },
      'eps_growth_yoy': {
            name: 'EPS Growth (YoY)',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: true,
            description: 'Year-over-Year Earnings Per Share Growth, measuring annual increase in profitability; higher values indicate improved earnings performance.',
      },
      'eps_cagr_3y': {
            name: 'EPS CAGR (3Y)',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: true,
            description: '3-Year Compound Annual Growth Rate of Earnings Per Share, indicating long-term profitability growth; higher values suggest sustained earnings expansion.',
      },
      'fcf_growth_yoy': {
            name: 'FCF Growth (YoY)',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: true,
            description: 'Year-over-Year Free Cash Flow Growth, measuring annual increase in free cash flow; higher values indicate improved cash generation.',
      },
      'fcf_cagr_3y': {
            name: 'FCF CAGR (3Y)',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: true,
            description: '3-Year Compound Annual Growth Rate of Free Cash Flow, indicating long-term cash flow growth; higher values suggest sustained cash generation improvement.',
      },
      'revenue_cagr_5y': {
            name: 'Revenue CAGR (5Y)',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: false,
            description: '5-Year Compound Annual Growth Rate of Revenue, indicating long-term sales growth; higher values suggest sustained expansion.',
      },
      'eps_cagr_5y': {
            name: 'EPS CAGR (5Y)',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: false,
            description: '5-Year Compound Annual Growth Rate of Earnings Per Share, indicating long-term profitability growth; higher values suggest sustained earnings expansion.',
      },
      'fcf_cagr_5y': {
            name: 'FCF CAGR (5Y)',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: false,
            description: '5-Year Compound Annual Growth Rate of Free Cash Flow, indicating long-term cash flow growth; higher values suggest sustained cash generation improvement.',
      },
      'ebitda_growth_yoy': {
            name: 'EBITDA Growth (YoY)',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: true,
            description: 'Year-over-Year EBITDA Growth, measuring annual increase in earnings before interest, taxes, depreciation, and amortization; higher values indicate improved operational profitability.',
      },
      'ebitda_cagr_3y': {
            name: 'EBITDA CAGR (3Y)',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: true,
            description: '3-Year Compound Annual Growth Rate of EBITDA, indicating long-term operational profitability growth; higher values suggest sustained improvement.',
      },
      'ebitda_cagr_5y': {
            name: 'EBITDA CAGR (5Y)',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: false,
            description: '5-Year Compound Annual Growth Rate of EBITDA, indicating long-term operational profitability growth; higher values suggest sustained improvement.',
      },
      'operating_income_growth_yoy': {
            name: 'Operating Income Growth (YoY)',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: false,
            description: 'Year-over-Year Operating Income Growth, measuring annual increase in operating profit; higher values indicate improved core business profitability.',
      },
      'forward_revenue_growth': {
            name: 'Forward Revenue Growth',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: false,
            description: 'Projected future revenue growth based on analyst estimates; higher values suggest expected sales expansion.',
      },
      'forward_eps_growth': {
            name: 'Forward EPS Growth',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: false,
            description: 'Projected future earnings per share growth based on analyst estimates; higher values suggest expected profitability improvement.',
      },
      'asset_turnover': {
            name: 'Asset Turnover',
            display_fn: formatRatio,
            inverse: false,
            displayByDefault: true,
            description: 'Asset Turnover Ratio, measuring efficiency in using assets to generate revenue; higher values indicate better asset utilization.',
      },
      'fixed_asset_turnover': {
            name: 'Fixed Asset Turnover',
            display_fn: formatRatio,
            inverse: false,
            displayByDefault: true,
            description: 'Fixed Asset Turnover Ratio, assessing efficiency in using fixed assets to generate revenue; higher values indicate better utilization of fixed assets.',
      },
      'opex_ratio': {
            name: 'Operating Expense Ratio',
            display_fn: formatPercentage,
            inverse: true,
            displayByDefault: true,
            description: 'Operating Expense Ratio, indicating the proportion of revenue consumed by operating expenses; lower values suggest better cost management.',
      },
      'cash_conversion_cycle': {
            name: 'Cash Conversion Cycle',
            display_fn: (value: unknown) => {
                  const n = coerceNumber(value);
                  return n === null ? 'N/A' : `${n.toFixed(1)} days`;
            },
            inverse: true,
            displayByDefault: true,
            description: 'Cash Conversion Cycle, indicating the time taken to convert investments in inventory and other resources into cash flows; lower values suggest better efficiency.',
      },
      'dso': {
            name: 'Days Sales Outstanding',
            display_fn: (value: unknown) => {
                  const n = coerceNumber(value);
                  return n === null ? 'N/A' : `${n.toFixed(1)} days`;
            },
            inverse: true,
            displayByDefault: false,
            description: 'Days Sales Outstanding, measuring the average number of days to collect payment after a sale; lower values indicate efficient receivables management.',
      },
      'dio': {
            name: 'Days Inventory Outstanding',
            display_fn: (value: unknown) => {
                  const n = coerceNumber(value);
                  return n === null ? 'N/A' : `${n.toFixed(1)} days`;
            },
            inverse: true,
            displayByDefault: false,
            description: 'Days Inventory Outstanding, indicating the average number of days to sell inventory; lower values suggest efficient inventory management.',
      },
      'dpo': {
            name: 'Days Payables Outstanding',
            display_fn: (value: unknown) => {
                  const n = coerceNumber(value);
                  return n === null ? 'N/A' : `${n.toFixed(1)} days`;
            },
            inverse: false,
            displayByDefault: false,
            description: 'Days Payables Outstanding, measuring the average number of days to pay suppliers; higher values can improve cash flow but may strain supplier relationships.',
      },
      'revenue_per_employee': {
            name: 'Revenue per Employee',
            display_fn: formatCurrency,
            inverse: false,
            displayByDefault: false,
            description: 'Revenue per Employee, measuring productivity by calculating revenue generated per employee; higher values suggest better workforce efficiency.',
      },
      'net_debt': {
            name: 'Net Debt',
            display_fn: formatCurrency,
            inverse: null,
            displayByDefault: true,
            description: 'Net Debt, calculated as total debt minus cash and cash equivalents; lower values indicate a stronger balance sheet.',
      },
      'net_debt_to_ebitda_ttm': {
            name: 'Net Debt to EBITDA',
            display_fn: (value: unknown) => {
                  const n = coerceNumber(value);
                  return n === null ? 'N/A' : n.toFixed(2);
            },
            inverse: true,
            displayByDefault: true,
            description: 'Net Debt to EBITDA ratio, assessing leverage by comparing net debt to earnings; lower values suggest better debt management.',
      },
      'interest_coverage_ttm': {
            name: 'Interest Coverage Ratio',
            display_fn: formatRatio,
            inverse: false,
            displayByDefault: true,
            description: 'Interest Coverage Ratio, measuring ability to meet interest obligations; higher values indicate stronger financial health.',
      },
      'current_ratio': {
            name: 'Current Ratio',
            display_fn: formatRatio,
            inverse: false,
            displayByDefault: true,
            description: 'Current Ratio, assessing short-term liquidity by comparing current assets to current liabilities; higher values suggest better ability to cover short-term obligations.',
      },
      'quick_ratio': {
            name: 'Quick Ratio',
            display_fn: formatRatio,
            inverse: false,
            displayByDefault: false,
            description: 'Quick Ratio, measuring immediate liquidity by excluding inventory from current assets; higher values indicate better short-term financial health.',
      },
      'cash_ratio': {
            name: 'Cash Ratio',
            display_fn: formatRatio,
            inverse: false,
            displayByDefault: false,
            description: 'Cash Ratio, evaluating liquidity by comparing cash and cash equivalents to current liabilities; higher values suggest strong ability to cover short-term obligations with cash.',
      },
      'debt_to_equity': {
            name: 'Debt to Equity',
            display_fn: formatPercentage,
            inverse: true,
            displayByDefault: false,
            description: 'Debt to Equity, assessing financial leverage by comparing total debt to shareholder equity; lower values indicate a more conservative capital structure.',
      },
      'debt_to_assets': {
            name: 'Debt to Assets',
            display_fn: formatPercentage,
            inverse: true,
            displayByDefault: false,
            description: 'Debt to Assets, measuring the proportion of assets financed by debt; lower values suggest a stronger balance sheet.',
      },
      // 'fixed_charge_coverage_ttm': {
      //       name: 'Fixed Charge Coverage Ratio',
      //       display_fn: formatRatio,
      //       inverse: false,
      //       displayByDefault: false,
      //       description: 'Fixed Charge Coverage Ratio, evaluating ability to cover fixed charges with earnings; higher values indicate better financial stability.',
      // },
      'altman_z_score': {
            name: 'Altman Z-Score',
            display_fn: (value: unknown) => {
                  const n = coerceNumber(value);
                  return n === null ? 'N/A' : `${n.toFixed(2)}`;
            },
            inverse: false,
            displayByDefault: false,
            description: 'Altman Z-Score, predicting bankruptcy risk based on financial ratios; higher values suggest lower risk of financial distress.',
      },
      // 'cash_runway_months': {
      //       name: 'Cash Runway (Months)',
      //       display_fn: (value: number | null) => value !== null ? `${value.toFixed(1)} months` : 'N/A',
      //       inverse: false,
      //       displayByDefault: false,
      //       description: 'Cash Runway, estimating the number of months a company can operate with its current cash reserves; higher values indicate better financial sustainability.',
      // },
      'roic': {
            name: 'Return on Invested Capital',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: false,
            description: 'Return on Invested Capital, measuring profitability relative to invested capital; higher values indicate efficient use of capital.',
      },
      'total_shareholder_yield_ttm': {
            name: 'Total Shareholder Yield',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: true,
            description: 'Total Shareholder Yield, combining dividends, share buybacks, and debt reduction as a percentage of market value; higher values suggest greater returns to shareholders.',
      },
      'share_count_change_yoy': {
            name: 'Share Count Change (YoY)',
            display_fn: formatPercentage,
            inverse: true,
            displayByDefault: true,
            description: 'Year-over-Year Share Count Change, measuring the percentage change in outstanding shares; lower values indicate less dilution for shareholders.',
      },
      'reinvestment_rate': {
            name: 'Reinvestment Rate',
            display_fn: formatPercentage,
            inverse: null,
            displayByDefault: false,
            description: 'Reinvestment Rate, indicating the proportion of earnings reinvested back into the business; reflects growth strategy.',
      },
      'fcf_per_share_growth_yoy': {
            name: 'FCF per Share Growth (YoY)',
            display_fn: formatPercentage,
            inverse: false,
            displayByDefault: false,
            description: 'Year-over-Year Free Cash Flow per Share Growth, measuring annual increase in free cash flow on a per-share basis; higher values indicate improved cash generation for shareholders.',
      },
};