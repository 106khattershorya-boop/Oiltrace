import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  Satellite,
  Droplets,
  Waves,
  Ship,
  History,
  BarChart3,
  FileText,
  Settings,
  HelpCircle,
  LogOut,
  Plus,
  ChevronRight,
  Radio,
} from "lucide-react";

const Sidebar = ({ onNavigate = () => {} }) => {
  const navigate = useNavigate();

  const navigation = [
    {
      section: "COMMAND",
      items: [
        {
          label: "Dashboard",
          path: "/dashboard",
          icon: LayoutDashboard,
        },
        {
          label: "New Analysis",
          path: "/analysis/new",
          icon: Plus,
        },
      ],
    },

    {
      section: "INTELLIGENCE",
      items: [
        {
          label: "Spill Analysis",
          path: "/analysis/spill",
          icon: Droplets,
        },
        {
          label: "Drift Prediction",
          path: "/analysis/drift",
          icon: Waves,
        },
        {
          label: "Vessel Attribution",
          path: "/analysis/vessels",
          icon: Ship,
        },
      ],
    },

    {
      section: "DATA",
      items: [
        {
          label: "History",
          path: "/history",
          icon: History,
        },
        {
          label: "Analytics",
          path: "/analytics",
          icon: BarChart3,
        },
        {
          label: "Reports",
          path: "/reports",
          icon: FileText,
        },
      ],
    },

    {
      section: "SYSTEM",
      items: [
        {
          label: "Settings",
          path: "/settings",
          icon: Settings,
        },
        {
          label: "Help & Support",
          path: "/help",
          icon: HelpCircle,
        },
      ],
    },
  ];

  const handleNavigation = () => {
    onNavigate();
  };

  const handleLogout = () => {
    localStorage.removeItem("isLoggedIn");
    localStorage.removeItem("oiltrace_token");

    onNavigate();
    navigate("/login", { replace: true });
  };

  return (
    <div className="flex h-full w-full flex-col overflow-hidden border-r border-white/10 bg-[#030712]/95 backdrop-blur-2xl">
      {/* Logo */}
      <div className="relative flex h-20 shrink-0 items-center border-b border-white/10 px-5">
        <div className="absolute left-0 top-0 h-px w-full bg-gradient-to-r from-transparent via-cyan-400/60 to-transparent" />

        <div className="flex items-center gap-3">
          <div className="relative flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-400/30 bg-gradient-to-br from-cyan-500/20 via-blue-500/10 to-violet-500/20">
            <Satellite size={21} className="text-cyan-300" />

            <span className="absolute -right-1 -top-1 h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
          </div>

          <div>
            <h1 className="text-lg font-black tracking-[0.18em] text-white">
              OILTRACE
            </h1>

            <p className="text-[9px] font-medium uppercase tracking-[0.22em] text-slate-500">
              Maritime Intelligence
            </p>
          </div>
        </div>
      </div>

      {/* System Status */}
      <div className="mx-4 mt-4 rounded-xl border border-emerald-400/10 bg-emerald-400/[0.04] px-3 py-2.5">
        <div className="flex items-center gap-2">
          <Radio size={13} className="text-emerald-400" />

          <span className="text-[10px] font-semibold uppercase tracking-wider text-emerald-400">
            Systems Operational
          </span>

          <span className="ml-auto h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
        </div>
      </div>

      {/* Navigation */}
      <div className="mt-4 flex-1 overflow-y-auto px-3 pb-4">
        {navigation.map((group) => (
          <div key={group.section} className="mb-5">
            <p className="mb-2 px-3 text-[9px] font-bold tracking-[0.22em] text-slate-600">
              {group.section}
            </p>

            <div className="space-y-1">
              {group.items.map((item) => {
                const Icon = item.icon;

                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    onClick={handleNavigation}
                    className={({ isActive }) =>
                      `group relative flex items-center gap-3 rounded-xl px-3 py-3 text-sm transition-all duration-300 ${
                        isActive
                          ? "bg-gradient-to-r from-cyan-500/15 via-blue-500/10 to-transparent text-cyan-300 shadow-[inset_3px_0_0_rgba(34,211,238,0.9)]"
                          : "text-slate-400 hover:bg-white/[0.04] hover:text-white"
                      }`
                    }
                  >
                    {({ isActive }) => (
                      <>
                        <div
                          className={`flex h-8 w-8 items-center justify-center rounded-lg transition-all ${
                            isActive
                              ? "bg-cyan-400/10 text-cyan-300"
                              : "bg-white/[0.03] text-slate-500 group-hover:text-cyan-300"
                          }`}
                        >
                          <Icon size={17} />
                        </div>

                        <span className="flex-1 font-medium">
                          {item.label}
                        </span>

                        <ChevronRight
                          size={14}
                          className={`transition-all ${
                            isActive
                              ? "translate-x-0 text-cyan-400 opacity-100"
                              : "-translate-x-1 opacity-0 group-hover:translate-x-0 group-hover:opacity-50"
                          }`}
                        />
                      </>
                    )}
                  </NavLink>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Bottom */}
      <div className="shrink-0 border-t border-white/10 p-3">
        <button
          onClick={handleLogout}
          className="group flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm text-slate-400 transition-all hover:bg-red-500/[0.07] hover:text-red-400"
        >
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/[0.03] transition-colors group-hover:bg-red-500/10">
            <LogOut size={17} />
          </div>

          <span className="font-medium">Logout</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;