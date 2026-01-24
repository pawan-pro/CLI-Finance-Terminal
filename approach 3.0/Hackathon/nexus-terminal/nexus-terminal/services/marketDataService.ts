
import { StockQuote, OHLCPoint, NewsItem } from '../types';
import { CONFIG } from '../config';

/**
 * Type definition for the backend API response
 */
interface BackendAsset {
  symbol: string;
  friendly_name?: string;
  price: number;
  change_24h: number | null;
  asset_class: string;
  status?: string;
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
  let category: 'future' | 'bond' | 'fx' | 'spread' | 'em' | 'stock' = 'future'; // default

  // Special handling for DXY - force to INDEX/future category
  if (asset.symbol === 'DXY') {
    category = 'future';
  } else {
    switch (asset.asset_class?.toUpperCase()) {
      case 'BONDS':
        category = 'bond';
        break;
      case 'INDEX':
        category = 'future';
        break;
      case 'METALS':
        category = 'fx';
        break;
      case 'SECTORS':
        category = 'em';
        break;
      case 'FX':
      case 'FOREX':
        category = 'fx';
        break;
      case 'COMMODITY':
      case 'COMMODITIES':
        category = 'em';
        break;
      case 'CRYPTO':
      case 'CRYPTOCURRENCY':
        category = 'em';
        break;
      case 'SPREAD':
        category = 'spread';
        break;
      case 'STOCK':
      case 'EQUITY':
        category = 'stock';
        break;
      default:
        category = 'future'; // default fallback
    }
  }

  // Handle change_24h as changePercent
  const changePercent = (asset.change_24h !== null && asset.change_24h !== undefined && !isNaN(asset.change_24h)) ? asset.change_24h : 0;
  const change = asset.price * (changePercent / 100);

  return {
    symbol: asset.symbol,
    name: asset.friendly_name || asset.symbol,
    category,
    price: asset.price,
    change,
    changePercent
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
  const price = asset.price;
  const change24h = asset.change_24h;

  // Handle NaN or null values for returns
  const percent_change = (change24h !== null && change24h !== undefined && !isNaN(change24h)) ? change24h : 0;
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
    is_market_open: true,
    status: asset.status
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
      const price = asset.price;
      const change24h = asset.change_24h;

      // Handle NaN or null values for returns
      const percent_change = (change24h !== null && change24h !== undefined && !isNaN(change24h)) ? change24h : 0;
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
        is_market_open: true,
        status: asset.status
      };
    }
  });

  return results;
};

/**
 * FETCH SPARKLINE DATA (FROM LOCAL BACKEND)
 * Returns price data from the sparkline API for charting
 */
export const fetchSparkline = async (symbol: string, range: '1D' | '1W' = '1D'): Promise<number[]> => {
  const url = `${CONFIG.BACKEND_API_BASE}/api/sparkline/${symbol}?range=${range}`;
  const res = await fetch(url);

  if (!res.ok) {
    throw new Error(`Sparkline data fetch failed: ${res.status} ${res.statusText}`);
  }

  const data = await res.json();
  if (!Array.isArray(data)) {
    throw new Error('Invalid response format: expected array of prices');
  }

  return data;
};

/**
 * FETCH TIME SERIES DATA (FROM LOCAL BACKEND)
 * Returns the last 10 points from the data lake for trend visualization
 */
export const fetchTimeSeries = async (symbol: string, range: '1D' | '1W' = '1D'): Promise<OHLCPoint[]> => {
  try {
    // Try to get actual data from the sparkline API
    const sparklineData = await fetchSparkline(symbol, range);

    // Convert the sparkline data to OHLCPoint format
    const now = new Date();
    const history: OHLCPoint[] = [];

    // Use the last 10 points from the sparkline data
    const pointsToUse = Math.min(sparklineData.length, 10);
    const startIndex = sparklineData.length - pointsToUse;

    for (let i = 0; i < pointsToUse; i++) {
      const date = new Date(now);
      date.setMinutes(date.getMinutes() - (pointsToUse - 1 - i) * 15); // 15-minute intervals

      const price = sparklineData[startIndex + i];

      history.push({
        datetime: date.toISOString().replace('T', ' ').substring(0, 19),
        open: price,
        high: price * (1 + Math.random() * 0.001), // Slight variation for high
        low: price * (1 - Math.random() * 0.001),  // Slight variation for low
        close: price,
        volume: Math.floor(Math.random() * 1000000) + 50000
      });
    }

    return history;
  } catch (error) {
    console.warn(`Failed to fetch sparkline data for ${symbol}, using mock data:`, error);

    // Fallback to mock data if API call fails
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
  }
};

/**
 * FETCH MULTIPLE MARKET DATA
 * Fetches data for multiple symbols from the backend API
 */
export const fetchMultipleMarketData = async (
  symbols: string[],
  timeframe: string = '15min',
  limit: number = 100
): Promise<{data: Record<string, any[]>}> => {
  try {
    const symbolsParam = symbols.join(',');
    const url = `${CONFIG.BACKEND_API_BASE}/api/multiple-market-data?symbols=${symbolsParam}&timeframe=${timeframe}&limit=${limit}`;
    const res = await fetch(url);

    if (!res.ok) {
      throw new Error(`Multiple market data fetch failed: ${res.status} ${res.statusText}`);
    }

    const data = await res.json();
    return data;
  } catch (error) {
    console.error('Error fetching multiple market data:', error);
    // Return empty data structure in case of error
    const emptyData: Record<string, any[]> = {};
    symbols.forEach(symbol => {
      emptyData[symbol] = [];
    });
    return { data: emptyData };
  }
};

/**
 * FETCH NEWS (LOCAL MOCK IMPLEMENTATION)
 * Placeholder function - in a real implementation, this would fetch from backend
 */
export const fetchNews = async (symbol?: string): Promise<NewsItem[]> => {
  // Return empty array for now - news would come from backend in real implementation
  return [];
};
