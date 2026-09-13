import React, { useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  CalendarDays,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Crosshair,
  Database,
  Eye,
  FileBarChart2,
  FileText,
  Layers3,
  Plus,
  Radar,
  Search,
  ShieldCheck,
  Ship,
  Sparkles,
  Target,
  Trash2,
  TrendingUp,
  Waves,
  X,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

import {
  getReports,
  saveReport,
  deleteReport,
  getInspections,
} from "../utils/storage";

/* =========================================================
   HELPERS
========================================================= */

function parseDate(item) {
  const raw =
    item?.detectedAt ||
    item?.createdAt ||
    item?.date ||
    item?.timestamp;

  if (!raw) return new Date();

  const d = new Date(raw);

  return Number.isNaN(d.getTime()) ? new Date() : d;
}

function formatDate(value) {
  const d = new Date(value);

  if (Number.isNaN(d.getTime())) return "—";

  return d.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function getScore(item) {
  const value =
    item?.score ??
    item?.confidence ??
    item?.compliance_score ??
    item?.compliance?.compliance_score ??
    0;

  const n = Number(value);

  return Number.isFinite(n) ? n : 0;
}

function getRisk(item) {
  return String(
    item?.risk ||
      item?.severity ||
      item?.riskLevel ||
      "LOW"
  ).toUpperCase();
}

function getArea(item) {
  const value =
    item?.area ??
    item?.spillArea ??
    item?.spill_area ??
    0;

  const n = Number(value);

  return Number.isFinite(n) ? n : 0;
}

function getRiskStyle(risk) {
  switch (String(risk).toUpperCase()) {
    case "CRITICAL":
      return {
        text: "text-red-300",
        bg: "bg-red-500/10",
        border: "border-red-400/20",
        glow: "bg-red-500",
      };

    case "HIGH":
      return {
        text: "text-orange-300",
        bg: "bg-orange-500/10",
        border: "border-orange-400/20",
        glow: "bg-orange-500",
      };

    case "MEDIUM":
      return {
        text: "text-amber-300",
        bg: "bg-amber-500/10",
        border: "border-amber-400/20",
        glow: "bg-amber-500",
      };

    default:
      return {
        text: "text-emerald-300",
        bg: "bg-emerald-500/10",
        border: "border-emerald-400/20",
        glow: "bg-emerald-500",
      };
  }
}

/* =========================================================
   BACKGROUND FX
========================================================= */

function BackgroundFX() {
  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
      {/* Ambient lights */}
      <motion.div
        animate={{
          x: [0, 80, 0],
          y: [0, 40, 0],
        }}
        transition={{
          duration: 12,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute -left-40 -top-40 h-[500px] w-[500px] rounded-full bg-cyan-500/[0.07] blur-[130px]"
      />

      <motion.div
        animate={{
          x: [0, -70, 0],
          y: [0, 50, 0],
        }}
        transition={{
          duration: 15,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute right-[-160px] top-[20%] h-[600px] w-[600px] rounded-full bg-violet-600/[0.07] blur-[150px]"
      />

      <motion.div
        animate={{
          scale: [1, 1.15, 1],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute bottom-[-200px] left-[30%] h-[500px] w-[500px] rounded-full bg-blue-600/[0.05] blur-[150px]"
      />

      {/* Grid */}
      <div
        className="absolute inset-0 opacity-[0.025]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(56,189,248,.8) 1px, transparent 1px), linear-gradient(90deg, rgba(56,189,248,.8) 1px, transparent 1px)",
          backgroundSize: "48px 48px",
        }}
      />

      {/* Moving scanline */}
      <motion.div
        animate={{
          y: ["-10vh", "110vh"],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "linear",
        }}
        className="absolute left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-400/30 to-transparent shadow-[0_0_25px_rgba(34,211,238,.25)]"
      />

      {/* Vertical scanner */}
      <motion.div
        animate={{
          x: ["-10vw", "110vw"],
        }}
        transition={{
          duration: 18,
          repeat: Infinity,
          ease: "linear",
        }}
        className="absolute top-0 bottom-0 w-px bg-gradient-to-b from-transparent via-blue-400/10 to-transparent"
      />
    </div>
  );
}

/* =========================================================
   KPI CARD
========================================================= */

function KPI({
  icon: Icon,
  title,
  value,
  description,
  index,
  accent = "cyan",
}) {
  const accentMap = {
    cyan: "text-cyan-300 bg-cyan-400/[0.06] border-cyan-400/10",
    blue: "text-blue-300 bg-blue-400/[0.06] border-blue-400/10",
    violet:
      "text-violet-300 bg-violet-400/[0.06] border-violet-400/10",
    orange:
      "text-orange-300 bg-orange-400/[0.06] border-orange-400/10",
    emerald:
      "text-emerald-300 bg-emerald-400/[0.06] border-emerald-400/10",
  };

  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 25,
        scale: 0.96,
      }}
      animate={{
        opacity: 1,
        y: 0,
        scale: 1,
      }}
      transition={{
        duration: 0.5,
        delay: index * 0.08,
      }}
      whileHover={{
        y: -7,
        scale: 1.015,
      }}
      className="group relative overflow-hidden rounded-[24px] border border-white/[0.07] bg-[#07101d]/80 p-5 shadow-[0_20px_60px_rgba(0,0,0,.18)] backdrop-blur-xl"
    >
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.4, 0.7, 0.4],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
        }}
        className="absolute -right-12 -top-12 h-32 w-32 rounded-full bg-cyan-400/[0.05] blur-2xl"
      />

      <div className="relative flex items-start justify-between">
        <div>
          <p className="text-[9px] font-black uppercase tracking-[0.22em] text-slate-600">
            {title}
          </p>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{
              delay: index * 0.08 + 0.25,
            }}
            className="mt-2 text-[28px] font-black tracking-tight text-white"
          >
            {value}
          </motion.p>

          <p className="mt-1 text-[10px] text-slate-600">
            {description}
          </p>
        </div>

        <div
          className={`rounded-xl border p-3 ${accentMap[accent]}`}
        >
          <Icon size={18} />
        </div>
      </div>

      <div className="mt-5 h-1 overflow-hidden rounded-full bg-white/[0.03]">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${30 + index * 13}%` }}
          transition={{
            duration: 1,
            delay: index * 0.1,
          }}
          className="h-full rounded-full bg-gradient-to-r from-cyan-400 via-blue-500 to-violet-500"
        />
      </div>

      <div className="absolute bottom-0 left-0 h-px w-0 bg-gradient-to-r from-cyan-400 to-violet-500 transition-all duration-500 group-hover:w-full" />
    </motion.div>
  );
}

/* =========================================================
   DATE FIELD
========================================================= */

function DateField({ label, value, onChange }) {
  return (
    <div className="flex-1">
      <label className="mb-2 flex items-center gap-2 text-[9px] font-black uppercase tracking-[0.2em] text-slate-500">
        <CalendarDays
          size={12}
          className="text-cyan-400"
        />
        {label}
      </label>

      <div className="group relative">
        <CalendarDays
          size={16}
          className="pointer-events-none absolute left-3 top-1/2 z-10 -translate-y-1/2 text-cyan-400/70"
        />

        <input
          type="date"
          value={value}
          onChange={(e) =>
            onChange(e.target.value)
          }
          className="
            w-full
            appearance-none
            rounded-xl
            border
            border-white/[0.09]
            bg-[#020812]
            px-4
            py-3
            pl-10
            text-sm
            font-semibold
            text-white
            outline-none
            transition-all
            hover:border-cyan-400/30
            focus:border-cyan-400/50
            focus:bg-[#06111f]
            focus:ring-2
            focus:ring-cyan-400/10
            [&::-webkit-calendar-picker-indicator]:cursor-pointer
            [&::-webkit-calendar-picker-indicator]:opacity-100
            [&::-webkit-calendar-picker-indicator]:brightness-200
            [&::-webkit-calendar-picker-indicator]:invert
          "
        />
      </div>
    </div>
  );
}

/* =========================================================
   REPORT CARD
========================================================= */

function ReportCard({
  report,
  inspections,
  index,
  onPreview,
  onDelete,
}) {
  const risk = getRisk(report);
  const riskStyle = getRiskStyle(risk);

  const related = inspections.filter(
    (inspection) =>
      Array.isArray(report.inspections)
        ? report.inspections.includes(
            inspection.id
          )
        : true
  );

  const score =
    report.score ??
    (related.length
      ? related.reduce(
          (sum, item) =>
            sum + getScore(item),
          0
        ) / related.length
      : 0);

  return (
    <motion.div
      layout
      initial={{
        opacity: 0,
        y: 30,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      exit={{
        opacity: 0,
        scale: 0.9,
      }}
      transition={{
        duration: 0.45,
        delay: index * 0.06,
      }}
      whileHover={{
        y: -9,
      }}
      className="group relative"
    >
      {/* Glow */}
      <div className="absolute -inset-px rounded-[28px] bg-gradient-to-r from-cyan-400/0 via-blue-500/0 to-violet-500/0 opacity-0 blur-md transition-all duration-500 group-hover:from-cyan-400/30 group-hover:via-blue-500/20 group-hover:to-violet-500/30 group-hover:opacity-100" />

      <div className="relative overflow-hidden rounded-[28px] border border-white/[0.07] bg-[#07101d]/90 shadow-[0_25px_70px_rgba(0,0,0,.25)] backdrop-blur-xl">
        {/* Top neon line */}
        <div className="h-[2px] bg-gradient-to-r from-cyan-400 via-blue-500 to-violet-500" />

        {/* Radar decoration */}
        <div className="absolute right-[-45px] top-[-45px] h-40 w-40 rounded-full border border-cyan-400/[0.05]">
          <div className="absolute inset-5 rounded-full border border-cyan-400/[0.05]" />
          <div className="absolute inset-10 rounded-full border border-cyan-400/[0.05]" />

          <motion.div
            animate={{
              rotate: 360,
            }}
            transition={{
              duration: 5,
              repeat: Infinity,
              ease: "linear",
            }}
            className="absolute left-1/2 top-1/2 h-1/2 w-px origin-bottom bg-gradient-to-t from-cyan-400/30 to-transparent"
          />
        </div>

        <div className="relative p-6">
          <div className="flex items-start justify-between gap-4">
            <div className="flex min-w-0 gap-4">
              <motion.div
                whileHover={{
                  rotate: 8,
                  scale: 1.08,
                }}
                className="relative flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border border-cyan-400/15 bg-gradient-to-br from-cyan-400/10 to-blue-500/5 text-cyan-300"
              >
                <FileBarChart2 size={21} />

                <span className="absolute -right-1 -top-1 flex h-3 w-3">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
                  <span className="relative inline-flex h-3 w-3 rounded-full bg-emerald-400" />
                </span>
              </motion.div>

              <div className="min-w-0">
                <p className="font-mono text-[8px] font-black uppercase tracking-[0.25em] text-cyan-400/70">
                  OILTRACE DOSSIER
                </p>

                <h3 className="mt-1 truncate text-[17px] font-black text-white">
                  {report.title ||
                    "Maritime Intelligence Report"}
                </h3>

                <p className="mt-1 font-mono text-[9px] text-slate-600">
                  {report.id}
                </p>
              </div>
            </div>

            <div
              className={`flex shrink-0 items-center gap-1.5 rounded-full border px-2.5 py-1 ${riskStyle.border} ${riskStyle.bg}`}
            >
              <span
                className={`h-1.5 w-1.5 rounded-full ${riskStyle.glow} shadow-[0_0_10px_currentColor]`}
              />

              <span
                className={`text-[8px] font-black tracking-widest ${riskStyle.text}`}
              >
                {risk}
              </span>
            </div>
          </div>

          {/* Metrics */}
          <div className="mt-6 grid grid-cols-3 overflow-hidden rounded-2xl border border-white/[0.06] bg-black/20">
            <div className="border-r border-white/[0.05] px-3 py-3 text-center">
              <p className="text-[8px] font-bold uppercase tracking-widest text-slate-600">
                Detections
              </p>

              <p className="mt-1 text-lg font-black text-white">
                {report.inspectionCount ??
                  related.length}
              </p>
            </div>

            <div className="border-r border-white/[0.05] px-3 py-3 text-center">
              <p className="text-[8px] font-bold uppercase tracking-widest text-slate-600">
                Confidence
              </p>

              <p className="mt-1 text-lg font-black text-cyan-300">
                {Number(score).toFixed(1)}%
              </p>
            </div>

            <div className="px-3 py-3 text-center">
              <p className="text-[8px] font-bold uppercase tracking-widest text-slate-600">
                Status
              </p>

              <p className="mt-1 flex items-center justify-center gap-1 text-lg font-black text-emerald-300">
                <CheckCircle2 size={14} />
                READY
              </p>
            </div>
          </div>

          {/* Confidence bar */}
          <div className="mt-5">
            <div className="mb-1 flex justify-between">
              <span className="text-[8px] font-bold uppercase tracking-widest text-slate-600">
                Intelligence confidence
              </span>

              <span className="font-mono text-[8px] text-cyan-400">
                {Number(score).toFixed(1)}%
              </span>
            </div>

            <div className="h-1.5 overflow-hidden rounded-full bg-white/[0.04]">
              <motion.div
                initial={{ width: 0 }}
                animate={{
                  width: `${Math.min(
                    Number(score),
                    100
                  )}%`,
                }}
                transition={{
                  duration: 1.1,
                  delay: index * 0.1,
                }}
                className="h-full rounded-full bg-gradient-to-r from-cyan-400 via-blue-500 to-violet-500"
              />
            </div>
          </div>

          <div className="mt-5 flex items-center justify-between border-t border-white/[0.05] pt-4">
            <div className="flex items-center gap-2">
              <CalendarDays
                size={13}
                className="text-slate-600"
              />

              <span className="text-[10px] text-slate-500">
                {formatDate(
                  report.createdAt ||
                    report.date
                )}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <Activity
                size={13}
                className="text-slate-600"
              />

              <span className="text-[10px] text-slate-500">
                {report.type ||
                  "Analysis"}
              </span>
            </div>
          </div>

          {/* Actions */}
          <div className="mt-5 flex gap-2">
            <motion.button
              whileTap={{ scale: 0.97 }}
              onClick={() =>
                onPreview(report.id)
              }
              className="group/open flex flex-1 items-center justify-center gap-2 rounded-xl border border-cyan-400/15 bg-cyan-400/[0.05] px-4 py-3 text-[10px] font-black uppercase tracking-wider text-cyan-300 transition-all hover:border-cyan-400/30 hover:bg-cyan-400/[0.1]"
            >
              <Eye size={14} />

              Open Intelligence

              <ChevronRight
                size={13}
                className="transition-transform duration-300 group-hover/open:translate-x-1"
              />
            </motion.button>

            <motion.button
              whileTap={{ scale: 0.9 }}
              onClick={() =>
                onDelete(report.id)
              }
              className="rounded-xl border border-white/[0.06] bg-white/[0.02] px-3 text-slate-600 transition hover:border-red-400/20 hover:bg-red-500/5 hover:text-red-300"
            >
              <Trash2 size={14} />
            </motion.button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

/* =========================================================
   GENERATION STEP
========================================================= */

function GenerationStep({
  icon: Icon,
  title,
  text,
  active,
  complete,
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -15 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex items-center gap-3"
    >
      <div
        className={`flex h-9 w-9 items-center justify-center rounded-xl border transition-all ${
          complete
            ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-300"
            : active
            ? "border-cyan-400/30 bg-cyan-400/10 text-cyan-300"
            : "border-white/[0.06] bg-white/[0.02] text-slate-600"
        }`}
      >
        {complete ? (
          <CheckCircle2 size={16} />
        ) : (
          <Icon
            size={16}
            className={
              active
                ? "animate-pulse"
                : ""
            }
          />
        )}
      </div>

      <div>
        <p className="text-[10px] font-black text-white">
          {title}
        </p>

        <p className="text-[8px] text-slate-600">
          {text}
        </p>
      </div>
    </motion.div>
  );
}

/* =========================================================
   MAIN
========================================================= */

export default function Reports() {
  const navigate = useNavigate();

  const [reports, setReports] = useState([]);
  const [inspections, setInspections] =
    useState([]);

  const [search, setSearch] = useState("");
  const [showCreate, setShowCreate] =
    useState(false);

  const [reportType, setReportType] =
    useState(
      "Comprehensive Incident Dossier"
    );

  const [fromDate, setFromDate] =
    useState("");

  const [toDate, setToDate] =
    useState("");

  const [generating, setGenerating] =
    useState(false);

  const [generationStep, setGenerationStep] =
    useState(0);

  useEffect(() => {
    setReports(getReports());
    setInspections(getInspections());
  }, []);

  const stats = useMemo(() => {
    const totalArea =
      inspections.reduce(
        (sum, item) =>
          sum + getArea(item),
        0
      );

    const confidence = inspections.length
      ? inspections.reduce(
          (sum, item) =>
            sum + getScore(item),
          0
        ) / inspections.length
      : 0;

    const highRisk =
      inspections.filter((item) =>
        ["HIGH", "CRITICAL"].includes(
          getRisk(item)
        )
      ).length;

    return {
      reports: reports.length,
      detections: inspections.length,
      confidence,
      highRisk,
      area: totalArea,
    };
  }, [reports, inspections]);

  const filteredReports =
    useMemo(() => {
      const query = search
        .toLowerCase()
        .trim();

      if (!query) return reports;

      return reports.filter((report) =>
        [
          report.id,
          report.title,
          report.type,
          report.status,
        ]
          .filter(Boolean)
          .join(" ")
          .toLowerCase()
          .includes(query)
      );
    }, [reports, search]);

  function createReport() {
    if (generating) return;

    setGenerating(true);
    setGenerationStep(0);

    const steps = [
      700,
      1400,
      2100,
      2800,
    ];

    steps.forEach((delay, index) => {
      setTimeout(() => {
        setGenerationStep(index + 1);
      }, delay);
    });

    setTimeout(() => {
      const relevant =
        inspections.filter((item) => {
          const date = parseDate(item);

          if (
            fromDate &&
            date < new Date(fromDate)
          ) {
            return false;
          }

          if (toDate) {
            const end = new Date(toDate);

            end.setHours(
              23,
              59,
              59,
              999
            );

            if (date > end)
              return false;
          }

          return true;
        });

      const source =
        relevant.length > 0
          ? relevant
          : inspections;

      const avgScore = source.length
        ? source.reduce(
            (sum, item) =>
              sum + getScore(item),
            0
          ) / source.length
        : 0;

      const high = source.filter((item) =>
        ["HIGH", "CRITICAL"].includes(
          getRisk(item)
        )
      ).length;

      const report = {
        id: `RPT-${Date.now()}`,
        type: reportType,
        title: reportType,
        date: new Date().toISOString(),
        createdAt:
          new Date().toISOString(),
        periodFrom: fromDate,
        periodTo: toDate,
        status: "Generated",
        inspectionCount:
          source.length,
        score: Number(
          avgScore.toFixed(1)
        ),
        risk:
          high >= 3
            ? "CRITICAL"
            : high >= 1
            ? "HIGH"
            : "LOW",
        summary:
          "Automated OILTRACE maritime intelligence dossier generated from satellite detection, environmental analysis and vessel correlation records.",
        inspections:
          source.map(
            (item) => item.id
          ),
      };

      const saved =
        saveReport(report);

      setReports(getReports());

      setGenerating(false);
      setGenerationStep(0);
      setShowCreate(false);

      navigate(
        `/reports/view/${saved.id}`
      );
    }, 3500);
  }

  function handleDelete(id) {
    const okay = window.confirm(
      "Delete this intelligence report?"
    );

    if (!okay) return;

    deleteReport(id);
    setReports(getReports());
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#020617] text-white">
      <BackgroundFX />

      <div className="relative z-10 mx-auto max-w-[1650px] px-4 py-5 sm:px-6 lg:px-8">
        {/* =====================================================
            HERO
        ====================================================== */}

        <motion.section
          initial={{
            opacity: 0,
            y: -30,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          transition={{
            duration: 0.7,
          }}
          className="relative overflow-hidden rounded-[32px] border border-white/[0.07] bg-gradient-to-br from-[#081521]/95 via-[#07101d]/95 to-[#0b1024]/95 p-6 shadow-[0_30px_100px_rgba(0,0,0,.3)] sm:p-8 lg:p-10"
        >
          {/* Radar */}
          <div className="absolute right-[-100px] top-[-100px] h-[400px] w-[400px] rounded-full border border-cyan-400/[0.06]">
            <div className="absolute inset-10 rounded-full border border-cyan-400/[0.05]" />
            <div className="absolute inset-20 rounded-full border border-cyan-400/[0.05]" />
            <div className="absolute inset-32 rounded-full border border-cyan-400/[0.04]" />

            <motion.div
              animate={{
                rotate: 360,
              }}
              transition={{
                duration: 7,
                repeat: Infinity,
                ease: "linear",
              }}
              className="absolute left-1/2 top-1/2 h-1/2 w-px origin-bottom bg-gradient-to-t from-cyan-400/40 to-transparent"
            />
          </div>

          <div className="absolute right-0 top-0 h-96 w-96 rounded-full bg-cyan-500/[0.06] blur-[120px]" />

          <div className="relative flex flex-col justify-between gap-8 xl:flex-row xl:items-center">
            <div>
              <div className="flex items-center gap-2">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-cyan-400 opacity-60" />
                  <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-cyan-400 shadow-[0_0_15px_rgba(34,211,238,.8)]" />
                </span>

                <span className="font-mono text-[9px] font-black uppercase tracking-[0.32em] text-cyan-400">
                  OILTRACE / REPORTING INTELLIGENCE
                </span>
              </div>

              <motion.h1
                initial={{
                  opacity: 0,
                  x: -20,
                }}
                animate={{
                  opacity: 1,
                  x: 0,
                }}
                transition={{
                  delay: 0.2,
                }}
                className="mt-4 text-3xl font-black tracking-[-0.05em] sm:text-4xl lg:text-5xl"
              >
                Intelligence{" "}
                <span className="bg-gradient-to-r from-cyan-300 via-blue-400 to-violet-400 bg-clip-text text-transparent">
                  Reports
                </span>
              </motion.h1>

              <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400">
                Transform satellite observations,
                spill characterization, drift
                intelligence and AIS correlations
                into investigation-ready dossiers.
              </p>

              <div className="mt-5 flex flex-wrap gap-2">
                {[
                  "SATELLITE",
                  "OCEANOGRAPHY",
                  "AIS",
                  "AI CORRELATION",
                  "RISK ENGINE",
                ].map((item, index) => (
                  <motion.span
                    key={item}
                    initial={{
                      opacity: 0,
                      y: 10,
                    }}
                    animate={{
                      opacity: 1,
                      y: 0,
                    }}
                    transition={{
                      delay:
                        0.35 +
                        index * 0.08,
                    }}
                    className="rounded-full border border-white/[0.07] bg-white/[0.025] px-3 py-1.5 font-mono text-[8px] font-bold tracking-[0.18em] text-slate-500"
                  >
                    {item}
                  </motion.span>
                ))}
              </div>
            </div>

            <motion.button
              whileHover={{
                scale: 1.04,
              }}
              whileTap={{
                scale: 0.97,
              }}
              onClick={() =>
                setShowCreate(true)
              }
              className="group relative flex items-center justify-center gap-3 overflow-hidden rounded-2xl bg-gradient-to-r from-cyan-500 via-blue-600 to-violet-600 px-6 py-4 text-xs font-black shadow-[0_0_45px_rgba(14,165,233,.2)]"
            >
              <span className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/20 to-transparent transition-transform duration-700 group-hover:translate-x-full" />

              <Plus
                size={17}
                className="relative transition-transform duration-300 group-hover:rotate-90"
              />

              <span className="relative">
                GENERATE INTELLIGENCE
              </span>

              <ArrowUpRight
                size={15}
                className="relative transition-transform group-hover:translate-x-1 group-hover:-translate-y-1"
              />
            </motion.button>
          </div>
        </motion.section>

        {/* =====================================================
            KPI
        ====================================================== */}

        <div className="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
          <KPI
            index={0}
            icon={FileText}
            title="Reports Generated"
            value={stats.reports}
            description="Intelligence archive"
            accent="cyan"
          />

          <KPI
            index={1}
            icon={Radar}
            title="Active Detections"
            value={stats.detections}
            description="Satellite observations"
            accent="blue"
          />

          <KPI
            index={2}
            icon={TrendingUp}
            title="Detection Confidence"
            value={`${stats.confidence.toFixed(
              1
            )}%`}
            description="Model confidence"
            accent="violet"
          />

          <KPI
            index={3}
            icon={AlertTriangle}
            title="Risk Signals"
            value={stats.highRisk}
            description="Priority investigations"
            accent="orange"
          />

          <KPI
            index={4}
            icon={Waves}
            title="Affected Area"
            value={`${stats.area.toFixed(
              1
            )}`}
            description="Estimated km²"
            accent="emerald"
          />
        </div>

        {/* =====================================================
            ARCHIVE HEADER
        ====================================================== */}

        <motion.div
          initial={{
            opacity: 0,
          }}
          animate={{
            opacity: 1,
          }}
          transition={{
            delay: 0.35,
          }}
          className="mt-10 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between"
        >
          <div>
            <div className="flex items-center gap-2">
              <Database
                size={15}
                className="text-cyan-400"
              />

              <span className="font-mono text-[9px] font-black uppercase tracking-[0.25em] text-cyan-400">
                Intelligence Archive
              </span>
            </div>

            <h2 className="mt-2 text-2xl font-black tracking-tight">
              Investigation Dossiers
            </h2>

            <p className="mt-1 text-xs text-slate-600">
              {filteredReports.length} intelligence
              record
              {filteredReports.length !== 1
                ? "s"
                : ""}{" "}
              available
            </p>
          </div>

          <div className="relative w-full lg:w-[380px]">
            <Search
              size={15}
              className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-600"
            />

            <input
              value={search}
              onChange={(e) =>
                setSearch(e.target.value)
              }
              placeholder="Search intelligence archive..."
              className="w-full rounded-2xl border border-white/[0.08] bg-[#07101d]/80 py-3.5 pl-11 pr-20 text-xs text-white outline-none backdrop-blur-xl transition-all focus:border-cyan-400/30 focus:ring-2 focus:ring-cyan-400/10"
            />

            <div className="absolute right-3 top-1/2 -translate-y-1/2 rounded-md border border-white/[0.06] px-1.5 py-1 font-mono text-[7px] text-slate-700">
              SEARCH
            </div>
          </div>
        </motion.div>

        {/* =====================================================
            REPORT GRID
        ====================================================== */}

        <AnimatePresence mode="popLayout">
          {filteredReports.length > 0 ? (
            <motion.div
              layout
              className="mt-5 grid gap-5 md:grid-cols-2 xl:grid-cols-3"
            >
              {filteredReports.map(
                (report, index) => (
                  <ReportCard
                    key={report.id}
                    report={report}
                    inspections={
                      inspections
                    }
                    index={index}
                    onPreview={(id) =>
                      navigate(
                        `/reports/view/${id}`
                      )
                    }
                    onDelete={
                      handleDelete
                    }
                  />
                )
              )}
            </motion.div>
          ) : (
            <motion.div
              initial={{
                opacity: 0,
                y: 20,
              }}
              animate={{
                opacity: 1,
                y: 0,
              }}
              className="mt-5 flex min-h-[430px] items-center justify-center rounded-[28px] border border-dashed border-white/[0.08] bg-[#050b15]/60"
            >
              <div className="text-center">
                <div className="relative mx-auto flex h-20 w-20 items-center justify-center rounded-3xl border border-cyan-400/10 bg-cyan-400/[0.04]">
                  <Radar
                    size={32}
                    className="text-cyan-400"
                  />

                  <span className="absolute inset-[-8px] animate-ping rounded-3xl border border-cyan-400/5" />
                </div>

                <p className="mt-6 font-mono text-[9px] font-black uppercase tracking-[0.25em] text-cyan-400/70">
                  ARCHIVE EMPTY
                </p>

                <h3 className="mt-2 text-xl font-black">
                  No intelligence dossiers
                </h3>

                <p className="mx-auto mt-2 max-w-md text-sm text-slate-600">
                  Generate an OILTRACE dossier from
                  your satellite detection and
                  maritime intelligence records.
                </p>

                <button
                  onClick={() =>
                    setShowCreate(true)
                  }
                  className="mt-6 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-5 py-3 text-[10px] font-black uppercase tracking-wider transition hover:scale-105"
                >
                  Create First Dossier
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* =======================================================
          CREATE MODAL
      ======================================================== */}

      <AnimatePresence>
        {showCreate && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 p-4 backdrop-blur-xl"
            onMouseDown={(e) => {
              if (
                e.target ===
                e.currentTarget
              ) {
                if (!generating)
                  setShowCreate(false);
              }
            }}
          >
            <motion.div
              initial={{
                opacity: 0,
                y: 40,
                scale: 0.94,
              }}
              animate={{
                opacity: 1,
                y: 0,
                scale: 1,
              }}
              exit={{
                opacity: 0,
                y: 30,
                scale: 0.95,
              }}
              transition={{
                type: "spring",
                stiffness: 280,
                damping: 24,
              }}
              className="relative max-h-[92vh] w-full max-w-2xl overflow-y-auto rounded-[32px] border border-cyan-400/10 bg-[#07101d] shadow-[0_30px_120px_rgba(0,0,0,.8)]"
            >
              <div className="absolute left-1/2 top-[-100px] h-60 w-80 -translate-x-1/2 rounded-full bg-cyan-400/10 blur-[100px]" />

              <div className="relative h-1 bg-gradient-to-r from-cyan-400 via-blue-500 to-violet-500" />

              <div className="relative p-6 sm:p-8">
                {!generating ? (
                  <>
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-400/15 bg-cyan-400/[0.06]">
                            <Sparkles
                              size={17}
                              className="text-cyan-300"
                            />
                          </div>

                          <div>
                            <p className="font-mono text-[8px] font-black uppercase tracking-[0.3em] text-cyan-400">
                              OILTRACE
                            </p>

                            <p className="text-[9px] text-slate-600">
                              Intelligence Generator
                            </p>
                          </div>
                        </div>

                        <h2 className="mt-5 text-2xl font-black tracking-tight">
                          Generate New Dossier
                        </h2>

                        <p className="mt-1 text-xs text-slate-600">
                          Configure the intelligence package
                          to synthesize.
                        </p>
                      </div>

                      <button
                        onClick={() =>
                          setShowCreate(false)
                        }
                        className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-2.5 text-slate-600 transition hover:border-white/10 hover:text-white"
                      >
                        <X size={17} />
                      </button>
                    </div>

                    {/* Type */}
                    <div className="mt-8">
                      <label className="mb-2 block text-[9px] font-black uppercase tracking-[0.2em] text-slate-500">
                        Intelligence Package
                      </label>

                      <div className="relative">
                        <FileText
                          size={15}
                          className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-cyan-400/70"
                        />

                        <select
                          value={
                            reportType
                          }
                          onChange={(e) =>
                            setReportType(
                              e.target.value
                            )
                          }
                          className="w-full appearance-none rounded-xl border border-white/[0.08] bg-[#020812] px-4 py-3.5 pl-11 text-xs font-semibold text-white outline-none transition hover:border-cyan-400/25 focus:border-cyan-400/40"
                        >
                          <option>
                            Comprehensive Incident Dossier
                          </option>

                          <option>
                            Spill Investigation Report
                          </option>

                          <option>
                            Drift & Origin Analysis
                          </option>

                          <option>
                            Vessel Attribution Report
                          </option>

                          <option>
                            Maritime Intelligence Report
                          </option>
                        </select>

                        <ChevronRight
                          size={14}
                          className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 rotate-90 text-slate-600"
                        />
                      </div>
                    </div>

                    {/* Date */}
                    <div className="mt-6 rounded-2xl border border-white/[0.06] bg-black/20 p-4">
                      <div className="mb-4 flex items-center gap-2">
                        <CalendarDays
                          size={15}
                          className="text-cyan-400"
                        />

                        <div>
                          <p className="text-[10px] font-black uppercase tracking-widest text-white">
                            Analysis Window
                          </p>

                          <p className="mt-0.5 text-[9px] text-slate-600">
                            Restrict source observations to
                            a specific period
                          </p>
                        </div>
                      </div>

                      <div className="flex flex-col gap-4 sm:flex-row">
                        <DateField
                          label="Start Date"
                          value={fromDate}
                          onChange={
                            setFromDate
                          }
                        />

                        <DateField
                          label="End Date"
                          value={toDate}
                          onChange={
                            setToDate
                          }
                        />
                      </div>
                    </div>

                    {/* Intelligence modules */}
                    <div className="mt-5 grid grid-cols-2 gap-2 sm:grid-cols-4">
                      {[
                        {
                          icon: Radar,
                          label: "Satellite",
                        },
                        {
                          icon: Waves,
                          label: "Drift Model",
                        },
                        {
                          icon: Ship,
                          label: "AIS Data",
                        },
                        {
                          icon: Crosshair,
                          label: "Risk Engine",
                        },
                      ].map(
                        ({
                          icon: Icon,
                          label,
                        }) => (
                          <motion.div
                            whileHover={{
                              y: -3,
                            }}
                            key={label}
                            className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-3 text-center transition hover:border-cyan-400/15"
                          >
                            <Icon
                              size={15}
                              className="mx-auto text-cyan-400"
                            />

                            <p className="mt-2 text-[8px] font-black uppercase tracking-wider text-slate-600">
                              {label}
                            </p>
                          </motion.div>
                        )
                      )}
                    </div>

                    {/* Info */}
                    <div className="mt-5 rounded-2xl border border-cyan-400/10 bg-gradient-to-r from-cyan-400/[0.04] to-blue-500/[0.03] p-4">
                      <div className="flex gap-3">
                        <ShieldCheck
                          size={18}
                          className="mt-0.5 shrink-0 text-cyan-300"
                        />

                        <div>
                          <p className="text-xs font-bold text-cyan-200">
                            Multi-source intelligence
                            synthesis
                          </p>

                          <p className="mt-1 text-[10px] leading-5 text-slate-600">
                            OILTRACE combines available
                            detection records, confidence
                            scores, risk signals, spill
                            characteristics and vessel
                            correlations.
                          </p>
                        </div>
                      </div>
                    </div>

                    <motion.button
                      whileHover={{
                        scale: 1.01,
                      }}
                      whileTap={{
                        scale: 0.98,
                      }}
                      onClick={
                        createReport
                      }
                      className="group relative mt-6 flex w-full items-center justify-center gap-3 overflow-hidden rounded-2xl bg-gradient-to-r from-cyan-500 via-blue-600 to-violet-600 py-4 text-[11px] font-black uppercase tracking-[0.15em] shadow-[0_0_45px_rgba(14,165,233,.15)]"
                    >
                      <span className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/20 to-transparent transition-transform duration-700 group-hover:translate-x-full" />

                      <Radar
                        size={17}
                        className="relative"
                      />

                      <span className="relative">
                        Generate Intelligence
                        Dossier
                      </span>

                      <ChevronRight
                        size={15}
                        className="relative transition-transform group-hover:translate-x-1"
                      />
                    </motion.button>
                  </>
                ) : (
                  /* ==========================================
                     GENERATION ANIMATION
                  ========================================== */

                  <div className="py-8">
                    <div className="relative mx-auto flex h-32 w-32 items-center justify-center">
                      <motion.div
                        animate={{
                          rotate: 360,
                        }}
                        transition={{
                          duration: 3,
                          repeat: Infinity,
                          ease: "linear",
                        }}
                        className="absolute inset-0 rounded-full border border-cyan-400/20 border-t-cyan-400"
                      />

                      <motion.div
                        animate={{
                          rotate: -360,
                        }}
                        transition={{
                          duration: 5,
                          repeat: Infinity,
                          ease: "linear",
                        }}
                        className="absolute inset-4 rounded-full border border-violet-400/20 border-b-violet-400"
                      />

                      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-cyan-400/[0.08] text-cyan-300 shadow-[0_0_50px_rgba(34,211,238,.15)]">
                        <Radar
                          size={30}
                          className="animate-pulse"
                        />
                      </div>
                    </div>

                    <div className="mt-7 text-center">
                      <p className="font-mono text-[9px] font-black uppercase tracking-[0.3em] text-cyan-400">
                        OILTRACE AI ENGINE
                      </p>

                      <h2 className="mt-2 text-2xl font-black">
                        Synthesizing Intelligence
                      </h2>

                      <p className="mt-2 text-xs text-slate-600">
                        Cross-correlating maritime
                        intelligence sources...
                      </p>
                    </div>

                    <div className="mx-auto mt-8 max-w-md space-y-4">
                      <GenerationStep
                        icon={Radar}
                        title="Satellite detection fusion"
                        text="Processing spill observations"
                        active={
                          generationStep ===
                          1
                        }
                        complete={
                          generationStep > 1
                        }
                      />

                      <GenerationStep
                        icon={Waves}
                        title="Environmental analysis"
                        text="Evaluating drift and origin signals"
                        active={
                          generationStep ===
                          2
                        }
                        complete={
                          generationStep > 2
                        }
                      />

                      <GenerationStep
                        icon={Ship}
                        title="AIS vessel correlation"
                        text="Ranking nearby maritime traffic"
                        active={
                          generationStep ===
                          3
                        }
                        complete={
                          generationStep > 3
                        }
                      />

                      <GenerationStep
                        icon={Target}
                        title="Risk intelligence synthesis"
                        text="Preparing investigation dossier"
                        active={
                          generationStep ===
                          4
                        }
                        complete={
                          generationStep > 4
                        }
                      />
                    </div>

                    <div className="mx-auto mt-8 h-1 max-w-md overflow-hidden rounded-full bg-white/[0.05]">
                      <motion.div
                        initial={{
                          width: 0,
                        }}
                        animate={{
                          width: `${Math.min(
                            generationStep *
                              25,
                            100
                          )}%`,
                        }}
                        transition={{
                          duration:
                            0.4,
                        }}
                        className="h-full rounded-full bg-gradient-to-r from-cyan-400 via-blue-500 to-violet-500"
                      />
                    </div>

                    <p className="mt-3 text-center font-mono text-[8px] text-slate-700">
                      SECURE SYNTHESIS PIPELINE •
                      ENCRYPTED SESSION
                    </p>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}