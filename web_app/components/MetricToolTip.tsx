

import { HelpCircle } from 'lucide-react';
import { CATEGORY_TOOLTIP, OVERALL_TOOLTIP } from '@/lib/constants';


export const MetricInfoToolTip: React.FC<{ showOverall?: boolean; align?: 'left' | 'right'; side?: 'top' | 'bottom' }> = ({ showOverall = true, align = 'left', side = 'bottom' }) => {
    const alignClasses = align === 'right' ? 'right-0' : 'left-0';
    const sideClasses = side === 'top' 
        ? `bottom-full mb-2 origin-bottom-${align}` 
        : `top-full mt-2 origin-top-${align}`;

    return (
          <div className={`absolute ${sideClasses} ${alignClasses} w-64 p-3 bg-slate-900 border border-slate-700 rounded shadow-xl text-xs text-slate-300 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 pointer-events-none z-999`}>
            {CATEGORY_TOOLTIP}
            {showOverall && (
                <>
                    <div className="my-2 border-t border-slate-600"></div>
                    {OVERALL_TOOLTIP}
                </>
            )}
          </div>
    );
};
