import React from "react";

import {
  Activity,
  AlertTriangle,
  Gauge,
  Radar,
  ScanLine,
  Satellite,
  ShieldCheck,
  Ship,
  Target,
  TrendingUp,
} from "lucide-react";

import {
  motion,
} from "framer-motion";

import StatCard from "../Components/StatCard";
import MapView from "../Components/MapView";
import SpillCard from "../Components/SpillCard";
import VesselTable from "../Components/VesselTable";
import RiskBadge from "../Components/RiskBadge";

const spills = [
  {
    id: "SPILL-001",
    location: "Arabian Sea",
    area: "42.6 km²",
    confidence: "94.8%",
    detectedAt: "12 Sep 2026 • 00:18",
    risk: "HIGH",
    status: "Active",
  },
  {
    id: "SPILL-002",
    location: "Bay of Bengal",
    area: "18.4 km²",
    confidence: "91.3%",
    detectedAt: "11 Sep 2026 • 18:42",
    risk: "MEDIUM",
    status: "Monitoring",
  },
  {
    id: "SPILL-003",
    location: "Indian Ocean",
    area: "8.7 km²",
    confidence: "89.6%",
    detectedAt: "11 Sep 2026 • 12:06",
    risk: "LOW",
    status: "Resolved",
  },
];

