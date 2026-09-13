import React from "react";

export default function RiskBadge({
  risk = "LOW",
}) {

  const styles = {
    LOW:
      "border-emerald-400/20 bg-emerald-400/10 text-emerald-300",

    MEDIUM:
      "border-yellow-400/20 bg-yellow-400/10 text-yellow-300",

    HIGH:
      "border-orange-400/20 bg-orange-400/10 text-orange-300",

    CRITICAL:
      "border-rose-400/20 bg-rose-400/10 text-rose-300",
  };

  return (
    <span
      className={`rounded-full border px-2.5 py-1 text-[9px] font-bold tracking-wider ${styles[risk] || styles.LOW}`}
    >
      {risk}
    </span>
  );
}