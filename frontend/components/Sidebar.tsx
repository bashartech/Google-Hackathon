"use client";
import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, MessageSquare, LayoutDashboard, Settings, Mail } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function Sidebar() {
  const location = usePathname();

  const navLinks = [
    { path: '/', icon: Home, label: 'Home' },
    { path: '/chat', icon: MessageSquare, label: 'Chat' },
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/messages', icon: Mail, label: 'Messages' },
  ];

  return (
    <aside className="w-20 border-r border-white/5 hidden md:flex flex-col items-center py-8 gap-10 bg-surface h-screen sticky top-0">
      <div className="w-10 h-10 bg-brand-primary rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(14,165,233,0.4)] transition-transform hover:scale-110">
        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </div>
      
      <nav className="flex flex-col gap-6">
        {navLinks.map((link) => {
          const isActive = location === link.path;
          const Icon = link.icon;
          return (
            <Link
              key={link.path}
              href={link.path}
              className={cn(
                "p-3 rounded-2xl transition-all duration-300 relative group",
                isActive 
                  ? "text-brand-primary bg-brand-primary/10 shadow-sm" 
                  : "text-slate-500 hover:text-white hover:bg-white/5"
              )}
              title={link.label}
            >
              <Icon className="w-6 h-6" />
              {isActive && (
                <span className="absolute -left-1 top-1/2 -translate-y-1/2 w-1 h-6 bg-brand-primary rounded-r-full" />
              )}
              <span className="absolute left-full ml-4 px-2 py-1 bg-surface-panel border border-white/10 rounded text-[10px] font-bold uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
                {link.label}
              </span>
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto">
        <div className="w-10 h-10 rounded-full border-2 border-brand-primary/20 p-0.5 cursor-pointer hover:border-brand-primary/50 transition-colors">
          <div className="w-full h-full rounded-full bg-gradient-to-tr from-sky-600 to-indigo-500"></div>
        </div>
      </div>
    </aside>
  );
}
