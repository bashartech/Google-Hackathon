
import React from 'react';
import { SERVICES_CATALOG } from '../data';
import { Snowflake, Wrench, Zap, Sparkles, Hammer, Paintbrush, ShieldCheck } from 'lucide-react';

const ICON_MAP: Record<string, any> = {
  Snowflake: Snowflake,
  Wrench: Wrench,
  Zap: Zap,
  Sparkles: Sparkles,
  Hammer: Hammer,
  Paintbrush: Paintbrush,
};

interface ServiceExplorerProps {
  onSelectedService: (serviceType: any) => void;
}

export default function ServiceExplorer({ onSelectedService }: ServiceExplorerProps) {
  return (
    <section className="py-24 px-6 max-w-7xl mx-auto border-t border-white/5" id="services-grid-section">
      <div className="text-center mb-16">
        <span className="text-[10px] uppercase font-bold tracking-[0.22em] text-brand-primary">
          Premium Professional Coverages
        </span>
        <h2 className="text-3xl md:text-5xl font-black text-white tracking-tight mt-2 mb-4">
          Integrated Home Service Sectors
        </h2>
        <p className="text-slate-400 max-w-2xl mx-auto text-sm leading-relaxed">
          Operational across Karachi, Lahore, and Islamabad. Instant pricing matching, dispatch protocols, and certified experts ready for immediate callouts.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {SERVICES_CATALOG.map((service, index) => {
          const IconComponent = ICON_MAP[service.icon] || Wrench;
          return (
            <div
              key={index}
              className="p-8 rounded-[2.2rem] border border-white/5 bg-gradient-to-tr from-surface-panel to-bg-deep hover:bg-white/[0.03] transition-all duration-300 group flex flex-col justify-between"
              id={`service-card-${index}`}
            >
              <div>
                {/* Header Row */}
                <div className="flex items-center justify-between mb-6">
                  <div className="p-4 rounded-2xl bg-brand-primary/5 border border-brand-primary/10 group-hover:bg-brand-primary/10 group-hover:scale-105 transition-all">
                    <IconComponent className="w-6 h-6 text-brand-primary" />
                  </div>
                  <div className="text-right">
                    <span className="text-[11px] font-mono uppercase text-slate-400 font-bold tracking-wider block">
                      Guaranteed Rate
                    </span>
                    <span className="text-base font-black text-emerald-400 mt-0.5 block">
                      {service.avgCostRange}
                    </span>
                  </div>
                </div>

                <h3 className="text-xl font-bold text-white mb-3 group-hover:text-brand-primary transition-colors">
                  {service.type}
                </h3>
                <p className="text-xs text-slate-400 leading-relaxed font-normal mb-6 min-h-[50px]">
                  {service.description}
                </p>

                {/* Bullets array */}
                <div className="space-y-2 mb-8">
                  {service.features.map((feat, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <ShieldCheck className="w-3.5 h-3.5 text-brand-primary shrink-0" />
                      <span className="text-[11px] text-slate-300 font-mono">{feat}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Action and meta details */}
              <div className="pt-6 border-t border-white/5 flex items-center justify-between">
                <div>
                  <span className="text-[9px] font-mono text-slate-500 uppercase block">
                    Avg Response
                  </span>
                  <span className="text-xs font-bold text-slate-300">
                    {service.avgResponse}
                  </span>
                </div>
                {/* <button
                  onClick={() => onSelectedService(service.type)}
                  className="px-4 py-2 bg-white/5 group-hover:bg-brand-primary text-slate-300 group-hover:text-white rounded-xl font-semibold text-xs tracking-wide transition-all group-hover:shadow-[0_0_15px_rgba(37,99,235,0.3)] cursor-pointer"
                >
                  Book Instant
                </button> */}
              </div>

            </div>
          );
        })}
      </div>
    </section>
  );
}
