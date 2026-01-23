import React from 'react';
import { MarketInstrument, RateProbability, EconomicEvent } from '../types';
import { TrendingUp, TrendingDown, Activity, Globe, Scale } from 'lucide-react';

interface MacroDashboardProps {
  instruments: MarketInstrument[];
  econEvents: EconomicEvent[];
  rateProbs: RateProbability[];
}

interface InstrumentCardProps {
  inst: MarketInstrument;
  onClick?: () => void;
}

const InstrumentCard: React.FC<InstrumentCardProps> = ({ inst, onClick }) => {
  const isPositive = inst.change >= 0;
  const isLive = inst.status && inst.status.toLowerCase() === 'live';

  // Format price differently for bonds (add % suffix) and special handling for DXY
  let formattedPrice = '';
  if (inst.symbol === 'DXY') {
    // Force DXY to display with 2 decimal places regardless of category
    formattedPrice = inst.price.toFixed(2);
  } else if (inst.category === 'bond') {
    formattedPrice = `${inst.price.toFixed(2)}%`;
  } else {
    formattedPrice = inst.price.toFixed(inst.category === 'fx' ? 4 : 2);
  }

  return (
    <div
      className="bg-nexus-800 border border-slate-700 p-3 rounded flex flex-col justify-between hover:border-nexus-accent transition-colors cursor-pointer"
      onClick={onClick}
    >
      <div className="flex justify-between items-start mb-2">
        <div>
          <span className="text-nexus-accent font-mono font-bold text-sm block">{inst.symbol}</span>
          <span className="text-slate-500 text-xs font-mono">{inst.name}</span>
        </div>
        <div className="flex flex-col items-end">
          {isPositive ? <TrendingUp className="w-4 h-4 text-nexus-up" /> : <TrendingDown className="w-4 h-4 text-nexus-down" />}
          <span className={`text-[8px] px-1 py-0.5 rounded mt-1 ${
            isLive
              ? 'bg-green-900/30 text-green-400 border border-green-800/50'
              : 'bg-red-900/30 text-red-400 border border-red-800/50'
          }`}>
            {isLive ? 'LIVE' : 'INACTIVE'}
          </span>
        </div>
      </div>
      <div className="flex justify-between items-baseline">
        <span className="text-slate-100 font-mono text-lg font-bold">{formattedPrice}</span>
        <span className={`text-xs font-mono ${isPositive ? 'text-nexus-up' : 'text-nexus-down'}`}>
          {isPositive ? '+' : ''}{inst.changePercent.toFixed(2)}%
        </span>
      </div>
    </div>
  );
};

interface MacroDashboardProps {
  instruments: MarketInstrument[];
  econEvents: EconomicEvent[];
  rateProbs: RateProbability[];
  onSelectSymbol?: (symbol: string) => void; // New prop for handling symbol selection
}

// Loading indicator component
const LoadingIndicator = () => (
  <div className="h-full w-full flex items-center justify-center">
    <div className="flex flex-col items-center space-y-2">
      <Activity className="w-8 h-8 text-nexus-accent animate-spin" />
      <span className="text-xs font-mono text-slate-500 uppercase">Loading macro data...</span>
    </div>
  </div>
);

