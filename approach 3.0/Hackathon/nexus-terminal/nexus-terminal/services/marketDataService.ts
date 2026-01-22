
import { StockQuote, OHLCPoint, NewsItem } from '../types';
import { CONFIG } from '../config';

/**
 * Type definition for the backend API response
 */
interface BackendAsset {
  symbol: string;
  friendly_name: string;
  display_price: number;
  return_24h: number | null;
  asset_class: string;
  status: string;
}

/**
 * FETCH MARKET DATA FROM LOCAL BACKEND
 */
export const fetchMarketData = async (): Promise<BackendAsset[]> => {
  const url = `${CONFIG.BACKEND_API_BASE}/api/market`;
  const res = await fetch(url);

  if (!res.ok) {
    throw new Error(`Market data fetch failed: ${res.status} ${res.statusText}`);
  }

  const data = await res.json();
  if (!Array.isArray(data)) {
    throw new Error('Invalid response format: expected array of assets');
  }

  return data;
};

/**
 * Converts BackendAsset to MarketInstrument format for MacroDashboard
 */
export const convertToMarketInstrument = (asset: BackendAsset): MarketInstrument => {
  // Map asset_class to category for proper display
  let category: 'future' | 'bond' | 'fx' | 'spread' | 'em' = 'future'; // default

  switch (asset.asset_class?.toLowerCase()) {
    case 'bonds':
    case 'bond':
      category = 'bond';
      break;
    case 'fx':
    case 'forex':
      category = 'fx';
      break;
    case 'commodity':
    case 'commodities':
      category = 'em'; // commodities often fall under emerging markets category
      break;
    case 'index':
    case 'indices':
      category = 'future';
      break;
    case 'crypto':
    case 'cryptocurrency':
      category = 'em';
      break;
    case 'spread':
      category = 'spread';
      break;
    default:
      category = 'future'; // default fallback
  }

  // Calculate change based on return_24h as percentage of price
  const percent_change = (asset.return_24h !== null && asset.return_24h !== undefined && !isNaN(asset.return_24h)) ? asset.return_24h : 0;
  const change = asset.display_price * (percent_change / 100);

  return {
    symbol: asset.symbol,
    name: asset.friendly_name || asset.symbol,
    category,
    price: asset.display_price,
    change,
    changePercent: percent_change
  };
};

/**
 * FETCH QUOTE (FROM LOCAL BACKEND)
 * Maps backend data to StockQuote format
 */
export const fetchQuote = async (symbol: string): Promise<StockQuote> => {
  const marketData = await fetchMarketData();
  const asset = marketData.find(a => a.symbol === symbol);

  if (!asset) {
    throw new Error(`Asset with symbol '${symbol}' not found in market data`);
  }

  // Map backend fields to StockQuote format
  const name = asset.friendly_name || asset.symbol;
  const price = asset.display_price;
  const return24h = asset.return_24h;

  // Handle NaN or null values for returns
  const percent_change = (return24h !== null && return24h !== undefined && !isNaN(return24h)) ? return24h : 0;
  // Calculate change based on percentage of price
  const change = price * (percent_change / 100);

  return {
    symbol: asset.symbol,
    name: name,
    price: price,
    change: change,
    percent_change: percent_change,
    volume: 0, // Volume not provided by backend
    timestamp: Date.now() / 1000,
    is_market_open: true
  };
};

/**
 * FETCH BATCH QUOTES (FROM LOCAL BACKEND)
 * Returns quotes for all assets from the backend
 */
export const fetchBatchQuotes = async (symbols: string[]): Promise<Record<string, StockQuote>> => {
  const marketData = await fetchMarketData();

  const results: Record<string, StockQuote> = {};

  marketData.forEach(asset => {
    if (symbols.includes(asset.symbol)) {
      // Map backend fields to StockQuote format
      const name = asset.friendly_name || asset.symbol;
      const price = asset.display_price;
      const return24h = asset.return_24h;

      // Handle NaN or null values for returns
      const percent_change = (return24h !== null && return24h !== undefined && !isNaN(return24h)) ? return24h : 0;
      // Calculate change based on percentage of price
      const change = price * (percent_change / 100);

      results[asset.symbol] = {
        symbol: asset.symbol,
        name: name,
        price: price,
        change: change,
        percent_change: percent_change,
        volume: 0, // Volume not provided by backend
        timestamp: Date.now() / 1000,
        is_market_open: true
      };
    }
  });

  return results;
};

/**
 * FETCH TIME SERIES DATA (FROM LOCAL BACKEND)
 * Returns the last 10 points from the data lake for trend visualization
 */
export const fetchTimeSeries = async (symbol: string): Promise<OHLCPoint[]> => {
  // For now, we'll generate mock data based on the current price
  // In a real implementation, this would fetch actual historical data from the backend
  const currentQuote = await fetchQuote(symbol);
  const now = new Date();

  // Generate 10 mock data points
  const history: OHLCPoint[] = [];
  let currentPrice = currentQuote.price;

  for (let i = 9; i >= 0; i--) {
    const date = new Date(now);
    date.setMinutes(date.getMinutes() - i * 15); // 15-minute intervals

    // Small random change for mock data
    const change = (Math.random() - 0.5) * (currentPrice * 0.01);
    currentPrice += change;

    history.push({
      datetime: date.toISOString().replace('T', ' ').substring(0, 19),
      open: currentPrice - change/2,
      high: currentPrice + Math.abs(change)/2,
      low: currentPrice - Math.abs(change)/2,
      close: currentPrice,
      volume: Math.floor(Math.random() * 1000000) + 50000
    });
  }

  return history;
};

/**
 * FETCH NEWS (LOCAL MOCK IMPLEMENTATION)
 * Placeholder function - in a real implementation, this would fetch from backend
 */
export const fetchNews = async (symbol?: string): Promise<NewsItem[]> => {
  // Return empty array for now - news would come from backend in real implementation
  return [];
};
