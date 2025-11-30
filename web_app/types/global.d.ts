declare global {
    type StockProfile = {
        tic: string;
        name: string;
        exchange: string;
        sector: string;
        industry: string;
    };
}

export {};