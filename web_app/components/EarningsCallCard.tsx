'use client';

import { useState } from 'react';
import { 
  ChevronDown, 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  Shield, 
  AlertTriangle, 
  Zap,
  MousePointer2,
  Target,
  PencilLine,
} from 'lucide-react';
import { EarningsCallAnalysis } from '@/types';

// --- Sub-components ---

const StatusBadge = ({ sentiment }: { sentiment: number }) => {
  if (sentiment === 1) {
    return (
      <span className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold tracking-wider flex items-center gap-1.5 shadow-[0_0_10px_-3px_rgba(16,185,129,0.3)]">
        <TrendingUp className="w-3.5 h-3.5" /> BULLISH
      </span>
    );
  }
  if (sentiment === -1) {
    return (
      <span className="px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-bold tracking-wider flex items-center gap-1.5 shadow-[0_0_10px_-3px_rgba(244,63,94,0.3)]">
        <TrendingDown className="w-3.5 h-3.5" /> BEARISH
      </span>
    );
  }
  return (
    <span className="px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-bold tracking-wider flex items-center gap-1.5">
      <Minus className="w-3.5 h-3.5" /> MIXED
    </span>
  );
};

const MetricIndicator = ({ label, value }: { label: string; value: number }) => {
  const isPositive = value === 1;
  const isNegative = value === -1;

  const textColor = isPositive
    ? 'text-emerald-400'
    : isNegative
      ? 'text-rose-400'
      : 'text-amber-400';

  const icon = isPositive
    ? <TrendingUp className="w-4 h-4" />
    : isNegative
      ? <TrendingDown className="w-4 h-4" />
      : <Minus className="w-4 h-4" />;

  const labelText = isPositive ? 'Positive' : isNegative ? 'Negative' : 'Neutral';

  return (
    <div className="flex flex-col items-center justify-center p-3 bg-[#0a0b10] rounded-lg border border-gray-800 hover:border-gray-700 transition-colors">
      <span className="text-xs uppercase text-gray-500 font-bold mb-1.5 tracking-wide">{label}</span>
      <div className={`flex items-center gap-1.5 font-bold ${textColor}`}>
        {icon}
        <span className="text-sm">{labelText}</span>
      </div>
    </div>
  );
};

interface BattleCardProps {
  title: string;
  icon: React.ElementType;
  type: 'risk' | 'mitigation';
  summary: string;
  tags: string[];
  subLabel: string;
  subValue: string;
}

