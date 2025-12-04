'use client';

import { Users } from 'lucide-react';

export const AnalystsSection = () => {
  return (
    <div className="min-h-[400px] flex flex-col items-center justify-center text-gray-500 animate-slide-up-fade" style={{ animationDuration: '0.4s' }}>
      <div className="w-16 h-16 bg-gray-800/50 rounded-full flex items-center justify-center mb-4 border border-gray-700">
        <Users size={32} className="text-gray-400" />
      </div>
      <h3 className="text-xl font-bold text-gray-300 mb-2">Analyst Ratings</h3>
      <p className="max-w-md text-center text-sm">
        Consensus ratings, price targets, and analyst coverage breakdown will be displayed here.
      </p>
    </div>
  );
};