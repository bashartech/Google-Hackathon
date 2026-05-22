"use client";
import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, MessageSquare, LayoutDashboard, Settings, Mail } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function Sidebar({ isOpen = false, onClose }: { isOpen?: boolean, onClose?: () => void }) {
  const location = usePathname();

  const navLinks = [
    { path: '/', icon: Home, label: 'Home' },
    { path: '/chat', icon: MessageSquare, label: 'Chat' },
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  ];

  // Responsive sidebar for mobile
  return (
    <aside
      className={cn(
        "z-40 flex flex-col items-center py-8 gap-10 bg-surface h-screen top-0 transition-transform duration-300",
        "fixed md:sticky left-0",
        isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0",
        "w-56 md:w-20 border-r border-white/5"
      )}
      style={{ boxShadow: isOpen ? '0 0 0 9999px rgba(0,0,0,0.4)' : undefined }}
    >
      <div className="w-10 h-10 bg-brand-primary rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(14,165,233,0.4)] transition-transform hover:scale-110 mb-6">
        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </div>
      {onClose && (
        <button className="md:hidden absolute top-4 right-4 text-white bg-brand-primary rounded-full p-2" onClick={onClose}>
          <span className="sr-only">Close sidebar</span>
          &times;
        </button>
      )}
      <nav className="flex flex-col gap-6 w-full items-center">
        {navLinks.map((link) => {
          const isActive = location === link.path;
          const Icon = link.icon;
          return (
            <Link
              key={link.path}
              href={link.path}
              className={cn(
                "flex items-center gap-3 p-3 rounded-2xl transition-all duration-300 relative group w-44 md:w-auto justify-start md:justify-center",
                isActive 
                  ? "text-brand-primary bg-brand-primary/10 shadow-sm" 
                  : "text-slate-500 hover:text-white hover:bg-white/5"
              )}
              title={link.label}
              onClick={onClose}
            >
              <Icon className="w-6 h-6" />
              <span className="hidden md:inline absolute left-full ml-4 px-2 py-1 bg-surface-panel border border-white/10 rounded text-[10px] font-bold uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
                {link.label}
              </span>
              <span className="md:hidden ml-2 text-sm font-bold">{link.label}</span>
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
