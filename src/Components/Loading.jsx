import React from "react";

import { motion } from "framer-motion";
import { Satellite } from "lucide-react";

export default function Loading({
  text = "Processing satellite intelligence...",
}) {

  return (
    <div className="flex min-h-[300px] items-center justify-center">

      <div className="text-center">

        <div className="relative mx-auto h-24 w-24">

          <motion.div
            animate={{
              scale: [1, 1.5, 1],
              opacity: [0.5, 0, 0.5],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
            }}
            className="absolute inset-0 rounded-full border border-cyan-400/30"
          />

          <motion.div
            animate={{
              scale: [1, 1.8, 1],
              opacity: [0.25, 0, 0.25],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              delay: .5,
            }}
            className="absolute inset-0 rounded-full border border-violet-400/20"
          />

          <motion.div
            animate={{
              rotate: 360,
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "linear",
            }}
            className="absolute left-1/2 top-1/2 flex h-14 w-14 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-2xl border border-cyan-400/20 bg-cyan-400/10 text-cyan-400"
          >
            <Satellite size={26} />
          </motion.div>

        </div>

        <p className="mt-6 text-xs font-medium text-slate-300">
          {text}
        </p>

        <div className="mt-3 flex justify-center gap-1">

          {[0,1,2].map((i) => (
            <motion.span
              key={i}
              animate={{
                opacity: [.2,1,.2],
              }}
              transition={{
                duration: 1,
                repeat: Infinity,
                delay: i * .2,
              }}
              className="h-1.5 w-1.5 rounded-full bg-cyan-400"
            />
          ))}

        </div>

        <p className="mt-3 text-[8px] uppercase tracking-[.3em] text-slate-700">
          OILTRACE Intelligence System
        </p>

      </div>

    </div>
  );
}