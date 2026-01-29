
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

const WATCHLIST = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'META', 'GOOGL', 'JPM', 'V'];

const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [activeSymbol, setActiveSymbol] = useState('AAPL');
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL'); // New state for selected symbol
  const [timeRange, setTimeRange] = useState<'1D' | '1W'>('1D'); // New state for chart time range
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

  // Fetch sparkline data when activeSymbol changes
  useEffect(() => {
    const fetchSparklineData = async () => {
      if (!user || !activeSymbol) return;
      try {
        const data = await fetchSparkline(activeSymbol);
        // Convert sparkline data to OHLCPoint format if needed
        const now = new Date();
        const newHistory: OHLCPoint[] = data.map((price: number, index: number) => {
          const date = new Date(now);
          date.setMinutes(date.getMinutes() - (data.length - 1 - index)); // Assuming minute intervals

          return {
            datetime: date.toISOString().replace('T', ' ').substring(0, 19),
            open: price,
            high: price * (1 + Math.random() * 0.001), // Slight variation for high
            low: price * (1 - Math.random() * 0.001),  // Slight variation for low
            close: price,
            volume: Math.floor(Math.random() * 1000000) + 50000
          };
        });
        setHistory(newHistory);
      } catch (error) {
        console.error('Error fetching sparkline data:', error);
      }
    };

    fetchSparklineData();
  }, [activeSymbol, user]);

  // 1. Fetch Active Symbol Data (Quote + History)
  const refreshActiveAsset = useCallback(async () => {
    if (!user) return;
    setChartError(null);
    try {
      // Ensure the quote lookup is done by symbol from the API
      const [q, h] = await Promise.all([
        fetchQuote(activeSymbol), // Use activeSymbol instead of selectedSymbol - this will look up by symbol field from API
        fetchTimeSeries(activeSymbol, timeRange) // Use activeSymbol and timeRange
      ]);
      setQuote(q);
      setHistory(h);
    } catch (e: any) {
      setChartError(e.message);
    }
  }, [activeSymbol, timeRange, user]);

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
    const assetInt = setInterval(refreshActiveAsset, 30000); // 30 seconds
    const watchlistInt = setInterval(refreshWatchlist, 30000); // 30 seconds
    const newsInt = setInterval(refreshNews, 300000); // 5 minutes

    return () => {
      clearInterval(assetInt);
      clearInterval(watchlistInt);
      clearInterval(newsInt);
    };
  }, [user, refreshActiveAsset, refreshNews, refreshWatchlist]);

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
                    <span className="text-[10px] font-mono font-bold text-slate-400">{sym}</span>
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
                  <div className="flex justify-between items-center mb-0.5">
                    <span className="font-mono font-bold text-xs text-white">{sym}</span>
                    <div className="flex items-center space-x-2">
                      <span className={`text-xs font-mono font-bold ${q && !isNaN(q.change) && q.change >= 0 ? 'text-nexus-up' : 'text-nexus-down'}`}>
                        {q ? (sym === 'DXY' && (isNaN(q.price) || q.price === 0) ? 'CALCULATING...' : (isNaN(q.price) ? 'CALC...' : q.price.toFixed(2))) : '---'}
                      </span>
                      {q?.status && (
                        <span className={`text-[8px] px-1 py-0.5 rounded ${
                          q.status.toLowerCase() === 'live'
                            ? 'bg-green-900/30 text-green-400 border border-green-800/50'
                            : 'bg-red-900/30 text-red-400 border border-red-800/50'
                        }`}>
                          {q.status}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex justify-between items-center text-[9px] font-mono text-slate-500">
                    {q ? (
                      <span>{(!isNaN(q.percent_change) && q.percent_change >= 0 ? '+' : '') + ((isNaN(q.percent_change) || q.percent_change === null || q.percent_change === undefined) ? 'CALC...' : (q.percent_change || 0).toFixed(2))}%</span>
                    ) : (
                      <span className="text-[8px] text-red-900/50 italic uppercase">{watchlistError ? 'Limit' : 'Loading'}</span>
                    )}
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
                    {news.map(item => (
                      <a key={item.id} href={item.url} target="_blank" rel="noopener noreferrer" className="block p-3 hover:bg-slate-700/30 transition-colors group">
                        <div className="flex justify-between text-[9px] font-mono text-slate-500 mb-1">
                          <span className="text-nexus-accent">{item.source}</span>
                          <span>{item.time}</span>
                        </div>
                        <h4 className="text-xs font-bold text-slate-200 group-hover:text-nexus-accent leading-snug line-clamp-2">{item.title}</h4>
                      </a>
                    ))}
                    {news.length === 0 && !newsError && <div className="p-10 text-center text-xs text-slate-600 font-mono italic">BUFFERING NEWS STREAM...</div>}
                    {newsError && (
                      <div className="p-10 text-center flex flex-col items-center justify-center">
                        <AlertTriangle size={24} className="text-red-900 mb-2 opacity-50" />
                        <span className="text-[10px] text-red-900 font-mono uppercase tracking-widest leading-relaxed">
                          News Access Restricted<br/>
                          <span className="opacity-70 text-[8px]">{newsError}</span>
                        </span>
                      </div>
                    )}
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
          <span className="text-nexus-accent font-bold">DATA FEED</span>
          <span className={chartError || watchlistError ? "text-red-500" : "text-green-500"}>
            SYNC: {chartError || watchlistError ? "DEGRADED" : "NOMINAL"}
          </span>
          <span>SOURCE: QUANTWATER_DUCKDB</span>
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
