import React from 'react';
import { Search, Bell, Settings } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function Navbar() {
  return (
    <header className="h-20 border-b border-white/5 flex items-center justify-between px-8 sticky top-0 z-40 bg-surface/50 backdrop-blur-md">
      <div className="flex flex-col">
        <h1 className="text-lg font-semibold tracking-tight text-white">
          ServiceLink <span className="text-brand-primary">Nexus</span>
        </h1>
        <p className="text-[10px] uppercase tracking-[0.2em] text-slate-500 font-bold">
          AI Orchestration Layer v4.0
        </p>
      </div>
      
      <div className="flex items-center gap-8">
        <div className="hidden lg:flex items-center gap-2 bg-white/5 px-4 py-1.5 rounded-full border border-white/10 group hover:border-white/20 transition-all">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-xs font-semibold text-slate-300">Agents: 5 Online</span>
        </div>
        
        <div className="flex items-center gap-5 text-slate-400">
          <button className="hover:text-white transition-colors relative group">
            <Search className="w-5 h-5" />
            <span className="absolute -bottom-10 left-1/2 -translate-x-1/2 px-2 py-1 bg-surface-panel border border-white/10 rounded text-[10px] font-bold uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity">Search</span>
          </button>
          <button className="hover:text-white transition-colors relative group">
            <Bell className="w-5 h-5" />
            <span className="absolute -bottom-10 left-1/2 -translate-x-1/2 px-2 py-1 bg-surface-panel border border-white/10 rounded text-[10px] font-bold uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity">Notifications</span>
            <span className="absolute top-0 right-0 w-2 h-2 bg-brand-primary rounded-full border-2 border-surface"></span>
          </button>
          <button className="hover:text-white transition-colors relative group">
            <Settings className="w-5 h-5" />
            <span className="absolute -bottom-10 left-1/2 -translate-x-1/2 px-2 py-1 bg-surface-panel border border-white/10 rounded text-[10px] font-bold uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity">Settings</span>
          </button>
        </div>

        <button className="bg-brand-primary hover:bg-sky-500 text-white px-5 py-2 rounded-xl text-sm font-bold transition-all shadow-[0_0_15px_rgba(14,165,233,0.3)]">
          Upgrade Pro
        </button>
      </div>
    </header>
  );
}
