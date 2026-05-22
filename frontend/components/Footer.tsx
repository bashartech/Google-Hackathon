/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { ShieldCheck, Cpu, Code2, Globe } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="mt-28 border-t border-white/5 bg-[#030712] relative z-10" id="global-footer">
      
      {/* Upper Footer: Hackathon deliverables checklist & info */}
      <div className="max-w-7xl mx-auto px-6 py-16 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-10">
        
        {/* Brand narrative */}
        <div className="lg:col-span-4 space-y-4">
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-brand-primary" />
            <span className="font-black text-sm tracking-wide uppercase text-white">ServiceLink AI</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed font-normal">
            A production-ready Enterprise Multi-Agent AI system designed to formalize Pakistan\'s informal economy. Empowering workers through transparent scheduling, fair matching, and automated customer matching.
          </p>
        </div>

      </div>

      {/* Bottom Footer Credits */}
      <div className="border-t border-white/5 py-6 px-6 bg-black/40">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-[10px] text-slate-500 font-mono">
          <div>
            © 2026 ServiceLink AI Orchestrator Systems. All Rights Reserved.
          </div>
          <div className="flex items-center gap-4">
            <span className="hover:text-white transition-colors cursor-pointer">Security Protocol Policy</span>
            <span>•</span>
            <span className="hover:text-white transition-colors cursor-pointer">Postgres Console Link</span>
            <span>•</span>
            <span className="hover:text-white transition-colors cursor-pointer">FastAPI Swagger Specs</span>
          </div>
        </div>
      </div>

    </footer>
  );
}
