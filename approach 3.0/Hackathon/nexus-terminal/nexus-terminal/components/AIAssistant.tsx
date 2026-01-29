import React, { useState, useEffect, useRef } from 'react';
import { AIChatMessage, MarketContext } from '../types';
import { sendMessageToGemini } from '../services/geminiService';
import { Bot, Send, Loader2, Sparkles, Filter } from 'lucide-react';

interface AIAssistantProps {
  marketContext: MarketContext;
}

export const AIAssistant: React.FC<AIAssistantProps> = ({ marketContext }) => {
  const [messages, setMessages] = useState<AIChatMessage[]>([
    {
      id: 'init',
      role: 'model',
      content: 'Nexus AI Terminal engaged. I am monitoring live feeds and your chart interactions. How can I assist with your strategy?',
      timestamp: Date.now()
    }
  ]);

  // Add vision analysis to messages when it's available
  useEffect(() => {
    if (marketContext.visionAnalysis) {
      const visionMsg: AIChatMessage = {
        id: `vision-${Date.now()}`,
        role: 'model',
        content: `📊 AGENTIC VISION ANALYSIS\n\n${marketContext.visionAnalysis}`,
        timestamp: Date.now()
      };
      setMessages(prev => [...prev, visionMsg]);
    }
  }, [marketContext.visionAnalysis]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg: AIChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    const response = await sendMessageToGemini(messages, input, marketContext);

    const modelMsg: AIChatMessage = {
      id: (Date.now() + 1).toString(),
      role: 'model',
      content: response,
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, modelMsg]);
    setIsLoading(false);
  };

  return (
    <div className="flex flex-col h-full bg-nexus-900 border-l border-slate-800">
      <div className="p-3 border-b border-slate-800 bg-nexus-900 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 bg-nexus-accent/10 rounded border border-nexus-accent/30">
            <Bot size={16} className="text-nexus-accent" />
          </div>
          <div>
            <h3 className="text-[10px] font-mono font-bold text-white uppercase tracking-tighter">NEXUS_ASSISTANT</h3>
            <div className="flex items-center space-x-1">
               <span className="text-[8px] font-mono text-slate-500 uppercase">Context Sync: </span>
               <span className="text-[8px] font-mono text-green-500 animate-pulse">ACTIVE</span>
            </div>
          </div>
        </div>
        <Sparkles size={14} className="text-nexus-accent opacity-50" />
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar bg-slate-950/30">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[95%] rounded-lg p-3 text-xs leading-relaxed ${
              msg.role === 'user' 
                ? 'bg-nexus-700 text-slate-100 rounded-tr-none' 
                : 'bg-nexus-800/80 border border-slate-700 text-slate-300 rounded-tl-none font-sans'
            }`}>
              {msg.content.split('\n').map((line, i) => (
                <p key={i} className={line.startsWith('•') || line.startsWith('-') ? 'ml-2 mb-1' : 'mb-2 last:mb-0'}>
                  {line}
                </p>
              ))}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-nexus-800/80 border border-slate-700 rounded-lg p-3 flex items-center space-x-2">
              <Loader2 size={12} className="text-nexus-accent animate-spin" />
              <span className="text-[10px] font-mono text-slate-500 uppercase">Analyzing Market Conditions...</span>
            </div>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      <div className="p-3 border-t border-slate-800 bg-nexus-900">
        {marketContext.selectedRange.startDate && (
           <div className="mb-2 px-2 py-1 bg-nexus-accent/5 border border-nexus-accent/20 rounded flex items-center justify-between animate-in fade-in duration-500">
             <div className="flex items-center text-[8px] font-mono text-nexus-accent">
               <Filter size={10} className="mr-1.5" />
               FOCUSED ON CHART RANGE
             </div>
             <span className="text-[8px] font-mono text-slate-500 italic">SYNC ENABLED</span>
           </div>
        )}
        <form onSubmit={handleSend} className="relative group">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
            className="w-full bg-slate-950 border border-slate-700 text-slate-200 text-xs rounded pl-3 pr-10 py-2.5 focus:border-nexus-accent focus:ring-0 focus:outline-none font-mono placeholder-slate-700 transition-all"
            placeholder="Search, analyze, verify..."
          />
          <button 
            type="submit" 
            disabled={isLoading || !input.trim()}
            className="absolute right-2 top-2 p-1 text-slate-600 hover:text-nexus-accent disabled:opacity-30 transition-colors"
          >
            <Send size={14} />
          </button>
        </form>
      </div>
    </div>
  );
};