export default function Dashboard() {

  return (
    <div className="page-enter p-4 sm:p-6">

      {/* HEADER */}

      <div className="mb-7 flex flex-col justify-between gap-5 xl:flex-row xl:items-end">

        <div>

          <div className="mb-2 flex items-center gap-2">

            <span className="status-dot" />

            <span className="text-[9px] font-bold uppercase tracking-[.25em] text-emerald-400">
              Intelligence Network Operational
            </span>

          </div>

          <h1 className="text-3xl font-black tracking-tight text-white sm:text-4xl">
            Maritime
            <span className="gradient-text">
              {" "}Command Center
            </span>
          </h1>

          <p className="mt-2 text-xs text-slate-500">
            Real-time oil spill detection, drift intelligence
            and vessel correlation.
          </p>

        </div>

        <button className="glow-button flex items-center justify-center gap-2 rounded-xl px-5 py-3 text-xs font-bold text-white">

          <ScanLine size={15} />

          NEW INVESTIGATION

        </button>

      </div>

      {/* KPI */}

      <div className="stagger grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

        <StatCard
          title="Active Detections"
          value="24"
          change="+12.4% this month"
          icon={AlertTriangle}
          color="red"
        />

        <StatCard
          title="Detection Confidence"
          value="94.8%"
          change="+3.2% model confidence"
          icon={Target}
          color="cyan"
        />

        <StatCard
          title="Vessels Correlated"
          value="167"
          change="+18 vessels today"
          icon={Ship}
          color="violet"
        />

        <StatCard
          title="Model Accuracy"
          value="97.2%"
          change="+1.8% improvement"
          icon={Gauge}
          color="green"
        />

      </div>

      {/* MAIN GRID */}

      <div className="mt-5 grid gap-5 xl:grid-cols-[1.6fr_.8fr]">

        {/* MAP */}

        <div className="glass overflow-hidden rounded-2xl">

          <div className="flex items-center justify-between border-b border-white/[.05] px-5 py-4">

            <div>

              <h2 className="flex items-center gap-2 text-sm font-bold text-white">

                <Satellite
                  size={16}
                  className="text-cyan-400"
                />

                Live Maritime Intelligence

              </h2>

              <p className="mt-1 text-[10px] text-slate-600">
                Satellite detections and vessel intelligence
              </p>

            </div>

            <div className="flex items-center gap-2">

              <span className="status-dot" />

              <span className="text-[9px] text-emerald-400">
                LIVE
              </span>

            </div>

          </div>

          <div className="p-2">

            <MapView height="520px" />

          </div>

        </div>

        {/* RADAR */}

        <div className="glass rounded-2xl p-5">

          <div className="flex items-center justify-between">

            <div>

              <h2 className="text-sm font-bold text-white">
                Intelligence Radar
              </h2>

              <p className="mt-1 text-[10px] text-slate-600">
                Regional activity monitor
              </p>

            </div>

            <Radar
              size={18}
              className="text-cyan-400"
            />

          </div>

          <div className="mt-8 flex justify-center">

            <div className="radar h-64 w-64">

              <div className="radar-sweep" />

              <span
                className="radar-point"
                style={{
                  top: "25%",
                  left: "65%",
                }}
              />

              <span
                className="radar-point"
                style={{
                  top: "55%",
                  left: "35%",
                }}
              />

              <span
                className="radar-point"
                style={{
                  top: "68%",
                  left: "67%",
                }}
              />

              <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">

                <div className="flex h-12 w-12 items-center justify-center rounded-full border border-cyan-400/30 bg-cyan-400/10">

                  <Activity
                    size={18}
                    className="text-cyan-400"
                  />

                </div>

              </div>

            </div>

          </div>

          <div className="mt-7 grid grid-cols-2 gap-3">

            <RadarStat
              label="Tracked"
              value="154"
            />

            <RadarStat
              label="Alerts"
              value="19"
            />

            <RadarStat
              label="Critical"
              value="05"
            />

            <RadarStat
              label="Regions"
              value="12"
            />

          </div>

        </div>

      </div>

      {/* INTELLIGENCE */}

      <div className="mt-5 grid gap-5 lg:grid-cols-3">

        <div className="glass rounded-2xl p-5 lg:col-span-2">

          <div className="flex items-center justify-between">

            <div>

              <p className="text-[9px] font-bold uppercase tracking-[.25em] text-violet-400">
                AI Intelligence Brief
              </p>

              <h2 className="mt-2 text-lg font-black text-white">
                Arabian Sea Event
              </h2>

            </div>

            <ShieldCheck
              className="text-emerald-400"
              size={20}
            />

          </div>

          <p className="mt-5 text-xs leading-6 text-slate-400">
            OILTRACE detected a high-confidence elongated
            anomaly in the Arabian Sea. Current correlation
            suggests a strong match between the spill
            origin window and nearby vessel traffic.
          </p>

          <div className="mt-5 flex flex-wrap gap-2">

            <Tag text="94.8% confidence" />

            <Tag text="42.6 km² area" />

            <Tag text="8–14h estimated age" />

            <Tag text="AIS correlation active" />

          </div>

        </div>

        <div className="critical rounded-2xl border border-rose-400/10 bg-rose-500/[.03] p-5">

          <div className="flex items-center gap-3">

            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-rose-500/10 text-rose-400">
              <AlertTriangle size={18} />
            </div>

            <div>

              <p className="text-[9px] font-bold uppercase tracking-widest text-rose-400">
                Priority Alert
              </p>

              <p className="mt-1 text-sm font-bold text-white">
                High-risk detection
              </p>

            </div>

          </div>

          <p className="mt-5 text-xs leading-6 text-slate-500">
            Spill-001 requires immediate investigation
            through drift prediction and AIS attribution.
          </p>

          <div className="mt-5">
            <RiskBadge risk="HIGH" />
          </div>

        </div>

      </div>

      {/* RECENT */}

      <div className="mt-5 grid gap-5 xl:grid-cols-2">

        <div>

          <div className="mb-3 flex items-center justify-between">

            <div>

              <h2 className="text-sm font-bold text-white">
                Recent Spill Detections
              </h2>

              <p className="mt-1 text-[10px] text-slate-600">
                Latest satellite-derived events
              </p>

            </div>

            <TrendingUp
              size={17}
              className="text-cyan-400"
            />

          </div>

          <div className="space-y-3">

            {spills.map((spill) => (
              <SpillCard
                key={spill.id}
                spill={spill}
              />
            ))}

          </div>

        </div>

        <VesselTable />

      </div>

    </div>
  );
}

function RadarStat({
  label,
  value,
}) {
  return (
    <div className="rounded-xl border border-white/[.05] bg-white/[.02] p-3">

      <p className="text-[8px] uppercase tracking-widest text-slate-600">
        {label}
      </p>

      <p className="mt-1 text-lg font-black text-white">
        {value}
      </p>

    </div>
  );
}

function Tag({ text }) {
  return (
    <span className="rounded-full border border-cyan-400/10 bg-cyan-400/[.04] px-3 py-1.5 text-[9px] text-cyan-300">
      {text}
    </span>
  );
}