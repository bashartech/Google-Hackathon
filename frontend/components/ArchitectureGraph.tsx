/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Cpu, ArrowRight, Zap, CheckCircle2, AlertTriangle, Network, Info } from 'lucide-react';

interface AgentNode {
  id: string;
  name: string;
  role: string;
  icon: string;
  color: string;
  borderClass: string;
  promptGuideline: string;
  inputs: string[];
  outputs: string[];
  edgeCaseAction: string;
}

const AGENTS_LIST: AgentNode[] = [
  {
    id: 'agent-1',
    name: '🤖 Service Coordinator Agent',
    role: 'Natural Language Understanding & Intent Extraction',
    icon: 'MessageSquare',
    color: 'text-sky-400 bg-sky-400/5',
    borderClass: 'border-sky-400/20 hover:border-sky-400/50',
    promptGuideline: 'You are the entry point. Detect language (Urdu text, Roman Urdu like "AC kharab hai DHA mein", or English). Extract: service_type, customer location (city/area), urgency tier, and preferred appointment window. Keep global session context in mind.',
    inputs: ['User Natural Language Message', 'Session Dialogue History', 'Current Location Context'],
    outputs: ['Extracted Service Type', 'Extracted City & Area', 'Urgency Score (1-10)', 'System Language Flag'],
    edgeCaseAction: 'Fallback if location metadata is absent: ask user for confirmation politely in their matching language dial.'
  },
  {
    id: 'agent-2',
    name: '🔍 Provider Discovery Agent',
    role: 'Database Queries & Initial Filtering',
    icon: 'Search',
    color: 'text-indigo-400 bg-indigo-400/5',
    borderClass: 'border-indigo-400/20 hover:border-indigo-400/50',
    promptGuideline: 'Query the Postgres/Neon database using specialized SQL filters. Filter list of providers by matching service_type AND verifying that the user\'s area is within the provider\'s registration areas array. Exclude fully-booked providers.',
    inputs: ['Parsed Service Type', 'Extracted Target Area', 'Required Date'],
    outputs: ['List of Registered Available Providers', 'Availability Timetable Match Status', 'Distance Multipliers'],
    edgeCaseAction: 'Local area empty: triggers nearby area lookup and passes recommendations to Edge Case Handler.'
  },
  {
    id: 'agent-3',
    name: '🛡️ Edge Case Handler',
    role: 'Proactive Fallbacks & Multiplier Calculations',
    icon: 'Shield',
    color: 'text-rose-400 bg-rose-400/5',
    borderClass: 'border-rose-400/20 hover:border-rose-400/50',
    promptGuideline: 'Evaluate system-wide and localized disruptions. Apply surge multipliers (30%) if active bookings in area double baseline. Check peak demand hours flags. Handle out-of-coverage requests with expansion feedback forms.',
    inputs: ['Raw List of Providers', 'Active Weather Warnings', 'Global Current Load Metrics'],
    outputs: ['Surge Pricing Factor', 'Validated Core Safe Status', 'Actionable Mitigation Suggestions'],
    edgeCaseAction: 'Simulated Rain Alert: flags extreme delay warnings (~40m) on plumbing/electrical and recommends standby status.'
  },
  {
    id: 'agent-4',
    name: '⭐ Matching & Ranking Agent',
    role: 'Composite Multi-Factor Partner Decision Routing',
    icon: 'TrendingUp',
    color: 'text-teal-400 bg-teal-400/5',
    borderClass: 'border-teal-400/20 hover:border-teal-400/50',
    promptGuideline: 'Execute scoring weights based on: urgency tier (boosts lower response times), ratings (power score of 3.5), experience years, and geographic proximity multipliers. Rank providers and isolate the absolute optimal choice.',
    inputs: ['Available Filtered Providers', 'Surge Multiplier Flag', 'Urgency Weight Scalar'],
    outputs: ['Top Ranked Provider Metadata', 'Sub-optimal Alternatives List', 'Scoring Metrics Breakdown'],
    edgeCaseAction: 'Tied high score: defaults to the provider with the higher historical acceptance rate metrics.'
  },
  {
    id: 'agent-5',
    name: '📝 Booking & Confirmation Agent',
    role: 'State Synchronization & Exterior Integrations',
    icon: 'CheckSquare',
    color: 'text-emerald-400 bg-emerald-400/5',
    borderClass: 'border-emerald-400/20 hover:border-emerald-400/50',
    promptGuideline: 'Confirm finalized slot reservation. Update provider booking schedules in PostgreSQL, dispatch event generation tags to Google Calendar API integrations (OAuth), format notification emails for provider workflow dashboards.',
    inputs: ['Top Selected Provider', 'Verified Time Reservation Slot', 'Client Contact Info'],
    outputs: ['Unique Booking ID (BKGxxxxx)', 'Google Calendar Event ID', 'Gmail Despatch Form Config'],
    edgeCaseAction: 'Failed provider dashboard response in 5 min: Auto-rejects reservation status and triggers instant fallback rerouting payload.'
  },
];

