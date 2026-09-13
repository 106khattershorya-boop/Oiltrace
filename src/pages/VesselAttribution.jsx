import React, { useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  Ship,
  Search,
  MapPin,
  Navigation,
  Clock3,
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  Radio,
  Target,
  Route,
  Activity,
  ShieldAlert,
  Filter,
  X,
} from "lucide-react";

const vesselData = [
  {
    rank: 1,
    name: "MV Ocean Pioneer",
    imo: "IMO 9876543",
    type: "Oil Tanker",
    flag: "India",
    distance: "7.2 km",
    proximity: 96,
    timing: 94,
    trajectory: 91,
    anomaly: 88,
    risk: "CRITICAL",
    speed: "8.4 kn",
    heading: "072°",
    lastSeen: "18 min ago",
  },
  {
    rank: 2,
    name: "MT Blue Horizon",
    imo: "IMO 9123456",
    type: "Chemical Tanker",
    flag: "Singapore",
    distance: "12.8 km",
    proximity: 88,
    timing: 91,
    trajectory: 86,
    anomaly: 77,
    risk: "HIGH",
    speed: "10.1 kn",
    heading: "084°",
    lastSeen: "32 min ago",
  },
  {
    rank: 3,
    name: "MV Eastern Star",
    imo: "IMO 9345678",
    type: "Cargo Vessel",
    flag: "Panama",
    distance: "18.6 km",
    proximity: 81,
    timing: 85,
    trajectory: 82,
    anomaly: 64,
    risk: "HIGH",
    speed: "12.2 kn",
    heading: "067°",
    lastSeen: "41 min ago",
  },
  {
    rank: 4,
    name: "MT Coastal Trader",
    imo: "IMO 9456123",
    type: "Oil Tanker",
    flag: "Liberia",
    distance: "26.4 km",
    proximity: 72,
    timing: 79,
    trajectory: 75,
    anomaly: 51,
    risk: "MEDIUM",
    speed: "9.8 kn",
    heading: "093°",
    lastSeen: "58 min ago",
  },
  {
    rank: 5,
    name: "MV Arabian Pearl",
    imo: "IMO 9567812",
    type: "Container Ship",
    flag: "Malta",
    distance: "34.9 km",
    proximity: 61,
    timing: 68,
    trajectory: 63,
    anomaly: 42,
    risk: "LOW",
    speed: "15.4 kn",
    heading: "101°",
    lastSeen: "1 hr ago",
  },
];

const riskStyles = {
  CRITICAL:
    "border-red-400/20 bg-red-400/10 text-red-400",
  HIGH:
    "border-orange-400/20 bg-orange-400/10 text-orange-400",
  MEDIUM:
    "border-amber-400/20 bg-amber-400/10 text-amber-400",
  LOW:
    "border-emerald-400/20 bg-emerald-400/10 text-emerald-400",
};

function ScoreBar({ label, value }) {
  return (
    <div>
      <div className="mb-1.5 flex justify-between text-[9px]">
        <span className="text-slate-600">{label}</span>
        <span className="font-semibold text-slate-400">
          {value}%
        </span>
      </div>

      <div className="h-1 overflow-hidden rounded-full bg-white/5">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 0.7 }}
          className="h-full rounded-full bg-cyan-400"
        />
      </div>
    </div>
  );
}

