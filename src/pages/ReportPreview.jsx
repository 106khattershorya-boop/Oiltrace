import {
  useMemo,
} from "react";

import {
  AlertTriangle,
  ArrowLeft,
  CalendarDays,
  CheckCircle2,
  Clock3,
  Crosshair,
  Download,
  FileText,
  Globe2,
  MapPin,
  Navigation,
  Printer,
  Radio,
  Radar,
  ShieldCheck,
  Ship,
  Target,
  TrendingUp,
  Waves,
  Wind,
} from "lucide-react";

import {
  motion,
} from "framer-motion";

import {
  useNavigate,
  useParams,
} from "react-router-dom";

import {
  getReportById,
  getInspections,
} from "../utils/storage";

/* =========================================================
   HELPERS
========================================================= */

function formatDate(value) {
  const d = new Date(value);

  if (Number.isNaN(d.getTime()))
    return "—";

  return d.toLocaleDateString(
    "en-IN",
    {
      day: "2-digit",
      month: "short",
      year: "numeric",
    }
  );
}

function formatDateTime(value) {
  const d = new Date(value);

  if (Number.isNaN(d.getTime()))
    return "—";

  return d.toLocaleString(
    "en-IN",
    {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }
  );
}

function getScore(item) {
  const value =
    item?.score ??
    item?.confidence ??
    item?.compliance_score ??
    item?.compliance?.compliance_score ??
    0;

  const n = Number(value);

  return Number.isFinite(n)
    ? n
    : 0;
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

  return Number.isFinite(n)
    ? n
    : 0;
}

function getLocation(item) {
  return (
    item?.location ||
    item?.region ||
    item?.areaName ||
    "Unknown Maritime Zone"
  );
}

function getCoordinates(item) {
  return (
    item?.coordinates ||
    item?.coords ||
    item?.locationCoordinates ||
    "18.742° N, 72.913° E"
  );
}

function getVesselCount(item) {
  return (
    Number(
      item?.vesselsCorrelated ??
        item?.vesselCount ??
        item?.vessels?.length ??
        0
    ) || 0
  );
}

function getRiskTone(risk) {
  switch (String(risk).toUpperCase()) {
    case "CRITICAL":
      return {
        text: "text-red-300",
        bg: "bg-red-500/10",
        border:
          "border-red-400/20",
      };

    case "HIGH":
      return {
        text: "text-orange-300",
        bg: "bg-orange-500/10",
        border:
          "border-orange-400/20",
      };

    case "MEDIUM":
      return {
        text: "text-amber-300",
        bg: "bg-amber-500/10",
        border:
          "border-amber-400/20",
      };

    default:
      return {
        text: "text-emerald-300",
        bg: "bg-emerald-500/10",
        border:
          "border-emerald-400/20",
      };
  }
}

/* =========================================================
   PRINT STYLES
========================================================= */

function PrintStyles() {
  return (
    <style>{`
      @page {
        size: A4;
        margin: 0;
      }

      @media print {

        html,
        body {
          background: #020617 !important;
          color: white !important;
          -webkit-print-color-adjust: exact !important;
          print-color-adjust: exact !important;
        }

        body {
          margin: 0 !important;
        }

        .no-print {
          display: none !important;
        }

        .report-page {
          width: 210mm !important;
          min-height: 297mm !important;
          margin: 0 !important;
          border: none !important;
          border-radius: 0 !important;
          box-shadow: none !important;
          page-break-after: always !important;
        }

        .report-page:last-child {
          page-break-after: auto !important;
        }

        .print-break {
          page-break-before: always !important;
        }
      }

      @media screen {

        .report-page {
          box-shadow:
            0 30px 100px rgba(0,0,0,.45);
        }
      }
    `}</style>
  );
}

/* =========================================================
   BACKGROUND
========================================================= */

function ReportBackground() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      <div
        className="absolute inset-0 opacity-[0.025]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(56,189,248,.7) 1px, transparent 1px), linear-gradient(90deg, rgba(56,189,248,.7) 1px, transparent 1px)",
          backgroundSize: "35px 35px",
        }}
      />

      <div className="absolute -right-40 -top-40 h-[500px] w-[500px] rounded-full bg-cyan-500/[0.06] blur-[130px]" />

      <div className="absolute -bottom-40 -left-40 h-[500px] w-[500px] rounded-full bg-violet-600/[0.05] blur-[130px]" />

      <motion.div
        animate={{
          y: ["-20%", "120%"],
        }}
        transition={{
          duration: 12,
          repeat: Infinity,
          ease: "linear",
        }}
        className="absolute left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-400/20 to-transparent"
      />
    </div>
  );
}

/* =========================================================
   SECTION HEADER
========================================================= */

function SectionHeader({
  number,
  icon: Icon,
  eyebrow,
  title,
}) {
  return (
    <div className="mb-5 flex items-center gap-4">
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-cyan-400/15 bg-cyan-400/[0.05] text-cyan-300">
        <Icon size={16} />
      </div>

      <div className="flex-1">
        <p className="font-mono text-[7px] font-black uppercase tracking-[0.3em] text-cyan-400/70">
          {number} / {eyebrow}
        </p>

        <h2 className="mt-1 text-[17px] font-black tracking-tight text-white">
          {title}
        </h2>
      </div>

      <div className="hidden h-px flex-1 bg-gradient-to-r from-white/[0.08] to-transparent sm:block" />
    </div>
  );
}

/* =========================================================
   SCORE GAUGE
========================================================= */

