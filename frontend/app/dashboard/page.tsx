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

interface Booking {
  booking_id: string;
  service_type: string;
  provider_name: string;
  customer_location: string;
  status: string;
  estimated_cost: string;
  customer_name?: string;
}

export default function DashboardPage() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<Stat[]>([]);
  const [recentBookings, setRecentBookings] = useState<Booking[]>([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      // Fetch dashboard stats
      const statsRes = await fetch('http://localhost:8001/api/dashboard/stats');
      if (!statsRes.ok) {
        throw new Error(`Stats API error: ${statsRes.status}`);
      }
      const statsData = await statsRes.json();

      // Fetch recent bookings
      const bookingsRes = await fetch('http://localhost:8001/api/bookings?limit=10');
      if (!bookingsRes.ok) {
        throw new Error(`Bookings API error: ${bookingsRes.status}`);
      }
      const bookingsData = await bookingsRes.json();

      console.log('Stats Data:', statsData);
      console.log('Bookings Data:', bookingsData);

      // Handle stats data
      if (statsData && (statsData.status === 'success' || statsData.stats)) {
        const stats = statsData.stats || statsData;
        const newStats: Stat[] = [
          {
            label: 'Total Bookings',
            value: stats.total_bookings || 0,
            change: `${stats.active_bookings || 0} Active`,
            trend: 'up',
            icon: Calendar,
            color: 'text-sky-400'
          },
          {
            label: 'Active Bookings',
            value: stats.active_bookings || 0,
            change: 'In Progress',
            trend: 'up',
            icon: TrendingUp,
            color: 'text-indigo-400'
          },
          {
            label: 'Completed',
            value: stats.completed_bookings || 0,
            change: 'Success',
            trend: 'up',
            icon: CheckCircle2,
            color: 'text-emerald-400'
          },
          {
            label: 'Total Providers',
            value: stats.total_providers || 0,
            change: 'Available',
            trend: 'up',
            icon: Users,
            color: 'text-amber-400'
          },
        ];
        setStats(newStats);
      }

      // Handle bookings data - check both response formats
      if (bookingsData) {
        const bookings = bookingsData.bookings || bookingsData.data || [];
        setRecentBookings(bookings.slice(0, 10));
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      console.error('Error details:', error);

      // Set default empty stats on error
      setStats([
        { label: 'Total Bookings', value: 0, change: '0 Active', trend: 'up', icon: Calendar, color: 'text-sky-400' },
        { label: 'Active Bookings', value: 0, change: 'In Progress', trend: 'up', icon: TrendingUp, color: 'text-indigo-400' },
        { label: 'Completed', value: 0, change: 'Success', trend: 'up', icon: CheckCircle2, color: 'text-emerald-400' },
        { label: 'Total Providers', value: 0, change: 'Available', trend: 'up', icon: Users, color: 'text-amber-400' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (bookingId: string, newStatus: string) => {
    try {
      const response = await fetch(`http://localhost:8001/api/bookings/${bookingId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });

      if (response.ok) {
        fetchDashboardData();
      }
    } catch (error) {
      console.error('Error updating booking status:', error);
    }
  };

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
           <h1 className="text-5xl font-black tracking-tight text-white">ServiceLink Dashboard</h1>
           <p className="text-slate-500 font-bold uppercase tracking-widest text-[10px]">Real-time Service Booking Analytics</p>
        </div>

        <button
          onClick={fetchDashboardData}
          className="px-6 py-3 rounded-2xl bg-brand-primary/10 border border-brand-primary/20 text-brand-primary hover:bg-brand-primary/20 transition-all text-xs font-bold"
        >
          Refresh Data
        </button>
      </div>

      {/* Stats Grid */}
      {loading ? (
        <div className="text-center py-20 text-slate-500">Loading dashboard data...</div>
      ) : (
        <>
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

          {/* Recent Bookings Table */}
          <div className="space-y-8">
             <div className="bg-surface-panel rounded-[2.5rem] overflow-hidden border border-white/5 shadow-2xl">
                <div className="px-10 py-8 border-b border-white/5 flex items-center justify-between bg-gradient-to-r from-white/[0.02] to-transparent">
                   <h2 className="font-bold text-xl tracking-tight">Recent Bookings</h2>
                   <Link href="/chat" className="text-[10px] font-black uppercase tracking-widest text-brand-primary hover:text-sky-400 flex items-center gap-2 group">
                      Book Service <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                   </Link>
                </div>

                <div className="overflow-x-auto">
                   <table className="w-full text-left">
                      <thead>
                         <tr className="border-b border-white/5 bg-white/[0.01]">
                            <th className="px-10 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Booking ID</th>
                            <th className="px-10 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Service</th>
                            <th className="px-10 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Location</th>
                            <th className="px-10 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Status</th>
                            <th className="px-10 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Cost</th>
                         </tr>
                      </thead>
                      <tbody className="divide-y divide-white/5">
                         {recentBookings.length === 0 ? (
                           <tr>
                             <td colSpan={5} className="px-10 py-12 text-center text-slate-500">
                               No bookings yet. <Link href="/chat" className="text-brand-primary hover:underline">Create your first booking</Link>
                             </td>
                           </tr>
                         ) : (
                           recentBookings.map((booking, i) => (
                             <tr key={i} className="group hover:bg-white/[0.02] transition-colors">
                                <td className="px-10 py-6 font-mono text-xs text-brand-primary font-bold">{booking.booking_id}</td>
                                <td className="px-10 py-6">
                                   <div className="flex flex-col">
                                      <span className="text-sm font-bold text-white group-hover:text-brand-primary transition-colors">{booking.service_type}</span>
                                      <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-1">{booking.provider_name}</span>
                                   </div>
                                </td>
                                <td className="px-10 py-6 text-xs text-slate-400 font-medium">{booking.customer_location}</td>
                                <td className="px-10 py-6">
                                   <select
                                     value={booking.status}
                                     onChange={(e) => handleStatusUpdate(booking.booking_id, e.target.value)}
                                     className={cn(
                                       "px-3 py-1.5 rounded-xl text-[9px] font-black uppercase tracking-widest border cursor-pointer bg-transparent",
                                       booking.status === 'completed' ? "text-emerald-500 border-emerald-500/20 bg-emerald-500/10" :
                                       booking.status === 'in_progress' ? "text-brand-primary border-brand-primary/20 bg-brand-primary/10" :
                                       booking.status === 'confirmed' ? "text-sky-500 border-sky-500/20 bg-sky-500/10" :
                                       booking.status === 'pending' ? "text-amber-500 border-amber-500/20 bg-amber-500/10" :
                                       "text-red-500 border-red-500/20 bg-red-500/10"
                                     )}
                                   >
                                     <option value="pending">Pending</option>
                                     <option value="confirmed">Confirmed</option>
                                     <option value="in_progress">In Progress</option>
                                     <option value="completed">Completed</option>
                                     <option value="cancelled">Cancelled</option>
                                   </select>
                                </td>
                                <td className="px-10 py-6 font-black text-sm text-white">{booking.estimated_cost}</td>
                             </tr>
                           ))
                         )}
                      </tbody>
                   </table>
                </div>
             </div>
          </div>
        </>
      )}
    </motion.div>
  );
}
