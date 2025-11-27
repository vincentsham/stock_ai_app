export const SYMBOL_INFO_WIDGET_CONFIG = (symbol: string, height: number) => ({
    symbol: symbol.toUpperCase(),
    colorTheme: 'dark',
    isTransparent: true,
    locale: 'en',
    width: '100%',
    height: height,
});



export const SYMBOL_CHART_WIDGET_CONFIG = (symbol: string, height: number) => ({
    "lineWidth": 2,
    "lineType": 0,
    "chartType": "area",
    "showVolume": true,
    "fontColor": "rgb(106, 109, 120)",
    "gridLineColor": "rgba(242, 242, 242, 0.06)",
    "volumeUpColor": "rgba(34, 171, 148, 0.5)",
    "volumeDownColor": "rgba(247, 82, 95, 0.5)",
    "backgroundColor": "#0F0F0F",
    "widgetFontColor": "#DBDBDB",
    "upColor": "#22ab94",
    "downColor": "#f7525f",
    "borderUpColor": "#22ab94",
    "borderDownColor": "#f7525f",
    "wickUpColor": "#22ab94",
    "wickDownColor": "#f7525f",
    "colorTheme": "dark",
    "isTransparent": false,
    "locale": "en",
    "chartOnly": true,
    "scalePosition": "right",
    "scaleMode": "Normal",
    "fontFamily": "-apple-system, BlinkMacSystemFont, Trebuchet MS, Roboto, Ubuntu, sans-serif",
    "valuesTracking": "1",
    "changeMode": "price-and-percent",
    "symbols": [
        [
            symbol.toUpperCase()
        ]
    ],
    "dateRanges": [
        "1d|1",
        "1m|30",
        "3m|60",
        "12m|1D",
        "60m|1W",
        "all|1M"
    ],
    "fontSize": "10",
    "headerFontSize": "small",
    "autosize": true,
    "lineColor": "rgba(41, 98, 255, 1)",
    "topColor": "rgba(12, 50, 153, 0.24)",
    "bottomColor": "rgba(12, 50, 153, 0.24)",
    "width": "100%",
    "height": height,
    "noTimeScale": false,
    "hideDateRanges": false,
    "hideMarketStatus": false,
    "hideSymbolLogo": false
});

