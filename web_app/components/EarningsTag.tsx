'use client';

interface EarningsTagProps {
  label: string;
  description: string;
  className?: string;
}

export const EarningsTag: React.FC<EarningsTagProps> = ({ label, description, className = '' }) => (
  <div className="group relative flex flex-col items-center cursor-help">
    <span className={`px-2 py-1 text-[10px] uppercase tracking-wider font-bold rounded border transition-colors ${className}`}>
      {label}
    </span>
    {/* Tooltip */}
    <div className="absolute bottom-full mb-2 hidden group-hover:flex flex-col items-center w-56 z-50 pointer-events-none animate-slide-up-fade" style={{ animationDuration: '0.2s' }}>
      <div className="bg-[#1f2937] text-gray-200 text-xs p-3 rounded-lg shadow-xl border border-gray-700 text-left leading-relaxed relative">
        {description}
        {/* Triangle arrow */}
        <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-2 h-2 rotate-45 bg-[#1f2937] border-b border-r border-gray-700"></div>
      </div>
    </div>
  </div>
);
