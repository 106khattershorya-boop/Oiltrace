import React from "react";

import { motion } from "framer-motion";

export default function StatCard({
  title,
  value,
  change,
  icon: Icon,
  color = "cyan",
}) {

  const colors = {
    cyan: "text-cyan-400 bg-cyan-400/10 border-cyan-400/10",
    violet: "text-violet-400 bg-violet-400/10 border-violet-400/10",
    green: "text-emerald-400 bg-emerald-400/10 border-emerald-400/10",
    red: "text-rose-400 bg-rose-400/10 border-rose-400/10",
  };

  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 20,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      whileHover={{
        y: -5,
      }}
      transition={{
        duration: .45,
      }}
      className="glass relative overflow-hidden rounded-2xl p-5"
    >

      <div className="absolute -right-10 -top-10 h-24 w-24 rounded-full bg-cyan-400/5 blur-2xl" />

      <div className="flex items-start justify-between">

        <div>

          <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500">
            {title}
          </p>

          <p className="mt-3 text-3xl font-black tracking-tight text-white">
            {value}
          </p>

          {change && (
            <p className="mt-2 text-[10px] text-emerald-400">
              {change}
            </p>
          )}

        </div>

        <div
          className={`rounded-xl border p-3 ${colors[color]}`}
        >
          <Icon size={20} />
        </div>

      </div>

    </motion.div>
  );
}