const BattleCard: React.FC<BattleCardProps> = ({ title, icon: Icon, type, summary, tags, subLabel, subValue }) => {
  const isRisk = type === 'risk';
  const borderColor = isRisk ? 'border-rose-900/30' : 'border-blue-900/30';
  const bgColor = isRisk ? 'bg-rose-950/5' : 'bg-blue-950/5';
  const titleColor = isRisk ? 'text-rose-400' : 'text-blue-400';
  const tagBg = isRisk ? 'bg-rose-500/10 text-rose-300 border-rose-500/20' : 'bg-blue-500/10 text-blue-300 border-blue-500/20';
  const tagHover = isRisk 
    ? 'hover:bg-rose-500/20 hover:text-rose-200 hover:border-rose-500/40' 
    : 'hover:bg-blue-500/20 hover:text-blue-200 hover:border-blue-500/40';


  return (
    <div className={`flex-1 rounded-xl border ${borderColor} ${bgColor} overflow-hidden flex flex-col`}>
      <div className={`px-4 py-3 border-b ${borderColor} flex items-center justify-between bg-opacity-50 bg-black/20`}>
        <div className="flex items-center gap-2">
          <Icon className={`w-4 h-4 ${titleColor}`} />
          <h4 className={`text-sm font-bold uppercase tracking-wider ${titleColor}`}>{title}</h4>
        </div>
        <div className="flex items-center gap-2">
           <span className="text-xs text-gray-500 uppercase font-semibold">{subLabel}</span>
           <span className={`text-xs font-bold ${titleColor}`}>{subValue}</span>
        </div>
      </div>
      <div className="p-4 flex-1 flex flex-col">
        <p className="text-sm text-gray-400 leading-relaxed mb-4 flex-1">
          {summary}
        </p>
        <div className="flex flex-wrap gap-2 mt-auto">
          {tags.map((tag: string, i: number) => (
            <span key={i} className={`text-xs font-bold px-2.5 py-1 rounded border ${tagBg} transition-colors cursor-default ${tagHover}`}>
              {tag}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export const EarningsCallCard = ({ report }: { report: EarningsCallAnalysis }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Border color based on sentiment for the left accent
  const accentColor = report.sentiment === 1 ? 'border-l-emerald-500' 
                    : report.sentiment === -1 ? 'border-l-rose-500' 
                    : 'border-l-amber-500';

  const quarterLabel = `Q${report.calendar_quarter} ${report.calendar_year}`;
  
  // Interpret numeric values for display
  const riskImpactLabel = report.risk_impact == 1 ? 'High' : report.risk_impact == 0 ? 'Moderate' : 'Low';
  const mitigationEffectivenessLabel = report.mitigation_effectiveness == 1 ? 'Strong' : report.mitigation_effectiveness == 0 ? 'Moderate' : 'Weak';

  return (
    <div className={`bg-[#111218] rounded-xl border border-gray-800 overflow-hidden transition-all duration-300 mb-4 ${isExpanded ? 'shadow-xl shadow-black/50 ring-1 ring-gray-700' : 'hover:border-gray-700'}`}>
      
      {/* --- COLLAPSED HEADER (Clickable) --- */}
      <div 
        onClick={() => setIsExpanded(!isExpanded)}
        className={`p-5 cursor-pointer border-l-[3px] ${accentColor} flex flex-col gap-4 relative`}
      >
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-1.5">
              <h3 className="text-lg font-bold text-gray-100">{quarterLabel}</h3>
              <StatusBadge sentiment={report.sentiment} />
            </div>
            <p className="text-gray-500 text-xs uppercase tracking-widest font-semibold flex items-center gap-2">
               <span>{report.tic} EARNINGS REPORT</span>
               <span className="w-1 h-1 rounded-full bg-gray-600"></span>
               <span>{new Date(report.earnings_date).toLocaleDateString()}</span>
            </p>
          </div>
          <button className={`text-gray-500 hover:text-white transition-all duration-300 transform ${isExpanded ? 'rotate-180' : ''}`}>
             <ChevronDown className="w-5 h-5" />
          </button>
        </div>

        <p className="text-gray-300 text-sm leading-relaxed line-clamp-2">
          {report.past_summary}
        </p>

        <div className="flex flex-wrap gap-2">
          {report.performance_factors.slice(0, 4).map((factor, i) => (
            <span key={i} className="text-xs font-bold px-2.5 py-1 rounded bg-gray-800 text-gray-300 border border-gray-700 
            transition-colors cursor-default hover:bg-gray-700 hover:text-white hover:border-gray-600">
              {factor}
            </span>
          ))}
          {isExpanded? report.performance_factors.slice(4).map((factor, i) => (
            <span key={i} className="text-xs font-bold px-2.5 py-1 rounded bg-gray-800 text-gray-300 border border-gray-700 
            transition-colors cursor-default hover:bg-gray-700 hover:text-white hover:border-gray-600">
              {factor}
            </span>
          )) 
          : report.performance_factors.length > 4 && (
            <span className="text-xs font-bold px-2.5 py-1 rounded bg-gray-800 text-gray-500 border border-gray-700
             transition-colors cursor-default hover:bg-gray-700 hover:text-white hover:border-gray-600">
              +{report.performance_factors.length - 4} more
            </span>
          )}
        </div>
      </div>

      {/* --- EXPANDED DEEP DIVE --- */}
      {isExpanded && (
        <div className="border-t border-gray-800 bg-[#0c0d12] animate-slide-up-fade" style={{ animationDuration: '0.3s' }}>
          
          {/* Section 1: Guidance Grid */}
          <div className="p-6 border-b border-gray-800">
            <h4 className="text-xs font-bold text-gray-400 mb-4 flex items-center gap-2 uppercase tracking-wider">
              <MousePointer2 className="w-3.5 h-3.5 text-yellow-500" />
              Forward Guidance
            </h4>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
              <MetricIndicator label="Revenue Outlook" value={report.revenue_outlook} />
              <MetricIndicator label="Margin Outlook" value={report.margin_outlook} />
              <MetricIndicator label="Earnings Outlook" value={report.earnings_outlook} />
              <MetricIndicator label="Cashflow" value={report.cashflow_outlook} />
            </div>

            <div className="bg-gray-800/20 rounded-lg p-4 border border-gray-800 relative">
              <p className="text-sm text-gray-300 mb-4 pl-8 leading-relaxed">
                {report.future_summary}
              </p>
              <div className="flex items-center gap-2 flex-wrap pl-8">
                <span className="text-xs text-gray-500 uppercase font-bold mr-1">Growth Drivers:</span>
                {report.growth_drivers.map((driver, i) => (
                  <span key={i} className="text-xs font-bold px-2.5 py-1 rounded bg-emerald-900/20 text-emerald-400 border border-emerald-900/40  transition-colors cursor-default hover:bg-emerald-900/40 hover:text-emerald-300 hover:border-emerald-500/50">
                    {driver}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Section 2: The Battle (Risk vs Mitigation) */}
          <div className="p-6">
            <h4 className="text-xs font-bold text-gray-400 mb-4 flex items-center gap-2 uppercase tracking-wider">
              <PencilLine className="w-3.5 h-3.5 text-blue-500" />
              Strategic Analysis
            </h4>
            
            <div className="flex flex-col md:flex-row gap-4">
              {/* Risk Column */}
              <BattleCard 
                type="risk"
                title="Headwinds & Risks"
                icon={AlertTriangle}
                summary={report.risk_summary}
                tags={report.risk_factors}
                subLabel="Severity"
                subValue={riskImpactLabel}
              />

              {/* Mitigation Column */}
              <BattleCard 
                type="mitigation"
                title="Management Strategy"
                icon={Shield}
                summary={report.mitigation_summary}
                tags={report.mitigation_actions}
                subLabel="Efficacy"
                subValue={mitigationEffectivenessLabel}
              />
            </div>
          </div>

        </div>
      )}
    </div>
  );
};