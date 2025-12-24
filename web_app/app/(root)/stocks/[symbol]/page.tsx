import { 
    SYMBOL_INFO_WIDGET_CONFIG,
    SYMBOL_CHART_WIDGET_CONFIG
 } from '@/lib/tradingview/configs';
import TradingViewWidget from '@/components/TradingViewWidget';
import { CustomSection } from '@/components/CustomSection';
import StockRadarChart from '@/components/StockRadarChart';

interface PageParams {
    params: {
        symbol: string;
    };
}

const StockPage = async ({ params }: PageParams) => {
    const { symbol } = await params;
    const scriptUrl = `https://s3.tradingview.com/external-embedding/embed-widget-`;

    return (
        <div className="flex flex-col gap-6 mx-0 md:mx-10 lg:mx-20 xl:mx-40">
            <TradingViewWidget
            scriptUrl={`${scriptUrl}symbol-info.js`}
            config={SYMBOL_INFO_WIDGET_CONFIG(symbol, 150)}
            height={150}
            />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-stretch">
                <div className="h-full lg:col-span-2 min-h-[400px]">
                    <TradingViewWidget
                        scriptUrl={`${scriptUrl}symbol-overview.js`}
                        config={SYMBOL_CHART_WIDGET_CONFIG(symbol, 400)}
                        height={400}
                    />
                </div>

                <div className="h-full lg:col-span-1 min-h-[400px]">
                    <StockRadarChart
                        tic={symbol}
                        height={400}
                        className="w-full"
                    />
                </div>
            </div>

            <CustomSection 
            tic={symbol} 
            />
        </div>
    )
}

export default StockPage