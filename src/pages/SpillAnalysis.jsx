import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  Satellite,
  MapPin,
  Target,
  Maximize2,
  Waves,
  AlertTriangle,
  CheckCircle2,
  ArrowRight,
  RotateCcw,
  Navigation,
  Clock3,
  Activity,
  ShieldCheck,
  Crosshair,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { getIncident } from "../Services/api";

const FALLBACK_ANALYSIS = {
  id: "N/A",
  location: "Unavailable",
  coordinates: "Unavailable",
  area: "Unavailable",
  confidence: 0,
  severity: "LOW",
  age: "Unavailable",
  shape: "Unavailable",
  perimeter: "Unavailable",
  detectedAt: "Unavailable",
};

function buildAnalysisData(incident) {
  if (!incident) {
    return FALLBACK_ANALYSIS;
  }

  const latitude =
    incident.latitude ??
    incident.lat ??
    incident.location?.latitude;

  const longitude =
    incident.longitude ??
    incident.lon ??
    incident.location?.longitude;

  const confidence = Number(
    incident.detection_confidence ??
      incident.confidence ??
      0
  );

  const area =
    incident.estimated_area_km2 ??
    incident.spill_area ??
    incident.area ??
    null;

  const severity =
    incident.severity ??
    incident.priority_level ??
    (confidence >= 80
      ? "HIGH"
      : confidence >= 60
        ? "MEDIUM"
        : "LOW");

  const location =
    incident.location_name ??
    incident.region ??
    (latitude != null && longitude != null
      ? "Gulf of Mexico / Coast"
      : "Unavailable");

  const rawDetectedAt =
    incident.detection_time ??
    incident.detected_at ??
    incident.timestamp ??
    null;

  const detectedAt = rawDetectedAt
    ? new Date(rawDetectedAt).toLocaleString("en-IN", {
        dateStyle: "medium",
        timeStyle: "short",
      })
    : "Unavailable";

  const latNum = latitude != null ? Number(latitude) : null;
  const lonNum = longitude != null ? Number(longitude) : null;
  const coordinates =
    latNum != null && lonNum != null
      ? `${Math.abs(latNum).toFixed(4)}° ${latNum >= 0 ? "N" : "S"}, ${Math.abs(lonNum).toFixed(4)}° ${lonNum >= 0 ? "E" : "W"}`
      : "Unavailable";

  return {
    id:
      incident.incident_id != null
        ? `INCIDENT-${incident.incident_id}`
        : "N/A",

    location,
    coordinates,

    area:
      area != null
        ? `${Number(area).toFixed(2)} km²`
        : "Unavailable",

    confidence: Number(confidence.toFixed(2)),

    severity: String(severity).toUpperCase(),

    age:
      incident.estimated_age ??
      incident.age ??
      "Unavailable",

    shape:
      incident.shape ??
      incident.morphology ??
      "Unavailable",

    perimeter:
      incident.perimeter_km != null
        ? `${Number(incident.perimeter_km).toFixed(2)} km`
        : incident.perimeter ?? "Unavailable",

    detectedAt,
  };
}

function Metric({ icon: Icon, label, value, sub }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
      <div className="flex items-center justify-between">
        <div className="rounded-xl bg-cyan-400/10 p-2 text-cyan-400">
          <Icon size={17} />
        </div>
      </div>

      <p className="mt-4 text-[10px] uppercase tracking-wider text-slate-600">
        {label}
      </p>

      <p className="mt-1 text-xl font-bold text-slate-100">
        {value}
      </p>

      {sub && (
        <p className="mt-1 text-[10px] text-slate-600">
          {sub}
        </p>
      )}
    </div>
  );
}