function ScoreGauge({
  score,
}) {
  const safeScore = Math.max(
    0,
    Math.min(
      Number(score) || 0,
      100
    )
  );

  const circumference =
    2 * Math.PI * 52;

  const offset =
    circumference -
    (safeScore / 100) *
      circumference;

  return (
    <div className="relative flex h-36 w-36 items-center justify-center">
      <svg
        viewBox="0 0 120 120"
        className="-rotate-90"
      >
        <circle
          cx="60"
          cy="60"
          r="52"
          fill="none"
          stroke="rgba(255,255,255,.05)"
          strokeWidth="8"
        />

        <motion.circle
          cx="60"
          cy="60"
          r="52"
          fill="none"
          stroke="url(#scoreGradient)"
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={
            circumference
          }
          initial={{
            strokeDashoffset:
              circumference,
          }}
          animate={{
            strokeDashoffset:
              offset,
          }}
          transition={{
            duration: 1.5,
            ease: "easeOut",
          }}
        />

        <defs>
          <linearGradient
            id="scoreGradient"
            x1="0%"
            x2="100%"
          >
            <stop
              offset="0%"
              stopColor="#22d3ee"
            />

            <stop
              offset="50%"
              stopColor="#3b82f6"
            />

            <stop
              offset="100%"
              stopColor="#8b5cf6"
            />
          </linearGradient>
        </defs>
      </svg>

      <div className="absolute text-center">
        <p className="text-3xl font-black text-white">
          {safeScore.toFixed(1)}
        </p>

        <p className="font-mono text-[7px] font-bold tracking-[0.2em] text-cyan-400">
          CONFIDENCE
        </p>
      </div>
    </div>
  );
}

/* =========================================================
   DATA CELL
========================================================= */

function DataCell({
  label,
  value,
  icon: Icon,
}) {
  return (
    <div className="rounded-2xl border border-white/[0.06] bg-white/[0.02] p-4 transition hover:border-cyan-400/15 hover:bg-cyan-400/[0.025]">
      <div className="flex items-center gap-2">
        {Icon && (
          <Icon
            size={13}
            className="text-cyan-400"
          />
        )}

        <p className="font-mono text-[7px] font-black uppercase tracking-[0.18em] text-slate-600">
          {label}
        </p>
      </div>

      <p className="mt-2 text-sm font-black text-white">
        {value}
      </p>
    </div>
  );
}

/* =========================================================
   TIMELINE
========================================================= */

function IntelligenceTimeline() {
  const events = [
    {
      time: "T−14h",
      title:
        "Probable origin window",
      text:
        "Environmental backtracking identifies a likely source corridor.",
      icon: Navigation,
    },
    {
      time: "T−8h",
      title:
        "Satellite observation",
      text:
        "SAR-based anomaly detected within the monitored maritime zone.",
      icon: Radar,
    },
    {
      time: "T−4h",
      title:
        "Spill characterization",
      text:
        "Geometry, area and confidence metrics extracted.",
      icon: Waves,
    },
    {
      time: "NOW",
      title:
        "Intelligence fusion",
      text:
        "AIS traffic and environmental signals correlated.",
      icon: Target,
    },
  ];

  return (
    <div className="relative ml-2">
      <div className="absolute bottom-5 left-4 top-5 w-px bg-gradient-to-b from-cyan-400/30 via-blue-500/20 to-transparent" />

      <div className="space-y-5">
        {events.map(
          (
            event,
            index
          ) => {
            const Icon =
              event.icon;

            return (
              <motion.div
                key={event.time}
                initial={{
                  opacity: 0,
                  x: -15,
                }}
                whileInView={{
                  opacity: 1,
                  x: 0,
                }}
                viewport={{
                  once: true,
                }}
                transition={{
                  delay:
                    index * 0.1,
                }}
                className="relative flex gap-4"
              >
                <div className="relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl border border-cyan-400/15 bg-[#07101d] text-cyan-300">
                  <Icon size={13} />
                </div>

                <div className="flex-1 rounded-xl border border-white/[0.05] bg-white/[0.015] p-3">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-[10px] font-black text-white">
                      {event.title}
                    </p>

                    <span className="font-mono text-[7px] text-cyan-400">
                      {event.time}
                    </span>
                  </div>

                  <p className="mt-1 text-[9px] leading-4 text-slate-600">
                    {event.text}
                  </p>
                </div>
              </motion.div>
            );
          }
        )}
      </div>
    </div>
  );
}

/* =========================================================
   DRIFT VISUAL
========================================================= */

