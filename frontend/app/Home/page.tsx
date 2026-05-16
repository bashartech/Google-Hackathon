import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Shield, Zap, Sparkles, Globe, Cpu, Wrench } from 'lucide-react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import { Variants } from 'framer-motion';
export default function HomePage() {
  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.15 } },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.8, ease: [0.23, 1, 0.32, 1] },
    },
  };

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="relative w-full"
    >
      {/* Hero Section */}
      <section className="relative pt-32 pb-24 px-8 max-w-6xl mx-auto flex flex-col items-center text-center">
        <motion.div 
          variants={itemVariants}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand-primary/10 border border-brand-primary/20 text-brand-primary text-[10px] font-bold uppercase tracking-[0.2em] mb-10"
        >
          <Sparkles className="w-3.5 h-3.5" />
          Protocol Initialized v4.0.2
        </motion.div>

        <motion.h1 
          variants={itemVariants}
          className="text-6xl md:text-8xl font-black tracking-tight leading-[0.95] text-gradient mb-8 max-w-4xl"
        >
          Orchestrating the <br />
          <span className="text-brand-primary">Nexus of Home.</span>
        </motion.h1>

        <motion.p 
          variants={itemVariants}
          className="text-lg md:text-xl text-slate-400 max-w-2xl leading-relaxed mb-12 font-medium"
        >
          Experience the autonomous future of service booking. Coordinated agent clusters handling discovery, verification, and execution with absolute precision.
        </motion.p>

        <motion.div variants={itemVariants} className="flex flex-col sm:flex-row gap-5">
          <Link
            href="/chat"
            className="group px-10 py-5 bg-brand-primary text-white rounded-2xl font-bold text-lg flex items-center justify-center gap-3 hover:bg-sky-500 transition-all duration-300 shadow-[0_0_30px_rgba(14,165,233,0.4)]"
          >
            Access Core
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Link>
          <Link
            href="/dashboard"
            className="px-10 py-5 bg-white/5 text-white/80 border border-white/10 rounded-2xl font-bold text-lg hover:bg-white/10 transition-all flex items-center justify-center"
          >
            System Metrics
          </Link>
        </motion.div>

        {/* Cinematic Dashboard Preview */}
        <motion.div 
          variants={itemVariants}
          className="mt-28 relative w-full aspect-video rounded-[2.5rem] border border-white/5 bg-[#05080f] overflow-hidden shadow-2xl p-6 group"
        >
           <div className="absolute inset-0 bg-gradient-to-t from-bg-deep via-transparent to-transparent z-10 pointer-events-none" />
           <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(14,165,233,0.1),transparent)] pointer-events-none" />
           
           <div className="grid grid-cols-12 gap-5 h-full">
             {/* Preview UI Elements */}
             <div className="col-span-3 space-y-5">
               <div className="h-10 bg-white/5 rounded-xl w-3/4" />
               <div className="h-[70%] bg-surface-panel/40 rounded-3xl border border-white/5 p-4">
                  <div className="space-y-3">
                    {[80, 60, 90, 40].map((w, i) => (
                      <div key={i} className="h-1.5 bg-white/5 rounded-full" style={{ width: `${w}%` }} />
                    ))}
                  </div>
               </div>
             </div>
             
             <div className="col-span-6 space-y-5">
               <div className="h-14 bg-brand-primary/5 border border-brand-primary/10 rounded-2xl w-full flex items-center justify-center">
                  <div className="w-2 h-2 rounded-full bg-brand-primary animate-ping mr-3" />
                  <span className="text-[10px] font-black uppercase tracking-widest text-brand-primary">Neural Link Active</span>
               </div>
               <div className="h-full bg-surface-panel/60 rounded-[2rem] border border-white/10 flex flex-col items-center justify-center p-10">
                  <Cpu className="w-16 h-16 text-brand-primary/20 mb-6" />
                  <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                    <motion.div 
                      animate={{ x: ['-100%', '100%'] }}
                      transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                      className="w-1/3 h-full bg-brand-primary"
                    />
                  </div>
               </div>
             </div>

             <div className="col-span-3 space-y-5">
                <div className="h-10 bg-white/5 rounded-xl w-3/4 ml-auto" />
                <div className="h-[70%] bg-surface-panel/40 rounded-3xl border border-white/5 p-4">
                  <div className="flex flex-col gap-4">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20" />
                      <div className="flex-1 space-y-1.5">
                        <div className="h-1.5 bg-white/10 rounded-full w-full" />
                        <div className="h-1 bg-white/5 rounded-full w-2/3" />
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                       <div className="w-8 h-8 rounded-lg bg-sky-500/10 border border-sky-500/20" />
                       <div className="flex-1 space-y-1.5">
                        <div className="h-1.5 bg-white/10 rounded-full w-full" />
                        <div className="h-1 bg-white/5 rounded-full w-1/2" />
                      </div>
                    </div>
                  </div>
                </div>
             </div>
           </div>
        </motion.div>
      </section>

      {/* Grid Features */}
      <section className="py-32 px-8 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
          {[
            {
              title: 'Multi-Agent Flow',
              desc: 'Autonomous agent clusters negotiating and executing complex service lifecycles without human friction.',
              icon: Cpu,
              color: 'text-brand-primary',
            },
            {
              title: 'Localized Search',
              desc: 'Deep integration with mapping protocols to pinpoint elite technicians in your exact digital territory.',
              icon: Globe,
              color: 'text-brand-secondary',
            },
            {
              title: 'Neural Trust Path',
              desc: 'Every provider is verified through a multi-point identity and performance consensus mechanism.',
              icon: Shield,
              color: 'text-emerald-400',
            },
          ].map((feature, i) => (
            <motion.div
              key={i}
              variants={itemVariants}
              whileHover={{ y: -8, borderColor: 'rgba(14,165,233,0.2)' }}
              className="p-10 rounded-[2.5rem] border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] transition-all group"
            >
              <div className={cn("p-4 rounded-2xl bg-white/5 w-fit mb-8 transition-all group-hover:scale-110", feature.color)}>
                <feature.icon className="w-7 h-7" />
              </div>
              <h3 className="text-2xl font-bold mb-4">{feature.title}</h3>
              <p className="text-slate-500 leading-relaxed font-medium">{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Narrative Stats */}
      <section className="py-24 px-8 border-t border-white/5 mb-20 bg-gradient-to-b from-transparent to-white/[0.01]">
        <div className="max-w-6xl mx-auto">
           <div className="grid grid-cols-2 lg:grid-cols-4 gap-12">
              {[
                { label: 'Latency', value: '142ms' },
                { label: 'Agent Clusters', value: '24' },
                { label: 'Success Rate', value: '99.8%' },
                { label: 'Nodes', value: '1.4k' },
              ].map((stat, i) => (
                <div key={i} className="flex flex-col items-center text-center">
                  <div className="text-4xl font-black text-white mb-2 leading-none">{stat.value}</div>
                  <div className="text-[10px] uppercase tracking-[0.2em] text-brand-primary font-black px-3 py-1 rounded bg-brand-primary/5">{stat.label}</div>
                </div>
              ))}
           </div>
        </div>
      </section>
    </motion.div>
  );
}
