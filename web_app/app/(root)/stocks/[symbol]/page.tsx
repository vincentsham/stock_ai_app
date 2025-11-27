import { 
    SYMBOL_INFO_WIDGET_CONFIG,
    SYMBOL_CHART_WIDGET_CONFIG
 } from '@/lib/tradingview/configs';
import TradingViewWidget from '@/components/TradingViewWidget';

interface PageParams {
    params: {
        symbol: string;
    };
}

const StockPage = async ({ params }: PageParams) => {
    const { symbol } = await params;
    const scriptUrl = `https://s3.tradingview.com/external-embedding/embed-widget-`;

    return (
        <div className="flex flex-col gap-6">
            <TradingViewWidget
                scriptUrl={`${scriptUrl}symbol-info.js`}
                config={SYMBOL_INFO_WIDGET_CONFIG(symbol, 150)}
                height={150}
            />

            <TradingViewWidget
                scriptUrl={`${scriptUrl}symbol-overview.js`}
                config={SYMBOL_CHART_WIDGET_CONFIG(symbol, 400)}
                height={400}
            />

        </div>
    )
}

export default StockPage
