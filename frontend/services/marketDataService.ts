
import { StockQuote, OHLCPoint, NewsItem, MarketInstrument } from '../types';
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
      case 'FX_METALS': 
        category = 'fx'; // Group Currencies and Metals together
        break;
      case 'BONDS':
        category = 'bond';
        break;
      case 'INDEX':
        category = 'future';
        break;
      case 'SECTORS':
        category = 'em'; // Use 'em' for Sectors
        break;
      case 'EM':
        category = 'em'; // Crypto stays in Digital Assets (Emerging Mkts)
        break;
      default:
        category = 'stock';
    }
  }

  // Handle change_24h as changePercent
  const changePercent = (asset.change_24h !== null && asset.change_24h !== undefined && !isNaN(asset.change_24h)) ? asset.change_24h : 0;
  const change = asset.price * (changePercent / 100);

  return {
    symbol: asset.symbol,
    name: asset.friendly_name || asset.symbol,
    category,
    assetClass: asset.asset_class,
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
export const fetchSparkline = async (symbol: string, range: '1D' | '1W' | '1M' = '1D'): Promise<number[]> => {
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
 * Returns the full array from the data lake for trend visualization
 */
export const fetchTimeSeries = async (symbol: string, range: '1D' | '1W' | '1M' = '1D'): Promise<OHLCPoint[]> => {
  try {
    const url = `${CONFIG.BACKEND_API_BASE}/api/sparkline/${symbol}?range=${range}`;
    console.log(`📡 API Request: ${url}`);
    
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Fetch failed`);

    const result = await res.json();
    const sparklineData = result.data || [];

    return sparklineData.map((point: any) => ({
      datetime: point.datetime,
      open: point.close,
      high: point.close,
      low: point.close,
      close: point.close,
      volume: 0
    }));
  } catch (error) {
    console.error("Chart Fetch Error:", error);
    return [];
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

export const fetchNews = async (symbol: string = 'Global'): Promise<NewsItem[]> => {
  try {
    const url = `${CONFIG.BACKEND_API_BASE}/api/news/${symbol}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`News fetch failed`);
    const data = await res.json();
    
    // Map backend headlines to NewsItem format
    return (data.headlines || []).map((h: any, i: number) => ({
      id: `news-${i}-${Date.now()}`,
      title: h.title,
      source: h.source || 'Market News',
      time: 'Just Now',
      summary: `Real-time coverage: ${h.title} from ${h.source || 'Reuters/Bloomberg'}.`,
      url: h.url || '#',
      symbol: symbol,
      sentiment: 'neutral',
      category: 'Market'
    }));
  } catch (error) {
    console.error("News Fetch Error:", error);
    return [];
  }
};
