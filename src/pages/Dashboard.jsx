import { useEffect, useMemo, useState } from "react";

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



import StatCard from "../Components/StatCard";
import MapView from "../Components/MapView";
import SpillCard from "../Components/SpillCard";
import VesselTable from "../Components/VesselTable";
import RiskBadge from "../Components/RiskBadge";

import {
  getIncident,
  getIncidentCandidates,
  getIncidentInvestigation,
} from "../Services/api";

export default function Dashboard() {
  const [incident, setIncident] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [investigation, setInvestigation] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    const loadDashboard = async () => {
      try {
        setLoading(true);
        setError("");

        const [
          incidentData,
          candidatesData,
          investigationData,
        ] = await Promise.all([
          getIncident(1),
          getIncidentCandidates(1),
          getIncidentInvestigation(1),
        ]);

        if (cancelled) return;

        setIncident(incidentData);

        setCandidates(
          Array.isArray(candidatesData)
            ? candidatesData
            : candidatesData?.candidates ?? []
        );

        setInvestigation(investigationData);
      } catch (err) {
        console.error("Dashboard API error:", err);

        if (!cancelled) {
          setError(
            "Live intelligence data could not be loaded."
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadDashboard();

    return () => {
      cancelled = true;
    };
  }, []);

  const rankedVessels = useMemo(() => {
    return investigation?.ranked_vessels ?? [];
  }, [investigation]);

  const activeDetections = incident ? 1 : 0;

  const detectionConfidence =
    incident?.detection_confidence != null
      ? `${Number(
          incident.detection_confidence
        ).toFixed(1)}%`
      : "—";

  const vesselCount =
    rankedVessels.length ||
    candidates.length ||
    0;

  const incidentArea =
    incident?.estimated_area_km2 != null
      ? `${Number(
          incident.estimated_area_km2
        ).toFixed(2)} km²`
      : "—";

  const incidentLocation =
    incident?.latitude != null &&
    incident?.longitude != null
      ? `${Number(incident.latitude).toFixed(4)}, ${Number(
          incident.longitude
        ).toFixed(4)}`
      : "Location unavailable";

  const incidentTime = incident?.detection_time
    ? new Date(
        incident.detection_time
      ).toLocaleString("en-IN", {
        dateStyle: "medium",
        timeStyle: "short",
      })
    : "Detection time unavailable";

  const topVessel = rankedVessels[0];

  const topRisk =
    topVessel?.priority_level ||
    "LOW";

  const topVesselName =
    topVessel?.vessel_name ||
    "No vessel identified";

  const topPriority =
    topVessel?.final_priority_score != null
      ? Number(
          topVessel.final_priority_score
        ).toFixed(2)
      : "—";

  const topCombined =
    topVessel?.combined_score != null
      ? `${(
          Number(topVessel.combined_score) * 100
        ).toFixed(1)}%`
      : "—";

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
              {" "}
              Command Center
            </span>
          </h1>

          <p className="mt-2 text-xs text-slate-500">
            Real-time oil spill detection, drift intelligence
            and vessel correlation.
          </p>
        </div>

        <button
          className="glow-button flex items-center justify-center gap-2 rounded-xl px-5 py-3 text-xs font-bold text-white"
          onClick={() =>
            (window.location.href = "/analysis/new")
          }
        >
          <ScanLine size={15} />
          NEW INVESTIGATION
        </button>
      </div>

      {/* ERROR */}

      {error && (
        <div className="mb-5 rounded-xl border border-rose-400/10 bg-rose-500/[.04] px-4 py-3 text-xs text-rose-300">
          {error}
        </div>
      )}

      {/* LIVE STATUS */}

      {loading && (
        <div className="mb-5 rounded-xl border border-cyan-400/10 bg-cyan-400/[.03] px-4 py-3 text-xs text-cyan-300">
          Loading live investigation intelligence...
        </div>
      )}

      {/* KPI */}

      <div className="stagger grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="Active Detections"
          value={loading ? "…" : activeDetections}
          change={
            incident
              ? `Incident ${incident.incident_id || "—"}`
              : "No active incident"
          }
          icon={AlertTriangle}
          color="red"
        />

        <StatCard
          title="Detection Confidence"
          value={
            loading
              ? "…"
              : detectionConfidence
          }
          change={
            incident?.satellite_source
              ? `Source: ${incident.satellite_source}`
              : "Live incident data"
          }
          icon={Target}
          color="cyan"
        />

        <StatCard
          title="Vessels Correlated"
          value={
            loading
              ? "…"
              : vesselCount
          }
          change={
            topVesselName !==
            "No vessel identified"
              ? `Top: ${topVesselName}`
              : "Awaiting correlation"
          }
          icon={Ship}
          color="violet"
        />

        <StatCard
          title="Priority Score"
          value={
            loading
              ? "…"
              : topPriority
          }
          change={
            topVessel
              ? `${topRisk} priority`
              : "Investigation pending"
          }
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
                Real incident location and vessel intelligence
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
              label="Candidates"
              value={
                loading
                  ? "…"
                  : candidates.length
              }
            />

            <RadarStat
              label="Correlated"
              value={
                loading
                  ? "…"
                  : rankedVessels.length
              }
            />

            <RadarStat
              label="Priority"
              value={
                loading
                  ? "…"
                  : topRisk
              }
            />

            <RadarStat
              label="Incident"
              value={
                incident?.incident_id ||
                "—"
              }
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
                {incident?.incident_id ||
                  "Current Investigation"}
              </h2>
            </div>

            <ShieldCheck
              className="text-emerald-400"
              size={20}
            />
          </div>

          <p className="mt-5 text-xs leading-6 text-slate-400">
            OILTRACE is processing live incident and
            vessel-correlation data from the backend.
            The investigation ranking is intended for
            further investigation and decision support.
          </p>

          <div className="mt-5 flex flex-wrap gap-2">
            <Tag
              text={`${detectionConfidence} confidence`}
            />

            <Tag
              text={`${incidentArea} estimated area`}
            />

            <Tag
              text={`Location: ${incidentLocation}`}
            />

            <Tag
              text={`Detected: ${incidentTime}`}
            />

            <Tag
              text={`Top correlation: ${topCombined}`}
            />
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
                {topVessel
                  ? `${topRisk} priority vessel`
                  : "No priority vessel"}
              </p>
            </div>
          </div>

          <p className="mt-5 text-xs leading-6 text-slate-500">
            {topVessel
              ? `${topVesselName} currently has the highest investigation priority score of ${topPriority}.`
              : "Live investigation data is not available yet."}
          </p>

          <div className="mt-5">
            <RiskBadge risk={topRisk} />
          </div>
        </div>
      </div>

      {/* RECENT */}

      <div className="mt-5 grid gap-5 xl:grid-cols-2">
        <div>
          <div className="mb-3 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-white">
                Current Spill Detection
              </h2>

              <p className="mt-1 text-[10px] text-slate-600">
                Live incident from backend
              </p>
            </div>

            <TrendingUp
              size={17}
              className="text-cyan-400"
            />
          </div>

          <div className="space-y-3">
            {incident ? (
              <SpillCard
                spill={{
                  id:
                    incident.incident_id ||
                    "INCIDENT",
                  location: incidentLocation,
                  area: incidentArea,
                  confidence:
                    detectionConfidence,
                  detectedAt:
                    incidentTime,
                  risk: topRisk,
                  status:
                    "Active",
                }}
              />
            ) : (
              <div className="glass rounded-xl p-5 text-xs text-slate-500">
                No live incident available.
              </div>
            )}
          </div>
        </div>

        <VesselTable vessels={rankedVessels} />
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