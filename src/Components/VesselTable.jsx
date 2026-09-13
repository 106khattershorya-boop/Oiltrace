import {
  ArrowUpRight,
  Ship,
} from "lucide-react";

import RiskBadge from "./RiskBadge";

export default function VesselTable({ vessels = [] }) {
  const displayVessels = vessels.slice(0, 5).map((vessel, index) => {
    const name = vessel.vessel_name || vessel.name || "Unknown Vessel";
    const identifier = vessel.mmsi
      ? `MMSI ${vessel.mmsi}`
      : vessel.imo || `Vessel #${index + 1}`;
    const type = vessel.vessel_type || vessel.type || "AIS vessel";
    const distance =
      vessel.distance_km != null
        ? `${Number(vessel.distance_km).toFixed(2)} km`
        : vessel.distance || "Unavailable";
    const risk = vessel.priority_level || vessel.risk || "LOW";

    return {
      key: vessel.mmsi || vessel.imo || `${name}-${index}`,
      name,
      identifier,
      type,
      distance,
      risk,
    };
  });

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
        {displayVessels.map((vessel) => (
          <div
            key={vessel.key}
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
                  {vessel.identifier} • {vessel.type}
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

        {displayVessels.length === 0 && (
          <div className="p-6 text-center text-xs text-slate-500">
            No correlated vessel signals currently available.
          </div>
        )}
      </div>

    </div>
  );
}