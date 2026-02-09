import { Stock, StockHistoryPoint, NewsItem, MarketInstrument, EconomicEvent, RateProbability } from '../types';
import { CONFIG } from '../config';

// --- Stocks Data ---
const SYMBOLS = [
  { s: 'AAPL', n: 'Apple Inc.' },
  { s: 'MSFT', n: 'Microsoft Corp.' },
  { s: 'GOOGL', n: 'Alphabet Inc.' },
  { s: 'AMZN', n: 'Amazon.com Inc.' },
  { s: 'TSLA', n: 'Tesla Inc.' },
  { s: 'NVDA', n: 'NVIDIA Corp.' },
  { s: 'JPM', n: 'JPMorgan Chase' },
  { s: 'V', n: 'Visa Inc.' },
];

export const generateHistory = (symbol: string, days: number = 90): StockHistoryPoint[] => {
  const history: StockHistoryPoint[] = [];
  let price = Math.random() * 500 + 50; 
  const now = new Date();
  
  for (let i = days; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    const change = (Math.random() - 0.5) * (price * 0.05);
    price += change;
    price = Math.max(1, price); 
    history.push({
      date: date.toISOString().split('T')[0],
      price: parseFloat(price.toFixed(2)),
      volume: Math.floor(Math.random() * 1000000) + 50000,
    });
  }
  return history;
};

export const generateStocks = (): Stock[] => {
  return SYMBOLS.map(sym => {
    const history = generateHistory(sym.s);
    const lastPrice = history[history.length - 1].price;
    const prevPrice = history[history.length - 2].price;
    const change = lastPrice - prevPrice;
    
    return {
      symbol: sym.s,
      name: sym.n,
      price: lastPrice,
      change: parseFloat(change.toFixed(2)),
      changePercent: parseFloat(((change / prevPrice) * 100).toFixed(2)),
      volume: history[history.length - 1].volume,
      history: history
    };
  });
};

export const updateStockPrice = (stock: Stock): Stock => {
  const volatility = 0.002; 
  const change = (Math.random() - 0.5) * (stock.price * volatility);
  const newPrice = stock.price + change;
  const newChange = stock.change + change;
  
  return {
    ...stock,
    price: parseFloat(newPrice.toFixed(2)),
    change: parseFloat(newChange.toFixed(2)),
    changePercent: parseFloat(((newChange / (stock.price - stock.change)) * 100).toFixed(2)),
  };
};

// --- News Data ---
const NEWS_SOURCES = ['Bloomberg', 'Reuters', 'CNBC', 'Financial Times', 'WSJ'];
const NEWS_TEMPLATES = [
  "reports quarterly earnings beat expectations.",
  "faces new regulatory scrutiny in EU.",
  "announces major acquisition strategy.",
  "CEO to step down effective immediately.",
  "stock surges on product announcement.",
  "hit by supply chain disruptions.",
  "analysts upgrade rating to 'Buy'.",
  "partners with AI startup for new venture."
];

export const generateNewsItem = (): NewsItem => {
  const symbol = SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)];
  const source = NEWS_SOURCES[Math.floor(Math.random() * NEWS_SOURCES.length)];
  const template = NEWS_TEMPLATES[Math.floor(Math.random() * NEWS_TEMPLATES.length)];
  
  return {
    id: Math.random().toString(36).substr(2, 9),
    title: `${symbol.s} ${template}`,
    source,
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    summary: `${symbol.n} has been in the news today as ${source} reports significant movements. Investors are advised to watch ${symbol.s} closely.`,
    sentiment: Math.random() > 0.6 ? 'positive' : Math.random() > 0.3 ? 'neutral' : 'negative',
    url: '#',
    category: 'stocks'
  };
};

// --- Macro Data ---

