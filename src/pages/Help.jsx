import React, { useState } from "react";
import {
  HelpCircle,
  Search,
  MessageSquare,
  Satellite,
  Ship,
  Waves,
  FileText,
  ChevronDown,
  Sparkles,
} from "lucide-react";
import { motion } from "framer-motion";

const faqs = [
  {
    q: "How does OILTRACE detect an oil spill?",
    a: "OILTRACE processes satellite imagery to identify anomalous surface signatures and generates a suspected spill boundary with confidence and geometric properties.",
  },
  {
    q: "How is the probable spill origin estimated?",
    a: "The drift module uses environmental conditions such as wind and ocean-current information to reconstruct probable movement and estimate an origin region.",
  },
  {
    q: "How does AIS attribution work?",
    a: "Historical AIS tracks around the estimated origin window are filtered and ranked using factors such as proximity, trajectory consistency and behavioral anomalies.",
  },
  {
    q: "Does a high-ranked vessel mean it caused the spill?",
    a: "No. A vessel ranking is an investigative lead based on available evidence. It should be validated with additional operational and environmental evidence.",
  },
  {
    q: "Can I export an investigation report?",
    a: "Yes. The Reports module provides structured report previews and export functionality for investigation documentation.",
  },
];

const guides = [
  {
    title: "Run Spill Detection",
    desc: "Upload satellite imagery and start a new investigation.",
    icon: Satellite,
    path: "/analysis/new",
  },
  {
    title: "Analyse Vessel Correlation",
    desc: "Review AIS candidates around the estimated origin.",
    icon: Ship,
    path: "/analysis/vessels",
  },
  {
    title: "Predict Spill Drift",
    desc: "Explore future movement under environmental conditions.",
    icon: Waves,
    path: "/analysis/drift",
  },
  {
    title: "Generate Reports",
    desc: "Create structured investigation documentation.",
    icon: FileText,
    path: "/reports",
  },
];

const Help = () => {
  const [search, setSearch] = useState("");
  const [open, setOpen] = useState(null);

  const filteredFaqs = faqs.filter(
    (item) =>
      item.q.toLowerCase().includes(search.toLowerCase()) ||
      item.a.toLowerCase().includes(search.toLowerCase())
  );

  const openAssistant = () => {
    window.dispatchEvent(new Event("open-oiltrace-chat"));
  };

  return (
    <div className="ot-page-enter space-y-8">
      {/* HERO */}
      <motion.div
        initial={{ opacity: 0, y: -15 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-3xl border border-violet-400/10 bg-slate-950/70 p-7 text-center backdrop-blur-xl md:p-10"
      >
        <div className="absolute left-1/2 top-[-120px] h-72 w-72 -translate-x-1/2 rounded-full bg-violet-500/10 blur-[100px]" />

        <div className="relative">
          <div className="mx-auto mb-5 flex w-fit rounded-2xl bg-violet-400/10 p-4 text-violet-300">
            <HelpCircle size={28} />
          </div>

          <h1 className="text-3xl font-black text-white md:text-4xl">
            OILTRACE <span className="ot-gradient-text">Help Center</span>
          </h1>

          <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-slate-500">
            Learn how to use the maritime intelligence workflow from satellite
            detection to vessel attribution.
          </p>

          <div className="relative mx-auto mt-7 max-w-xl">
            <Search
              size={18}
              className="absolute left-4 top-3.5 text-slate-600"
            />

            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search help articles..."
              className="w-full rounded-2xl border border-slate-700 bg-slate-900/80 py-3.5 pl-11 pr-4 text-sm text-white placeholder:text-slate-600 focus:border-violet-400/40"
            />
          </div>
        </div>
      </motion.div>

      {/* GUIDES */}
      <div>
        <div className="mb-4 flex items-center gap-2">
          <Sparkles size={17} className="text-cyan-300" />
          <h2 className="font-bold text-white">Quick Guides</h2>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {guides.map((guide, index) => {
            const Icon = guide.icon;

            return (
              <motion.div
                key={guide.title}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.07 }}
                whileHover={{ y: -5 }}
                onClick={() => (window.location.href = guide.path)}
                className="ot-card cursor-pointer p-5"
              >
                <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-300">
                  <Icon size={20} />
                </div>

                <h3 className="text-sm font-bold text-slate-200">
                  {guide.title}
                </h3>

                <p className="mt-2 text-xs leading-5 text-slate-500">
                  {guide.desc}
                </p>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* FAQ + AI */}
      <div className="grid gap-6 xl:grid-cols-[1.4fr_0.6fr]">
        <div className="ot-card p-6">
          <h2 className="mb-5 text-lg font-bold text-white">
            Frequently Asked Questions
          </h2>

          <div className="space-y-2">
            {filteredFaqs.map((faq, index) => (
              <div
                key={faq.q}
                className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/50"
              >
                <button
                  onClick={() =>
                    setOpen(open === index ? null : index)
                  }
                  className="flex w-full items-center justify-between gap-4 px-4 py-4 text-left"
                >
                  <span className="text-sm font-semibold text-slate-300">
                    {faq.q}
                  </span>

                  <ChevronDown
                    size={17}
                    className={`shrink-0 text-slate-600 transition ${
                      open === index ? "rotate-180 text-cyan-300" : ""
                    }`}
                  />
                </button>

                {open === index && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    className="border-t border-slate-800 px-4 pb-4 pt-3 text-xs leading-6 text-slate-500"
                  >
                    {faq.a}
                  </motion.div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* AI ASSISTANT */}
        <motion.div
          whileHover={{ y: -4 }}
          className="relative overflow-hidden rounded-2xl border border-violet-400/10 bg-gradient-to-br from-violet-950/40 to-slate-950 p-6"
        >
          <div className="absolute right-[-40px] top-[-40px] h-36 w-36 rounded-full bg-violet-500/10 blur-3xl" />

          <div className="relative">
            <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-xl bg-violet-400/10 text-violet-300">
              <MessageSquare size={21} />
            </div>

            <h2 className="text-xl font-black text-white">
              OILTRACE AI Assistant
            </h2>

            <p className="mt-3 text-sm leading-6 text-slate-500">
              Need help understanding an investigation step? Ask the
              integrated AI assistant for guidance.
            </p>

            <button
              onClick={openAssistant}
              className="ot-button mt-7 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-500 to-blue-600 py-3 text-sm font-bold text-white"
            >
              <MessageSquare size={17} />
              Ask OILTRACE AI
            </button>
          </div>
        </motion.div>
      </div>

      {/* WORKFLOW */}
      <div className="ot-card p-6">
        <h2 className="mb-6 flex items-center gap-2 text-lg font-bold text-white">
          <Satellite size={19} className="text-cyan-300" />
          Investigation Workflow
        </h2>

        <div className="grid gap-3 md:grid-cols-6">
          {[
            "Satellite",
            "Detection",
            "Origin",
            "Drift",
            "AIS",
            "Report",
          ].map((item, index) => (
            <div
              key={item}
              className="relative rounded-xl border border-slate-800 bg-slate-900/60 p-4 text-center"
            >
              <div className="mx-auto flex h-8 w-8 items-center justify-center rounded-full bg-cyan-400/10 text-xs font-black text-cyan-300">
                {index + 1}
              </div>

              <p className="mt-3 text-xs font-semibold text-slate-400">
                {item}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Help;