export default function SpillAnalysis() {
  const navigate = useNavigate();

  const [incident, setIncident] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [progress, setProgress] = useState(0);
  const processing = progress < 100;

  const analysisData = buildAnalysisData(incident);

  useEffect(() => {
    let cancelled = false;

    async function fetchIncidentData() {
      try {
        const data = await getIncident(1);

        if (cancelled) {
          return;
        }

        setIncident(data);
        setError("");
        setLoading(false);
      } catch (err) {
        if (cancelled) {
          return;
        }

        console.error(
          "Oiltrace incident API failed:",
          err
        );

        setError(
          "Live incident data could not be loaded."
        );

        setLoading(false);
      }
    }

    void fetchIncidentData();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    const timer = setInterval(() => {
      if (cancelled) {
        return;
      }

      setProgress((previous) => {
        if (previous >= 100) {
          return 100;
        }

        return Math.min(previous + 5, 100);
      });
    }, 70);

    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  const rerunAnalysis = async () => {
    setProgress(0);

    try {
      const data = await getIncident(1);

      setIncident(data);
      setError("");
    } catch (err) {
      console.error(
        "Oiltrace re-run analysis failed:",
        err
      );

      setError(
        "Unable to refresh live incident data."
      );
    }
  };

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
              <Satellite size={14} />
              Satellite Investigation
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-3xl font-bold md:text-4xl">
                Spill Analysis
              </h1>

              <span
                className={`rounded-full border px-3 py-1 text-[10px] font-bold uppercase tracking-wider ${
                  error
                    ? "border-amber-400/20 bg-amber-400/10 text-amber-400"
                    : "border-emerald-400/20 bg-emerald-400/10 text-emerald-400"
                }`}
              >
                {loading
                  ? "Loading Analysis"
                  : error
                    ? "Fallback Mode"
                    : "AI Analysis Complete"}
              </span>
            </div>

            <p className="mt-2 text-sm text-slate-400">
              Satellite-derived characterization of the
              detected maritime anomaly.
            </p>
          </div>

          <button
            onClick={rerunAnalysis}
            className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-xs font-semibold text-slate-300 transition hover:border-cyan-400/30 hover:bg-cyan-400/5"
          >
            <RotateCcw size={15} />
            Re-run Analysis
          </button>
        </motion.div>

        {/* Error */}
        {error && (
          <div className="rounded-2xl border border-amber-400/20 bg-amber-400/[0.04] p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle
                size={17}
                className="mt-0.5 shrink-0 text-amber-400"
              />

              <div>
                <p className="text-sm font-semibold text-amber-300">
                  Live data warning
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  {error}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Processing */}
        {processing && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="rounded-2xl border border-cyan-400/20 bg-cyan-400/[0.03] p-4"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Activity
                  size={17}
                  className="animate-pulse text-cyan-400"
                />

                <div>
                  <p className="text-sm font-semibold">
                    Processing satellite data...
                  </p>

                  <p className="text-[10px] text-slate-600">
                    Loading spill detection and investigation data.
                  </p>
                </div>
              </div>

              <span className="text-sm font-bold text-cyan-400">
                {progress}%
              </span>
            </div>

            <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-white/5">
              <motion.div
                className="h-full rounded-full bg-cyan-400"
                animate={{
                  width: `${progress}%`,
                }}
                transition={{
                  duration: 0.15,
                }}
              />
            </div>
          </motion.div>
        )}

        <div className="grid gap-6 xl:grid-cols-[1.35fr_.65fr]">

          {/* Satellite visualization */}
          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            className="overflow-hidden rounded-3xl border border-white/10 bg-white/[0.03] backdrop-blur-xl"
          >
            <div className="flex items-center justify-between border-b border-white/10 p-4">
              <div className="flex items-center gap-3">
                <div className="rounded-xl bg-cyan-400/10 p-2 text-cyan-400">
                  <Crosshair size={18} />
                </div>

                <div>
                  <h2 className="text-sm font-semibold">
                    Detection Visualization
                  </h2>

                  <p className="text-[10px] text-slate-600">
                    AI segmentation overlay
                  </p>
                </div>
              </div>

              <button
                type="button"
                className="rounded-lg border border-white/10 p-2 text-slate-500 hover:text-white"
              >
                <Maximize2 size={15} />
              </button>
            </div>

            <div className="relative h-[470px] overflow-hidden bg-[#06131d]">

              {/* Ocean grid */}
              <div
                className="absolute inset-0 opacity-20"
                style={{
                  backgroundImage:
                    "linear-gradient(rgba(34,211,238,.18) 1px, transparent 1px), linear-gradient(90deg, rgba(34,211,238,.18) 1px, transparent 1px)",
                  backgroundSize: "45px 45px",
                }}
              />

              {/* Simulated ocean */}
              <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(14,116,144,.22),transparent_65%)]" />

              {/* Spill */}
              <motion.div
                animate={{
                  scale: [1, 1.04, 1],
                  opacity: [0.72, 0.85, 0.72],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                }}
                className="absolute left-[43%] top-[43%] h-40 w-64 -rotate-12 rounded-[50%] border border-orange-400/50 bg-orange-500/20 shadow-[0_0_60px_rgba(249,115,22,.18)]"
              />

              <div className="absolute left-[48%] top-[45%] h-4 w-4 rounded-full bg-orange-400 shadow-[0_0_25px_rgba(251,146,60,.8)]" />

              {/* Detection boundary */}
              <div className="absolute left-[37%] top-[35%] h-56 w-[390px] rotate-[-10deg] rounded-[50%] border border-dashed border-cyan-400/50" />

              {/* Coordinates */}
              <div className="absolute left-5 top-5 rounded-xl border border-white/10 bg-black/30 px-3 py-2 backdrop-blur-md">
                <p className="text-[9px] uppercase tracking-wider text-slate-600">
                  Detected Coordinates
                </p>

                <p className="mt-1 text-xs font-semibold text-cyan-400">
                  {analysisData.coordinates}
                </p>
              </div>

              {/* Legend */}
              <div className="absolute bottom-5 left-5 rounded-xl border border-white/10 bg-black/40 p-3 backdrop-blur-md">
                <div className="flex items-center gap-3 text-[10px] text-slate-400">
                  <span className="h-2.5 w-2.5 rounded-full bg-orange-400" />
                  Detected Spill
                </div>

                <div className="mt-2 flex items-center gap-3 text-[10px] text-slate-400">
                  <span className="h-2.5 w-2.5 rounded-full border border-cyan-400" />
                  AI Boundary
                </div>
              </div>

              <div className="absolute bottom-5 right-5 flex items-center gap-2 rounded-xl border border-white/10 bg-black/40 px-3 py-2 text-[10px] text-slate-500 backdrop-blur-md">
                <Satellite
                  size={13}
                  className="text-cyan-400"
                />
                SATELLITE ANALYSIS
              </div>
            </div>
          </motion.div>

          {/* Metrics */}
          <div className="space-y-4">
            <Metric
              icon={Maximize2}
              label="Estimated Spill Area"
              value={analysisData.area}
              sub="AI geometric estimation"
            />

            <Metric
              icon={Target}
              label="Detection Confidence"
              value={`${analysisData.confidence}%`}
              sub="Model confidence score"
            />

            <Metric
              icon={Clock3}
              label="Detection Time"
              value={analysisData.detectedAt}
              sub="Backend incident record"
            />

            <Metric
              icon={Navigation}
              label="Spill Shape"
              value={analysisData.shape}
              sub={`Perimeter: ${analysisData.perimeter}`}
            />

            {/* Risk */}
            <div className="rounded-2xl border border-orange-400/20 bg-orange-400/[0.04] p-5">
              <div className="flex items-center gap-3">
                <div className="rounded-xl bg-orange-400/10 p-2.5 text-orange-400">
                  <AlertTriangle size={19} />
                </div>

                <div>
                  <p className="text-[10px] uppercase tracking-wider text-slate-600">
                    Environmental Risk
                  </p>

                  <p className="mt-1 text-xl font-bold text-orange-400">
                    {analysisData.severity}
                  </p>
                </div>
              </div>

              <p className="mt-4 text-xs leading-6 text-slate-500">
                Detected spill characteristics are presented as
                investigation-support information. They do not independently
                establish responsibility or liability.
              </p>
            </div>

            {/* Location */}
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <div className="flex items-center gap-3">
                <MapPin
                  size={17}
                  className="text-cyan-400"
                />

                <div>
                  <p className="text-[10px] text-slate-600">
                    Detection Region
                  </p>

                  <p className="mt-1 text-sm font-semibold">
                    {analysisData.location}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Analysis confidence */}
        <div className="grid gap-4 md:grid-cols-3">
          {[
            [
              "Satellite Detection",
              analysisData.confidence,
              "Backend incident confidence",
              CheckCircle2,
            ],
            [
              "Geometric Confidence",
              analysisData.confidence,
              "Derived from available incident data",
              Maximize2,
            ],
            [
              "Environmental Signal",
              analysisData.confidence,
              "Available incident signal",
              Waves,
            ],
          ].map(([title, value, sub, Icon]) => (
            <div
              key={title}
              className="rounded-2xl border border-white/10 bg-white/[0.03] p-5"
            >
              <div className="flex items-center justify-between">
                <p className="text-xs text-slate-500">
                  {title}
                </p>

                <Icon
                  size={16}
                  className="text-cyan-400"
                />
              </div>

              <div className="mt-4 flex items-end justify-between">
                <p className="text-2xl font-bold">
                  {Number(value || 0).toFixed(1)}%
                </p>

                <span className="text-[10px] font-semibold text-emerald-400">
                  {sub}
                </span>
              </div>

              <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-white/5">
                <div
                  className="h-full rounded-full bg-cyan-400"
                  style={{
                    width: `${Math.min(
                      Number(value || 0),
                      100
                    )}%`,
                  }}
                />
              </div>
            </div>
          ))}
        </div>

        {/* Next step */}
        <div className="flex flex-col justify-between gap-4 rounded-3xl border border-cyan-400/10 bg-cyan-400/[0.025] p-5 sm:flex-row sm:items-center">
          <div className="flex gap-3">
            <div className="rounded-xl bg-cyan-400/10 p-2.5 text-cyan-400">
              <ShieldCheck size={19} />
            </div>

            <div>
              <h3 className="text-sm font-semibold">
                Continue Investigation
              </h3>

              <p className="mt-1 text-xs text-slate-600">
                Use environmental conditions to predict spill movement
                and estimate its probable origin.
              </p>
            </div>
          </div>

          <button
            onClick={() => navigate("/analysis/drift")}
            className="group flex items-center justify-center gap-2 rounded-xl bg-cyan-400 px-5 py-3 text-xs font-bold text-slate-950 transition hover:bg-cyan-300"
          >
            Run Drift Prediction

            <ArrowRight
              size={15}
              className="transition-transform group-hover:translate-x-1"
            />
          </button>
        </div>
      </div>
    </div>
  );
}