import { Plus } from "lucide-react";


export const StockEmptyCard: React.FC = () => {
    const handleClick = () => {
        // Dispatch a custom event
        window.dispatchEvent(new CustomEvent('focus-search'));
    };
    return (
        <div 
            onClick={handleClick}
            className="w-[200px] border-2 border-dashed border-gray-500 rounded-lg flex flex-col items-center justify-center space-y-4 flex-shrink-0 cursor-pointer hover:bg-gray-500/10 hover:border-gray-400 transition-all group h-32"
        >
                <div className="w-12 h-12 rounded-full border border-gray-500 flex items-center justify-center text-gray-500 group-hover:text-gray-400 group-hover:border-gray-400 transition-all shadow-inner">
                <Plus size={24} />
                </div>
                <div className='text-center'>
                <p className="text-gray-500 text-[10px] font-bold uppercase tracking-widest text-center px-1  group-hover:text-gray-200 transition-colors">Add to Compare</p>
                <p className="text-[8px] text-gray-500 font-medium transition-colors group-hover:text-gray-200 transition-colors">Search by name or ticker</p>
                </div>
        </div>
    );
}
;