function DriftVisualization() {
  return (
    <div className="relative h-[250px] overflow-hidden rounded-2xl border border-white/[0.06] bg-[#030914]">
      {/* Grid */}
      <div
        className="absolute inset-0 opacity-[0.12]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(34,211,238,.35) 1px, transparent 1px), linear-gradient(90deg, rgba(34,211,238,.35) 1px, transparent 1px)",
          backgroundSize: "30px 30px",
        }}
      />

      {/* Rings */}
      <div className="absolute left-1/2 top-1/2 h-32 w-32 -translate-x-1/2 -translate-y-1/2 rounded-full border border-cyan-400/10" />

      <div className="absolute left-1/2 top-1/2 h-20 w-20 -translate-x-1/2 -translate-y-1/2 rounded-full border border-cyan-400/10" />

      {/* Origin */}
      <div className="absolute left-[24%] top-[60%]">
        <motion.div
          animate={{
            scale: [1, 1.4, 1],
            opacity: [0.5, 0.15, 0.5],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
          }}
          className="absolute -inset-4 rounded-full bg-cyan-400/20"
        />

        <div className="relative h-3 w-3 rounded-full bg-cyan-300 shadow-[0_0_20px_rgba(34,211,238,.9)]" />

        <span className="absolute left-5 top-[-4px] whitespace-nowrap font-mono text-[7px] font-bold text-cyan-300">
          ORIGIN
        </span>
      </div>

      {/* Path */}
      <svg
        className="absolute inset-0 h-full w-full"
        viewBox="0 0 600 250"
        preserveAspectRatio="none"
      >
        <defs>
          <linearGradient
            id="driftPath"
            x1="0%"
            x2="100%"
          >
            <stop
              offset="0%"
              stopColor="#22d3ee"
            />

            <stop
              offset="100%"
              stopColor="#8b5cf6"
            />
          </linearGradient>
        </defs>

        <motion.path
          d="M145 150 C220 130, 250 100, 320 120 S420 180, 510 70"
          fill="none"
          stroke="url(#driftPath)"
          strokeWidth="3"
          strokeDasharray="8 8"
          initial={{
            pathLength: 0,
          }}
          whileInView={{
            pathLength: 1,
          }}
          viewport={{
            once: true,
          }}
          transition={{
            duration: 2,
          }}
        />
      </svg>

      {/* Forecast points */}
      {[
        {
          left: "42%",
          top: "49%",
          label: "+6H",
        },
        {
          left: "58%",
          top: "57%",
          label: "+12H",
        },
        {
          left: "72%",
          top: "52%",
          label: "+18H",
        },
        {
          left: "84%",
          top: "28%",
          label: "+24H",
        },
      ].map(
        (point, index) => (
          <motion.div
            key={point.label}
            initial={{
              opacity: 0,
              scale: 0,
            }}
            whileInView={{
              opacity: 1,
              scale: 1,
            }}
            viewport={{
              once: true,
            }}
            transition={{
              delay:
                0.5 +
                index * 0.3,
            }}
            className="absolute"
            style={{
              left: point.left,
              top: point.top,
            }}
          >
            <div className="h-2.5 w-2.5 rounded-full bg-violet-300 shadow-[0_0_15px_rgba(167,139,250,.8)]" />

            <span className="absolute left-4 top-[-5px] whitespace-nowrap font-mono text-[7px] text-violet-300">
              {point.label}
            </span>
          </motion.div>
        )
      )}

      <div className="absolute bottom-3 left-3 rounded-lg border border-white/[0.06] bg-black/30 px-3 py-2 backdrop-blur">
        <p className="font-mono text-[7px] text-slate-600">
          DRIFT MODEL
        </p>

        <p className="mt-1 text-[9px] font-bold text-cyan-300">
          CURRENT + WIND VECTOR
        </p>
      </div>
    </div>
  );
}

/* =========================================================
   VESSEL RANK
========================================================= */

function VesselRank({
  index,
  name,
  type,
  distance,
  score,
  risk,
}) {
  const tone =
    getRiskTone(risk);

  return (
    <motion.div
      initial={{
        opacity: 0,
        x: 25,
      }}
      whileInView={{
        opacity: 1,
        x: 0,
      }}
      viewport={{
        once: true,
      }}
      transition={{
        delay: index * 0.1,
      }}
      whileHover={{
        x: 5,
      }}
      className="group rounded-2xl border border-white/[0.06] bg-white/[0.02] p-4 transition hover:border-cyan-400/15"
    >
      <div className="flex items-center gap-4">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-400/10 to-violet-500/10 font-mono text-xs font-black text-cyan-300">
          #{index + 1}
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <p className="text-[11px] font-black text-white">
              {name}
            </p>

            <span
              className={`rounded-full border px-2 py-0.5 text-[6px] font-black tracking-widest ${tone.border} ${tone.bg} ${tone.text}`}
            >
              {risk}
            </span>
          </div>

          <p className="mt-1 text-[8px] text-slate-600">
            {type} • {distance} from
            probable origin
          </p>
        </div>

        <div className="text-right">
          <p className="text-lg font-black text-cyan-300">
            {score}%
          </p>

          <p className="font-mono text-[6px] tracking-wider text-slate-700">
            CORRELATION
          </p>
        </div>
      </div>

      <div className="mt-3 h-1 overflow-hidden rounded-full bg-white/[0.04]">
        <motion.div
          initial={{
            width: 0,
          }}
          whileInView={{
            width: `${score}%`,
          }}
          viewport={{
            once: true,
          }}
          transition={{
            duration: 1,
            delay:
              index * 0.1,
          }}
          className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-violet-500"
        />
      </div>
    </motion.div>
  );
}

/* =========================================================
   MAIN
========================================================= */

