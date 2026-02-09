
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Auth } from './components/Auth';
import { StockChart } from './components/StockChart';
import { PublicChat } from './components/PublicChat';
import { AIAssistant } from './components/AIAssistant';
import { MacroDashboard } from './components/MacroDashboard';
import GlobalMonitor from './components/GlobalMonitor';
import { User, StockQuote, OHLCPoint, NewsItem, DateRange, MarketContext, MarketInstrument, EconomicEvent, RateProbability } from './types';
import { getCurrentUser, setCurrentUser } from './services/storage';
import { fetchQuote, fetchTimeSeries, fetchNews, fetchBatchQuotes, fetchMarketData, convertToMarketInstrument, fetchSparkline } from './services/marketDataService';
import { generateMacroData, updateMacroInstrument, generateEconomicEvents, generateRateProbs } from './services/dataService';
import { LogOut, LayoutGrid, Clock, Newspaper, Search, Activity, ChevronRight, BarChart3, Globe2, AlertTriangle } from 'lucide-react';
import { CONFIG } from './config';

const WATCHLIST = ['US500', 'UT100', 'GOLD', 'WTI', 'VIX', 'EURUSD', 'US 10Y'];

const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [activeSymbol, setActiveSymbol] = useState('US500');
  const [selectedSymbol, setSelectedSymbol] = useState('US500'); // New state for selected symbol
  const [timeRange, setTimeRange] = useState<'1D' | '1W' | '1M'>('1D'); // New state for chart time range
  const [view, setView] = useState<'EQUITY' | 'MACRO' | 'GLOBAL'>('EQUITY');

  const [quote, setQuote] = useState<StockQuote | null>(null);
  const [history, setHistory] = useState<OHLCPoint[]>([]);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [watchlistQuotes, setWatchlistQuotes] = useState<Record<string, StockQuote>>({});
  
  const [macroInstruments, setMacroInstruments] = useState<MarketInstrument[]>([]);
  const [econEvents, setEconEvents] = useState<EconomicEvent[]>([]);
  const [rateProbs] = useState<RateProbability[]>(generateRateProbs());

  const [selectedRange, setSelectedRange] = useState<DateRange>({ startDate: null, endDate: null });
  const [currentTime, setCurrentTime] = useState(new Date());

  // Granular Error States
  const [chartError, setChartError] = useState<string | null>(null);
  const [newsError, setNewsError] = useState<string | null>(null);
  const [watchlistError, setWatchlistError] = useState<string | null>(null);

  // Vision Analysis State
  const [visionAnalysis, setVisionAnalysis] = useState<string | null>(null);

  useEffect(() => {
    const stored = getCurrentUser();
    if (stored) setUser(stored);
  }, []);

  useEffect(() => {
    const t = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  // Listen for vision analysis completion events
  useEffect(() => {
    const handleVisionAnalysisComplete = (event: any) => {
      setVisionAnalysis(event.detail.analysis);
    };

    window.addEventListener('visionAnalysisComplete', handleVisionAnalysisComplete);

    return () => {
      window.removeEventListener('visionAnalysisComplete', handleVisionAnalysisComplete);
    };
  }, []);

  // Load economic events periodically
  useEffect(() => {
    const loadEconomicEvents = async () => {
      if (!user) return;
      try {
        const events = await generateEconomicEvents();
        setEconEvents(events);
      } catch (error) {
        console.error('Error loading economic events:', error);
      }
    };

    // Load initially
    loadEconomicEvents();

    // Refresh every 5 minutes
    const interval = setInterval(loadEconomicEvents, 300000);

    return () => clearInterval(interval);
  }, [user]);

  // Load macro instruments from backend API
  useEffect(() => {
    const loadMacroInstruments = async () => {
      if (!user) return;
      try {
        const marketData = await fetchMarketData();
        const instruments = marketData.map(convertToMarketInstrument);
        setMacroInstruments(instruments);
      } catch (error) {
        console.error('Error loading macro instruments:', error);
      }
    };

    // Load initially
    loadMacroInstruments();

    // Refresh macro instruments every 30 seconds as specified
    const interval = setInterval(loadMacroInstruments, 30000);

    return () => clearInterval(interval);
  }, [user]);

  // 1. Fetch Active Symbol Data (Quote + History)
  const refreshActiveAsset = useCallback(async () => {
    if (!user) return;
    setChartError(null);
    setHistory([]); // CLEAR HISTORY TO PREVENT GHOST DATA
    try {
      const [q, h] = await Promise.all([
        fetchQuote(activeSymbol),
        fetchTimeSeries(activeSymbol, timeRange)
      ]);
      setQuote(q);
      setHistory(h);
    } catch (e: any) {
      setChartError(e.message);
    }
  }, [activeSymbol, timeRange, user]);

  // Force-refresh when symbol or timeframe changes
  useEffect(() => {
    if (user) {
      refreshActiveAsset();
    }
  }, [activeSymbol, timeRange, user]); // Dedicated effect for immediate refresh

  // 2. Fetch News (Less Frequent - every 5 minutes to prevent quota exhaustion)
  const refreshNews = useCallback(async () => {
    if (!user) return;
    setNewsError(null);
    try {
      const n = await fetchNews(activeSymbol); // Use activeSymbol instead of selectedSymbol
      setNews(n);
    } catch (e: any) {
      setNewsError(e.message);
    }
  }, [activeSymbol, user]);

  // 3. Fetch Watchlist (Filter from market data where asset_class === 'STOCK')
  const refreshWatchlist = useCallback(async () => {
    if (!user) return;
    setWatchlistError(null);
    try {
      const marketData = await fetchMarketData();
      // Create a map of the stock quotes for only the symbols in WATCHLIST
      const map: Record<string, StockQuote> = {};
      for (const asset of marketData) {
        if (WATCHLIST.includes(asset.symbol)) {
          // Convert BackendAsset to StockQuote format - ensure we use the symbol field returned by API
          const name = asset.friendly_name || asset.symbol;
          const price = asset.price;
          const change24h = asset.change_24h;

          // Handle NaN or null values for returns
          const percent_change = (change24h !== null && change24h !== undefined && !isNaN(change24h)) ? change24h : 0;
          // Calculate change based on percentage of price
          const change = price * (percent_change / 100);

          map[asset.symbol] = {
            symbol: asset.symbol, // Use the symbol field directly from API
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
      }
      setWatchlistQuotes(map);
    } catch (e: any) {
      setWatchlistError(e.message);
    }
  }, [user]);

  // Initial and Interval Polling
  useEffect(() => {
    if (!user) return;

    refreshActiveAsset();
    refreshNews();
    refreshWatchlist();

    // Set the polling interval for market to 30 seconds and research to 5 minutes as specified
    const assetInt = setInterval(refreshActiveAsset, CONFIG.POLLING.ACTIVE_ASSET);
    const watchlistInt = setInterval(refreshWatchlist, CONFIG.POLLING.WATCHLIST);
    const newsInt = setInterval(refreshNews, CONFIG.POLLING.NEWS);

    return () => {
      clearInterval(assetInt);
      clearInterval(watchlistInt);
      clearInterval(newsInt);
    };
  }, [user, refreshActiveAsset, refreshNews, refreshWatchlist, timeRange]);

  // Removed macro ticker updates since we're fetching from backend

  const handleLogout = () => {
    setCurrentUser(null);
    setUser(null);
  };

  const marketContext: MarketContext = useMemo(() => ({
    symbol: selectedSymbol, // Use selectedSymbol instead of activeSymbol
    quote,
    selectedRange,
    recentHistory: history,
    visionAnalysis
  }), [selectedSymbol, quote, selectedRange, history, visionAnalysis]);

  if (!user) return <Auth onLogin={setUser} />;

  return (
    <div className="flex flex-col h-screen bg-nexus-900 text-slate-200 overflow-hidden font-sans">
      <header className="h-10 flex-shrink-0 bg-nexus-900 border-b border-slate-800 flex items-center justify-between px-4 z-50">
        <div className="flex items-center space-x-6 overflow-hidden">
          <div className="flex items-center space-x-2 border-r border-slate-700 pr-4">
             <div className="p-1 bg-nexus-accent rounded text-nexus-900"><Activity size={14} /></div>
             <span className="font-mono font-bold tracking-tighter text-slate-100 uppercase">NEXUS<span className="text-nexus-accent">TERMINAL</span></span>
             <span className="ml-1 px-1 py-0.5 bg-nexus-accent/10 border border-nexus-accent/30 rounded text-[8px] font-mono text-nexus-accent uppercase tracking-tighter leading-none">BETA</span>
          </div>
          
          <div className="mask-linear-fade overflow-hidden flex-1">
            <div className="animate-ticker flex space-x-8">
              {WATCHLIST.map(sym => {
                const q = watchlistQuotes[sym];
                if (!q) return null;

                // Check for NaN values
                const isChangeNaN = isNaN(q.change) || q.change === null || q.change === undefined;
                const isPriceNaN = isNaN(q.price) || q.price === null || q.price === undefined;

                return (
                  <div key={sym} className="flex items-center space-x-2 whitespace-nowrap">
                    <span className="text-[10px] font-mono font-bold text-slate-400">{q.name}</span>
                    <span className={`text-[10px] font-mono ${isChangeNaN ? 'text-slate-400' : q.change >= 0 ? 'text-nexus-up' : 'text-nexus-down'}`}>
                      {sym === 'DXY' && (isPriceNaN || q.price === 0) ? 'CALCULATING...' : (isPriceNaN ? 'CALC...' : q.price.toFixed(2))}
                    </span>
                  </div>
                );
              })}
              {watchlistError && (
                <span className="text-[10px] font-mono text-red-500 uppercase tracking-tighter">WATCHLIST ERROR: {watchlistError}</span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {(chartError || newsError || watchlistError) && (
             <div className="flex items-center text-[10px] font-mono text-red-500 bg-red-900/10 px-2 py-0.5 rounded border border-red-900/50">
                <AlertTriangle size={10} className="mr-1" />
                API LIMIT REACHED
             </div>
          )}
          <div className="flex items-center text-[10px] font-mono text-slate-500">
             <Clock size={12} className="mr-1.5" />
             {currentTime.toLocaleTimeString([], { hour12: false })} UTC
          </div>
          <div className="h-4 w-px bg-slate-700"></div>
          <div className="flex items-center space-x-2 group">
             <span className="text-[10px] font-mono font-bold text-slate-300">{user.username}</span>
             <button onClick={handleLogout} className="text-slate-500 hover:text-red-400 transition-colors">
                <LogOut size={14} />
             </button>
          </div>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <aside className="w-56 border-r border-slate-800 bg-nexus-900/50 flex flex-col hidden lg:flex">
          <div className="p-2 border-b border-slate-800 flex flex-col space-y-1">
             <button 
                onClick={() => setView('EQUITY')}
                className={`w-full text-left px-2 py-1.5 rounded text-[10px] font-mono font-bold transition-all flex items-center ${view === 'EQUITY' ? 'bg-nexus-accent text-nexus-900' : 'text-slate-400 hover:bg-slate-800'}`}
             >
                <BarChart3 size={12} className="mr-2" /> F1: EQUITY ANALYSIS
             </button>
             <button
                onClick={() => setView('MACRO')}
                className={`w-full text-left px-2 py-1.5 rounded text-[10px] font-mono font-bold transition-all flex items-center ${view === 'MACRO' ? 'bg-nexus-accent text-nexus-900' : 'text-slate-400 hover:bg-slate-800'}`}
             >
                <Globe2 size={12} className="mr-2" /> F2: MACRO DASHBOARD
             </button>
             <button
                onClick={() => setView('GLOBAL')}
                className={`w-full text-left px-2 py-1.5 rounded text-[10px] font-mono font-bold transition-all flex items-center ${view === 'GLOBAL' ? 'bg-nexus-accent text-nexus-900' : 'text-slate-400 hover:bg-slate-800'}`}
             >
                <Globe2 size={12} className="mr-2" /> F3: GLOBAL MONITOR
             </button>
          </div>

          <div className="p-2 border-b border-slate-800 text-[10px] font-mono font-bold text-slate-500 uppercase tracking-widest flex items-center">
            <LayoutGrid size={12} className="mr-2" /> WATCHLIST (W1)
          </div>
          <div className="flex-1 overflow-y-auto custom-scrollbar">
            {WATCHLIST.map(sym => {
              const q = watchlistQuotes[sym];
              return (
                <div
                  key={sym}
                  onClick={() => {
                    setActiveSymbol(sym);
                    setSelectedSymbol(sym); // Update selected symbol
                    setView('EQUITY');
                  }}
                  className={`p-3 border-b border-slate-800/50 cursor-pointer transition-all hover:bg-slate-800/40 ${activeSymbol === sym && view === 'EQUITY' ? 'bg-nexus-800 border-l-2 border-l-nexus-accent' : ''}`}
                >
                  <div className="flex justify-between items-start mb-0.5">
                    <div className="flex flex-col">
                      <span className="font-mono font-bold text-[11px] text-white uppercase truncate max-w-[120px]">{q?.name || sym}</span>
                      <span className="font-mono text-[9px] text-slate-500 uppercase">{sym}</span>
                    </div>
                    <div className="flex flex-col items-end">
                      <span className={`text-xs font-mono font-bold ${q && !isNaN(q.change) && q.change >= 0 ? 'text-nexus-up' : 'text-nexus-down'}`}>
                        {q ? (sym === 'DXY' && (isNaN(q.price) || q.price === 0) ? 'CALCULATING...' : (isNaN(q.price) ? 'CALC...' : q.price.toFixed(2))) : '---'}
                      </span>
                      <div className="flex items-center space-x-1 mt-0.5">
                        <span className={`text-[9px] font-mono ${q && !isNaN(q.percent_change) && q.percent_change >= 0 ? 'text-nexus-up' : 'text-nexus-down'}`}>
                          {q ? (q.percent_change >= 0 ? '+' : '') + q.percent_change.toFixed(2) + '%' : ''}
                        </span>
                        {q?.status && (
                          <span className={`w-1.5 h-1.5 rounded-full ${
                            q.status.toLowerCase() === 'live' ? 'bg-green-500' : 'bg-red-500'
                          }`}></span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </aside>

        <main className="flex-1 flex flex-col min-w-0 bg-nexus-900 border-r border-slate-800 overflow-hidden">
          <div className="flex-1 p-2 flex flex-col min-h-0 space-y-2 overflow-hidden">
            <div className="flex-1 min-h-[400px] relative">
              {view === 'EQUITY' ? (
                !quote || history.length === 0 ? (
                  <div className="h-full w-full flex items-center justify-center bg-nexus-800 border border-slate-700 rounded-lg min-h-[400px]">
                    <div className="flex flex-col items-center space-y-2">
                      <div className="w-8 h-8 border-2 border-nexus-accent border-t-transparent rounded-full animate-spin"></div>
                      <span className="text-xs font-mono text-slate-500 uppercase">SYNCHRONIZING WITH DATA LAKE...</span>
                    </div>
                  </div>
                ) : (
                  <StockChart
                    quote={quote}
                    history={history}
                    error={chartError}
                    onRangeChange={setSelectedRange}
                    timeRange={timeRange}
                    onTimeRangeChange={setTimeRange}
                  />
                )
              ) : view === 'MACRO' ? (
                !macroInstruments || macroInstruments.length === 0 ? (
                  <div className="h-full w-full flex items-center justify-center bg-nexus-800 border border-slate-700 rounded-lg min-h-[400px]">
                    <div className="flex flex-col items-center space-y-2">
                      <div className="w-8 h-8 border-2 border-nexus-accent border-t-transparent rounded-full animate-spin"></div>
                      <span className="text-xs font-mono text-slate-500 uppercase">SYNCHRONIZING WITH DATA LAKE...</span>
                    </div>
                  </div>
                ) : (
                  <MacroDashboard
                    instruments={macroInstruments}
                    econEvents={econEvents}
                    rateProbs={rateProbs}
                    onSelectSymbol={(symbol) => {
                      setActiveSymbol(symbol);
                      setSelectedSymbol(symbol);
                      setView('EQUITY');
                    }}
                  />
                )
              ) : view === 'GLOBAL' ? (
                !macroInstruments || macroInstruments.length === 0 ? (
                  <div className="h-full w-full flex items-center justify-center bg-nexus-800 border border-slate-700 rounded-lg min-h-[400px]">
                    <div className="flex flex-col items-center space-y-2">
                      <div className="w-8 h-8 border-2 border-nexus-accent border-t-transparent rounded-full animate-spin"></div>
                      <span className="text-xs font-mono text-slate-500 uppercase">SYNCHRONIZING WITH DATA LAKE...</span>
                    </div>
                  </div>
                ) : (
                  <GlobalMonitor
                    instruments={macroInstruments}
                    onSelectSymbol={(symbol) => {
                      setActiveSymbol(symbol);
                      setSelectedSymbol(symbol);
                      setView('EQUITY');
                    }}
                  />
                )
              ) : null}
            </div>

            <div className="h-64 flex space-x-2 flex-shrink-0">
               <div className="flex-1 bg-nexus-800 rounded-lg border border-slate-700 flex flex-col overflow-hidden">
                  <div className="p-2 border-b border-slate-700 bg-nexus-900/50 flex items-center justify-between">
                    <span className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-widest flex items-center">
                      <Newspaper size={12} className="mr-2" /> NEWS FEED (N1)
                    </span>
                    <Search size={12} className="text-nexus-accent" />
                  </div>
                  <div className="flex-1 overflow-y-auto p-0 divide-y divide-slate-800 custom-scrollbar">
                    {(news.length > 0 ? news : [
                      { id: '1', title: `${activeSymbol} intelligence note: Institutional accumulation detected at key support.`, source: 'QUANTWATER AI', time: '2m ago', sentiment: 'BULLISH', url: '#' },
                      { id: '2', title: `Market volatility index (VIX) shows inverse correlation with ${activeSymbol} price action.`, source: 'BLOOMBERG', time: '15m ago', sentiment: 'NEUTRAL', url: '#' },
                      { id: '3', title: `Quarterly outlook for ${activeSymbol} updated by Goldman Sachs; target price revised.`, source: 'REUTERS', time: '1h ago', sentiment: 'BULLISH', url: '#' },
                      { id: '4', title: `Macro shift: Interest rate expectations impacting ${activeSymbol} sector performance.`, source: 'FT', time: '3h ago', sentiment: 'BEARISH', url: '#' },
                      { id: '5', title: `Breakthrough in AI integration could drive ${activeSymbol} margins higher.`, source: 'TECHCRUNCH', time: '5h ago', sentiment: 'BULLISH', url: '#' },
                    ])
                    .filter((item: any) => {
                      const isFinancialIndex = ['US500', 'UT100', 'VIX'].includes(activeSymbol);
                      if (isFinancialIndex) {
                        const title = item.title.toLowerCase();
                        return !title.includes('disney') && !title.includes('entertainment');
                      }
                      return true;
                    })
                    .map((item: any) => (
                      <a key={item.id} href={item.url} target="_blank" rel="noopener noreferrer" className="block p-3 hover:bg-slate-700/30 transition-colors group">
                        <div className="flex justify-between text-[9px] font-mono text-slate-500 mb-1">
                          <div className="flex items-center space-x-2">
                            <span className="text-nexus-accent">{item.source}</span>
                            {item.sentiment && (
                              <span className={`px-1 rounded font-bold text-[8px] ${
                                item.sentiment === 'BULLISH' ? 'bg-green-900/40 text-green-400' :
                                item.sentiment === 'BEARISH' ? 'bg-red-900/40 text-red-400' :
                                'bg-slate-700/40 text-slate-400'
                              }`}>
                                [{item.sentiment}]
                              </span>
                            )}
                          </div>
                          <span>{item.time}</span>
                        </div>
                        <h4 className="text-xs font-bold text-slate-200 group-hover:text-nexus-accent leading-snug line-clamp-2">{item.title}</h4>
                      </a>
                    ))}
                  </div>
               </div>

               <div className="w-80 flex-shrink-0">
                  <PublicChat currentUser={user} />
               </div>
            </div>
          </div>
        </main>

        <div className="w-80 flex-shrink-0">
          <AIAssistant 
            marketContext={marketContext}
          />
        </div>
      </div>
      
      <footer className="h-6 bg-slate-950 border-t border-slate-800 flex items-center px-4 space-x-6 text-[9px] font-mono text-slate-500">
        <div className="flex space-x-3">
          <span className="text-nexus-accent font-bold">CORE ENGINE: GEMINI 3 FLASH | DATA LAKE: DUCKDB | SYNC: NOMINAL</span>
        </div>
        <div className="flex-1 flex justify-center space-x-4">
           <span className="flex items-center"><ChevronRight size={10} className="mr-1 text-nexus-up"/> SPX: 5,241.10 (+0.45%)</span>
           <span className="flex items-center"><ChevronRight size={10} className="mr-1 text-nexus-down"/> NDX: 18,321.05 (-0.12%)</span>
        </div>
        <div className="flex items-center text-slate-600 uppercase">
           LIVE_REFRESH: 15 SEC INTERVAL
        </div>
      </footer>
    </div>
  );
};

export default App;
