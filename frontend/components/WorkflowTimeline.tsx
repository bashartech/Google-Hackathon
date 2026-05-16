import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, Circle, AlertCircle, Loader2, ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';

interface WorkflowStep {
  agent: string;
  stage: string;
  status: 'in_progress' | 'completed' | 'failed' | 'pending';
  timestamp: string;
  action: string;
  error?: string;
}

interface WorkflowTimelineProps {
  workflow: WorkflowStep[];
}

const AGENT_EMOJIS: Record<string, string> = {
  'Service Coordinator': '🗣️',
  'Service Request Coordinator': '🗣️',
  'Provider Discovery': '🔍',
  'Matching & Ranking': '⭐',
  'Booking & Confirmation': '✅',
  'Follow-up Agent': '📧',
  'Information Extractor': '🧠',
  'System': '⚙️',
};

export default function WorkflowTimeline({ workflow }: WorkflowTimelineProps) {
  if (workflow.length === 0) return null;

  return (
    <div className="bg-surface-panel rounded-[2rem] border border-white/5 p-8 flex flex-col shadow-xl">
      <div className="flex items-center justify-between mb-8">
        <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">Orchestration Timeline</h3>
        <div className="px-2 py-0.5 rounded bg-brand-primary/10 border border-brand-primary/20 text-brand-primary text-[10px] font-black tracking-widest">
           {workflow.filter(s => s.status === 'completed').length} / {workflow.length} SEGMENTS
        </div>
      </div>

      <div className="relative space-y-8 flex-1">
        {/* Progress Line */}
        <div className="absolute left-[11px] top-2 bottom-2 w-px bg-slate-800" />

        {workflow.map((step, index) => {
          const status = step.status;
          
          return (
            <motion.div 
              key={index}
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              className="relative pl-9 flex flex-col group"
            >
              <div className="absolute left-0 top-0 z-10">
                 {status === 'completed' ? (
                   <div className="w-6 h-6 rounded-full bg-brand-primary shadow-[0_0_15px_rgba(14,165,233,0.5)] flex items-center justify-center">
                     <CheckCircle2 className="w-3.5 h-3.5 text-white" />
                   </div>
                 ) : status === 'in_progress' ? (
                   <div className="w-6 h-6 rounded-full bg-slate-800 border border-brand-primary/50 flex items-center justify-center">
                      <div className="w-1.5 h-1.5 bg-brand-primary rounded-full animate-ping" />
                   </div>
                 ) : status === 'failed' ? (
                    <div className="w-6 h-6 rounded-full bg-red-500 shadow-[0_0_15px_rgba(239,68,68,0.5)] flex items-center justify-center">
                      <AlertCircle className="w-3.5 h-3.5 text-white" />
                    </div>
                 ) : (
                    <div className="w-6 h-6 rounded-full bg-slate-900 border border-white/5 flex items-center justify-center">
                      <div className="w-1 h-1 bg-slate-700 rounded-full" />
                    </div>
                 )}
              </div>

              <div className="flex flex-col">
                <div className="flex items-center gap-2 mb-1">
                   <h4 className={cn(
                     "text-sm font-bold tracking-tight transition-colors",
                     status === 'completed' ? "text-white" : "text-slate-500"
                   )}>
                     {step.stage}
                   </h4>
                   {status === 'completed' && <span className="text-[10px] text-emerald-500 font-bold uppercase tracking-widest bg-emerald-500/10 px-1 rounded">Sync</span>}
                </div>
                <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-2">
                  {step.agent}
                </p>
                
                {status === 'completed' && step.action && (
                  <p className="text-[11px] text-slate-600 leading-relaxed max-w-sm">
                    {step.action}
                  </p>
                )}
                
                {status === 'in_progress' && (
                  <div className="mt-2 flex items-center gap-2">
                    <Loader2 className="w-3 h-3 text-brand-primary animate-spin" />
                    <span className="text-[10px] text-brand-primary font-bold animate-pulse">Processing Segment...</span>
                  </div>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>
      
      <div className="mt-10 p-5 bg-brand-primary/5 border border-brand-primary/10 rounded-2xl">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-brand-primary/20 rounded-xl">
             <ArrowRight className="w-4 h-4 text-brand-primary" />
          </div>
          <p className="text-[11px] text-slate-300 leading-tight font-medium">
             <span className="text-brand-primary font-bold">Execution Engine</span> suggests high-performance routing for this request.
          </p>
        </div>
      </div>
    </div>
  );
}
