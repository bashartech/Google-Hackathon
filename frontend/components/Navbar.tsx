import React from 'react';
import { Search, Bell, Settings, Menu } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function Navbar({ onMenuClick }: { onMenuClick?: () => void }) {
  return (
    <header className="h-20 border-b border-white/5 flex items-center justify-between px-4 sm:px-8 sticky top-0 z-40 bg-surface/50 backdrop-blur-md">
      <div className="flex items-center gap-3">
        {/* Mobile menu button */}
        {onMenuClick && (
          <button className="lg:hidden p-2 rounded-full bg-brand-primary text-white" onClick={onMenuClick}>
            <Menu className="w-6 h-6" />
            <span className="sr-only">Open sidebar</span>
          </button>
        )}
        <div className="flex flex-col">
          <h1 className="text-lg font-semibold tracking-tight text-white">
            SERVICELINK <span className="text-brand-primary">AI</span>
          </h1>
          <p className="text-[10px] uppercase tracking-[0.2em] text-slate-500 font-bold">
            AI Orchestration Layer v4.0
          </p>
        </div>
      </div>
      <div className="flex items-center gap-8">
        <div className="lg:flex items-center gap-2 bg-white/5 px-4 py-1.5 rounded-full border border-white/10 group hover:border-white/20 transition-all">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-xs font-semibold text-slate-300">Agents: 5 Online</span>
        </div>
      </div>
    </header>
  );
}