export default function ArchitectureGraph() {
  const [selectedAgentId, setSelectedAgentId] = useState<string>('agent-1');

  const activeAgent = AGENTS_LIST.find(a => a.id === selectedAgentId) || AGENTS_LIST[0];

  return (
    <section className="py-24 px-6 max-w-7xl mx-auto border-t border-white/5" id="agent-orchestration-section">
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-5xl font-black tracking-tight mb-4">5-Agent Orchestration Architecture</h2>
        <p className="text-slate-400 max-w-2xl mx-auto text-sm leading-relaxed">
          Unlike black-box booking widgets, ServiceLink AI operates a multi-agent workflow where distinct LLM clusters verify, audit, and execute your scheduling requirements. Select any agent below to dissect its operational parameters.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-stretch">
        
        {/* Interactive Pipeline Nodes */}
        <div className="lg:col-span-6 flex flex-col justify-between gap-4" id="agent-pipeline-nodes">
          {AGENTS_LIST.map((agent, index) => (
            <div key={agent.id} className="relative flex items-center">
              {/* Connector Pipeline line */}
              {index < AGENTS_LIST.length - 1 && (
                <div className="absolute left-[30px] top-[54px] w-0.5 h-[34px] bg-gradient-to-b from-brand-primary/40 to-transparent -z-10" />
              )}
              
              <button
                onClick={() => setSelectedAgentId(agent.id)}
                className={`w-full flex items-center justify-between text-left p-4 rounded-2xl border transition-all duration-300 group cursor-pointer ${
                  selectedAgentId === agent.id
                    ? 'bg-brand-primary/[0.08] border-brand-primary shadow-[0_0_20px_rgba(37,99,235,0.15)]'
                    : 'bg-white/[0.01] border-white/5 hover:bg-white/[0.03]'
                }`}
                id={`agent-node-btn-${agent.id}`}
              >
                <div className="flex items-center gap-4">
                  <div className={`p-3 rounded-xl border border-white/5 font-extrabold text-xs tracking-mono ${
                    selectedAgentId === agent.id ? 'bg-brand-primary text-white' : 'bg-black/40 text-slate-400'
                  }`}>
                    0{index + 1}
                  </div>
                  <div>
                    <h3 className="font-extrabold text-sm text-white tracking-wide">{agent.name}</h3>
                    <p className="text-[11px] text-slate-400 mt-0.5 truncate max-w-xs md:max-w-md">{agent.role}</p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded-full border border-white/5 uppercase ${
                    selectedAgentId === agent.id ? 'bg-brand-primary/20 text-brand-primary' : 'bg-white/5 text-slate-500'
                  }`}>
                    Active
                  </span>
                  <ArrowRight className={`w-4 h-4 transition-transform duration-300 ${
                    selectedAgentId === agent.id ? 'text-brand-primary translate-x-1' : 'text-slate-600 group-hover:translate-x-0.5'
                  }`} />
                </div>
              </button>
            </div>
          ))}
        </div>

        {/* Selected Node Spec Sheet (Advanced AI Transparency panel) */}
        <div className="lg:col-span-6" id="agent-specification-cabinet">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeAgent.id}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="h-full rounded-[2.5rem] border border-white/10 bg-gradient-to-b from-surface-panel to-bg-deep p-8 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <span className="text-[10px] font-mono font-bold uppercase tracking-widest text-brand-primary">
                      System Node Specification
                    </span>
                    <h3 className="text-2xl font-black text-gradient mt-1">{activeAgent.name}</h3>
                  </div>
                  <div className="p-3 bg-brand-primary/5 border border-brand-primary/10 rounded-2xl">
                    <Cpu className="w-6 h-6 text-brand-primary" />
                  </div>
                </div>

                <div className="space-y-6">
                  {/* Prompt Guidelines */}
                  <div>
                    <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 font-mono block mb-2">
                      Prompt instructions (Llama LLM Orchestrator Guidelines)
                    </span>
                    <div className="p-4 rounded-2xl bg-black/40 border border-white/5 text-xs text-slate-300 leading-relaxed font-mono">
                      "{activeAgent.promptGuideline}"
                    </div>
                  </div>

                  {/* Inputs & Outputs Columns */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 font-mono block mb-2">
                        Data Inputs Array
                      </span>
                      <ul className="space-y-1.5">
                        {activeAgent.inputs.map((inp, idx) => (
                          <li key={idx} className="flex items-center gap-2 text-xs text-slate-300">
                            <span className="w-1.5 h-1.5 rounded-full bg-brand-primary" />
                            {inp}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 font-mono block mb-2">
                        Extracted Outputs
                      </span>
                      <ul className="space-y-1.5">
                        {activeAgent.outputs.map((out, idx) => (
                          <li key={idx} className="flex items-center gap-2 text-xs text-emerald-400 font-medium">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                            {out}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              {/* Robust edge case actions */}
              <div className="mt-8 pt-6 border-t border-white/5 flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
                <div>
                  <span className="text-[10px] font-bold tracking-wider uppercase text-rose-300 block">
                    Edge Case Defense Strategy
                  </span>
                  <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                    {activeAgent.edgeCaseAction}
                  </p>
                </div>
              </div>

            </motion.div>
          </AnimatePresence>
        </div>

      </div>
    </section>
  );
}
