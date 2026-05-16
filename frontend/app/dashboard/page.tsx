"use client"
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Wrench, Calendar, Star, TrendingUp, Users, Search, 
  ArrowUpRight, Clock, MapPin, Filter, MoreHorizontal,
  CheckCircle2, AlertCircle, Play
} from 'lucide-react';
import { cn } from '@/lib/utils';
import Link from 'next/link';

interface Stat {
  label: string;
  value: string | number;
  change: string;
  trend: 'up' | 'down';
  icon: any;
  color: string;
}

export default function DashboardPage() {
  const [loading, setLoading] = useState(false);

  const stats: Stat[] = [
    { label: 'Network Throughput', value: '1.4 TB', change: '+12%', trend: 'up', icon: TrendingUp, color: 'text-sky-400' },
    { label: 'Active Sessions', value: '42', change: '+5%', trend: 'up', icon: Calendar, color: 'text-indigo-400' },
    { label: 'Agent Availability', value: '99.99%', change: 'Stable', trend: 'up', icon: Clock, color: 'text-emerald-400' },
    { label: 'Precision Score', value: '98.5', change: '+0.2', trend: 'up', icon: Star, color: 'text-amber-400' },
  ];

  const recentBookings = [
    { id: 'NX-9021', service: 'AC Core Repair', provider: 'FastCool Protocols', area: 'G-13 Cluster', status: 'In Progress', cost: '$120' },
    { id: 'NX-9022', service: 'Neural Electric Fix', provider: 'Sparky AI', area: 'F-10 Hub', status: 'Completed', cost: '$85' },
    { id: 'NX-9023', service: 'Critical Plumbing', provider: 'FlowOrchestra', area: 'Central Node', status: 'Pending', cost: '$45' },
    { id: 'NX-9024', service: 'Environment Clean', provider: 'Higiene Nexus', area: 'Sector I-8', status: 'Cancelled', cost: '$150' },
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="py-12 px-8 max-w-7xl mx-auto"
    >
      {/* Dashboard Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-8 mb-16">
        <div className="space-y-2">
           <h1 className="text-5xl font-black tracking-tight text-white">System Nexus</h1>
           <p className="text-slate-500 font-bold uppercase tracking-widest text-[10px]">AI Orchestration Control Panel</p>
        </div>
        
        <div className="flex items-center gap-4">
           <div className="flex bg-white/5 rounded-2xl p-1 border border-white/5">
              {['Live', 'History', 'Forecast'].map((range) => (
                <button 
                  key={range}
                  className={cn(
                    "px-6 py-2 text-[10px] font-black uppercase tracking-widest rounded-xl transition-all",
                    range === 'Live' ? "bg-white/10 text-white shadow-sm" : "text-slate-500 hover:text-white/60"
                  )}
                >
                  {range}
                </button>
              ))}
           </div>
           <button className="p-3 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 text-slate-400">
              <Filter className="w-5 h-5" />
           </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
        {stats.map((stat, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.1 }}
            className="group p-8 rounded-[2rem] border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] transition-all relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 p-8 opacity-[0.03] group-hover:opacity-[0.06] transition-opacity">
               <stat.icon className="w-24 h-24 rotate-12" />
            </div>
            
            <div className="flex items-center justify-between mb-8">
              <div className={cn("p-3 rounded-2xl bg-white/5 border border-white/5", stat.color)}>
                 <stat.icon className="w-6 h-6" />
              </div>
              <div className={cn(
                "flex items-center text-[9px] font-black uppercase tracking-widest px-3 py-1 rounded-full border",
                stat.trend === 'up' ? "text-emerald-400 bg-emerald-400/10 border-emerald-400/20" : "text-red-400 bg-red-400/10 border-red-400/20"
              )}>
                 <ArrowUpRight className="w-3.5 h-3.5 mr-1" />
                 {stat.change}
              </div>
            </div>
            
            <div className="space-y-1 relative z-10">
               <div className="text-4xl font-black text-white tracking-tighter">{stat.value}</div>
               <div className="text-[10px] font-black text-slate-600 uppercase tracking-[0.2em]">{stat.label}</div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
        
        {/* Recent Activity Table */}
        <div className="lg:col-span-2 space-y-8">
           <div className="bg-surface-panel rounded-[2.5rem] overflow-hidden border border-white/5 shadow-2xl">
              <div className="px-10 py-8 border-b border-white/5 flex items-center justify-between bg-gradient-to-r from-white/[0.02] to-transparent">
                 <h2 className="font-bold text-xl tracking-tight">Active Operation Pipeline</h2>
                 <Link href="/chat" className="text-[10px] font-black uppercase tracking-widest text-brand-primary hover:text-sky-400 flex items-center gap-2 group">
                    Neural Interface <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                 </Link>
              </div>

              <div className="overflow-x-auto">
                 <table className="w-full text-left">
                    <thead>
                       <tr className="border-b border-white/5 bg-white/[0.01]">
                          <th className="px-10 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Op ID</th>
                          <th className="px-10 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Service Unit</th>
                          <th className="px-10 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Region</th>
                          <th className="px-10 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Status</th>
                          <th className="px-10 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Volume</th>
                       </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                       {recentBookings.map((bk, i) => (
                         <tr key={i} className="group hover:bg-white/[0.02] transition-colors cursor-pointer">
                            <td className="px-10 py-6 font-mono text-xs text-brand-primary font-bold">{bk.id}</td>
                            <td className="px-10 py-6">
                               <div className="flex flex-col">
                                  <span className="text-sm font-bold text-white group-hover:text-brand-primary transition-colors">{bk.service}</span>
                                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-1">{bk.provider}</span>
                               </div>
                            </td>
                            <td className="px-10 py-6 text-xs text-slate-400 font-medium">{bk.area}</td>
                            <td className="px-10 py-6">
                               <div className={cn(
                                 "inline-flex items-center gap-2 px-3 py-1.5 rounded-xl text-[9px] font-black uppercase tracking-widest",
                                 bk.status === 'Completed' ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20" :
                                 bk.status === 'In Progress' ? "bg-brand-primary/10 text-brand-primary border border-brand-primary/20" :
                                 bk.status === 'Pending' ? "bg-amber-500/10 text-amber-500 border border-amber-500/20" :
                                 "bg-red-500/10 text-red-500 border border-red-500/20"
                               )}>
                                  {bk.status === 'Completed' && <CheckCircle2 className="w-3.5 h-3.5" />}
                                  {bk.status === 'In Progress' && <Play className="w-3.5 h-3.5" />}
                                  {bk.status === 'Pending' && <Clock className="w-3.5 h-3.5" />}
                                  {bk.status === 'Cancelled' && <AlertCircle className="w-3.5 h-3.5" />}
                                  {bk.status}
                               </div>
                            </td>
                            <td className="px-10 py-6 font-black text-sm text-white">{bk.cost}</td>
                         </tr>
                       ))}
                    </tbody>
                 </table>
              </div>
           </div>
        </div>

        {/* Side Panels */}
        <div className="space-y-10">
           {/* Top Performers */}
           <div className="bg-surface-panel p-10 rounded-[2.5rem] border border-white/5 shadow-2xl">
              <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 mb-10 flex items-center justify-between">
                 Elite Providers
                 <MoreHorizontal className="w-5 h-5 text-slate-700" />
              </h3>
              <div className="space-y-8">
                 {[
                   { name: 'UltraFlow Plumbers', score: 4.9, jobs: 120, img: '🌊' },
                   { name: 'ColdBox Experts', score: 4.8, jobs: 94, img: '❄️' },
                   { name: 'SparkPoint Elec', score: 4.9, jobs: 86, img: '⚡' },
                 ].map((p, i) => (
                   <div key={i} className="flex items-center gap-5 group">
                      <div className="w-14 h-14 rounded-2xl bg-white/2 border border-white/10 flex items-center justify-center text-2xl grayscale group-hover:grayscale-0 group-hover:scale-110 transition-all shadow-inner">
                         {p.img}
                      </div>
                      <div className="flex-1">
                         <div className="text-sm font-bold text-white group-hover:text-brand-primary transition-colors">{p.name}</div>
                         <div className="text-[10px] text-slate-600 font-bold uppercase tracking-widest mt-1">{p.jobs} Cycles</div>
                      </div>
                      <div className="text-right">
                         <div className="text-lg font-black text-amber-400">{p.score}</div>
                         <div className="text-[9px] text-slate-600 font-black uppercase tracking-widest">Score</div>
                      </div>
                   </div>
                 ))}
              </div>
           </div>

           {/* System Health */}
           <div className="bg-surface-panel p-10 rounded-[2.5rem] border border-white/5 bg-gradient-to-br from-brand-primary/[0.03] to-transparent shadow-2xl">
              <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 mb-8">System Health</h3>
              <div className="space-y-6">
                 {[
                   { label: 'Neural Latency', val: '240ms', color: 'bg-emerald-500' },
                   { label: 'Logic Accuracy', val: '98.2%', color: 'bg-brand-primary' },
                   { label: 'Cluster Load', val: 'Optimal', color: 'bg-emerald-500' },
                 ].map((h, i) => (
                   <div key={i} className="flex flex-col gap-2">
                      <div className="flex items-center justify-between">
                         <span className="text-[10px] font-black uppercase tracking-widest text-slate-600">{h.label}</span>
                         <span className="text-xs font-black text-white">{h.val}</span>
                      </div>
                      <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                         <motion.div 
                           initial={{ width: 0 }}
                           animate={{ width: i === 1 ? '98.2%' : '100%' }}
                           className={cn("h-full rounded-full", h.color)}
                         />
                      </div>
                   </div>
                 ))}
              </div>
           </div>
        </div>

      </div>
    </motion.div>
  );
}
