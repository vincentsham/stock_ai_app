'use client';

import { useState } from 'react';
import { CatalystSection } from './CatalystSection';
import { EarningsSection } from './EarningsSection';
import { EarningsCallSection } from './EarningsCallSection';
import { AnalystSection } from './AnalystSection';
import { MetricsSection } from './MetricsSection';
import { Zap, DollarSign, Calendar, Users, BarChart3 } from 'lucide-react';

export const CustomSection: React.FC<{ tic: string }> = ({ tic }) => {
  const [activeTab, setActiveTab] = useState<'catalysts' | 'earnings' | 'earningsCalls' | 'analysts' | 'metrics'>('catalysts');

  return (
    <div className="w-full bg-[#0c0e15] border border-gray-800 rounded-xl p-6 pt-1">
      {/* Tab Navigation */}
      <div className="flex border-b border-gray-800 mb-6 overflow-x-auto">
        <button
          onClick={() => setActiveTab('catalysts')}
          className={`px-4 py-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'catalysts'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-gray-400 hover:text-gray-200'
          }`}
        >
          <Zap size={16} />
          Catalysts
        </button>
        <button
          onClick={() => setActiveTab('earnings')}
          className={`px-4 py-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'earnings'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-gray-400 hover:text-gray-200'
          }`}
        >
          <DollarSign size={16} />
          Earnings
        </button>
        <button
          onClick={() => setActiveTab('earningsCalls')}
          className={`px-4 py-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'earningsCalls'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-gray-400 hover:text-gray-200'
          }`}
        >
          <Calendar size={16} />
          Earnings Calls
        </button>
        <button
          onClick={() => setActiveTab('analysts')}
          className={`px-4 py-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'analysts'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-gray-400 hover:text-gray-200'
          }`}
        >
          <Users size={16} />
          Analysts
        </button>
        <button
          onClick={() => setActiveTab('metrics')}
          className={`px-4 py-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'metrics'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-gray-400 hover:text-gray-200'
          }`}
        >
          <BarChart3 size={16} />
          Metrics
        </button>
      </div>

      {/* Content Area */}
      <div>
        {activeTab === 'catalysts' && <CatalystSection tic={tic} />}
        {activeTab === 'earnings' && <EarningsSection tic={tic} />}
        {activeTab === 'earningsCalls' && <EarningsCallSection tic={tic} />}
        {activeTab === 'analysts' && <AnalystSection />}
        {activeTab === 'metrics' && <MetricsSection />}
      </div>
    </div>
  );
};