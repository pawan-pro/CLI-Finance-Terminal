import React, { useState, useEffect, useRef } from 'react';
import { User, ChatMessage } from '../types';
import { subscribeToChat, sendPublicMessage, getChatHistory } from '../services/storage';
import { Send, Users } from 'lucide-react';

interface PublicChatProps {
  currentUser: User;
}

export const PublicChat: React.FC<PublicChatProps> = ({ currentUser }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Load initial history
    setMessages(getChatHistory());

    // Subscribe to real-time updates
    const unsubscribe = subscribeToChat((msg) => {
      setMessages(prev => [...prev, msg]);
    });

    return () => unsubscribe();
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    const newMessage: ChatMessage = {
      id: Math.random().toString(36).substr(2, 9),
      userId: currentUser.id,
      username: currentUser.username,
      content: inputText,
      timestamp: Date.now(),
    };

    // Optimistic update for sender
    setMessages(prev => [...prev, newMessage]);
    
    // Send to others
    sendPublicMessage(newMessage);
    
    setInputText('');
  };

  return (
    <div className="flex flex-col h-full bg-nexus-800 border border-slate-700 rounded-lg overflow-hidden">
      <div className="p-3 bg-nexus-900 border-b border-slate-700 flex items-center justify-between">
        <h3 className="text-xs font-mono font-bold text-nexus-accent uppercase tracking-wider flex items-center">
          <Users className="w-3 h-3 mr-2" />
          Public Floor
        </h3>
        <div className="flex items-center space-x-1">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
          <span className="text-[10px] text-slate-400 font-mono">LIVE</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3 bg-nexus-800 scrollbar-thin">
        {messages.length === 0 && (
          <div className="text-center text-slate-500 text-xs font-mono py-10">No messages yet. Start the conversation.</div>
        )}
        {messages.map((msg) => {
          const isMe = msg.userId === currentUser.id;
          return (
            <div key={msg.id} className={`flex flex-col ${isMe ? 'items-end' : 'items-start'}`}>
              <div className="flex items-baseline space-x-2 mb-1">
                <span className={`text-[10px] font-mono font-bold ${isMe ? 'text-nexus-accent' : 'text-blue-400'}`}>
                  {msg.username}
                </span>
                <span className="text-[10px] text-slate-600 font-mono">
                  {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
              <div className={`px-3 py-2 rounded text-sm max-w-[85%] break-words shadow-sm border ${
                isMe 
                ? 'bg-nexus-700 text-slate-100 border-slate-600' 
                : 'bg-slate-800 text-slate-200 border-slate-700'
              }`}>
                {msg.content}
              </div>
            </div>
          );
        })}
        <div ref={endRef} />
      </div>

      <form onSubmit={handleSend} className="p-2 bg-nexus-900 border-t border-slate-700">
        <div className="relative">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            className="w-full bg-nexus-800 border border-slate-700 text-slate-200 text-sm rounded pl-3 pr-10 py-2 focus:ring-1 focus:ring-nexus-accent focus:border-nexus-accent focus:outline-none font-mono placeholder-slate-600"
            placeholder="Broadcast message..."
          />
          <button 
            type="submit" 
            className="absolute right-2 top-2 text-slate-400 hover:text-nexus-accent transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
};