const MACRO_INSTRUMENTS: {s: string, n: string, c: MarketInstrument['category'], p: number}[] = [
  // Equity Futures
  { s: 'ES1', n: 'S&P 500 Future', c: 'future', p: 5240.50 },
  { s: 'NQ1', n: 'Nasdaq 100 Future', c: 'future', p: 18320.25 },
  { s: 'YM1', n: 'Dow Jones Future', c: 'future', p: 39500.00 },
  { s: 'RTY1', n: 'Russell 2000 Future', c: 'future', p: 2050.10 },
  // Bonds
  { s: 'US10Y', n: 'US 10-Year Yield', c: 'bond', p: 4.25 },
  { s: 'US02Y', n: 'US 2-Year Yield', c: 'bond', p: 4.65 },
  { s: 'DE10Y', n: 'Germany 10Y Bund', c: 'bond', p: 2.35 },
  // FX
  { s: 'EURUSD', n: 'Euro / USD', c: 'fx', p: 1.0850 },
  { s: 'USDJPY', n: 'USD / JPY', c: 'fx', p: 151.20 },
  { s: 'GBPUSD', n: 'GBP / USD', c: 'fx', p: 1.2650 },
  // Spreads
  { s: 'HYOAS', n: 'US High Yield OAS', c: 'spread', p: 320 }, // basis points
  { s: 'IGOAS', n: 'US Inv Grade OAS', c: 'spread', p: 95 },
  // Emerging Markets (EMKT)
  { s: 'EEM', n: 'MSCI Emerging Mkts', c: 'em', p: 41.50 },
  { s: 'USDCNH', n: 'USD / Offshore Yuan', c: 'em', p: 7.2450 },
  { s: 'IBOV', n: 'Bovespa Index', c: 'em', p: 128500 },
];

export const generateMacroData = (): MarketInstrument[] => {
  return MACRO_INSTRUMENTS.map(inst => ({
    symbol: inst.s,
    name: inst.n,
    category: inst.c,
    price: inst.p,
    change: 0,
    changePercent: 0
  }));
};

// We no longer need updateMacroInstrument since we're fetching from backend
// Instead, we'll just return the instrument unchanged
export const updateMacroInstrument = (inst: MarketInstrument): MarketInstrument => {
  // Return the instrument as-is since we're getting fresh data from backend
  return inst;
};

// --- Economic Data (ECST) ---

export const generateEconomicEvents = async (): Promise<EconomicEvent[]> => {
  try {
    const response = await fetch(`${CONFIG.BACKEND_API_BASE}/api/calendar`);
    if (!response.ok) {
      throw new Error(`Calendar API error: ${response.status} ${response.statusText}`);
    }
    const data = await response.json();

    // Map backend fields to EconomicEvent format as per requirements
    // Backend API returns: time, ctry, event, act, fcst
    return data.map((event: any) => ({
      id: event.id || event.event_id || Math.random().toString(36).substr(2, 9),
      time: event.time || '--:--',
      country: event.ctry || event.country || 'N/A',
      event: event.event || event.event_name || event.title || 'Economic Event',
      actual: event.act || event.actual || event.actual_value || '-',
      forecast: event.fcst || event.forecast || event.forecast_value || '-',
      previous: event.previous || event.previous_value || '-',
      impact: event.impact || event.impact_level || 'medium'
    }));
  } catch (error) {
    console.warn('Failed to fetch economic events from backend, using mock data:', error);
    // Return mock data if the API call fails
    return [
      { id: '1', time: '08:30', country: 'US', event: 'Non-Farm Payrolls', actual: '275K', forecast: '200K', previous: '229K', impact: 'high' },
      { id: '2', time: '08:30', country: 'US', event: 'Unemployment Rate', actual: '3.9%', forecast: '3.7%', previous: '3.7%', impact: 'high' },
      { id: '3', time: '10:00', country: 'US', event: 'ISM Manufacturing PMI', actual: '47.8', forecast: '49.5', previous: '49.1', impact: 'medium' },
      { id: '4', time: '14:00', country: 'US', event: 'Fed Beige Book', actual: '-', forecast: '-', previous: '-', impact: 'medium' },
      { id: '5', time: '02:00', country: 'CN', event: 'Caixin Services PMI', actual: '52.5', forecast: '52.9', previous: '52.7', impact: 'medium' },
      { id: '6', time: '04:00', country: 'EU', event: 'CPI YoY', actual: '2.6%', forecast: '2.5%', previous: '2.8%', impact: 'high' },
    ];
  }
};

// --- Interest Rate Probabilities (FEDWATCH) ---
export const generateRateProbs = (): RateProbability[] => {
  return [
    { meeting: 'May 2025', hike: 2.5, hold: 95.5, cut: 2.0 },
    { meeting: 'Jun 2025', hike: 1.0, hold: 45.0, cut: 54.0 },
    { meeting: 'Jul 2025', hike: 0.0, hold: 25.0, cut: 75.0 },
  ];
};