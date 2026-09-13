import React, { useState } from "react";
import {
  Settings as SettingsIcon,
  User,
  Bell,
  Shield,
  Palette,
  Database,
  Save,
  CheckCircle2,
} from "lucide-react";
import { motion } from "framer-motion";

const Settings = () => {
  const [saved, setSaved] = useState(false);

  const [settings, setSettings] = useState({
    name: "OILTRACE Analyst",
    email: "analyst@oiltrace.local",
    notifications: true,
    criticalAlerts: true,
    aiUpdates: true,
    autoSave: true,
  });

  const update = (key, value) => {
    setSettings((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const saveSettings = () => {
    localStorage.setItem(
      "oiltrace_settings",
      JSON.stringify(settings)
    );

    setSaved(true);

    setTimeout(() => {
      setSaved(false);
    }, 2200);
  };

  return (
    <div className="ot-page-enter space-y-7">
      <div>
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400">
          <SettingsIcon size={15} />
          System Configuration
        </div>

        <h1 className="mt-2 text-3xl font-black text-white">
          OILTRACE <span className="ot-gradient-text">Settings</span>
        </h1>

        <p className="mt-2 text-sm text-slate-500">
          Configure analyst preferences and intelligence notifications.
        </p>
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.7fr_1.3fr]">
        {/* PROFILE */}
        <motion.div
          initial={{ opacity: 0, x: -15 }}
          animate={{ opacity: 1, x: 0 }}
          className="ot-card p-6"
        >
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400/20 to-violet-500/20 text-cyan-300">
              <User size={25} />
            </div>

            <div>
              <h2 className="font-bold text-white">Analyst Profile</h2>
              <p className="text-xs text-slate-500">
                Investigation operator
              </p>
            </div>
          </div>

          <div className="mt-7 space-y-5">
            <div>
              <label className="mb-2 block text-xs font-semibold text-slate-400">
                Display Name
              </label>

              <input
                value={settings.name}
                onChange={(e) => update("name", e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-900/70 px-4 py-3 text-sm text-white focus:border-cyan-400/40"
              />
            </div>

            <div>
              <label className="mb-2 block text-xs font-semibold text-slate-400">
                Email
              </label>

              <input
                value={settings.email}
                onChange={(e) => update("email", e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-900/70 px-4 py-3 text-sm text-white focus:border-cyan-400/40"
              />
            </div>
          </div>
        </motion.div>

        {/* PREFERENCES */}
        <motion.div
          initial={{ opacity: 0, x: 15 }}
          animate={{ opacity: 1, x: 0 }}
          className="ot-card p-6"
        >
          <h2 className="flex items-center gap-2 text-lg font-bold text-white">
            <Bell size={19} className="text-violet-300" />
            Intelligence Preferences
          </h2>

          <div className="mt-6 divide-y divide-slate-800">
            {[
              {
                key: "notifications",
                title: "System Notifications",
                desc: "Receive updates about completed analyses.",
                icon: Bell,
              },
              {
                key: "criticalAlerts",
                title: "Critical Spill Alerts",
                desc: "Immediately highlight high-risk detections.",
                icon: Shield,
              },
              {
                key: "aiUpdates",
                title: "AI Intelligence Updates",
                desc: "Show AI-generated investigation insights.",
                icon: Palette,
              },
              {
                key: "autoSave",
                title: "Automatic Case Saving",
                desc: "Persist analysis results locally.",
                icon: Database,
              },
            ].map(({ key, title, desc, icon: Icon }) => (
              <div
                key={key}
                className="flex items-center justify-between gap-5 py-5"
              >
                <div className="flex gap-3">
                  <div className="rounded-xl bg-slate-800/70 p-2.5 text-slate-400">
                    <Icon size={17} />
                  </div>

                  <div>
                    <p className="text-sm font-semibold text-slate-200">
                      {title}
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      {desc}
                    </p>
                  </div>
                </div>

                <button
                  onClick={() => update(key, !settings[key])}
                  className={`relative h-6 w-11 shrink-0 rounded-full transition ${
                    settings[key]
                      ? "bg-cyan-500"
                      : "bg-slate-700"
                  }`}
                >
                  <span
                    className={`absolute top-1 h-4 w-4 rounded-full bg-white transition ${
                      settings[key]
                        ? "left-6"
                        : "left-1"
                    }`}
                  />
                </button>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* SYSTEM STATUS */}
      <div className="ot-card grid gap-4 p-6 md:grid-cols-3">
        {[
          ["AI Detection Engine", "Operational"],
          ["AIS Correlation Engine", "Operational"],
          ["Drift Simulation", "Operational"],
        ].map(([name, status]) => (
          <div
            key={name}
            className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-900/60 p-4"
          >
            <span className="text-xs font-semibold text-slate-400">
              {name}
            </span>

            <span className="flex items-center gap-2 text-[10px] font-bold text-emerald-300">
              <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-lg shadow-emerald-400/50" />
              {status}
            </span>
          </div>
        ))}
      </div>

      <div className="flex justify-end">
        <button
          onClick={saveSettings}
          className="ot-button flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-6 py-3 text-sm font-bold text-white"
        >
          {saved ? (
            <>
              <CheckCircle2 size={17} />
              Settings Saved
            </>
          ) : (
            <>
              <Save size={17} />
              Save Configuration
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default Settings;