
'use client';

import{ useMemo } from 'react';
import {
    ComposedChart,
    Line,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from 'recharts';
import { AnalystAnalysis } from '../types';


const formatCurrency = (value: number | null) => {
    if (value === null || value === undefined) return 'N/A';
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
};

const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
        const originalData = payload[0].payload;
        
        // Format date nicer for the tooltip header
        const dateObj = new Date(label);
        const dateStr = dateObj.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
        });
        
        return (
        <div className="bg-[#111218] border border-gray-700 p-3 rounded-lg shadow-xl text-sm z-50 min-w-[180px]">
            <p className="font-bold text-gray-200 mb-2 font-mono text-xs pb-2 border-b border-gray-800">{dateStr}</p>
            
            <div className="space-y-1.5">
            {/* Price */}
            <div className="flex justify-between items-center gap-4">
                <div className="flex items-center text-blue-400 text-xs font-semibold">
                <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mr-2"></div>
                Price
                </div>
                <span className="text-gray-100 font-mono text-xs">{formatCurrency(originalData.close)}</span>
            </div>

            {/* High (Green) */}
            <div className="flex justify-between items-center gap-4">
                <div className="flex items-center text-emerald-400 text-xs">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-2"></div>
                High
                </div>
                <span className="text-gray-300 font-mono text-xs">{formatCurrency(originalData.pt_high)}</span>
            </div>

            {/* Median */}
            <div className="flex justify-between items-center gap-4">
                <div className="flex items-center text-amber-400 text-xs">
                <div className="w-1.5 h-1.5 rounded-full bg-amber-500 mr-2"></div>
                Median
                </div>
                <span className="text-gray-200 font-mono text-xs">{formatCurrency(originalData.pt_median)}</span>
            </div>

            {/* Low (Red) */}
            <div className="flex justify-between items-center gap-4">
                <div className="flex items-center text-rose-400 text-xs">
                <div className="w-1.5 h-1.5 rounded-full bg-rose-500 mr-2"></div>
                Low
                </div>
                <span className="text-gray-300 font-mono text-xs">{formatCurrency(originalData.pt_low)}</span>
            </div>
            </div>
        </div>
        );
    }
    return null;
};

