'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

// --- Helpers ---

const formatCurrency = (value: number) => {
  if (value >= 1e9) {
    return `$${(value / 1e9).toFixed(2)}B`;
  }
  if (value >= 1e6) {
    return `$${(value / 1e6).toFixed(0)}M`;
  }
  return `$${value}`;
};

const getStatus = (actual: number | null | undefined, estimated: number) => {
  if (actual === null || actual === undefined) {
    return { diff: null, percentChange: null, status: 'Estimated', color: '#64748b' };
  }

  const diff = actual - estimated;
  // Prevent division by zero
  const percentChange = estimated !== 0 ? (diff / estimated) * 100 : 0;
  const absPercent = Math.abs(percentChange);

  let status = 'In-Line';
  let color = '#3b82f6'; // Blue for In-Line

  if (absPercent >= 3) {
    if (diff > 0) {
      status = 'Beat';
      color = '#10b981'; // Emerald-500
    } else {
      status = 'Miss';
      color = '#f43f5e'; // Rose-500
    }
  }

  return { diff, percentChange, status, color };
};

// --- Custom Components for Graph ---

const CustomizedDot = (props: any) => {
  const { cx, cy, payload, metric } = props;
  
  if (!cx || !cy) return null;

  const actual = payload[metric];
  
  // Do not render dot if actual data is missing
  if (actual === null || actual === undefined) return null;

  const estimated = payload[`${metric}_estimated`];
  const { color } = getStatus(actual, estimated);

  return (
    <circle cx={cx} cy={cy} r={4} stroke={color} strokeWidth={2} fill="#0c0e15" />
  );
};

const CustomizedActiveDot = (props: any) => {
  const { cx, cy, payload, metric } = props;
  
  if (!cx || !cy) return null;

  const actual = payload[metric];
  
  // Do not render dot if actual data is missing
  if (actual === null || actual === undefined) return null;

  const estimated = payload[`${metric}_estimated`];
  const { color } = getStatus(actual, estimated);

  return (
    <g>
        {/* Outer Glow/Halo */}
        <circle cx={cx} cy={cy} r={10} fill={color} fillOpacity={0.2} />
        {/* Main Active Dot */}
        <circle cx={cx} cy={cy} r={6} fill={color} stroke="#0c0e15" strokeWidth={2} />
    </g>
  );
};

const CustomTooltip = ({ active, payload, label, type }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    const metricKey = type === 'number' ? 'eps' : 'revenue';
    const actual = data[metricKey];
    const estimated = data[`${metricKey}_estimated`];

    const { diff, percentChange, status, color } = getStatus(actual, estimated);

    let diffText = null;
    if (diff !== null && percentChange !== null) {
        const diffValueStr = type === 'currency' ? formatCurrency(Math.abs(diff)) : `$${Math.abs(diff).toFixed(2)}`;
        let percentStr = 'N/A';
        if (estimated !== 0) {
            percentStr = `${percentChange.toFixed(2)}%`;
        }

        diffText = `Diff: ${diff >= 0 ? '+' : '-'}${diffValueStr} (${percentStr}) ${status}`;
    }

    // Sort payload to ensure Actual appears before Estimated
    const sortedPayload = [...payload].sort((a: any, b: any) => {
      const aKey = a.dataKey || '';
      const bKey = b.dataKey || '';
      const isAEst = aKey.includes('estimated');
      const isBEst = bKey.includes('estimated');
      
      if (isAEst && !isBEst) return 1;
      if (!isAEst && isBEst) return -1;
      return 0;
    });

    return (
      <div className="bg-[#111218] border border-gray-700 p-3 rounded-lg shadow-xl text-sm z-50">
        <p className="text-gray-300 font-bold mb-2 font-mono text-xs">{label}</p>
        
        {sortedPayload.map((entry: any, index: number) => (
          <div key={index} className="flex items-center gap-2 mb-1">
            <div
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-gray-400 capitalize text-xs">
              {entry.dataKey === 'eps' ? 'EPS' : 
               entry.dataKey === 'eps_estimated' ? 'EPS Est.' :
               entry.dataKey === 'revenue' ? 'Rev' : 
               entry.dataKey === 'revenue_estimated' ? 'Rev Est.' : entry.name}:
            </span>
            <span className="text-white font-mono text-xs">
              {type === 'currency' 
                ? formatCurrency(entry.value)
                : `$${Number(entry.value).toFixed(2)}`}
            </span>
          </div>
        ))}

        {diffText && (
            <div className="mt-2 pt-2 border-t border-gray-800 flex items-center gap-2 text-xs">
                <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: color }}></div>
                <span className="font-bold uppercase" style={{ color: color }}>
                    {diffText}
                </span>
            </div>
        )}
        {!diffText && (
             <div className="mt-2 pt-2 border-t border-gray-800 flex items-center gap-2">
                <span className="text-gray-500 italic text-xs">
                    Future Estimate
                </span>
            </div>
        )}
      </div>
    );
  }
  return null;
};

interface EarningsGraphProps {
    data: any[];
    metric: 'eps' | 'revenue';
}

export const EarningsGraph: React.FC<EarningsGraphProps> = ({ data, metric }) => {
  const isCurrency = metric === 'revenue';
  const estimatedKey = `${metric}_estimated`;

  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
        >
          <CartesianGrid 
            strokeDasharray="3 3" 
            vertical={false} 
            stroke="#1f2937" 
          />
          <XAxis 
            dataKey="name" 
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#6b7280', fontSize: 10, fontFamily: 'monospace' }}
            dy={10}
            padding={{ left: 10, right: 10 }}
            interval="preserveStartEnd"
          />
          <YAxis 
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#6b7280', fontSize: 10, fontFamily: 'monospace' }}
            tickFormatter={isCurrency ? formatCurrency : (value) => `$${value.toFixed(2)}`}
          />
          <Tooltip content={<CustomTooltip type={isCurrency ? 'currency' : 'number'} />} cursor={{ stroke: 'rgba(255,255,255,0.1)', strokeWidth: 1 }} />
          <ReferenceLine y={0} stroke="#374151" />
          
          {/* Render Estimated FIRST so it appears behind Actual */}
          <Line 
            type="monotone" 
            dataKey={estimatedKey}  
            name="Estimated"
            stroke="#64748b" 
            strokeWidth={0}
            dot={{ r: 4, fill: '#121926', stroke: '#64748b', strokeWidth: 2 }}
            activeDot={{ r: 6, fill: '#64748b', strokeWidth: 4 }}
            legendType="circle"
          />


          {/* Render Actual LAST so it appears in front */}
          <Line 
            type="monotone" 
            dataKey={metric} 
            name="Actual"
            stroke="#3b82f6" 
            strokeWidth={3}
            dot={<CustomizedDot metric={metric} />}
            activeDot={<CustomizedActiveDot metric={metric} />}
            connectNulls={false} 
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};