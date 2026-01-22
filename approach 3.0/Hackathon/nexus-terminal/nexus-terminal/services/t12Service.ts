
import { StockQuote, OHLCPoint, NewsItem } from '../types';
import { CONFIG } from '../config';

const BASE_URL = 'https://api.twelvedata.com';

export const fetchQuote = async (symbol: string): Promise<StockQuote> => {
  const res = await fetch(`${BASE_URL}/quote?symbol=${symbol}&apikey=${CONFIG.T12_API_KEY}`);
  const data = await res.json();
  
  if (data.status === 'error' || !data.symbol) {
    throw new Error(data.message || 'Invalid API Response');
  }

  return {
    symbol: data.symbol,
    name: data.name || symbol,
    price: parseFloat(data.close || data.price || '0'),
    change: parseFloat(data.change || '0'),
    percent_change: parseFloat(data.percent_change || '0'),
    volume: parseInt(data.volume || '0'),
    timestamp: data.timestamp || Date.now() / 1000,
    is_market_open: data.is_market_open || false
  };
};

export const fetchBatchQuotes = async (symbols: string[]): Promise<Record<string, StockQuote>> => {
  const symString = symbols.join(',');
  const res = await fetch(`${BASE_URL}/quote?symbol=${symString}&apikey=${CONFIG.T12_API_KEY}`);
  const data = await res.json();

  if (data.status === 'error') {
    throw new Error(data.message);
  }

  const results: Record<string, StockQuote> = {};
  symbols.forEach(s => {
    const item = data[s];
    if (item && item.symbol) {
      results[s] = {
        symbol: item.symbol,
        name: item.name || s,
        price: parseFloat(item.close || item.price || '0'),
        change: parseFloat(item.change || '0'),
        percent_change: parseFloat(item.percent_change || '0'),
        volume: parseInt(item.volume || '0'),
        timestamp: item.timestamp || Date.now() / 1000,
        is_market_open: item.is_market_open || false
      };
    }
  });
  return results;
};

export const fetchTimeSeries = async (symbol: string, interval: string = '15min'): Promise<OHLCPoint[]> => {
  const res = await fetch(`${BASE_URL}/time_series?symbol=${symbol}&interval=${interval}&outputsize=78&apikey=${CONFIG.T12_API_KEY}`);
  const data = await res.json();
  
  if (data.status === 'error' || !data.values) {
    throw new Error(data.message || "Historical data fetch failed.");
  }
  
  return data.values.map((v: any) => ({
    datetime: v.datetime,
    open: parseFloat(v.open),
    high: parseFloat(v.high),
    low: parseFloat(v.low),
    close: parseFloat(v.close),
    volume: parseInt(v.volume)
  })).reverse();
};

export const fetchNews = async (symbol?: string): Promise<NewsItem[]> => {
  const query = symbol ? `&symbol=${symbol}` : '';
  const res = await fetch(`${BASE_URL}/news?apikey=${CONFIG.T12_API_KEY}${query}`);
  const data = await res.json();
  
  if (data.status === 'error' || !data.articles) throw new Error(data.message || "News fetch failed.");

  return data.articles.map((a: any, i: number) => ({
    id: `news-${i}`,
    title: a.title,
    source: a.source_name,
    time: new Date(a.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    summary: a.content || '',
    url: a.link,
    symbol: symbol
  }));
};
