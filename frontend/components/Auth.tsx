import React, { useState } from 'react';
import { User } from '../types';
import { getUsers, saveUser, setCurrentUser } from '../services/storage';
import { Button } from './Button';
import { Terminal, Lock, User as UserIcon } from 'lucide-react';

interface AuthProps {
  onLogin: (user: User) => void;
}

export const Auth: React.FC<AuthProps> = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState(''); // Note: In a real app, hash this!
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Allow login with any non-empty username/password
    if (!username.trim() || !password.trim()) {
      setError('Username and password are required');
      return;
    }

    // Create user without checking existence
    const user: User = {
      id: Math.random().toString(36).substr(2, 9),
      username: username.trim(),
    };

    setCurrentUser(user);
    onLogin(user);
  };

  const handleBypassAuth = () => {
    // Bypass Authentication button
    const devUser: User = {
      id: 'dev',
      username: 'GUEST_TRADER',
    };

    setCurrentUser(devUser);
    onLogin(devUser);
  };

  const handleSkipToDashboard = () => {
    // Create a default user for development
    const devUser: User = {
      id: 'dev-user-' + Date.now(),
      username: 'Developer',
    };

    setCurrentUser(devUser);
    onLogin(devUser);
  };

  const handleToggleMode = () => {
    setIsLogin(!isLogin);
    setError('');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-nexus-900 relative overflow-hidden">
      {/* Background Decor */}
      <div className="absolute inset-0 z-0 opacity-10 pointer-events-none">
        <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-nexus-700 to-nexus-900"></div>
        <div className="grid grid-cols-12 h-full w-full">
            {Array.from({ length: 12 }).map((_, i) => (
                <div key={i} className="border-r border-slate-800 h-full"></div>
            ))}
        </div>
      </div>

      <div className="relative z-10 w-full max-w-md p-8 bg-nexus-800 border border-slate-700 rounded-lg shadow-2xl">
        <div className="flex flex-col items-center mb-8">
          <div className="p-3 bg-nexus-900 rounded-full border border-nexus-accent mb-4">
            <Terminal className="w-8 h-8 text-nexus-accent" />
          </div>
          <h1 className="text-2xl font-mono font-bold text-slate-100 tracking-tight">NEXUS TERMINAL</h1>
          <p className="text-nexus-accent text-xs tracking-widest uppercase mt-1">Institutional Access</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-xs font-mono text-slate-400 mb-2 uppercase">Username</label>
            <div className="relative">
              <UserIcon className="absolute left-3 top-2.5 w-5 h-5 text-slate-500" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full bg-nexus-900 border border-slate-700 text-slate-100 text-sm rounded focus:ring-1 focus:ring-nexus-accent focus:border-nexus-accent block pl-10 p-2.5 font-mono placeholder-slate-600"
                placeholder="TRADER_01"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono text-slate-400 mb-2 uppercase">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-2.5 w-5 h-5 text-slate-500" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-nexus-900 border border-slate-700 text-slate-100 text-sm rounded focus:ring-1 focus:ring-nexus-accent focus:border-nexus-accent block pl-10 p-2.5 font-mono placeholder-slate-600"
                placeholder="••••••••"
              />
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-900/30 border border-red-800 rounded text-red-400 text-xs font-mono">
              [ERROR]: {error}
            </div>
          )}

          <Button type="submit" className="w-full">
            {isLogin ? 'AUTHENTICATE' : 'INITIALIZE NEW ACCOUNT'}
          </Button>
        </form>

        <div className="mt-4 space-y-3">
          <div className="text-center">
            <button
              onClick={() => { setIsLogin(!isLogin); setError(''); }}
              className="text-xs font-mono text-slate-500 hover:text-nexus-accent transition-colors underline mr-4"
            >
              {isLogin ? 'Request New Access ID' : 'Return to Login'}
            </button>

            <button
              onClick={handleSkipToDashboard}
              className="text-xs font-mono text-slate-300 hover:text-nexus-accent transition-colors underline"
            >
              Skip to Dashboard
            </button>
          </div>

          <div className="pt-2">
            <button
              onClick={handleBypassAuth}
              className="w-full py-2 text-xs font-mono bg-slate-700 hover:bg-slate-600 text-slate-200 rounded border border-slate-600 transition-colors"
            >
              BYPASS AUTHENTICATION
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};