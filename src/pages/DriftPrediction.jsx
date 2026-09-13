import React, { useState } from "react";
import {
  Wind,
  Waves,
  Navigation,
  Clock3,
  Target,
  MapPin,
  Activity,
  Play,
  RotateCcw,
  AlertTriangle,
  Cloud,
  Gauge,
} from "lucide-react";
import { motion } from "framer-motion";

export default function DriftPrediction() {
  const [hours, setHours] = useState(24);
  const [running, setRunning] = useState(false);

  const runPrediction = () => {
    setRunning(true);

    setTimeout(() => {
      setRunning(false);
    }, 1800);
  };

  return (
    <div className="space-y-6">

      {/* =====================================================
          HEADER
      ====================================================== */}

      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between"
      >
        <div>

          <div className="mb-2 flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-400/10 text-blue-400">
              <Wind size={15} />
            </div>

            <span className="text-[9px] font-bold uppercase tracking-[0.2em] text-blue-400">
              Ocean Dynamics Engine
            </span>
          </div>

          <h1 className="text-2xl font-bold text-white md:text-3xl">
            Drift Prediction
          </h1>

          <p className="mt-2 max-w-2xl text-xs leading-relaxed text-slate-500">
            Simulate probable oil-spill movement using ocean
            currents, wind conditions and historical environmental
            data.
          </p>
        </div>

        <button
          onClick={runPrediction}
          disabled={running}
          className="flex items-center justify-center gap-2 rounded-xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2.5 text-[10px] font-semibold text-cyan-300 transition hover:bg-cyan-400/15 disabled:opacity-50"
        >
          {running ? (
            <>
              <Activity
                size={13}
                className="animate-pulse"
              />
              Running Model...
            </>
          ) : (
            <>
              <Play size={13} />
              Run Prediction
            </>
          )}
        </button>
      </motion.div>

      {/* =====================================================
          CONDITIONS
      ====================================================== */}

      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">

        <ConditionCard
          icon={Wind}
          label="Wind Speed"
          value="18 km/h"
          sub="North-East"
          color="cyan"
        />

        <ConditionCard
          icon={Waves}
          label="Ocean Current"
          value="1.8 knots"
          sub="Eastward"
          color="blue"
        />

        <ConditionCard
          icon={Cloud}
          label="Weather"
          value="Partly Cloudy"
          sub="Visibility 9 km"
          color="amber"
        />

        <ConditionCard
          icon={Gauge}
          label="Model Confidence"
          value="91.8%"
          sub="High confidence"
          color="emerald"
        />

      </div>

      {/* =====================================================
          PREDICTION MAP
      ====================================================== */}

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1.7fr_0.65fr]">

        <div className="relative min-h-[560px] overflow-hidden rounded-3xl border border-slate-800/80 bg-[#06131f] shadow-xl">

          {/* Grid */}

          <div
            className="absolute inset-0 opacity-30"
            style={{
              backgroundImage: `
                linear-gradient(rgba(34,211,238,0.06) 1px, transparent 1px),
                linear-gradient(90deg, rgba(34,211,238,0.06) 1px, transparent 1px)
              `,
              backgroundSize: "45px 45px",
            }}
          />

          {/* Ocean background */}

          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(14,116,144,0.22),transparent_35%)]" />

          {/* Header */}

          <div className="absolute left-0 right-0 top-0 z-20 flex items-center justify-between border-b border-white/5 bg-[#06131f]/80 px-4 py-3 backdrop-blur-xl">

            <div className="flex items-center gap-2">
              <Navigation
                size={14}
                className="text-cyan-400"
              />

              <div>
                <p className="text-[10px] font-semibold text-white">
                  Predicted Spill Trajectory
                </p>

                <p className="text-[8px] text-slate-600">
                  Arabian Sea • Simulation active
                </p>
              </div>
            </div>

            <span className="rounded-lg border border-emerald-400/15 bg-emerald-400/5 px-2 py-1 text-[8px] font-semibold text-emerald-400">
              91.8% CONFIDENCE
            </span>
          </div>

          {/* Origin */}

          <div className="absolute left-[31%] top-[57%] z-10">

            <motion.div
              animate={{
                scale: [1, 1.4, 1],
                opacity: [0.6, 0, 0.6],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
              }}
              className="absolute -inset-5 rounded-full border border-red-400/40"
            />

            <div className="relative flex h-10 w-10 items-center justify-center rounded-full border-2 border-red-300 bg-red-500/20 text-red-300 shadow-[0_0_25px_rgba(239,68,68,0.4)]">
              <Target size={17} />
            </div>

            <div className="absolute left-12 top-0 whitespace-nowrap rounded-lg border border-red-400/20 bg-black/50 px-2.5 py-2 backdrop-blur-md">
              <p className="text-[8px] font-bold text-red-300">
                ORIGIN
              </p>

              <p className="mt-1 font-mono text-[7px] text-slate-500">
                18.742° N • 72.913° E
              </p>
            </div>
          </div>

          {/* Prediction path */}

          <svg
            className="absolute inset-0 h-full w-full"
            viewBox="0 0 1000 600"
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient
                id="predictionPath"
                x1="0"
                y1="1"
                x2="1"
                y2="0"
              >
                <stop
                  offset="0%"
                  stopColor="#22d3ee"
                  stopOpacity="0.1"
                />
                <stop
                  offset="50%"
                  stopColor="#22d3ee"
                  stopOpacity="0.8"
                />
                <stop
                  offset="100%"
                  stopColor="#60a5fa"
                  stopOpacity="0.2"
                />
              </linearGradient>
            </defs>

            <motion.path
              d="M320 350 C400 320, 430 290, 500 275 C580 250, 650 205, 760 170"
              fill="none"
              stroke="url(#predictionPath)"
              strokeWidth="5"
              strokeDasharray="12 10"
              animate={{
                strokeDashoffset: [0, -44],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "linear",
              }}
            />

            <path
              d="M760 170 L735 175 L750 192 Z"
              fill="#38bdf8"
            />
          </svg>

          {/* Forecast points */}

          <ForecastPoint
            left="45%"
            top="49%"
            label="+6h"
          />

          <ForecastPoint
            left="57%"
            top="42%"
            label="+12h"
          />

          <ForecastPoint
            left="68%"
            top="34%"
            label="+18h"
          />

          <ForecastPoint
            left="77%"
            top="27%"
            label="+24h"
            final
          />

          {/* Bottom info */}

          <div className="absolute bottom-4 left-4 right-4 z-20 flex flex-col gap-3 rounded-2xl border border-white/5 bg-[#07131f]/85 p-3 backdrop-blur-xl sm:flex-row sm:items-center sm:justify-between">

            <div className="flex items-center gap-3">
              <Waves
                size={15}
                className="text-blue-400"
              />

              <div>
                <p className="text-[8px] uppercase tracking-wider text-slate-600">
                  Predicted Direction
                </p>

                <p className="mt-1 text-[10px] font-semibold text-white">
                  North-East • 68 km projected
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Clock3
                size={12}
                className="text-slate-600"
              />

              <span className="text-[9px] text-slate-500">
                Updated 2 min ago
              </span>
            </div>
          </div>
        </div>

        {/* =================================================
            SETTINGS
        ================================================== */}

        <div className="space-y-4">

          <div className="rounded-2xl border border-slate-800/80 bg-[#07131f]/80 p-5 shadow-xl">

            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-400">
                <Clock3 size={16} />
              </div>

              <div>
                <h3 className="text-xs font-semibold text-white">
                  Forecast Horizon
                </h3>

                <p className="mt-1 text-[8px] text-slate-600">
                  Select prediction duration
                </p>
              </div>
            </div>

            <div className="mt-6 grid grid-cols-2 gap-2">
              {[6, 12, 24, 48].map(
                (value) => (
                  <button
                    key={value}
                    onClick={() =>
                      setHours(value)
                    }
                    className={`rounded-xl border px-3 py-3 text-[9px] font-semibold transition ${
                      hours === value
                        ? "border-cyan-400/25 bg-cyan-400/10 text-cyan-300"
                        : "border-slate-800 bg-slate-900/40 text-slate-600 hover:text-slate-300"
                    }`}
                  >
                    {value} Hours
                  </button>
                )
              )}
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800/80 bg-[#07131f]/80 p-5 shadow-xl">

            <p className="text-[9px] font-bold uppercase tracking-[0.15em] text-slate-600">
              Environmental Inputs
            </p>

            <div className="mt-4 space-y-3">

              <InputRow
                icon={Wind}
                label="Wind"
                value="18 km/h NE"
              />

              <InputRow
                icon={Waves}
                label="Current"
                value="1.8 knots E"
              />

              <InputRow
                icon={Cloud}
                label="Weather"
                value="Partly Cloudy"
              />

              <InputRow
                icon={Gauge}
                label="Sea State"
                value="Moderate"
              />

            </div>
          </div>

          <div className="rounded-2xl border border-amber-400/15 bg-amber-400/[0.035] p-4">

            <div className="flex gap-3">
              <AlertTriangle
                size={15}
                className="mt-0.5 shrink-0 text-amber-400"
              />

              <div>
                <p className="text-[9px] font-semibold text-amber-300">
                  Prediction Notice
                </p>

                <p className="mt-1 text-[8px] leading-relaxed text-slate-500">
                  Forecast accuracy may decrease beyond
                  the selected horizon due to changing
                  oceanographic conditions.
                </p>
              </div>
            </div>
          </div>

          <button
            onClick={() => setHours(24)}
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-slate-800 bg-slate-900/50 py-2.5 text-[9px] font-medium text-slate-500 transition hover:text-slate-200"
          >
            <RotateCcw size={12} />
            Reset Parameters
          </button>
        </div>
      </div>
    </div>
  );
}