export const MacroDashboard: React.FC<MacroDashboardProps> = ({ instruments, econEvents, rateProbs, onSelectSymbol }) => {
  // Safety check at the very top as required
  if (!instruments || instruments.length === 0) return null;
  // For the UI, ensure the filter uses category === 'bond', category === 'future', and category === 'fx'
  // Ensure DXY (if present in the instruments array) is filtered into the 'Indices' section
  const futures = instruments.filter(i => i.category === 'future' || i.symbol === 'DXY'); // Includes INDEX assets and DXY
  const bonds = instruments.filter(i => i.category === 'bond'); // Includes BONDS assets
  const fx = instruments.filter(i => i.category === 'fx'); // Includes METALS assets
  const em = instruments.filter(i => i.category === 'em'); // Includes SECTORS assets
  const stocks = instruments.filter(i => i.category === 'stock');
  const spreads = instruments.filter(i => i.category === 'spread');

  return (
    <div className="h-full overflow-y-auto p-4 bg-nexus-900 space-y-6 scrollbar-thin">
      
      {/* Top Row: Futures & Bonds */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        
        {/* Equity Futures */}
        <div className="bg-nexus-900 border border-slate-700 rounded-lg overflow-hidden">
          <div className="bg-nexus-800 px-3 py-2 border-b border-slate-700 flex items-center justify-between">
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center">
              <Activity className="w-3 h-3 mr-2 text-nexus-accent" />
              Equity Futures (WEF)
            </span>
          </div>
          <div className="p-3 grid grid-cols-2 gap-2">
            {futures.map(i => <InstrumentCard key={i.symbol} inst={i} onClick={() => onSelectSymbol && onSelectSymbol(i.symbol)} />)}
          </div>
        </div>

        {/* Rates & Bonds */}
        <div className="bg-nexus-900 border border-slate-700 rounded-lg overflow-hidden">
           <div className="bg-nexus-800 px-3 py-2 border-b border-slate-700 flex items-center justify-between">
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center">
              <Scale className="w-3 h-3 mr-2 text-nexus-accent" />
              Sovereign Debt (WB)
            </span>
          </div>
          <div className="p-3 grid grid-cols-2 lg:grid-cols-3 gap-2">
            {bonds.map(i => <InstrumentCard key={i.symbol} inst={i} onClick={() => onSelectSymbol && onSelectSymbol(i.symbol)} />)}
          </div>
        </div>
      </div>

      {/* Middle Row: FX, Spreads, EM */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        
        {/* FX */}
        <div className="bg-nexus-900 border border-slate-700 rounded-lg overflow-hidden">
          <div className="bg-nexus-800 px-3 py-2 border-b border-slate-700">
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center">
              <Globe className="w-3 h-3 mr-2 text-nexus-accent" />
              FX Major (WCV)
            </span>
          </div>
          <div className="p-3 space-y-2">
            {fx.map(i => (
               <div
                 key={i.symbol}
                 className="flex justify-between items-center py-1 border-b border-slate-700/50 last:border-0 cursor-pointer hover:bg-slate-800/50 transition-colors"
                 onClick={() => onSelectSymbol && onSelectSymbol(i.symbol)}
               >
                 <span className="text-sm font-mono text-nexus-accent">{i.symbol}</span>
                 <span className="text-sm font-mono text-white">{i.price.toFixed(4)}</span>
                 <span className={`text-xs font-mono ${i.change >= 0 ? 'text-nexus-up' : 'text-nexus-down'}`}>
                   {i.changePercent.toFixed(2)}%
                 </span>
               </div>
            ))}
          </div>
        </div>

        {/* Credit Spreads */}
        <div className="bg-nexus-900 border border-slate-700 rounded-lg overflow-hidden">
           <div className="bg-nexus-800 px-3 py-2 border-b border-slate-700">
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">Credit Spreads (OAS)</span>
          </div>
          <div className="p-3 space-y-2">
             {spreads.map(i => (
               <div
                 key={i.symbol}
                 className="flex justify-between items-center py-1 border-b border-slate-700/50 last:border-0 cursor-pointer hover:bg-slate-800/50 transition-colors"
                 onClick={() => onSelectSymbol && onSelectSymbol(i.symbol)}
               >
                 <div>
                    <span className="text-sm font-mono text-white block">{i.name}</span>
                 </div>
                 <div className="text-right">
                    <span className="text-sm font-mono text-nexus-accent block">{i.price.toFixed(0)} bps</span>
                 </div>
               </div>
            ))}
             <div className="mt-4 text-[10px] text-slate-500 font-mono">
                *OAS indicates spread over risk-free rate. Higher implies more stress.
             </div>
          </div>
        </div>

        {/* EMKT */}
        <div className="bg-nexus-900 border border-slate-700 rounded-lg overflow-hidden">
          <div className="bg-nexus-800 px-3 py-2 border-b border-slate-700">
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center">
                <Globe className="w-3 h-3 mr-2 text-yellow-500" />
                Emerging Mkts (EMKT)
            </span>
          </div>
          <div className="p-3 space-y-2">
            {em.map(i => (
               <div
                 key={i.symbol}
                 className="flex justify-between items-center py-1 border-b border-slate-700/50 last:border-0 cursor-pointer hover:bg-slate-800/50 transition-colors"
                 onClick={() => onSelectSymbol && onSelectSymbol(i.symbol)}
               >
                 <span className="text-sm font-mono text-slate-200">{i.symbol}</span>
                 <span className="text-sm font-mono text-white">{i.price.toFixed(2)}</span>
                 <span className={`text-xs font-mono ${i.change >= 0 ? 'text-nexus-up' : 'text-nexus-down'}`}>
                   {i.changePercent.toFixed(2)}%
                 </span>
               </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Row: Fed Watch & Econ Calendar */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        
        {/* Fed Fund Futures */}
        <div className="bg-nexus-900 border border-slate-700 rounded-lg overflow-hidden">
          <div className="bg-nexus-800 px-3 py-2 border-b border-slate-700">
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">Interest Rate Probabilities (FEDWATCH)</span>
          </div>
          <div className="p-4">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="text-[10px] font-mono text-slate-500 uppercase border-b border-slate-700">
                  <th className="pb-2">Meeting</th>
                  <th className="pb-2 text-right text-red-400">Hike %</th>
                  <th className="pb-2 text-right text-slate-300">Hold %</th>
                  <th className="pb-2 text-right text-green-400">Cut %</th>
                </tr>
              </thead>
              <tbody className="font-mono text-sm">
                {rateProbs.map((r, i) => (
                  <tr key={i} className="border-b border-slate-800 last:border-0 hover:bg-slate-800/50">
                    <td className="py-2 text-nexus-accent">{r.meeting}</td>
                    <td className="py-2 text-right text-slate-300">{r.hike.toFixed(1)}</td>
                    <td className="py-2 text-right text-slate-100 font-bold">{r.hold.toFixed(1)}</td>
                    <td className="py-2 text-right text-slate-300">{r.cut.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Economic Data Snapshot */}
        <div className="bg-nexus-900 border border-slate-700 rounded-lg overflow-hidden">
           <div className="bg-nexus-800 px-3 py-2 border-b border-slate-700 flex justify-between">
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">Economic Calendar (ECST)</span>
            <span className="text-[10px] text-slate-500 font-mono">Top Impact Only</span>
          </div>
          <div className="p-0 overflow-x-auto">
             <table className="w-full text-left">
               <thead className="bg-slate-800/50">
                 <tr className="text-[10px] font-mono text-slate-500 uppercase">
                   <th className="px-3 py-2">Time</th>
                   <th className="px-3 py-2">Ctry</th>
                   <th className="px-3 py-2">Event</th>
                   <th className="px-3 py-2 text-right">Act</th>
                   <th className="px-3 py-2 text-right">Fcst</th>
                 </tr>
               </thead>
               <tbody className="font-mono text-xs">
                 {econEvents.map((e) => (
                   <tr key={e.id} className="border-b border-slate-800 hover:bg-slate-800/30">
                     <td className="px-3 py-2 text-slate-400">{e.time}</td>
                     <td className="px-3 py-2 text-slate-300">{e.country}</td>
                     <td className="px-3 py-2 text-nexus-accent font-medium truncate max-w-[120px]">{e.event}</td>
                     <td className="px-3 py-2 text-right text-white font-bold">{e.actual}</td>
                     <td className="px-3 py-2 text-right text-slate-500">{e.forecast}</td>
                   </tr>
                 ))}
               </tbody>
             </table>
          </div>
        </div>

      </div>
    </div>
  );
};