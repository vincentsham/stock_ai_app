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
import { Earnings } from '@/types';
import { coerceNumber } from '@/lib/utils';

// --- Helpers ---

const formatPercent = (value: unknown) => {
  const n = coerceNumber(value);
  if (n === null || typeof n !== 'number' || isNaN(n)) {
    return 'N/A';
  }
  const sign = n > 0 ? '+' : '';
  return `${sign}${n.toFixed(2)}%`;
};

// --- Custom Components ---


interface GrowthDotPayload {
  [key: string]: number;
}
interface CustomizedDotProps {
    cx?: number;
    cy?: number;
    payload: GrowthDotPayload;
    metric: string;
}

const CustomizedDot = (props: CustomizedDotProps) => {
  const { cx, cy, payload, metric } = props;
  if (!cx || !cy) return null;
  const value = payload[metric];
  if (value === null || value === undefined) return null;
  const color = value >= 0 ? '#10b981' : '#f43f5e';
  return (
    <circle cx={cx} cy={cy} r={4} stroke={color} strokeWidth={2} fill="#0c0e15" />
  );
};

const CustomizedActiveDot = (props: CustomizedDotProps) => {
  const { cx, cy, payload, metric } = props;
  if (!cx || !cy) return null;
  const value = payload[metric];
  if (value === null || value === undefined) return null;
  const color = value >= 0 ? '#10b981' : '#f43f5e';
  return (
    <g>
        <circle cx={cx} cy={cy} r={10} fill={color} fillOpacity={0.2} />
        <circle cx={cx} cy={cy} r={6} fill={color} stroke="#0c0e15" strokeWidth={2} />
    </g>
  );
};

interface GrowthTooltipEntry {
  name: string;
  value: number;
}
interface CustomTooltipProps {
    active?: boolean;
    payload?: GrowthTooltipEntry[];
    label?: string;
}

const CustomTooltip = ({ active, payload, label }: CustomTooltipProps) => {
  if (active && payload && payload.length) {
    const entry = payload[0];
    const value = entry.value;
    const color = value >= 0 ? '#10b981' : '#f43f5e';

    return (
      <div className="bg-[#111218] border border-gray-700 p-3 rounded-lg shadow-xl text-sm z-50">
        <p className="text-gray-300 font-bold mb-2 font-mono text-xs">{label}</p>
        
        <div className="flex items-center gap-2 mb-1">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
            <span className="text-gray-400 capitalize text-xs">
               {entry.name}:
            </span>
            <span className="font-mono text-xs font-bold" style={{ color: color }}>
              {value !== null ? formatPercent(value) : 'N/A'}
            </span>
        </div>
      </div>
    );
  }
  return null;
};

interface EarningsGrowthGraphProps {
    data: Earnings[];
    metric: 'eps' | 'revenue';
    type: 'growth' | 'acceleration';
}

export const EarningsGrowthGraph: React.FC<EarningsGrowthGraphProps> = ({ data, metric, type }) => {
  const gradientId = `growthGradient_${metric}`;
  const keyName = `${metric}_yoy_${type}`;

  // Calculate gradient offset
  const dataValues = data
    .map((d) => Number(d[keyName as keyof Earnings]))
    .filter((v) => !isNaN(v));

  const hasData = dataValues.length > 0;
  const dataMax = hasData ? Math.max(...dataValues) : 0;
  const dataMin = hasData ? Math.min(...dataValues) : 0;

  let off = 0.5;
  if (hasData) {
    if (dataMax <= 0) {
      off = 0;
    } else if (dataMin >= 0) {
      off = 1;
    } else if (dataMax - dataMin !== 0) {
      off = dataMax / (dataMax - dataMin);
    }
  }

  const transitionPadding = 0.02;
  const lowerWhiteStop = Math.max(0, off - transitionPadding);
  const upperWhiteStop = Math.min(1, off + transitionPadding);

  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={0}>
        <LineChart
          data={data}
          margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
        >
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor="#10b981" stopOpacity={1} />
              <stop offset={lowerWhiteStop} stopColor="#ffffff" stopOpacity={0.5} />
              <stop offset={upperWhiteStop} stopColor="#ffffff" stopOpacity={0.5} />
              <stop offset="1" stopColor="#f43f5e" stopOpacity={1} />
            </linearGradient>
          </defs>
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
            tickFormatter={(value) => {
              const n = coerceNumber(value);
              if (n === null || typeof n !== 'number' || isNaN(n)) {
                return '';
              }
              return `${n.toFixed(1)}%`;
            }}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'rgba(255,255,255,0.1)', strokeWidth: 1 }} />
          <ReferenceLine y={0} stroke="#374151" />
          
          <Line 
            type="monotone" 
            dataKey={keyName} 
            name={type === "growth" ? "YoY Growth" : "YoY Acceleration"}
            stroke={`url(#${gradientId})`} 
            strokeWidth={3}
            dot={<CustomizedDot metric={keyName} payload={{}} />}
            activeDot={<CustomizedActiveDot metric={keyName} payload={{}} />}
            connectNulls={false} 
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};




export const EarningsGrowthLegend: React.FC = () => {
  return (
    <div className="flex gap-4 text-[10px] uppercase font-bold tracking-wider bg-[#111218] px-3 py-2 rounded-lg border border-gray-800 w-full justify-center md:justify-end">  
      <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full border-2 border-[#10b981] bg-transparent"></div>
          <span className="text-gray-400">Positive</span>
      </div>
      <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full border-2 border-[#f43f5e] bg-transparent"></div>
          <span className="text-gray-400">Negative</span>
      </div>
    </div>
  );
};