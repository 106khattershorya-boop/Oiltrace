import React, { useMemo, useState } from "react";
import {
  Activity,
  BarChart3,
  TrendingUp,
  TrendingDown,
  Droplets,
  Ship,
  ShieldCheck,
  CalendarDays,
  Download,
  Target,
  AlertTriangle,
  Waves,
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { motion } from "framer-motion";

const monthlyData = [
  { month: "Mar", spills: 12, vessels: 86, accuracy: 91 },
  { month: "Apr", spills: 16, vessels: 102, accuracy: 92 },
  { month: "May", spills: 13, vessels: 118, accuracy: 93 },
  { month: "Jun", spills: 21, vessels: 131, accuracy: 94 },
  { month: "Jul", spills: 18, vessels: 145, accuracy: 95 },
  { month: "Aug", spills: 24, vessels: 167, accuracy: 96 },
  { month: "Sep", spills: 19, vessels: 154, accuracy: 97 },
];

const riskData = [
  { name: "Low", value: 48 },
  { name: "Medium", value: 31 },
  { name: "High", value: 16 },
  { name: "Critical", value: 5 },
];

const regionData = [
  { region: "Arabian Sea", detections: 42 },
  { region: "Bay of Bengal", detections: 31 },
  { region: "Indian Ocean", detections: 24 },
  { region: "Gulf Region", detections: 18 },
  { region: "Other", detections: 11 },
];

const pieColors = [
  "rgba(16,185,129,0.8)",
  "rgba(245,158,11,0.8)",
  "rgba(249,115,22,0.8)",
  "rgba(239,68,68,0.8)",
];

export default function Analytics() {
  const [period, setPeriod] = useState("7M");

  const totalSpills = useMemo(
    () =>
      monthlyData.reduce(
        (sum, item) => sum + item.spills,
        0
      ),
    []
  );

  return (
    <div className="space-y-6">

      {/* =====================================================
          HEADER
      ====================================================== */}

      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between"
      >
        <div>
          <div className="mb-2 flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-cyan-400/15 bg-cyan-400/10">
              <BarChart3
                size={15}
                className="text-cyan-400"
              />
            </div>

            <span className="text-[9px] font-bold uppercase tracking-[0.2em] text-cyan-400">
              Intelligence Analytics
            </span>
          </div>

          <h1 className="text-2xl font-bold tracking-tight text-white md:text-3xl">
            Maritime Analytics
          </h1>

          <p className="mt-2 max-w-2xl text-xs leading-relaxed text-slate-500">
            Monitor oil-spill detection trends, vessel correlations,
            model performance and regional intelligence activity.
          </p>
        </div>

        <div className="flex items-center gap-2">

          <div className="flex rounded-xl border border-slate-800 bg-slate-900/50 p-1">
            {["30D", "90D", "7M"].map((item) => (
              <button
                key={item}
                onClick={() => setPeriod(item)}
                className={`rounded-lg px-3 py-2 text-[9px] font-semibold transition ${
                  period === item
                    ? "bg-cyan-400/10 text-cyan-300"
                    : "text-slate-600 hover:text-slate-300"
                }`}
              >
                {item}
              </button>
            ))}
          </div>

          <button className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-900/50 px-3 py-2.5 text-[9px] font-medium text-slate-400 transition hover:border-cyan-400/20 hover:text-cyan-300">
            <Download size={13} />
            Export
          </button>
        </div>
      </motion.div>

      {/* =====================================================
          KPI CARDS
      ====================================================== */}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">

        <MetricCard
          title="Total Spill Events"
          value={totalSpills}
          change="+12.4%"
          positive={false}
          icon={Droplets}
          color="red"
        />

        <MetricCard
          title="Vessels Correlated"
          value="903"
          change="+18.7%"
          positive
          icon={Ship}
          color="cyan"
        />

        <MetricCard
          title="Detection Accuracy"
          value="96.8%"
          change="+2.1%"
          positive
          icon={Target}
          color="emerald"
        />

        <MetricCard
          title="Compliance / Confidence"
          value="94.2%"
          change="+4.6%"
          positive
          icon={ShieldCheck}
          color="blue"
        />

      </div>

      {/* =====================================================
          MAIN CHART
      ====================================================== */}

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1.7fr_1fr]">

        <ChartCard
          title="Detection & Vessel Correlation"
          subtitle="Monthly intelligence activity"
          icon={Activity}
        >
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={monthlyData}>
              <defs>
                <linearGradient
                  id="spillGradient"
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop
                    offset="0%"
                    stopColor="#22d3ee"
                    stopOpacity={0.28}
                  />
                  <stop
                    offset="100%"
                    stopColor="#22d3ee"
                    stopOpacity={0}
                  />
                </linearGradient>
              </defs>

              <CartesianGrid
                stroke="rgba(148,163,184,0.06)"
                vertical={false}
              />

              <XAxis
                dataKey="month"
                axisLine={false}
                tickLine={false}
                tick={{
                  fill: "#475569",
                  fontSize: 9,
                }}
              />

              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{
                  fill: "#475569",
                  fontSize: 9,
                }}
              />

              <Tooltip
                contentStyle={{
                  background: "#07131f",
                  border: "1px solid rgba(148,163,184,0.12)",
                  borderRadius: "12px",
                  fontSize: "10px",
                }}
              />

              <Area
                type="monotone"
                dataKey="vessels"
                stroke="#22d3ee"
                strokeWidth={2}
                fill="url(#spillGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Risk distribution */}

        <ChartCard
          title="Risk Distribution"
          subtitle="Current classified events"
          icon={AlertTriangle}
        >
          <div className="relative h-full min-h-[230px]">

            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={riskData}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={65}
                  outerRadius={90}
                  paddingAngle={4}
                  stroke="none"
                >
                  {riskData.map((_, index) => (
                    <Cell
                      key={index}
                      fill={pieColors[index]}
                    />
                  ))}
                </Pie>

                <Tooltip
                  contentStyle={{
                    background: "#07131f",
                    border: "1px solid rgba(148,163,184,0.12)",
                    borderRadius: "12px",
                    fontSize: "10px",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>

            <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <p className="text-xl font-bold text-white">
                  100%
                </p>

                <p className="text-[8px] uppercase tracking-wider text-slate-600">
                  Classified
                </p>
              </div>
            </div>

            <div className="absolute bottom-0 left-1/2 flex -translate-x-1/2 gap-3">
              {riskData.map((item, index) => (
                <div
                  key={item.name}
                  className="flex items-center gap-1"
                >
                  <span
                    className="h-1.5 w-1.5 rounded-full"
                    style={{
                      background: pieColors[index],
                    }}
                  />

                  <span className="text-[8px] text-slate-500">
                    {item.name}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </ChartCard>
      </div>

      {/* =====================================================
          REGIONAL ANALYTICS
      ====================================================== */}

      <ChartCard
        title="Regional Spill Activity"
        subtitle="Detection count by maritime region"
        icon={Waves}
      >
        <div className="h-[280px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={regionData}
              layout="vertical"
              margin={{
                left: 20,
                right: 20,
              }}
            >
              <CartesianGrid
                stroke="rgba(148,163,184,0.05)"
                horizontal={false}
              />

              <XAxis
                type="number"
                axisLine={false}
                tickLine={false}
                tick={{
                  fill: "#475569",
                  fontSize: 9,
                }}
              />

              <YAxis
                type="category"
                dataKey="region"
                axisLine={false}
                tickLine={false}
                width={100}
                tick={{
                  fill: "#64748b",
                  fontSize: 9,
                }}
              />

              <Tooltip
                cursor={{
                  fill: "rgba(34,211,238,0.03)",
                }}
                contentStyle={{
                  background: "#07131f",
                  border: "1px solid rgba(148,163,184,0.12)",
                  borderRadius: "12px",
                  fontSize: "10px",
                }}
              />

              <Bar
                dataKey="detections"
                fill="#22d3ee"
                radius={[0, 6, 6, 0]}
                barSize={18}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </ChartCard>

      {/* =====================================================
          MODEL PERFORMANCE
      ====================================================== */}

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">

        <PerformanceCard
          title="Spill Detection"
          value="97.4%"
          subtitle="Image classification accuracy"
          icon={Droplets}
          progress={97.4}
        />

        <PerformanceCard
          title="Drift Prediction"
          value="91.8%"
          subtitle="Origin / trajectory accuracy"
          icon={Waves}
          progress={91.8}
        />

        <PerformanceCard
          title="Vessel Attribution"
          value="94.1%"
          subtitle="AIS correlation confidence"
          icon={Ship}
          progress={94.1}
        />

      </div>
    </div>
  );
}

/* ============================================================
   METRIC CARD
============================================================ */

function MetricCard({
  title,
  value,
  change,
  positive,
  icon: Icon,
  color,
}) {
  const colors = {
    cyan: "text-cyan-400 bg-cyan-400/10 border-cyan-400/15",
    blue: "text-blue-400 bg-blue-400/10 border-blue-400/15",
    emerald:
      "text-emerald-400 bg-emerald-400/10 border-emerald-400/15",
    red: "text-red-400 bg-red-400/10 border-red-400/15",
  };

  return (
    <motion.div
      whileHover={{ y: -4 }}
      className="relative overflow-hidden rounded-2xl border border-slate-800/80 bg-[#07131f]/80 p-4 shadow-xl backdrop-blur-xl"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[8px] uppercase tracking-[0.15em] text-slate-600">
            {title}
          </p>

          <p className="mt-2 text-2xl font-bold text-white">
            {value}
          </p>
        </div>

        <div
          className={`flex h-10 w-10 items-center justify-center rounded-xl border ${colors[color]}`}
        >
          <Icon size={17} />
        </div>
      </div>

      <div
        className={`mt-4 flex items-center gap-1 text-[9px] font-semibold ${
          positive
            ? "text-emerald-400"
            : "text-red-400"
        }`}
      >
        {positive ? (
          <TrendingUp size={11} />
        ) : (
          <TrendingDown size={11} />
        )}

        {change}

        <span className="ml-1 font-normal text-slate-600">
          vs previous period
        </span>
      </div>
    </motion.div>
  );
}

/* ============================================================
   CHART CARD
============================================================ */

function ChartCard({
  title,
  subtitle,
  icon: Icon,
  children,
}) {
  return (
    <div className="rounded-2xl border border-slate-800/80 bg-[#07131f]/80 p-4 shadow-xl backdrop-blur-xl">

      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-400">
          <Icon size={15} />
        </div>

        <div>
          <h3 className="text-xs font-semibold text-white">
            {title}
          </h3>

          <p className="mt-1 text-[8px] text-slate-600">
            {subtitle}
          </p>
        </div>
      </div>

      <div className="h-[280px]">
        {children}
      </div>
    </div>
  );
}

/* ============================================================
   PERFORMANCE CARD
============================================================ */

function PerformanceCard({
  title,
  value,
  subtitle,
  icon: Icon,
  progress,
}) {
  return (
    <div className="rounded-2xl border border-slate-800/80 bg-[#07131f]/80 p-5 shadow-xl backdrop-blur-xl">

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">

          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-400">
            <Icon size={16} />
          </div>

          <div>
            <p className="text-xs font-semibold text-white">
              {title}
            </p>

            <p className="mt-1 text-[8px] text-slate-600">
              {subtitle}
            </p>
          </div>
        </div>

        <span className="text-lg font-bold text-cyan-400">
          {value}
        </span>
      </div>

      <div className="mt-5 h-1.5 overflow-hidden rounded-full bg-slate-800">
        <motion.div
          initial={{ width: 0 }}
          animate={{
            width: `${progress}%`,
          }}
          transition={{
            duration: 1,
            ease: "easeOut",
          }}
          className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-blue-500"
        />
      </div>
    </div>
  );
}