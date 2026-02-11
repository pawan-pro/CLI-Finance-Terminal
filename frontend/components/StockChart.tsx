
import React, { useState, useEffect, useRef } from 'react';
import {
  ComposedChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Brush,
  Area,
  ReferenceLine,
  Label
} from 'recharts';
import { OHLCPoint, DateRange, StockQuote } from '../types';
import { Activity, TrendingUp, TrendingDown, AlertCircle, Eye } from 'lucide-react';
import { fetchTimeSeries } from '../services/marketDataService';
import html2canvas from 'html2canvas';
import { CONFIG } from '../config';

interface StockChartProps {
  quote: StockQuote | null;
  history: OHLCPoint[];
  error?: string | null;
  onRangeChange: (range: DateRange) => void;
  timeRange?: '1D' | '1W' | '1M';
  onTimeRangeChange?: (range: '1D' | '1W' | '1M') => void;
}

// Utility function to handle NaN values
const formatValue = (value: number | null | undefined): string => {
  if (value === null || value === undefined || isNaN(value)) {
    return 'CALC...';
  }
  return value.toString();
};

export const StockChart: React.FC<StockChartProps> = ({ quote, history, error, onRangeChange, timeRange = '1D', onTimeRangeChange }) => {
  const [activeRange, setActiveRange] = useState<DateRange>({ startDate: null, endDate: null });
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const [isCapturing, setIsCapturing] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;
    const resizeObserver = new ResizeObserver((entries) => {
      for (let entry of entries) {
        setDimensions({
          width: entry.contentRect.width,
          height: entry.contentRect.height
        });
      }
    });
    resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, []);

  const captureVisionReport = async () => {
    if (!containerRef.current) return;

    setIsCapturing(true);

    try {
      // Capture the chart container as a canvas
      const canvas = await html2canvas(containerRef.current, {
        backgroundColor: '#0f172a', // Match the chart background
        scale: 2, // Higher resolution for better AI analysis
        useCORS: true,
        allowTaint: true
      });

      // Convert canvas to base64 PNG
      const imageData = canvas.toDataURL('image/png');

      // Send to the vision API
      const response = await fetch(`${CONFIG.BACKEND_API_BASE}/api/vision/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image: imageData,
          symbol: quote?.symbol,
          context: 'stock_chart_analysis',
          range: timeRange
        })
      });

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }

      const result = await response.json();

      // Dispatch a custom event to notify the parent component about the vision result
      window.dispatchEvent(new CustomEvent('visionAnalysisComplete', {
        detail: {
          symbol: quote?.symbol,
          analysis: result.analysis || result
        }
      }));
    } catch (error) {
      console.error('Error capturing vision report:', error);
      // Dispatch an error event
      window.dispatchEvent(new CustomEvent('visionAnalysisComplete', {
        detail: {
          symbol: quote?.symbol,
          analysis: `Error: ${(error as Error).message || 'Failed to analyze chart'}`
        }
      }));
    } finally {
      setIsCapturing(false);
    }
  };

  const handleBrushChange = (e: any) => {
    if (e && e.startIndex !== undefined && e.endIndex !== undefined) {
      const start = history[e.startIndex]?.datetime;
      const end = history[e.endIndex]?.datetime;
      if (start && end) {
        const newRange = { startDate: start, endDate: end };
        setActiveRange(newRange);
        onRangeChange(newRange);
      }
    }
  };

  if (error) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-nexus-800 border border-red-900/50 rounded-lg min-h-[400px] p-6 text-center">
        <div className="flex flex-col items-center space-y-4">
          <AlertCircle className="w-12 h-12 text-red-500" />
          <div>
            <h3 className="text-lg font-mono font-bold text-red-400 uppercase">Data Fetch Error</h3>
            <p className="text-xs font-mono text-slate-400 mt-2 max-w-md">{error}</p>
            <p className="text-[10px] font-mono text-slate-500 mt-4 uppercase">Verify API Keys in config.ts and check rate limits.</p>
          </div>
        </div>
      </div>
    );
  }

  if (!quote || history.length === 0) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-nexus-800 border border-slate-700 rounded-lg min-h-[400px]">
        <div className="flex flex-col items-center space-y-4">
          <Activity className="w-8 h-8 text-nexus-accent animate-spin" />
          <div className="flex flex-col items-center">
            <span className="text-xs font-mono text-slate-500 uppercase">Synchronizing with Data Lake...</span>
            <span className="text-[10px] font-mono text-slate-600 mt-1 uppercase">Insufficient historical data in lake for this range.</span>
          </div>
        </div>
      </div>
    );
  }

  // Check for NaN values in quote data and handle them
  const isChangeNaN = isNaN(quote.change) || quote.change === null || quote.change === undefined;
  const isPercentChangeNaN = isNaN(quote.percent_change) || quote.percent_change === null || quote.percent_change === undefined;
  const isPriceNaN = isNaN(quote.price) || quote.price === null || quote.price === undefined;

  const isUp = !isChangeNaN && quote.change >= 0;
  const color = isUp ? '#22c55e' : '#ef4444';

  return (
    <div className="h-full flex flex-col bg-nexus-800 border border-slate-700 rounded-lg overflow-hidden min-h-[400px]">
      <div className="p-4 flex justify-between items-start border-b border-slate-700 bg-nexus-900/50 flex-shrink-0">
        <div>
            <h2 className="text-2xl font-mono font-bold text-white tracking-tighter uppercase">{quote.name}</h2>
            <span className="text-slate-400 text-xs font-medium uppercase tracking-widest">{quote.symbol}</span>
          <div className="flex items-center space-x-3 mt-1">
            <span className="text-3xl font-mono font-bold text-white">${isPriceNaN ? 'CALC...' : quote.price.toFixed(2)}</span>
            <div className={`flex items-center font-mono font-bold ${isChangeNaN ? 'text-slate-400' : isUp ? 'text-nexus-up' : 'text-nexus-down'}`}>
              {!isChangeNaN && (isUp ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />)}
              <span>{isChangeNaN ? 'CALC...' : (isUp ? '+' : '') + quote.change.toFixed(2)}</span>
              <span className="ml-2 text-sm">({isPercentChangeNaN ? 'CALC...' : '(' + quote.percent_change.toFixed(2) + '%)'})</span>
            </div>
          </div>
        </div>
        <div className="flex flex-col items-end">
          <div className="flex items-center space-x-2 mb-1">
            <button
              onClick={captureVisionReport}
              disabled={isCapturing}
              className="p-1.5 rounded border border-slate-600 hover:border-nexus-accent transition-all duration-300 disabled:opacity-50 flex items-center justify-center"
              style={{
                boxShadow: '0 0 8px rgba(255, 215, 0, 0.5)',
                background: 'radial-gradient(circle, rgba(255,215,0,0.1) 0%, rgba(255,215,0,0) 70%)'
              }}
            >
              {isCapturing ? (
                <div className="w-4 h-4 border-2 border-nexus-accent border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <Eye size={16} className="text-yellow-400" />
              )}
            </button>
            <div className="flex space-x-1 bg-nexus-800 rounded border border-slate-700 p-0.5">
              {(['1D', '1W', '1M'] as const).map((range) => (
                <button
                  key={range}
                  onClick={() => onTimeRangeChange && onTimeRangeChange(range)}
                  className={`px-3 py-1 text-[10px] font-mono rounded transition-all duration-200 ${
                    timeRange === range
                      ? 'bg-nexus-accent text-nexus-900 font-bold shadow-[0_0_10px_rgba(255,215,0,0.6)] active-timeframe-pulse'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
                  }`}
                  style={timeRange === range ? { 
                    boxShadow: '0 0 12px rgba(255, 215, 0, 0.4)',
                    textShadow: '0 0 1px rgba(0,0,0,0.2)'
                  } : {}}
                >
                  {range}
                </button>
              ))}
            </div>
            <span className={`w-2 h-2 rounded-full ${quote.is_market_open ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></span>
            {quote.status && (
              <span className={`w-2 h-2 rounded-full ${
                quote.status.toLowerCase() === 'live' ? 'bg-green-500' : 'bg-red-500'
              }`}></span>
            )}
          </div>
          {activeRange.startDate && (
             <div className="text-[10px] font-mono text-nexus-accent border border-nexus-accent/30 px-2 py-0.5 rounded bg-nexus-accent/5">
                RANGE: {activeRange.startDate} - {activeRange.endDate}
             </div>
          )}
        </div>
      </div>

      <div className="flex-1 bg-nexus-900 relative min-h-0" ref={containerRef}>
        {dimensions.width > 0 && dimensions.height > 0 && (
          <div className="absolute inset-0 p-2">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={history}>
                <defs>
                  <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={color} stopOpacity={0.2}/>
                    <stop offset="95%" stopColor={color} stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="1 4" stroke="#1e293b" vertical={false} />
                <XAxis
                  dataKey="datetime"
                  tick={{fill: '#475569', fontSize: 9, fontFamily: 'JetBrains Mono'}}
                  tickFormatter={(v) => {
                    // v is in "DD MMM HH:mm" format
                    if (!v) return '';
                    if (timeRange === '1D') {
                      // Show only time HH:mm
                      return v.split(' ').slice(-1)[0];
                    } else {
                      // Show date DD MMM
                      return v.split(' ').slice(0, 2).join(' ');
                    }
                  }}
                  axisLine={false}
                  tickLine={false}
                  minTickGap={timeRange === '1D' ? 40 : 80}
                />
                <YAxis
                  domain={['auto', 'auto']}
                  orientation="right"
                  tick={{fill: '#475569', fontSize: 9, fontFamily: 'JetBrains Mono'}}
                  axisLine={false}
                  tickLine={false}
                  width={45}
                />
                <Tooltip
                  contentStyle={{backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '4px', fontSize: '11px'}}
                  labelStyle={{color: '#94a3b8', fontFamily: 'JetBrains Mono'}}
                  itemStyle={{color: '#f1f5f9'}}
                  formatter={(value, name) => {
                    if (typeof value === 'number' && isNaN(value)) {
                      return ['CALC...', name];
                    }
                    if (typeof value === 'number') {
                      if (name === 'volume') {
                        return [value.toLocaleString(), name];
                      }
                      return [value.toFixed(2), name];
                    }
                    return [value, name];
                  }}
                />
                <Area type="monotone" dataKey="close" stroke={color} fillOpacity={1} fill="url(#colorPrice)" strokeWidth={2} isAnimationActive={false} />
                <ReferenceLine 
                  y={quote.price} 
                  stroke="#FFD700" 
                  strokeDasharray="3 3" 
                  label={{ 
                    value: `CMP: ${quote.price.toFixed(2)}`, 
                    position: 'right', 
                    fill: '#FFD700', 
                    fontSize: 10,
                    fontFamily: 'JetBrains Mono',
                    fontWeight: 'bold'
                  }} 
                />
                <Bar dataKey="volume" fill="#334155" yAxisId={1} opacity={0.2} barSize={4} isAnimationActive={false} />
                <YAxis yAxisId={1} hide />
                <Brush
                  dataKey="datetime"
                  height={20}
                  stroke="#334155"
                  fill="#020617"
                  tickFormatter={() => ''}
                  onChange={handleBrushChange}
                />
              </ComposedChart>
            </ResponsiveContainer>

            {/* Scanning Overlay */}
            {isCapturing && (
              <div className="absolute inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
                <div className="text-center">
                  <div className="w-8 h-8 border-4 border-nexus-accent border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
                  <p className="text-nexus-accent font-mono text-sm uppercase tracking-wider">SCANNING PIXELS...</p>
                  <p className="text-slate-400 text-xs font-mono mt-1">Analyzing chart patterns</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
