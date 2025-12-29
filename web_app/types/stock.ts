// types/stock.ts
export type StockProfile = {
  tic: string;
  name: string;
  exchange: string;
  sector: string;
  industry: string;
  logo: string | null;
};

export type StockPrice = {
  tic: string;
  price: number;
  change: number;
  changePercent: number;
};