export default function ReportPreview() {
  const navigate =
    useNavigate();

  const { id } =
    useParams();

  const report =
    getReportById(id);

  const inspections =
    getInspections();

  const related =
    useMemo(() => {
      if (!report)
        return [];

      if (
        Array.isArray(
          report.inspections
        )
      ) {
        return inspections.filter(
          (item) =>
            report.inspections.includes(
              item.id
            )
        );
      }

      return inspections;
    }, [
      report,
      inspections,
    ]);

  const primary =
    related[0] || {};

  const score =
    report?.score ??
    (related.length
      ? related.reduce(
          (sum, item) =>
            sum +
            getScore(item),
          0
        ) /
        related.length
      : 0);

  const risk =
    report?.risk ||
    getRisk(primary);

  const tone =
    getRiskTone(risk);

  const area =
    related.reduce(
      (sum, item) =>
        sum + getArea(item),
      0
    ) || getArea(primary);

  const vesselCount =
    related.reduce(
      (sum, item) =>
        sum +
        getVesselCount(item),
      0
    );

  const location =
    getLocation(primary);

  const coordinates =
    getCoordinates(primary);

  const createdAt =
    report?.createdAt ||
    report?.date ||
    new Date().toISOString();

  if (!report) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#020617] px-6 text-white">
        <div className="text-center">
          <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-3xl border border-red-400/10 bg-red-400/[0.04]">
            <AlertTriangle
              size={32}
              className="text-red-300"
            />
          </div>

          <h1 className="mt-5 text-2xl font-black">
            Intelligence Record Not Found
          </h1>

          <p className="mt-2 text-sm text-slate-600">
            The requested OILTRACE dossier
            could not be located.
          </p>

          <button
            onClick={() =>
              navigate(
                "/reports"
              )
            }
            className="mt-6 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-5 py-3 text-xs font-black"
          >
            Return to Reports
          </button>
        </div>
      </div>
    );
  }

  function printReport() {
    window.print();
  }

  function downloadReport() {
    const content = `
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"/>
<title>${report.id} - OILTRACE Intelligence Dossier</title>
<style>
body{
  margin:0;
  background:#020617;
  color:#e2e8f0;
  font-family:Arial,sans-serif;
}
.container{
  max-width:900px;
  margin:auto;
  padding:50px;
}
h1{
  font-size:42px;
  margin-bottom:10px;
}
h2{
  color:#67e8f9;
  margin-top:35px;
}
.card{
  border:1px solid #1e293b;
  border-radius:18px;
  padding:20px;
  margin:15px 0;
  background:#07101d;
}
.metric{
  display:inline-block;
  width:22%;
  margin-right:2%;
}
.small{
  color:#64748b;
  font-size:12px;
}
.value{
  font-size:24px;
  font-weight:bold;
}
.footer{
  margin-top:60px;
  padding-top:20px;
  border-top:1px solid #1e293b;
  color:#64748b;
}
</style>
</head>
<body>
<div class="container">
<div class="small">OILTRACE / MARITIME INTELLIGENCE</div>
<h1>${report.title}</h1>
<div class="small">${report.id} • ${formatDateTime(createdAt)}</div>

<div class="card">
<h2>Executive Summary</h2>
<p>${report.summary || "OILTRACE generated intelligence dossier combining satellite, environmental and vessel correlation data."}</p>
</div>

<div class="card">
<h2>Incident Metrics</h2>
<div class="metric"><div class="small">CONFIDENCE</div><div class="value">${Number(score).toFixed(1)}%</div></div>
<div class="metric"><div class="small">RISK</div><div class="value">${risk}</div></div>
<div class="metric"><div class="small">AREA</div><div class="value">${area.toFixed(1)} km²</div></div>
<div class="metric"><div class="small">DETECTIONS</div><div class="value">${related.length}</div></div>
</div>

<div class="card">
<h2>Location</h2>
<p>${location}</p>
<p>${coordinates}</p>
</div>

<div class="card">
<h2>Investigative Note</h2>
<p>Vessel correlations presented by OILTRACE represent investigative leads based on available data and should not be interpreted as definitive attribution without independent verification.</p>
</div>

<div class="footer">
OILTRACE • Maritime Intelligence Platform<br/>
Generated ${formatDateTime(createdAt)}
</div>
</div>
</body>
</html>
`;

    const blob =
      new Blob(
        [content],
        {
          type: "text/html",
        }
      );

    const url =
      URL.createObjectURL(
        blob
      );

    const a =
      document.createElement(
        "a"
      );

    a.href = url;
    a.download = `${report.id}-OILTRACE.html`;
    a.click();

    URL.revokeObjectURL(
      url
    );
  }

  return (
    <div className="min-h-screen bg-[#020617] text-white">
      <PrintStyles />

      {/* =====================================================
          TOP TOOLBAR
      ====================================================== */}

      <div className="no-print sticky top-0 z-50 border-b border-white/[0.06] bg-[#020617]/85 backdrop-blur-2xl">
        <div className="mx-auto flex max-w-[1250px] items-center justify-between gap-4 px-4 py-3 sm:px-6">
          <button
            onClick={() =>
              navigate(
                "/reports"
              )
            }
            className="flex items-center gap-2 rounded-xl border border-white/[0.06] bg-white/[0.02] px-3 py-2 text-[9px] font-black uppercase tracking-wider text-slate-500 transition hover:border-cyan-400/20 hover:text-cyan-300"
          >
            <ArrowLeft size={14} />
            Reports
          </button>

          <div className="hidden items-center gap-2 sm:flex">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />

            <span className="font-mono text-[8px] tracking-[0.25em] text-slate-600">
              SECURE INTELLIGENCE VIEW
            </span>
          </div>

          <div className="flex gap-2">
            <button
              onClick={
                downloadReport
              }
              className="flex items-center gap-2 rounded-xl border border-white/[0.06] bg-white/[0.02] px-3 py-2 text-[9px] font-black uppercase tracking-wider text-slate-500 transition hover:border-cyan-400/20 hover:text-cyan-300"
            >
              <Download size={14} />
              <span className="hidden sm:inline">
                Export
              </span>
            </button>

            <button
              onClick={
                printReport
              }
              className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-3 py-2 text-[9px] font-black uppercase tracking-wider"
            >
              <Printer size={14} />
              Print / PDF
            </button>
          </div>
        </div>
      </div>

      {/* =====================================================
          REPORT PAGE 1
      ====================================================== */}

      <motion.main
        initial={{
          opacity: 0,
          y: 20,
        }}
        animate={{
          opacity: 1,
          y: 0,
        }}
        transition={{
          duration: 0.7,
        }}
        className="report-page relative mx-auto mt-6 min-h-[297mm] w-full max-w-[1100px] overflow-hidden border border-white/[0.06] bg-[#050b15] shadow-2xl"
      >
        <ReportBackground />

        <div className="relative p-7 sm:p-10 lg:p-14">
          {/* Header */}
          <div className="flex items-start justify-between gap-5 border-b border-white/[0.07] pb-7">
            <div>
              <div className="flex items-center gap-2">
                <span className="flex h-2 w-2 rounded-full bg-cyan-400 shadow-[0_0_12px_rgba(34,211,238,.8)]" />

                <span className="font-mono text-[8px] font-black uppercase tracking-[0.3em] text-cyan-400">
                  OILTRACE
                </span>
              </div>

              <p className="mt-2 font-mono text-[7px] uppercase tracking-[0.28em] text-slate-700">
                MARITIME INTELLIGENCE SYSTEM
              </p>
            </div>

            <div className="text-right">
              <p className="font-mono text-[7px] uppercase tracking-widest text-slate-700">
                CASE ID
              </p>

              <p className="mt-1 font-mono text-[10px] font-bold text-cyan-300">
                {report.id}
              </p>

              <p className="mt-1 text-[8px] text-slate-700">
                {formatDateTime(
                  createdAt
                )}
              </p>
            </div>
          </div>

          {/* Hero */}
          <div className="mt-12 grid gap-10 lg:grid-cols-[1fr_180px] lg:items-center">
            <div>
              <motion.p
                initial={{
                  opacity: 0,
                  x: -15,
                }}
                animate={{
                  opacity: 1,
                  x: 0,
                }}
                transition={{
                  delay: 0.2,
                }}
                className="font-mono text-[8px] font-black uppercase tracking-[0.35em] text-cyan-400"
              >
                INVESTIGATION DOSSIER
              </motion.p>

              <motion.h1
                initial={{
                  opacity: 0,
                  y: 15,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                }}
                transition={{
                  delay: 0.3,
                }}
                className="mt-4 max-w-3xl text-4xl font-black tracking-[-0.05em] sm:text-5xl"
              >
                {report.title}
              </motion.h1>

              <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-500">
                Satellite-derived maritime
                intelligence fused with
                environmental drift signals
                and AIS vessel correlations.
              </p>

              <div className="mt-6 flex flex-wrap gap-2">
                <span
                  className={`rounded-full border px-3 py-1.5 text-[8px] font-black tracking-[0.18em] ${tone.border} ${tone.bg} ${tone.text}`}
                >
                  {risk} PRIORITY
                </span>

                <span className="rounded-full border border-cyan-400/10 bg-cyan-400/[0.04] px-3 py-1.5 font-mono text-[8px] font-bold tracking-wider text-cyan-300">
                  AI FUSED
                </span>

                <span className="rounded-full border border-white/[0.07] bg-white/[0.02] px-3 py-1.5 font-mono text-[8px] font-bold tracking-wider text-slate-600">
                  ANALYSIS COMPLETE
                </span>
              </div>
            </div>

            <ScoreGauge
              score={score}
            />
          </div>

          {/* Main metrics */}
          <div className="mt-12 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <DataCell
              icon={Radar}
              label="Detections"
              value={
                related.length
              }
            />

            <DataCell
              icon={Waves}
              label="Affected Area"
              value={`${area.toFixed(
                1
              )} km²`}
            />

            <DataCell
              icon={Ship}
              label="Vessels Correlated"
              value={
                vesselCount ||
                "Pending"
              }
            />

            <DataCell
              icon={AlertTriangle}
              label="Risk Level"
              value={
                risk
              }
            />
          </div>

          {/* Executive summary */}
          <div className="mt-10 rounded-[24px] border border-cyan-400/10 bg-gradient-to-br from-cyan-400/[0.045] via-transparent to-blue-500/[0.025] p-6">
            <div className="flex gap-4">
              <ShieldCheck
                size={20}
                className="mt-0.5 shrink-0 text-cyan-300"
              />

              <div>
                <p className="font-mono text-[8px] font-black uppercase tracking-[0.25em] text-cyan-400">
                  EXECUTIVE ASSESSMENT
                </p>

                <p className="mt-3 text-sm leading-7 text-slate-400">
                  {report.summary ||
                    "OILTRACE has synthesized satellite observations, spill characteristics, environmental signals and maritime traffic correlations into this investigation dossier."}
                </p>
              </div>
            </div>
          </div>

          {/* Incident location */}
          <div className="mt-10">
            <SectionHeader
              number="01"
              icon={MapPin}
              eyebrow="INCIDENT"
              title="Detection Overview"
            />

            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <DataCell
                icon={MapPin}
                label="Maritime Zone"
                value={location}
              />

              <DataCell
                icon={Crosshair}
                label="Coordinates"
                value={
                  coordinates
                }
              />

              <DataCell
                icon={CalendarDays}
                label="Detected"
                value={formatDate(
                  primary.detectedAt ||
                    primary.createdAt
                )}
              />

              <DataCell
                icon={Clock3}
                label="Report Generated"
                value={formatDate(
                  createdAt
                )}
              />
            </div>
          </div>

          {/* Timeline */}
          <div className="mt-10">
            <SectionHeader
              number="02"
              icon={Clock3}
              eyebrow="EVENT CHAIN"
              title="Intelligence Timeline"
            />

            <IntelligenceTimeline
              inspection={
                primary
              }
            />
          </div>

          <div className="mt-10 flex items-center justify-between border-t border-white/[0.06] pt-4">
            <p className="font-mono text-[7px] tracking-[0.2em] text-slate-700">
              OILTRACE • CLASSIFIED MARITIME
              INTELLIGENCE
            </p>

            <p className="font-mono text-[7px] text-slate-700">
              PAGE 01
            </p>
          </div>
        </div>
      </motion.main>

      {/* =====================================================
          REPORT PAGE 2
      ====================================================== */}

      <motion.section
        initial={{
          opacity: 0,
          y: 30,
        }}
        whileInView={{
          opacity: 1,
          y: 0,
        }}
        viewport={{
          once: true,
        }}
        className="report-page relative mx-auto mt-8 min-h-[297mm] w-full max-w-[1100px] overflow-hidden border border-white/[0.06] bg-[#050b15]"
      >
        <ReportBackground />

        <div className="relative p-7 sm:p-10 lg:p-14">
          <SectionHeader
            number="03"
            icon={Waves}
            eyebrow="SPILL ANALYSIS"
            title="Spill Characterization"
          />

          <div className="grid gap-5 lg:grid-cols-[1fr_1.4fr]">
            <div className="rounded-[24px] border border-white/[0.06] bg-black/20 p-6">
              <p className="font-mono text-[7px] font-black uppercase tracking-[0.25em] text-slate-700">
                DETECTION SIGNATURE
              </p>

              <div className="mt-6 space-y-5">
                {[
                  [
                    "Area",
                    `${area.toFixed(
                      1
                    )} km²`,
                  ],
                  [
                    "Confidence",
                    `${Number(
                      score
                    ).toFixed(
                      1
                    )}%`,
                  ],
                  [
                    "Shape",
                    primary.shape ||
                      primary.geometry ||
                      "Elongated / Irregular",
                  ],
                  [
                    "Severity",
                    risk,
                  ],
                ].map(
                  ([label, value]) => (
                    <div
                      key={label}
                      className="flex items-end justify-between border-b border-white/[0.05] pb-3"
                    >
                      <span className="text-[9px] text-slate-600">
                        {label}
                      </span>

                      <span className="text-[11px] font-black text-white">
                        {value}
                      </span>
                    </div>
                  )
                )}
              </div>
            </div>

            {/* Satellite simulation */}
            <div className="relative min-h-[280px] overflow-hidden rounded-[24px] border border-white/[0.06] bg-[#030914]">
              <div
                className="absolute inset-0 opacity-20"
                style={{
                  backgroundImage:
                    "radial-gradient(circle at 50% 50%, rgba(34,211,238,.2), transparent 35%), linear-gradient(135deg, rgba(255,255,255,.03) 25%, transparent 25%, transparent 50%, rgba(255,255,255,.03) 50%, rgba(255,255,255,.03) 75%, transparent 75%)",
                  backgroundSize:
                    "100% 100%, 30px 30px",
                }}
              />

              {/* Simulated spill */}
              <motion.div
                initial={{
                  scale: 0,
                  opacity: 0,
                }}
                whileInView={{
                  scale: 1,
                  opacity: 1,
                }}
                viewport={{
                  once: true,
                }}
                transition={{
                  duration: 1,
                }}
                className="absolute left-[42%] top-[42%] h-24 w-44 rotate-[-18deg] rounded-[50%] bg-gradient-to-br from-black via-slate-900 to-cyan-950/70 shadow-[0_0_45px_rgba(34,211,238,.12)]"
              />

              <motion.div
                animate={{
                  scale: [
                    1,
                    1.15,
                    1,
                  ],
                  opacity: [
                    0.2,
                    0.4,
                    0.2,
                  ],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                }}
                className="absolute left-[39%] top-[37%] h-32 w-52 rotate-[-18deg] rounded-[50%] border border-cyan-400/20"
              />

              {/* Scanner */}
              <motion.div
                animate={{
                  x: [
                    "-100%",
                    "300%",
                  ],
                }}
                transition={{
                  duration: 4,
                  repeat: Infinity,
                  ease: "linear",
                }}
                className="absolute top-0 h-full w-20 bg-gradient-to-r from-transparent via-cyan-400/[0.08] to-transparent"
              />

              <div className="absolute left-4 top-4">
                <p className="font-mono text-[7px] font-black tracking-[0.25em] text-cyan-400">
                  SAR / ANOMALY MAP
                </p>

                <p className="mt-1 font-mono text-[6px] text-slate-700">
                  DETECTION LAYER
                </p>
              </div>

              <div className="absolute bottom-4 right-4 rounded-lg border border-cyan-400/10 bg-black/40 px-3 py-2 backdrop-blur">
                <p className="font-mono text-[7px] text-cyan-300">
                  CONFIDENCE{" "}
                  {Number(
                    score
                  ).toFixed(
                    1
                  )}%
                </p>
              </div>
            </div>
          </div>

          {/* Drift */}
          <div className="mt-12">
            <SectionHeader
              number="04"
              icon={Navigation}
              eyebrow="OCEANOGRAPHY"
              title="Drift & Origin Prediction"
            />

            <div className="grid gap-5 lg:grid-cols-[1.5fr_1fr]">
              <DriftVisualization />

              <div className="space-y-3">
                <DataCell
                  icon={Waves}
                  label="Current Direction"
                  value="NE / Coastal Vector"
                />

                <DataCell
                  icon={Wind}
                  label="Wind Influence"
                  value="Moderate"
                />

                <DataCell
                  icon={Navigation}
                  label="Forecast Horizon"
                  value="24 hours"
                />

                <DataCell
                  icon={Target}
                  label="Origin Confidence"
                  value="High"
                />
              </div>
            </div>
          </div>

          {/* Environmental */}
          <div className="mt-10 grid gap-3 sm:grid-cols-3">
            <DataCell
              icon={Waves}
              label="Sea State"
              value="Moderate"
            />

            <DataCell
              icon={Wind}
              label="Wind Speed"
              value="12–18 kn"
            />

            <DataCell
              icon={Globe2}
              label="Model"
              value="Ocean Current + Wind"
            />
          </div>

          <div className="mt-10 flex items-center justify-between border-t border-white/[0.06] pt-4">
            <p className="font-mono text-[7px] tracking-[0.2em] text-slate-700">
              ENVIRONMENTAL MODEL / DRIFT
              FORECAST
            </p>

            <p className="font-mono text-[7px] text-slate-700">
              PAGE 02
            </p>
          </div>
        </div>
      </motion.section>

      {/* =====================================================
          REPORT PAGE 3
      ====================================================== */}

      <motion.section
        initial={{
          opacity: 0,
          y: 30,
        }}
        whileInView={{
          opacity: 1,
          y: 0,
        }}
        viewport={{
          once: true,
        }}
        className="report-page relative mx-auto mt-8 min-h-[297mm] w-full max-w-[1100px] overflow-hidden border border-white/[0.06] bg-[#050b15]"
      >
        <ReportBackground />

        <div className="relative p-7 sm:p-10 lg:p-14">
          <SectionHeader
            number="05"
            icon={Ship}
            eyebrow="VESSEL INTELLIGENCE"
            title="AIS Vessel Attribution"
          />

          <div className="rounded-[24px] border border-orange-400/10 bg-orange-400/[0.025] p-5">
            <div className="flex gap-3">
              <AlertTriangle
                size={18}
                className="mt-0.5 shrink-0 text-orange-300"
              />

              <div>
                <p className="text-[11px] font-black text-orange-200">
                  Investigative lead — not
                  definitive responsibility
                </p>

                <p className="mt-1 text-[9px] leading-5 text-slate-600">
                  Vessel ranking is based on
                  available proximity,
                  trajectory and correlation
                  signals. Independent
                  verification is required
                  before attributing
                  responsibility.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-6 space-y-3">
            <VesselRank
              index={0}
              name="MV Ocean Pioneer"
              type="Oil Tanker"
              distance="7.2 km"
              score={94}
              risk="CRITICAL"
            />

            <VesselRank
              index={1}
              name="MT Blue Horizon"
              type="Chemical Tanker"
              distance="12.8 km"
              score={87}
              risk="HIGH"
            />

            <VesselRank
              index={2}
              name="MV Eastern Star"
              type="Cargo Vessel"
              distance="18.6 km"
              score={79}
              risk="HIGH"
            />

            <VesselRank
              index={3}
              name="MT Coastal Trader"
              type="Oil Tanker"
              distance="26.4 km"
              score={62}
              risk="MEDIUM"
            />

            <VesselRank
              index={4}
              name="MV Arabian Pearl"
              type="Container Ship"
              distance="34.9 km"
              score={38}
              risk="LOW"
            />
          </div>

          {/* Evidence chain */}
          <div className="mt-12">
            <SectionHeader
              number="06"
              icon={Radio}
              eyebrow="EVIDENCE CHAIN"
              title="Intelligence Fusion"
            />

            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {[
                {
                  icon: Radar,
                  title: "Satellite",
                  text: "Spill anomaly detected",
                },
                {
                  icon: Waves,
                  title: "Ocean Model",
                  text: "Drift corridor estimated",
                },
                {
                  icon: Ship,
                  title: "AIS",
                  text: "Traffic reconstructed",
                },
                {
                  icon: Target,
                  title: "Correlation",
                  text: "Suspect ranking generated",
                },
              ].map(
                ({
                  icon: Icon,
                  title,
                  text,
                }) => (
                  <motion.div
                    key={title}
                    whileHover={{
                      y: -5,
                    }}
                    className="rounded-2xl border border-white/[0.06] bg-white/[0.02] p-4"
                  >
                    <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-cyan-400/10 bg-cyan-400/[0.04] text-cyan-300">
                      <Icon size={15} />
                    </div>

                    <p className="mt-4 text-[10px] font-black text-white">
                      {title}
                    </p>

                    <p className="mt-1 text-[8px] leading-4 text-slate-600">
                      {text}
                    </p>
                  </motion.div>
                )
              )}
            </div>
          </div>

          {/* Risk assessment */}
          <div className="mt-12">
            <SectionHeader
              number="07"
              icon={ShieldCheck}
              eyebrow="RISK ENGINE"
              title="Investigation Priority"
            />

            <div className="grid gap-5 lg:grid-cols-[1fr_1fr]">
              <div className="rounded-[24px] border border-white/[0.06] bg-black/20 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-mono text-[7px] tracking-[0.2em] text-slate-700">
                      OVERALL RISK
                    </p>

                    <p
                      className={`mt-2 text-3xl font-black ${tone.text}`}
                    >
                      {risk}
                    </p>
                  </div>

                  <div
                    className={`flex h-14 w-14 items-center justify-center rounded-2xl border ${tone.border} ${tone.bg}`}
                  >
                    <AlertTriangle
                      size={23}
                      className={
                        tone.text
                      }
                    />
                  </div>
                </div>

                <div className="mt-6 h-2 overflow-hidden rounded-full bg-white/[0.04]">
                  <motion.div
                    initial={{
                      width: 0,
                    }}
                    whileInView={{
                      width:
                        risk ===
                        "CRITICAL"
                          ? "95%"
                          : risk ===
                            "HIGH"
                          ? "80%"
                          : risk ===
                            "MEDIUM"
                          ? "55%"
                          : "25%",
                    }}
                    viewport={{
                      once: true,
                    }}
                    transition={{
                      duration: 1.2,
                    }}
                    className="h-full rounded-full bg-gradient-to-r from-emerald-400 via-orange-400 to-red-500"
                  />
                </div>
              </div>

              <div className="space-y-3">
                <DataCell
                  icon={TrendingUp}
                  label="Detection Confidence"
                  value={`${Number(
                    score
                  ).toFixed(
                    1
                  )}%`}
                />

                <DataCell
                  icon={Ship}
                  label="Top Correlation"
                  value="MV Ocean Pioneer"
                />
              </div>
            </div>
          </div>

          <div className="mt-10 rounded-[24px] border border-cyan-400/10 bg-cyan-400/[0.025] p-6">
            <div className="flex gap-4">
              <CheckCircle2
                size={20}
                className="mt-0.5 shrink-0 text-emerald-300"
              />

              <div>
                <p className="font-mono text-[8px] font-black uppercase tracking-[0.25em] text-emerald-300">
                  INVESTIGATION STATUS
                </p>

                <p className="mt-2 text-sm font-bold text-white">
                  Intelligence synthesis
                  complete.
                </p>

                <p className="mt-1 text-[9px] leading-5 text-slate-600">
                  OILTRACE has generated a
                  consolidated evidence chain
                  connecting satellite
                  detection, environmental
                  drift analysis and AIS
                  vessel correlation.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-10 flex items-center justify-between border-t border-white/[0.06] pt-4">
            <p className="font-mono text-[7px] tracking-[0.2em] text-slate-700">
              OILTRACE / AIS CORRELATION
            </p>

            <p className="font-mono text-[7px] text-slate-700">
              PAGE 03
            </p>
          </div>
        </div>
      </motion.section>

      {/* =====================================================
          REPORT PAGE 4
      ====================================================== */}

      <motion.section
        initial={{
          opacity: 0,
          y: 30,
        }}
        whileInView={{
          opacity: 1,
          y: 0,
        }}
        viewport={{
          once: true,
        }}
        className="report-page relative mx-auto mb-10 mt-8 min-h-[297mm] w-full max-w-[1100px] overflow-hidden border border-white/[0.06] bg-[#050b15]"
      >
        <ReportBackground />

        <div className="relative flex min-h-[297mm] flex-col p-7 sm:p-10 lg:p-14">
          <div>
            <SectionHeader
              number="08"
              icon={FileText}
              eyebrow="CONCLUSION"
              title="Investigative Assessment"
            />

            <div className="rounded-[28px] border border-white/[0.06] bg-black/20 p-7">
              <p className="text-sm leading-7 text-slate-400">
                The OILTRACE intelligence
                pipeline indicates a
                potentially significant
                maritime pollution event at{" "}
                <span className="font-bold text-white">
                  {location}
                </span>
                .
              </p>

              <p className="mt-4 text-sm leading-7 text-slate-400">
                Satellite-derived detection
                confidence is{" "}
                <span className="font-bold text-cyan-300">
                  {Number(
                    score
                  ).toFixed(
                    1
                  )}%
                </span>
                , with an estimated affected
                area of{" "}
                <span className="font-bold text-white">
                  {area.toFixed(
                    1
                  )} km²
                </span>
                .
              </p>

              <p className="mt-4 text-sm leading-7 text-slate-400">
                Environmental backtracking
                provides a probable origin
                corridor, which is subsequently
                cross-referenced against
                historical AIS traffic.
              </p>

              <p className="mt-4 text-sm leading-7 text-slate-400">
                The resulting vessel rankings
                should be treated as{" "}
                <span className="font-bold text-orange-300">
                  investigative leads
                </span>
                , not definitive attribution.
                Further evidence and
                independent validation are
                required.
              </p>
            </div>
          </div>

          {/* Final intelligence chain */}
          <div className="mt-12">
            <SectionHeader
              number="09"
              icon={Crosshair}
              eyebrow="MISSION OUTPUT"
              title="OILTRACE Intelligence Chain"
            />

            <div className="relative">
              <div className="absolute left-8 right-8 top-8 hidden h-px bg-gradient-to-r from-cyan-400/20 via-blue-500/20 to-violet-500/20 lg:block" />

              <div className="grid gap-5 lg:grid-cols-4">
                {[
                  {
                    icon: Radar,
                    title: "DETECT",
                    text: "Satellite anomaly",
                  },
                  {
                    icon: Waves,
                    title: "TRACE",
                    text: "Drift & origin",
                  },
                  {
                    icon: Ship,
                    title: "CORRELATE",
                    text: "AIS traffic",
                  },
                  {
                    icon: Target,
                    title: "ATTRIBUTE",
                    text: "Ranked leads",
                  },
                ].map(
                  ({
                    icon: Icon,
                    title,
                    text,
                  }) => (
                    <motion.div
                      key={title}
                      whileHover={{
                        y: -6,
                      }}
                      className="relative z-10 rounded-2xl border border-white/[0.06] bg-[#07101d] p-5 text-center"
                    >
                      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl border border-cyan-400/10 bg-cyan-400/[0.04] text-cyan-300">
                        <Icon size={19} />
                      </div>

                      <p className="mt-4 font-mono text-[8px] font-black tracking-[0.2em] text-cyan-300">
                        {title}
                      </p>

                      <p className="mt-1 text-[8px] text-slate-600">
                        {text}
                      </p>
                    </motion.div>
                  )
                )}
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="mt-auto pt-16">
            <div className="rounded-[28px] border border-cyan-400/10 bg-gradient-to-r from-cyan-400/[0.04] via-blue-500/[0.025] to-violet-500/[0.04] p-6">
              <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="font-mono text-[8px] font-black uppercase tracking-[0.28em] text-cyan-400">
                    OILTRACE
                  </p>

                  <p className="mt-2 text-lg font-black">
                    Maritime Intelligence,
                    Connected.
                  </p>

                  <p className="mt-1 text-[9px] text-slate-600">
                    Satellite • Oceanography •
                    AIS • AI Correlation
                  </p>
                </div>

                <div className="text-left sm:text-right">
                  <p className="font-mono text-[7px] text-slate-700">
                    GENERATED
                  </p>

                  <p className="mt-1 text-[9px] text-slate-500">
                    {formatDateTime(
                      createdAt
                    )}
                  </p>

                  <p className="mt-2 font-mono text-[7px] text-slate-700">
                    {report.id}
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-6 flex items-center justify-between border-t border-white/[0.06] pt-4">
              <p className="font-mono text-[7px] tracking-[0.2em] text-slate-700">
                END OF INTELLIGENCE DOSSIER
              </p>

              <p className="font-mono text-[7px] text-slate-700">
                PAGE 04
              </p>
            </div>
          </div>
        </div>
      </motion.section>

      {/* =====================================================
          REDUCED MOTION
      ====================================================== */}

      <style>{`
        @media (prefers-reduced-motion: reduce) {
          *,
          *::before,
          *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
            scroll-behavior: auto !important;
          }
        }
      `}</style>
    </div>
  );
}