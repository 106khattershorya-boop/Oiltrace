import React from "react";

import {
  ArrowUpRight,
  Ship,
} from "lucide-react";

import RiskBadge from "./RiskBadge";

const vessels = [
  {
    name: "MV Ocean Pioneer",
    imo: "IMO 9876543",
    type: "Oil Tanker",
    distance: "7.2 km",
    risk: "CRITICAL",
  },
  {
    name: "MT Blue Horizon",
    imo: "IMO 9123456",
    type: "Chemical Tanker",
    distance: "12.8 km",
    risk: "HIGH",
  },
  {
    name: "MV Eastern Star",
    imo: "IMO 9345678",
    type: "Cargo Vessel",
    distance: "18.6 km",
    risk: "HIGH",
  },
  {
    name: "MT Coastal Trader",
    imo: "IMO 9456123",
    type: "Oil Tanker",
    distance: "26.4 km",
    risk: "MEDIUM",
  },
];

export default function VesselTable() {

  return (
    <div className="glass overflow-hidden rounded-2xl">

      <div className="border-b border-white/[.05] px-5 py-4">

        <div className="flex items-center justify-between">

          <div>

            <h3 className="text-sm font-bold text-white">
              AIS Correlation
            </h3>

            <p className="mt-1 text-[10px] text-slate-600">
              Highest correlation signals
            </p>

          </div>

          <Ship
            size={18}
            className="text-cyan-400"
          />

        </div>

      </div>

      <div className="divide-y divide-white/[.04]">

        {vessels.map((vessel) => (
          <div
            key={vessel.imo}
            className="group flex items-center justify-between gap-4 px-5 py-4 transition hover:bg-white/[.025]"
          >

            <div className="flex min-w-0 items-center gap-3">

              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-400">
                <Ship size={16} />
              </div>

              <div className="min-w-0">

                <p className="truncate text-xs font-bold text-slate-200">
                  {vessel.name}
                </p>

                <p className="mt-1 text-[9px] text-slate-600">
                  {vessel.imo} • {vessel.type}
                </p>

              </div>

            </div>

            <div className="hidden text-right sm:block">

              <p className="text-[9px] uppercase text-slate-600">
                Distance
              </p>

              <p className="mt-1 text-xs font-bold text-slate-300">
                {vessel.distance}
              </p>

            </div>

            <RiskBadge risk={vessel.risk} />

            <ArrowUpRight
              size={14}
              className="hidden text-slate-600 transition group-hover:text-cyan-400 sm:block"
            />

          </div>
        ))}

      </div>

    </div>
  );
}