/* ============================================================
   CONDITION CARD
============================================================ */

function ConditionCard({
  icon: Icon,
  label,
  value,
  sub,
  color,
}) {
  const colors = {
    cyan: "text-cyan-400 bg-cyan-400/10",
    blue: "text-blue-400 bg-blue-400/10",
    amber: "text-amber-400 bg-amber-400/10",
    emerald: "text-emerald-400 bg-emerald-400/10",
  };

  return (
    <div className="rounded-2xl border border-slate-800/80 bg-[#07131f]/80 p-4 backdrop-blur-xl">
      <div className="flex items-center gap-3">

        <div
          className={`flex h-9 w-9 items-center justify-center rounded-xl ${colors[color]}`}
        >
          <Icon size={15} />
        </div>

        <div>
          <p className="text-[8px] uppercase tracking-wider text-slate-600">
            {label}
          </p>

          <p className="mt-1 text-sm font-bold text-white">
            {value}
          </p>

          <p className="mt-0.5 text-[8px] text-slate-600">
            {sub}
          </p>
        </div>
      </div>
    </div>
  );
}

/* ============================================================
   FORECAST POINT
============================================================ */

function ForecastPoint({
  left,
  top,
  label,
  final = false,
}) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="absolute z-10"
      style={{ left, top }}
    >
      <div
        className={`h-3 w-3 rounded-full border ${
          final
            ? "border-blue-200 bg-blue-400 shadow-[0_0_15px_rgba(96,165,250,0.7)]"
            : "border-cyan-300 bg-cyan-400"
        }`}
      />

      <span className="absolute left-4 top-[-3px] whitespace-nowrap rounded-md bg-black/40 px-1.5 py-1 text-[7px] text-slate-400 backdrop-blur">
        {label}
      </span>
    </motion.div>
  );
}

/* ============================================================
   INPUT ROW
============================================================ */

function InputRow({
  icon: Icon,
  label,
  value,
}) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-slate-800/70 bg-slate-900/30 p-2.5">

      <div className="flex items-center gap-2">
        <Icon
          size={13}
          className="text-cyan-400"
        />

        <span className="text-[9px] text-slate-500">
          {label}
        </span>
      </div>

      <span className="text-[9px] font-semibold text-slate-300">
        {value}
      </span>
    </div>
  );
}