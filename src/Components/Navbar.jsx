
import {
  Bell,
  Menu,
  X,
  Radio,
  User,
  LogOut,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Navbar({
  sidebarOpen,
  setSidebarOpen,
}) {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("isLoggedIn");
    navigate("/login");
  };

  return (
    <nav
      className="
        fixed
        left-0
        right-0
        top-0
        z-[100]
        h-16
        w-full
        border-b
        border-white/[0.08]
        bg-[#020817]/95
        backdrop-blur-2xl
      "
    >
      <div className="flex h-full w-full items-center">

        {/* ==================================================
            LEFT SECTION
        ================================================== */}

        <div className="flex h-full items-center">

          {/* MOBILE HAMBURGER */}
          <button
            type="button"
            onClick={() =>
              setSidebarOpen((prev) => !prev)
            }
            className="
              ml-3
              flex
              h-10
              w-10
              shrink-0
              items-center
              justify-center
              rounded-xl
              border
              border-cyan-400/20
              bg-cyan-400/[0.08]
              text-cyan-300
              shadow-[0_0_20px_rgba(34,211,238,0.08)]
              transition-all
              duration-300
              hover:border-cyan-400/40
              hover:bg-cyan-400/[0.15]
              hover:text-cyan-200
              active:scale-95
              lg:hidden
            "
            aria-label={
              sidebarOpen
                ? "Close navigation"
                : "Open navigation"
            }
          >
            {sidebarOpen ? (
              <X
                size={21}
                strokeWidth={2.5}
              />
            ) : (
              <Menu
                size={21}
                strokeWidth={2.5}
              />
            )}
          </button>

          {/* DESKTOP BRAND AREA */}
          <div
            className="
              hidden
              h-full
              w-64
              items-center
              border-r
              border-white/[0.06]
              px-5
              lg:flex
            "
          >
            <div className="flex items-center gap-3">

              {/* LOGO */}
              <div
                className="
                  relative
                  flex
                  h-9
                  w-9
                  items-center
                  justify-center
                  rounded-xl
                  border
                  border-cyan-400/20
                  bg-gradient-to-br
                  from-cyan-400/10
                  via-blue-500/10
                  to-violet-500/10
                  text-cyan-300
                  shadow-[0_0_20px_rgba(34,211,238,0.08)]
                "
              >
                <Radio
                  size={17}
                  className="animate-pulse"
                />

                <span
                  className="
                    absolute
                    -right-1
                    -top-1
                    h-2
                    w-2
                    animate-ping
                    rounded-full
                    bg-cyan-400
                  "
                />
              </div>

              <div>
                <p className="text-sm font-black tracking-[0.12em] gradient-text">
                  OILTRACE
                </p>

                <p className="font-mono text-[7px] uppercase tracking-[0.2em] text-cyan-400/60">
                  Maritime Intelligence
                </p>
              </div>

            </div>
          </div>

          {/* MOBILE BRAND */}
          <div className="ml-3 flex items-center lg:hidden">

            <div
              className="
                mr-2
                flex
                h-8
                w-8
                items-center
                justify-center
                rounded-lg
                border
                border-cyan-400/20
                bg-cyan-400/[0.06]
                text-cyan-300
              "
            >
              <Radio
                size={15}
                className="animate-pulse"
              />
            </div>

            <div>
              <p className="text-sm font-black tracking-[0.12em] text-white">
                OILTRACE
              </p>

              <p className="font-mono text-[6px] uppercase tracking-[0.18em] text-cyan-400/60">
                Intelligence
              </p>
            </div>

          </div>

        </div>

        {/* ==================================================
            RIGHT SECTION
        ================================================== */}

        <div className="ml-auto flex h-full items-center gap-2 px-3 sm:gap-3 sm:px-5">

          {/* SYSTEM STATUS */}
          <div
            className="
              hidden
              items-center
              gap-2
              rounded-xl
              border
              border-emerald-400/10
              bg-emerald-400/[0.04]
              px-3
              py-2
              sm:flex
            "
          >
            <span className="relative flex h-2 w-2">

              <span
                className="
                  absolute
                  h-full
                  w-full
                  animate-ping
                  rounded-full
                  bg-emerald-400
                  opacity-50
                "
              />

              <span className="relative h-2 w-2 rounded-full bg-emerald-400" />

            </span>

            <span className="font-mono text-[8px] font-bold uppercase tracking-wider text-emerald-400/80">
              Systems Online
            </span>
          </div>

          {/* NOTIFICATION */}
          <button
            type="button"
            className="
              relative
              flex
              h-10
              w-10
              items-center
              justify-center
              rounded-xl
              border
              border-white/[0.08]
              bg-white/[0.03]
              text-slate-400
              transition-all
              duration-300
              hover:border-cyan-400/20
              hover:bg-cyan-400/[0.06]
              hover:text-cyan-300
            "
            aria-label="Notifications"
          >
            <Bell size={17} />

            <span
              className="
                absolute
                right-2
                top-2
                h-1.5
                w-1.5
                rounded-full
                bg-cyan-400
                shadow-[0_0_8px_#22d3ee]
              "
            />
          </button>

          {/* USER */}
          <div
            className="
              hidden
              items-center
              gap-2
              rounded-xl
              border
              border-white/[0.07]
              bg-white/[0.025]
              px-3
              py-1.5
              md:flex
            "
          >
            <div
              className="
                flex
                h-7
                w-7
                items-center
                justify-center
                rounded-lg
                bg-gradient-to-br
                from-cyan-400/10
                to-violet-500/10
                text-cyan-300
              "
            >
              <User size={14} />
            </div>

            <div className="leading-none">
              <p className="text-[10px] font-bold text-slate-200">
                Operator
              </p>

              <p className="mt-1 font-mono text-[7px] text-slate-600">
                AUTHENTICATED
              </p>
            </div>
          </div>

          {/* LOGOUT */}
          <button
            type="button"
            onClick={handleLogout}
            className="
              flex
              h-10
              w-10
              items-center
              justify-center
              rounded-xl
              border
              border-white/[0.08]
              bg-white/[0.03]
              text-slate-400
              transition-all
              duration-300
              hover:border-red-400/20
              hover:bg-red-400/[0.06]
              hover:text-red-300
            "
            aria-label="Logout"
            title="Logout"
          >
            <LogOut size={16} />
          </button>

        </div>

      </div>
    </nav>
  );
}