export default function VesselAttribution() {
  const [search, setSearch] = useState("");
  const [riskFilter, setRiskFilter] = useState("All");
  const [selected, setSelected] = useState(null);

  const filteredVessels = useMemo(() => {
    return vesselData.filter((vessel) => {
      const searchMatch =
        vessel.name.toLowerCase().includes(search.toLowerCase()) ||
        vessel.imo.toLowerCase().includes(search.toLowerCase()) ||
        vessel.type.toLowerCase().includes(search.toLowerCase());

      const riskMatch =
        riskFilter === "All" ||
        vessel.risk === riskFilter;

      return searchMatch && riskMatch;
    });
  }, [search, riskFilter]);

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute left-0 top-20 h-96 w-96 rounded-full bg-cyan-500/5 blur-3xl" />
        <div className="absolute right-0 top-1/3 h-96 w-96 rounded-full bg-blue-500/5 blur-3xl" />
      </div>

      <div className="relative space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -15 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col justify-between gap-4 lg:flex-row lg:items-end"
        >
          <div>
            <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400">
              <Ship size={14} />
              AIS Correlation Engine
            </div>

            <h1 className="text-3xl font-bold md:text-4xl">
              Vessel Attribution
            </h1>

            <p className="mt-2 max-w-2xl text-sm text-slate-400">
              Correlate historical AIS traffic with the estimated spill origin
              and rank vessels by investigation relevance.
            </p>
          </div>

          <div className="flex items-center gap-2 rounded-xl border border-emerald-400/20 bg-emerald-400/5 px-4 py-3">
            <Radio
              size={15}
              className="animate-pulse text-emerald-400"
            />

            <span className="text-xs font-semibold text-emerald-400">
              AIS NETWORK CONNECTED
            </span>
          </div>
        </motion.div>

        {/* Origin card */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-3xl border border-cyan-400/10 bg-cyan-400/[0.025] p-5 backdrop-blur-xl"
        >
          <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan-400/10 text-cyan-400">
                <Target size={22} />
              </div>

              <div>
                <p className="text-[10px] uppercase tracking-widest text-slate-600">
                  Probable Spill Origin
                </p>

                <p className="mt-1 text-lg font-bold">
                  Arabian Sea
                </p>

                <p className="mt-1 text-xs text-cyan-400">
                  18.742° N, 72.913° E
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {[
                ["Time Window", "08–14 hr"],
                ["Radius", "50 km"],
                ["Vessels", "42"],
                ["Ranked", "05"],
              ].map(([label, value]) => (
                <div
                  key={label}
                  className="rounded-xl border border-white/10 bg-black/10 px-4 py-3"
                >
                  <p className="text-[9px] uppercase text-slate-600">
                    {label}
                  </p>

                  <p className="mt-1 text-sm font-bold text-slate-200">
                    {value}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Stats */}
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {[
            ["Traffic Analysed", "42", Ship, "Historical AIS"],
            ["High Relevance", "03", ShieldAlert, "Priority review"],
            ["Trajectory Match", "91.4%", Route, "Top vessel"],
            ["Data Confidence", "96.2%", CheckCircle2, "Correlation model"],
          ].map(([label, value, Icon, sub], index) => (
            <motion.div
              key={label}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="rounded-2xl border border-white/10 bg-white/[0.03] p-5"
            >
              <div className="flex items-center justify-between">
                <div className="rounded-xl bg-cyan-400/10 p-2.5 text-cyan-400">
                  <Icon size={18} />
                </div>
              </div>

              <p className="mt-5 text-2xl font-bold">
                {value}
              </p>

              <p className="mt-1 text-xs text-slate-400">
                {label}
              </p>

              <p className="mt-1 text-[9px] text-slate-700">
                {sub}
              </p>
            </motion.div>
          ))}
        </div>

        {/* Search/filter */}
        <div className="flex flex-col gap-3 rounded-2xl border border-white/10 bg-white/[0.03] p-4 md:flex-row">
          <div className="relative flex-1">
            <Search
              size={17}
              className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-600"
            />

            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search vessel name, IMO number or vessel type..."
              className="h-11 w-full rounded-xl border border-white/10 bg-black/10 pl-11 pr-4 text-sm text-slate-300 outline-none placeholder:text-slate-700 focus:border-cyan-400/40"
            />
          </div>

          <div className="flex items-center gap-2">
            <Filter size={15} className="text-slate-600" />

            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="h-11 rounded-xl border border-white/10 bg-[#07101f] px-4 text-xs text-slate-300 outline-none"
            >
              <option>All</option>
              <option>CRITICAL</option>
              <option>HIGH</option>
              <option>MEDIUM</option>
              <option>LOW</option>
            </select>
          </div>
        </div>

        {/* Vessel list */}
        <div className="space-y-3">
          {filteredVessels.map((vessel, index) => (
            <motion.div
              key={vessel.imo}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="rounded-3xl border border-white/10 bg-white/[0.03] p-5 backdrop-blur-xl transition hover:border-cyan-400/20"
            >
              <div className="flex flex-col gap-5 xl:flex-row xl:items-center">
                {/* Rank */}
                <div className="flex items-center gap-4 xl:w-[300px]">
                  <div
                    className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border text-sm font-bold ${
                      vessel.rank === 1
                        ? "border-red-400/30 bg-red-400/10 text-red-400"
                        : "border-white/10 bg-white/[0.03] text-slate-400"
                    }`}
                  >
                    #{vessel.rank}
                  </div>

                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="truncate font-semibold text-slate-200">
                        {vessel.name}
                      </h3>

                      <span
                        className={`rounded-full border px-2 py-1 text-[8px] font-bold ${riskStyles[vessel.risk]}`}
                      >
                        {vessel.risk}
                      </span>
                    </div>

                    <div className="mt-1 flex flex-wrap gap-3 text-[10px] text-slate-600">
                      <span>{vessel.imo}</span>
                      <span>{vessel.type}</span>
                      <span>{vessel.flag}</span>
                    </div>
                  </div>
                </div>

                {/* Distance */}
                <div className="flex items-center gap-3 xl:w-[150px]">
                  <div className="rounded-xl bg-cyan-400/10 p-2 text-cyan-400">
                    <MapPin size={16} />
                  </div>

                  <div>
                    <p className="text-[9px] uppercase text-slate-600">
                      Origin Distance
                    </p>

                    <p className="mt-1 text-sm font-bold">
                      {vessel.distance}
                    </p>
                  </div>
                </div>

                {/* Scores */}
                <div className="grid flex-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
                  <ScoreBar
                    label="Proximity"
                    value={vessel.proximity}
                  />

                  <ScoreBar
                    label="Timing"
                    value={vessel.timing}
                  />

                  <ScoreBar
                    label="Trajectory"
                    value={vessel.trajectory}
                  />

                  <ScoreBar
                    label="Anomaly"
                    value={vessel.anomaly}
                  />
                </div>

                {/* Button */}
                <button
                  onClick={() => setSelected(vessel)}
                  className="flex h-10 items-center justify-center gap-2 rounded-xl border border-white/10 px-4 text-xs font-semibold text-slate-300 transition hover:border-cyan-400/30 hover:bg-cyan-400/10 hover:text-cyan-300"
                >
                  Details
                  <ChevronRight size={15} />
                </button>
              </div>
            </motion.div>
          ))}

          {filteredVessels.length === 0 && (
            <div className="rounded-3xl border border-dashed border-white/10 py-20 text-center">
              <Ship
                size={30}
                className="mx-auto text-slate-700"
              />

              <p className="mt-4 text-sm font-semibold text-slate-400">
                No matching vessels
              </p>

              <p className="mt-1 text-xs text-slate-700">
                Try changing your search or risk filter.
              </p>
            </div>
          )}
        </div>

        {/* Methodology */}
        <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
          <div className="flex items-start gap-3">
            <Activity
              size={18}
              className="mt-0.5 text-cyan-400"
            />

            <div>
              <h3 className="text-sm font-semibold">
                Attribution Methodology
              </h3>

              <p className="mt-1 max-w-4xl text-xs leading-6 text-slate-600">
                Vessel relevance is calculated using a multi-factor
                correlation model combining distance from the estimated
                origin, temporal compatibility, trajectory similarity and
                behavioural anomalies. Higher scores indicate stronger
                investigative relevance and do not independently establish
                responsibility.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Details modal */}
      {selected && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-md"
          onClick={() => setSelected(null)}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-2xl rounded-3xl border border-white/10 bg-[#07101f] p-6"
          >
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <Ship size={18} className="text-cyan-400" />

                  <span className="text-[10px] uppercase tracking-widest text-cyan-400">
                    Vessel Profile
                  </span>
                </div>

                <h2 className="mt-2 text-2xl font-bold">
                  {selected.name}
                </h2>

                <p className="mt-1 text-xs text-slate-600">
                  {selected.imo} • {selected.type}
                </p>
              </div>

              <button
                onClick={() => setSelected(null)}
                className="rounded-xl border border-white/10 p-2 text-slate-500 hover:text-white"
              >
                <X size={18} />
              </button>
            </div>

            <div className="mt-6 grid gap-3 sm:grid-cols-2">
              {[
                ["Flag State", selected.flag],
                ["Distance", selected.distance],
                ["Current Speed", selected.speed],
                ["Heading", selected.heading],
                ["Last AIS Signal", selected.lastSeen],
                ["Investigation Rank", `#${selected.rank}`],
              ].map(([label, value]) => (
                <div
                  key={label}
                  className="rounded-xl border border-white/10 bg-white/[0.03] p-4"
                >
                  <p className="text-[9px] uppercase tracking-wider text-slate-600">
                    {label}
                  </p>

                  <p className="mt-1 text-sm font-semibold text-slate-200">
                    {value}
                  </p>
                </div>
              ))}
            </div>

            <div className="mt-5 rounded-2xl border border-cyan-400/10 bg-cyan-400/[0.03] p-5">
              <div className="flex items-center gap-2">
                <Route size={16} className="text-cyan-400" />

                <h3 className="text-sm font-semibold">
                  Correlation Scores
                </h3>
              </div>

              <div className="mt-5 space-y-4">
                <ScoreBar
                  label="Proximity Match"
                  value={selected.proximity}
                />

                <ScoreBar
                  label="Temporal Match"
                  value={selected.timing}
                />

                <ScoreBar
                  label="Trajectory Match"
                  value={selected.trajectory}
                />

                <ScoreBar
                  label="Behavioural Anomaly"
                  value={selected.anomaly}
                />
              </div>
            </div>

            <div className="mt-5 flex items-start gap-3 rounded-xl border border-amber-400/10 bg-amber-400/[0.03] p-4">
              <AlertTriangle
                size={16}
                className="mt-0.5 shrink-0 text-amber-400"
              />

              <p className="text-[10px] leading-5 text-slate-600">
                This vessel is ranked as an investigative lead based on AIS
                correlation signals. The ranking is not a determination of
                responsibility.
              </p>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}