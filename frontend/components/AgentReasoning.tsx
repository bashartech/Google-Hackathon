import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Users, Calendar, Bell, Lightbulb, Zap, Info } from 'lucide-react';
import { cn } from '@/lib/utils';

interface WorkflowStep {
  agent: string;
  stage: string;
  status: 'in_progress' | 'completed' | 'failed' | 'pending';
  timestamp: string;
  action: string;
  error?: string;
}

interface AgentReasoningProps {
  workflow: WorkflowStep[];
}

export default function AgentReasoning({ workflow }: AgentReasoningProps) {
  const getAgentIcon = (agentName: string) => {
    const name = agentName.toLowerCase();
    if (name.includes('coordinator')) return <Brain className="w-4 h-4" />;
    if (name.includes('discovery')) return <Users className="w-4 h-4" />;
    if (name.includes('matching') || name.includes('ranking')) return <Zap className="w-4 h-4" />;
    if (name.includes('booking')) return <Calendar className="w-4 h-4" />;
    if (name.includes('follow-up')) return <Bell className="w-4 h-4" />;
    return <Info className="w-4 h-4" />;
  };

  const getAgentColorClass = (agentName: string) => {
    const name = agentName.toLowerCase();
    if (name.includes('coordinator')) return 'text-sky-400 bg-sky-400/10 border-sky-400/20 shadow-[0_0_10px_rgba(14,165,233,0.1)]';
    if (name.includes('discovery')) return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20';
    if (name.includes('matching')) return 'text-indigo-400 bg-indigo-400/10 border-indigo-400/20';
    if (name.includes('booking')) return 'text-amber-400 bg-amber-400/10 border-amber-400/20';
    return 'text-slate-500 bg-white/5 border-white/10';
  };

  const activeSteps = workflow.filter(
    (step) => step.status === 'completed' && step.action
  ).slice(-3); // Only show last 3 reasoning steps to keep it sleek

  if (activeSteps.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center p-12 bg-white/[0.02] rounded-[2rem] border border-white/5 border-dashed">
         <div className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center mb-6">
            <Lightbulb className="w-6 h-6 text-slate-600" />
         </div>
         <p className="text-xs text-slate-600 font-bold uppercase tracking-widest max-w-[180px] leading-relaxed">Agent insights will materialize here.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-8 px-2">
        <div className="w-2 h-2 rounded-full bg-brand-primary animate-pulse" />
        <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">Neural Insights</h3>
      </div>

      <AnimatePresence mode="popLayout">
        {activeSteps.map((step, index) => (
          <motion.div
            key={index + step.agent}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            layout
            className="group p-6 rounded-[2rem] border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] transition-all"
          >
            <div className="flex items-center justify-between mb-4">
               <div className={cn(
                 "flex items-center gap-2 px-3 py-1 rounded-full border text-[9px] font-black uppercase tracking-widest",
                 getAgentColorClass(step.agent)
               )}>
                  {getAgentIcon(step.agent)}
                  {step.agent}
               </div>
               <span className="text-[9px] font-bold text-slate-700 tracking-tighter">
                  {new Date(step.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
               </span>
            </div>

            <p className="text-sm text-slate-300 leading-relaxed font-bold mb-2">
               {step.action}
            </p>
            <div className="flex items-center gap-2">
               <span className="h-px w-4 bg-slate-800" />
               <span className="text-[10px] text-slate-600 font-bold uppercase tracking-widest">{step.stage}</span>
            </div>

            {step.error && (
              <div className="mt-4 p-4 rounded-xl bg-red-500/5 border border-red-500/10 text-red-400 text-[10px] leading-relaxed">
                 <span className="font-black uppercase tracking-widest block mb-1">Neural Fault:</span> {step.error}
              </div>
            )}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
