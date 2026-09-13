import React, { useMemo, useState } from "react";
import {
  Search,
  Filter,
  Eye,
  MapPin,
  CalendarDays,
  Satellite,
  ChevronRight,
  Activity,
} from "lucide-react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import RiskBadge from "../Components/RiskBadge";

const initialData = [
  {
    id: "OT-2026-0912-001",
    location: "Arabian Sea",
    area: "42.6 km²",
    confidence: 94.8,
    risk: "HIGH",
    status: "Active",
    date: "12 Sep 2026 • 00:18",
  },
  {
    id: "OT-2026-0911-002",
    location: "Bay of Bengal",
    area: "18.4 km²",
    confidence: 91.3,
    risk: "MEDIUM",
    status: "Monitoring",
    date: "11 Sep 2026 • 18:42",
  },
  {
    id: "OT-2026-0911-003",
    location: "Indian Ocean",
    area: "8.7 km²",
    confidence: 89.6,
    risk: "LOW",
    status: "Resolved",
    date: "11 Sep 2026 • 12:06",
  },
  {
    id: "OT-2026-0910-004",
    location: "Gulf of Kutch",
    area: "27.2 km²",
    confidence: 93.1,
    risk: "HIGH",
    status: "Investigating",
    date: "10 Sep 2026 • 21:31",
  },
  {
    id: "OT-2026-0909-005",
    location: "Lakshadweep Sea",
    area: "6.9 km²",
    confidence: 87.4,
    risk: "LOW",
    status: "Resolved",
    date: "09 Sep 2026 • 16:20",
  },
];

const History = () => {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("ALL");

  const filtered = useMemo(() => {
    return initialData.filter((item) => {
      const matchesSearch =
        item.id.toLowerCase().includes(search.toLowerCase()) ||
        item.location.toLowerCase().includes(search.toLowerCase());

      const matchesFilter =
        filter === "ALL" || item.risk === filter;

      return matchesSearch && matchesFilter;
    });
  }, [search, filter]);

  return (
    <div className="ot-page-enter space-y-7">
      <div>
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400">
          <Activity size={15} />
          Investigation Archive
        </div>

        <h1 className="mt-2 text-3xl font-black text-white">
          Analysis <span className="ot-gradient-text">History</span>
        </h1>

        <p className="mt-2 text-sm text-slate-500">
          Review previous satellite detections and investigation cases.
        </p>
      </div>

      {/* CONTROLS */}
      <div className="ot-card flex flex-col gap-4 p-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="relative w-full lg:max-w-md">
          <Search
            size={17}
            className="absolute left-3 top-3.5 text-slate-500"
          />

          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search case ID or location..."
            className="w-full rounded-xl border border-slate-700 bg-slate-900/70 py-3 pl-10 pr-4 text-sm text-white placeholder:text-slate-600 focus:border-cyan-400/40"
          />
        </div>

        <div className="flex items-center gap-2 overflow-x-auto">
          <Filter size={16} className="text-slate-500" />

          {["ALL", "LOW", "MEDIUM", "HIGH"].map((item) => (
            <button
              key={item}
              onClick={() => setFilter(item)}
              className={`rounded-lg px-4 py-2 text-xs font-bold transition ${
                filter === item
                  ? "bg-cyan-400/10 text-cyan-300 ring-1 ring-cyan-400/20"
                  : "text-slate-500 hover:bg-slate-800 hover:text-slate-300"
              }`}
            >
              {item}
            </button>
          ))}
        </div>
      </div>

      {/* DESKTOP TABLE */}
      <div className="ot-card hidden overflow-hidden md:block">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/50 text-left text-[10px] uppercase tracking-wider text-slate-500">
                <th className="px-5 py-4">Case</th>
                <th className="px-5 py-4">Location</th>
                <th className="px-5 py-4">Area</th>
                <th className="px-5 py-4">Confidence</th>
                <th className="px-5 py-4">Risk</th>
                <th className="px-5 py-4">Status</th>
                <th className="px-5 py-4">Date</th>
                <th className="px-5 py-4" />
              </tr>
            </thead>

            <tbody>
              {filtered.map((item, index) => (
                <motion.tr
                  key={item.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: index * 0.04 }}
                  className="border-b border-slate-800/70 transition hover:bg-cyan-400/[0.025]"
                >
                  <td className="px-5 py-5">
                    <div className="flex items-center gap-3">
                      <div className="rounded-lg bg-cyan-400/10 p-2 text-cyan-300">
                        <Satellite size={16} />
                      </div>

                      <span className="text-sm font-semibold text-slate-200">
                        {item.id}
                      </span>
                    </div>
                  </td>

                  <td className="px-5 py-5">
                    <div className="flex items-center gap-2 text-sm text-slate-300">
                      <MapPin size={14} className="text-slate-600" />
                      {item.location}
                    </div>
                  </td>

                  <td className="px-5 py-5 text-sm text-slate-400">
                    {item.area}
                  </td>

                  <td className="px-5 py-5">
                    <span className="font-bold text-cyan-300">
                      {item.confidence}%
                    </span>
                  </td>

                  <td className="px-5 py-5">
                    <RiskBadge risk={item.risk} />
                  </td>

                  <td className="px-5 py-5">
                    <span className="rounded-full bg-slate-800 px-3 py-1 text-[10px] font-semibold text-slate-400">
                      {item.status}
                    </span>
                  </td>

                  <td className="px-5 py-5 text-xs text-slate-500">
                    {item.date}
                  </td>

                  <td className="px-5 py-5">
                    <button
                      onClick={() => navigate("/analysis/spill")}
                      className="rounded-lg p-2 text-slate-500 transition hover:bg-cyan-400/10 hover:text-cyan-300"
                    >
                      <Eye size={17} />
                    </button>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* MOBILE */}
      <div className="grid gap-4 md:hidden">
        {filtered.map((item, index) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="ot-card p-5"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-sm font-bold text-white">{item.id}</p>
                <p className="mt-1 flex items-center gap-1 text-xs text-slate-500">
                  <MapPin size={12} />
                  {item.location}
                </p>
              </div>

              <RiskBadge risk={item.risk} />
            </div>

            <div className="mt-5 grid grid-cols-2 gap-3">
              <div className="rounded-xl bg-slate-900/70 p-3">
                <p className="text-[10px] uppercase text-slate-600">
                  Area
                </p>
                <p className="mt-1 text-sm font-bold text-slate-300">
                  {item.area}
                </p>
              </div>

              <div className="rounded-xl bg-slate-900/70 p-3">
                <p className="text-[10px] uppercase text-slate-600">
                  Confidence
                </p>
                <p className="mt-1 text-sm font-bold text-cyan-300">
                  {item.confidence}%
                </p>
              </div>
            </div>

            <button
              onClick={() => navigate("/analysis/spill")}
              className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl border border-slate-700 py-2.5 text-xs font-semibold text-slate-300 hover:border-cyan-400/30 hover:text-cyan-300"
            >
              View Investigation
              <ChevronRight size={14} />
            </button>
          </motion.div>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="ot-card py-16 text-center">
          <Satellite className="mx-auto text-slate-700" size={40} />
          <p className="mt-4 text-sm font-semibold text-slate-400">
            No investigations found
          </p>
        </div>
      )}
    </div>
  );
};

export default History;