/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { motion, Variants } from 'framer-motion';
import { Sparkles, ArrowRight} from 'lucide-react';
import Link from 'next/link';
interface HeroProps {
  onAccessSandbox: () => void;
  onAccessDashboard: () => void;
}

export default function Hero({ onAccessSandbox, onAccessDashboard }: HeroProps) {
  const itemVariants: Variants = {
    hidden: { opacity: 0, y: 25 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.8, ease: [0.16, 1, 0.3, 1] },
    },
  };

  return (
    <section className="relative pt-36 pb-20 px-6 max-w-6xl mx-auto flex flex-col items-center text-center">
      {/* Background Orbs */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-brand-primary/10 rounded-full blur-[120px] pointer-events-none -z-10" />
      <div className="absolute top-1/3 left-1/4 w-[300px] h-[300px] bg-brand-secondary/5 rounded-full blur-[100px] pointer-events-none -z-10" />

   

      {/* Re-designed Core Hero Text */}
      <motion.h1 
        variants={itemVariants}
        className="text-5xl md:text-7xl lg:text-8xl font-black tracking-tight leading-[1.05] mb-6 max-w-5xl"
        id="hero-title"
      >
        Orchestrating Pakistan's <br />
        <span className="text-gradient">Informal Home Services.</span>
      </motion.h1>

      <motion.p 
        variants={itemVariants}
        className="text-base md:text-lg text-slate-300 max-w-2xl leading-relaxed mb-10 font-normal"
        id="hero-description"
      >
        Experience a production-grade multi-agent autonomous booking platform. 
        Five specialized AI agents coordinate natural language intent parsing, mapping calculations, 
        and Google Calendar availability checks across <strong>Karachi, Lahore, and Islamabad</strong>.
      </motion.p>

      {/* Call to Actions */}
      <motion.div 
        variants={itemVariants} 
        className="flex flex-col sm:flex-row gap-4 mb-20 z-10"
        id="hero-actions"
      >
        <Link href="/chat">
          <button
            className="group px-8 py-4 bg-brand-primary text-white rounded-2xl font-bold text-sm tracking-wide flex items-center justify-center gap-2 hover:bg-blue-600 hover:shadow-[0_0_25px_rgba(37,99,235,0.4)] transition-all duration-300 active:scale-95 cursor-pointer"
          >
            Open Autonomous Sandbox
          <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </button>
        </Link>
        <Link href="/dashboard">
          <button
            className="px-8 py-4 bg-white/5 text-white/90 border border-white/10 rounded-2xl font-bold text-sm tracking-wide hover:bg-white/10 transition-all active:scale-95 cursor-pointer"
          >
            View Live Metrics
          </button>
        </Link>
      </motion.div>

      {/* Integrated Supported Cities Panel */}
      <motion.div
        variants={itemVariants}
        className="grid grid-cols-3 gap-4 max-w-xl mx-auto mb-16 px-4 py-3 rounded-2xl border border-white/5 bg-black/30 backdrop-blur-sm self-stretch"
        id="hero-supported-cities"
      >
        {[
          { city: 'Karachi', tag: 'DHA, Clifton, Gulshan' },
          { city: 'Lahore', tag: 'Gulberg, DHAP5, Model Town' },
          { city: 'Islamabad', tag: 'F-6, F-10, G-11, Bahria' },
        ].map((item, id) => (
          <div key={id} className="text-center border-r last:border-0 border-white/5 px-2">
            <div className="text-xs font-extrabold text-white tracking-wide uppercase">{item.city}</div>
            <div className="text-[9px] text-slate-400 font-mono mt-0.5 truncate">{item.tag}</div>
          </div>
        ))}
      </motion.div>

      {/* Stats Counter Row */}
      <motion.div 
        variants={itemVariants}
        className="w-full grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto border-y border-white/5 py-8 bg-gradient-to-r from-transparent via-white/[0.01] to-transparent"
        id="hero-stats-panel"
      >
        {[
          { label: 'Autonomous Agents', value: '5 Clusters', sub: 'Groq + Llama-3.3' },
          { label: 'Verified Partners', value: '26 Experts', sub: 'Karachi | Lahore | Isb' },
          { label: 'Slots Configured', value: '7,020 Total', sub: 'Real-Time Database' },
          { label: 'Booking Latency', value: '< 1.8s Avg', sub: 'Optimized PostgreSQL' },
        ].map((stat, i) => (
          <div key={i} className="flex flex-col items-center">
            <span className="text-[10px] uppercase font-bold tracking-widest text-brand-primary mb-1.5">{stat.label}</span>
            <span className="text-xl md:text-2xl font-black text-white leading-none">{stat.value}</span>
            <span className="text-[9px] text-slate-400 font-mono mt-1">{stat.sub}</span>
          </div>
        ))}
      </motion.div>
    </section>
  );
}