export const AnalystPTGraph: React.FC<{ data: AnalystAnalysis[] }> = ({ data }) => {
    // Process data: reverse to be chronological (Oldest -> Newest) and add ranges
    const chartData = useMemo(() => {
        // We assume incoming data is reverse chronological (newest first), so we reverse it for the chart.
        return [...data].reverse().map(item => ({
        ...item,
        // Create array ranges for the Area charts
        rangeLowHigh: [item.pt_low, item.pt_high],
        rangeConsensus: [item.pt_p25, item.pt_p75]
        }));
    }, [data]);

    // Calculate ticks: finding the first data point for each month to use as a label
    const xAxisTicks = useMemo(() => {
        const ticks: string[] = [];
        let lastMonth: string | null = null;

        chartData.forEach(item => {
        // item.date format is "YYYY-MM-DD". Extract "YYYY-MM" to check for month changes
        const currentMonth = item.date.substring(0, 7);
        
        if (currentMonth !== lastMonth) {
            ticks.push(item.date);
            lastMonth = currentMonth;
        }
        });
        return ticks.length > 1 ? ticks.slice(1) : ticks; 
    }, [chartData]);

    // Custom Formatter: "2025" for Jan, "Feb" otherwise
    const formatXAxis = (dateStr: string) => {
        // dateStr is "YYYY-MM-DD"
        const year = dateStr.substring(0, 4);
        const month = dateStr.substring(5, 7);
        
        if (month === '01') return year;
        
        const months: Record<string, string> = {
        '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun',
        '07': 'Jul', '08': 'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
        };
        return months[month] || month;
  };

  return (
    <div className="w-full h-[550px] flex flex-col">
       {/* Graph Header Area with Title & Legend */}
       <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 mb-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            Price Target Distribution
          </h2>
        </div>

        {/* Legend */}
        <div className="flex flex-wrap gap-x-4 gap-y-2 text-[10px] uppercase font-bold tracking-wider px-3 py-2 rounded-lg border border-gray-800/50 bg-black/20 w-fit">
           <div className="flex items-center gap-1.5">
              {/* <div className="w-2 h-2 rounded-full bg-[#3b82f6]"></div> */}
              <div className="w-6 h-0.5 bg-blue-500"></div>
              <span className="text-gray-400">Price</span>
           </div>
           <div className="flex items-center gap-1.5">
               {/* <div className="w-2 h-2 rounded-full bg-[#10b981]"></div> */}
               <div className="w-6 h-0.5 border-t-2 border-dashed border-[#10b981]"></div>
              <span className="text-gray-400">High</span>
           </div>
            <div className="flex items-center gap-1.5">
              {/* <div className="w-2 h-2 rounded-full bg-[#f59e0b]"></div> */}
              <div className="w-6 h-0.5 border-t-2 border-dashed border-yellow-500"></div>
              <span className="text-gray-400">Median</span>
           </div>
            <div className="flex items-center gap-1.5">
               {/* <div className="w-2 h-2 rounded-full bg-[#f43f5e]"></div> */}
               <div className="w-6 h-0.5 border-t-2 border-dashed border-[#f43f5e]"></div>
              <span className="text-gray-400">Low</span>
           </div>
           <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 bg-[#6366f1ff]/40"></div>
              <span className="text-gray-400">Consensus</span>
           </div>
        </div>
      </div>

      <div className="flex-1 w-full min-h-0">
        <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
            data={chartData}
            margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
            >
            <defs>
                <linearGradient id="colorConsensus" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366f1ff" stopOpacity={0.4}/>
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0.1}/>
                </linearGradient>
                <linearGradient id="colorRange" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#94a3b8" stopOpacity={0.15}/>
                <stop offset="95%" stopColor="#94a3b8" stopOpacity={0.05}/>
                </linearGradient>
            </defs>
            
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} vertical={false} />
            
            <XAxis 
                dataKey="date" 
                axisLine={false}
                tickLine={false}
                tick={{ fill: '#6b7280', fontSize: 10, fontFamily: 'monospace' }}
                tickMargin={10}
                ticks={xAxisTicks}
                tickFormatter={formatXAxis}
                interval={0}
            />
            
            <YAxis 
                axisLine={false}
                tickLine={false}
                tick={{ fill: '#6b7280', fontSize: 10, fontFamily: 'monospace' }}
                tickFormatter={(val) => `$${val}`}
                domain={['auto', 'auto']}
            />
            
            <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'rgba(255,255,255,0.1)', strokeWidth: 1 }} />
            
            {/* Full Range Area (Low to High) */}
            <Area
                type="monotone"
                dataKey="rangeLowHigh"
                stroke="none"
                fill="url(#colorRange)"
                name="Analyst Range (Low-High)"
                legendType="none"
                tooltipType="none"
                isAnimationActive={false}
            />

            {/* Max Target Line - Dashed Emerald */}
            <Line
                type="monotone"
                dataKey="pt_high"
                stroke="#10b981"
                strokeWidth={1}
                strokeDasharray="5 5"
                dot={false}
                name="Max Target"
                isAnimationActive={false}
            />

            {/* Min Target Line - Dashed Rose */}
            <Line
                type="monotone"
                dataKey="pt_low"
                stroke="#f43f5e"
                strokeWidth={1}
                strokeDasharray="5 5"
                dot={false}
                name="Min Target"
                isAnimationActive={false}
            />

            {/* Consensus Range (25th to 75th) */}
            <Area
                type="monotone"
                dataKey="rangeConsensus"
                stroke="none"
                fill="url(#colorConsensus)"
                name="Consensus (25-75%)"
                legendType="rect"
                isAnimationActive={false}
            />

            {/* Median Prediction - Dashed Amber */}
            <Line
                type="monotone"
                dataKey="pt_median"
                stroke="#f59e0b"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                name="Analyst Median"
                isAnimationActive={false}
            />

            {/* Actual Stock Price - Solid Blue */}
            <Line
                type="monotone"
                dataKey="close"
                stroke="#3b82f6"
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 6, fill: "#3b82f6", stroke: "#000", strokeWidth: 2 }}
                name="Stock Price"
                animationDuration={1500}
            />

            </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
