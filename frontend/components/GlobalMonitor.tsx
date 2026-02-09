import React, { useState, useEffect, useMemo } from 'react';
import { AreaChart, Area, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { fetchMultipleMarketData } from '../services/marketDataService';
import { MarketInstrument } from '../types';

interface ChartDataPoint {
  time: string;
  [key: string]: number | string;
}

interface CorrelationMatrix {
  [key: string]: {
    [key: string]: number;
  };
}

interface RiskIndicator {
  label: string;
  value: number;
  max: number;
}

interface GlobalMonitorProps {
  instruments: MarketInstrument[];
  onSelectSymbol: (symbol: string) => void;
}

const GlobalMonitor: React.FC<GlobalMonitorProps> = ({ instruments, onSelectSymbol }) => {
  const [rawData, setRawData] = useState<any>(null);
  const [correlationMatrix, setCorrelationMatrix] = useState<CorrelationMatrix>({});
  const [riskIndicators, setRiskIndicators] = useState<RiskIndicator[]>([
    { label: "Risk-On/Off Sentiment", value: 65, max: 100 },
    { label: "Equity-Bond Divergence", value: 32, max: 100 },
    { label: "USD Strength Index", value: 78, max: 100 }
  ]);

  // Define the asset pairs for each panel
  const panels = [
    { id: 'A1', title: 'Equities Beta', assets: ['US500Roll', 'UT100Roll'], type: 'area' },
    { id: 'A2', title: 'Global Value', assets: ['JP225Roll', 'DE40Roll'], type: 'area' },
    { id: 'B1', title: 'Dollar Dynamics', assets: ['EURUSD.sd', 'DXY'], type: 'line' },
    { id: 'B2', title: 'Yen/CNH Carry', assets: ['USDJPY.sd', 'USDCNH.sd'], type: 'line' },
    { id: 'C1', title: 'Hard Assets', assets: ['XAUUSD.sd', 'USOILRoll'], type: 'area' },
    { id: 'C2', title: 'Rates Curve', assets: ['US10Y.px', 'US02Y'], type: 'area' }
  ];

  // 1. SAFE DATA FETCH (Reduced history to 30 bars to save RAM)
  useEffect(() => {
    const fetchGlobalData = async () => {
      try {
        const allSymbols = ['US500Roll', 'UT100Roll', 'JP225Roll', 'DE40Roll', 'EURUSD.sd', 'DXY', 'USDJPY.sd', 'USDCNH.sd', 'XAUUSD.sd', 'USOILRoll', 'US10Y.px', 'US02Y'];
        const data = await fetchMultipleMarketData(allSymbols, '15min', 30);
        if (data && data.data) setRawData(data.data);
      } catch (e) { console.error(e); }
    };
    fetchGlobalData();
    fetchCorrelationData();
  }, []);

  const fetchCorrelationData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/correlation');
      const data = await response.json();
      setCorrelationMatrix(data);
    } catch (e) { console.error(e); }
  };

  // 2. PERFORMANCE FIX: Memoize the data transformation
  // This ensures the heavy math only runs when data arrives, NOT when the mouse moves.
  const chartData = useMemo(() => {
    if (!rawData) return [];

    const symbols = Object.keys(rawData);
    if (symbols.length === 0) return [];

    // Use the first symbol as the master timeline to avoid the infinite while-loop
    const masterTimeline = rawData[symbols[0]];

    return masterTimeline.map((point: any, idx: number) => {
      const row: any = { time: point.time_utc };
      symbols.forEach(sym => {
        const symPoint = rawData[sym][idx];
        if (symPoint) {
          row[sym] = symPoint.close;
          // Calculate % change relative to the start of the window
          const startPrice = rawData[sym][0].close;
          row[`${sym}_norm`] = ((symPoint.close - startPrice) / startPrice) * 100;
        }
      });
      return row;
    });
  }, [rawData]);

  // 3. RENDER FIX: Simplified Chart (No animations to save RAM)
  const renderChart = (panel: any) => {
    if (chartData.length === 0) return <div className="text-[10px] animate-pulse">SYNCING...</div>;

    const isArea = panel.type === 'area';
    const ChartComponent = isArea ? AreaChart : LineChart;

    return (
      <ChartComponent data={chartData} syncId="global-sync">
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
        <XAxis dataKey="time" hide />
        <YAxis hide domain={['auto', 'auto']} />
        <Tooltip
            isAnimationActive={false} // CRITICAL: Stop GPU drain
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '10px' }}
        />
        {panel.assets.map((asset: string, i: number) => (
          isArea ? (
            <Area
              key={asset}
              type="monotone"
              dataKey={`${asset}_norm`}
              stroke={i === 0 ? '#3b82f6' : '#10b981'}
              fill={i === 0 ? '#3b82f6' : '#10b981'}
              fillOpacity={0.1}
              isAnimationActive={false} // CRITICAL
              dot={false}
            />
          ) : (
            <Line
              key={asset}
              type="monotone"
              dataKey={`${asset}_norm`}
              stroke={i === 0 ? '#f59e0b' : '#8b5cf6'}
              strokeWidth={2}
              isAnimationActive={false} // CRITICAL
              dot={false}
            />
          )
        ))}
      </ChartComponent>
    );
  };

  // Render correlation heatmap
  const renderCorrelationHeatmap = () => {
    const symbols = ['US500Roll', 'UT100Roll', 'XAUUSD.sd', 'USOILRoll', 'US10Y.px', 'EURUSD.sd'];

    return (
      <div className="grid grid-cols-6 gap-0.5 bg-slate-800 rounded-md overflow-hidden">
        {symbols.map(rowSym => (
          symbols.map(colSym => {
            const value = correlationMatrix[rowSym]?.[colSym] ?? 0;
            const absValue = Math.abs(value);
            const intensity = Math.round(absValue * 100);

            // Determine color based on correlation strength and direction
            let bgColor = '';
            if (value > 0) {
              // Positive correlation - shades of blue
              if (intensity > 70) bgColor = 'bg-blue-900/80';
              else if (intensity > 40) bgColor = 'bg-blue-700/60';
              else bgColor = 'bg-blue-500/40';
            } else {
              // Negative correlation - shades of red
              if (intensity > 70) bgColor = 'bg-red-900/80';
              else if (intensity > 40) bgColor = 'bg-red-700/60';
              else bgColor = 'bg-red-500/40';
            }

            return (
              <div
                key={`${rowSym}-${colSym}`}
                className={`h-8 flex items-center justify-center ${bgColor} border border-slate-700`}
                title={`${rowSym} vs ${colSym}: ${value.toFixed(2)}`}
              >
                <span className="text-[8px] font-mono text-slate-200">
                  {value.toFixed(2)}
                </span>
              </div>
            );
          })
        ))}
      </div>
    );
  };

  // Render risk indicators
  const renderRiskIndicators = () => {
    return (
      <div className="grid grid-cols-3 gap-2">
        {riskIndicators.map((indicator, index) => (
          <div key={index} className="bg-slate-800/50 border border-slate-700 rounded p-2">
            <div className="text-[9px] font-mono text-slate-400 mb-1 truncate">{indicator.label}</div>
            <div className="w-full bg-slate-700 rounded-full h-1.5">
              <div
                className="bg-gradient-to-r from-emerald-500 to-amber-500 h-1.5 rounded-full"
                style={{ width: `${(indicator.value / indicator.max) * 100}%` }}
              ></div>
            </div>
            <div className="text-[10px] font-mono text-right mt-1">
              <span className="text-slate-300">{indicator.value}</span>
              <span className="text-slate-500">/{indicator.max}</span>
            </div>
          </div>
        ))}
      </div>
    );
  };

  // Create watchlist grouped by asset class
  const groupedInstruments = instruments.reduce((acc: Record<string, MarketInstrument[]>, instrument) => {
    const category = instrument.category.toUpperCase();
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(instrument);
    return acc;
  }, {});

  return (
    <div className="h-full w-full bg-nexus-900 grid grid-rows-[1fr_130px] overflow-hidden">
        {/* Chart Grid */}
        <div className="grid grid-cols-2 grid-rows-3 gap-1 p-1">
            {panels.map(p => (
                <div key={p.id} className="bg-nexus-800/50 border border-slate-800 rounded p-1 flex flex-col">
                    <div className="flex justify-between text-[10px] font-mono mb-1 px-1">
                        <span className="text-slate-400">{p.title}</span>
                        <span className="text-nexus-gold">{p.assets.join(' / ')}</span>
                    </div>
                    <div className="flex-1">
                        <ResponsiveContainer width="100%" height="100%">
                            {renderChart(p)}
                        </ResponsiveContainer>
                    </div>
                </div>
            ))}
        </div>

        {/* Correlation Heatmap (Kept simple) */}
        <div className="border-t border-slate-800 p-2 flex gap-4 bg-nexus-950">
             {/* Heatmap implementation here... */}
             <div className="flex-1">
              <div className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-widest mb-1">CORRELATION MATRIX</div>
              {Object.keys(correlationMatrix).length > 0 ? renderCorrelationHeatmap() : (
                <div className="h-20 w-full flex items-center justify-center bg-slate-800/50 rounded">
                  <div className="text-xs font-mono text-slate-600">LOADING CORRELATIONS...</div>
                </div>
              )}
            </div>
            <div className="w-2/5">
              <div className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-widest mb-1">RISK INDICATORS</div>
              {renderRiskIndicators()}
            </div>
        </div>
    </div>
  );
};

export default GlobalMonitor;