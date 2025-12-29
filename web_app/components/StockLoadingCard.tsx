import { X, Loader2 } from 'lucide-react';



export const StockLoadingCard: React.FC<{ tic: string; onRemove?: (tic: string) => void; }> = ({ tic, onRemove }) => {
    return (
        <div className="w-[200px] h-32 bg-[#111218] rounded-xl border border-gray-800 shadow-sm flex-shrink-0 flex flex-col overflow-hidden relative">
            <div className="p-3 h-full flex flex-col justify-between">
                <div className="flex justify-between items-start">
                    <div className="w-7 h-7 md:w-11 md:h-11 bg-gray-800 rounded-lg animate-pulse"></div>
                    <div className="h-4 w-12 bg-gray-800 rounded-full animate-pulse"></div>
                    {
                        onRemove && (
                            <button 
                                onClick={() => onRemove(tic)}
                                className="flex items-center gap-1 text-[8px] font-extrabold text-gray-300 bg-black/20 px-2 py-0.5 rounded-full hover:scale-[1.05] transition-transform cursor-pointer"
                            >
                                Remove <X size={8} strokeWidth={3} />
                            </button>
                        )
                    }


                </div>
                <div className="space-y-2">
                    <div className="h-5 w-16 bg-gray-800 rounded animate-pulse"></div>
                    <div className="h-3 w-24 bg-gray-800 rounded animate-pulse"></div>
                </div>
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <span className="text-xs text-gray-500 font-medium flex gap-1 items-center animate-pulse">
                        <Loader2 className="w-3 h-3 animate-spin" />
                        Loading {tic}...
                    </span>
                </div>
            </div>
        </div>
    );
};
