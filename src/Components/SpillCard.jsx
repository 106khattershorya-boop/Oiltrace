import React from "react";

import {
  ArrowUpRight,
  MapPin,
  ScanLine,
} from "lucide-react";

import RiskBadge from "./RiskBadge";

export default function SpillCard({
  spill,
}) {

  return (
    <div className="glass group rounded-2xl p-5">

      <div className="flex items-start justify-between">

        <div className="flex items-center gap-3">

          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-orange-400/10 text-orange-400">
            <ScanLine size={18} />
          </div>

          <div>

            <p className="text-sm font-bold text-white">
              {spill.id}
            </p>

            <div className="mt-1 flex items-center gap-1 text-[10px] text-slate-500">

              <MapPin size={11} />

              {spill.location}

            </div>

          </div>

        </div>

        <RiskBadge risk={spill.risk} />

      </div>

      <div className="mt-5 grid grid-cols-3 gap-3">

        <Metric
          label="Area"
          value={spill.area}
        />

        <Metric
          label="Confidence"
          value={spill.confidence}
        />

        <Metric
          label="Status"
          value={spill.status}
        />

      </div>

      <div className="mt-5 flex items-center justify-between border-t border-white/[.05] pt-4">

        <span className="text-[10px] text-slate-600">
          {spill.detectedAt}
        </span>

        <button className="flex items-center gap-1 text-[10px] font-bold text-cyan-400 transition hover:text-cyan-300">

          Investigate

          <ArrowUpRight size={12} />

        </button>

      </div>

    </div>
  );
}

function Metric({
  label,
  value,
}) {
  return (
    <div>

      <p className="text-[8px] uppercase tracking-widest text-slate-600">
        {label}
      </p>

      <p className="mt-1 truncate text-xs font-bold text-slate-200">
        {value}
      </p>

    </div>
  );
}