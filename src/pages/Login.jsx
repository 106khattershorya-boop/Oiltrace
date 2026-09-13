
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Satellite,
  Lock,
  Mail,
  ArrowRight,
  ShieldCheck,
  Radar,
  Eye,
  EyeOff,
  Radio,
  Waves,
  Globe2,
  ScanLine,
  Activity,
  Crosshair,
  Ship,
  Sparkles,
  KeyRound,
} from "lucide-react";
import { motion } from "framer-motion";

const Login = () => {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [time, setTime] = useState(new Date());

  // =========================================================
  // FIXED LOGIN CREDENTIALS
  // =========================================================

  const FIXED_EMAIL = "oiltrace@gmail.com";
  const FIXED_PASSWORD = "oiltrace@123";

  useEffect(() => {
    const timer = setInterval(() => {
      setTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // =========================================================
  // LOGIN FUNCTION
  // =========================================================

  const handleLogin = (e) => {
    e.preventDefault();

    setError("");

    const enteredEmail = email.trim().toLowerCase();
    const enteredPassword = password;

    // Empty fields
    if (!enteredEmail || !enteredPassword) {
      setError("Please enter email and password.");
      return;
    }

    // Check fixed email
    if (enteredEmail !== FIXED_EMAIL) {
      setError("Invalid email or password.");
      return;
    }

    // Check fixed password
    if (enteredPassword !== FIXED_PASSWORD) {
      setError("Invalid email or password.");
      return;
    }

    // Correct credentials
    setLoading(true);

    localStorage.setItem("isLoggedIn", "true");
    localStorage.setItem("oiltrace_token", "demo-token");
    localStorage.setItem("oiltraceUser", FIXED_EMAIL);

    setTimeout(() => {
      navigate("/dashboard", { replace: true });
    }, 900);
  };

  const formatTime = () => {
    return time.toLocaleTimeString("en-IN", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#020617] text-white">

      {/* =========================================================
          ANIMATED BACKGROUND
      ========================================================= */}

      <div className="pointer-events-none absolute inset-0">

        {/* Atmospheric glows */}

        <motion.div
          className="absolute -left-40 -top-40 h-[550px] w-[550px] rounded-full bg-cyan-500/[0.14] blur-[120px]"
          animate={{
            x: [0, 60, 0],
            y: [0, 40, 0],
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />

        <motion.div
          className="absolute -right-40 top-10 h-[550px] w-[550px] rounded-full bg-violet-600/[0.14] blur-[130px]"
          animate={{
            x: [0, -70, 0],
            y: [0, 50, 0],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />

        <motion.div
          className="absolute bottom-[-250px] left-[30%] h-[650px] w-[650px] rounded-full bg-blue-600/[0.12] blur-[150px]"
          animate={{
            scale: [1, 1.15, 1],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />

        {/* DARK TECH GRID */}

        <div
          className="absolute inset-0 opacity-[0.13]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(34,211,238,0.45) 1px, transparent 1px),
              linear-gradient(90deg, rgba(34,211,238,0.45) 1px, transparent 1px)
            `,
            backgroundSize: "65px 65px",
          }}
        />

        {/* OILTRACE WATERMARK */}

        <div className="absolute inset-0 flex items-center justify-center overflow-hidden">
          <motion.div
            className="select-none whitespace-nowrap text-[14vw] font-black tracking-[0.16em] text-cyan-300/[0.055]"
            animate={{
              x: [-25, 25, -25],
              scale: [1, 1.025, 1],
            }}
            transition={{
              duration: 18,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          >
            OILTRACE
          </motion.div>
        </div>

        {/* =====================================================
            RADAR
        ===================================================== */}

        <div className="absolute left-[7%] top-[17%] hidden h-[300px] w-[300px] md:block">

          <motion.div
            className="absolute inset-0 rounded-full border border-cyan-300/[0.18]"
            animate={{ rotate: 360 }}
            transition={{
              duration: 35,
              repeat: Infinity,
              ease: "linear",
            }}
          />

          <div className="absolute inset-[12%] rounded-full border border-cyan-300/[0.16]" />
          <div className="absolute inset-[25%] rounded-full border border-cyan-300/[0.14]" />
          <div className="absolute inset-[38%] rounded-full border border-cyan-300/[0.12]" />

          <div className="absolute left-1/2 top-0 h-full w-px bg-cyan-300/[0.13]" />
          <div className="absolute left-0 top-1/2 h-px w-full bg-cyan-300/[0.13]" />

          <motion.div
            className="absolute left-1/2 top-1/2 h-1/2 w-[3px] origin-bottom bg-gradient-to-t from-cyan-300/80 to-transparent"
            animate={{ rotate: 360 }}
            transition={{
              duration: 5,
              repeat: Infinity,
              ease: "linear",
            }}
          />

          <motion.div
            className="absolute left-1/2 top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-300 shadow-[0_0_25px_rgba(34,211,238,0.95)]"
            animate={{
              scale: [1, 1.5, 1],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
            }}
          />

          <motion.div
            className="absolute left-[28%] top-[35%] h-2.5 w-2.5 rounded-full bg-emerald-400 shadow-[0_0_18px_rgba(52,211,153,0.9)]"
            animate={{
              opacity: [0.25, 1, 0.25],
              scale: [0.8, 1.3, 0.8],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
            }}
          />

          <motion.div
            className="absolute right-[25%] top-[28%] h-2 w-2 rounded-full bg-cyan-300 shadow-[0_0_15px_rgba(34,211,238,0.8)]"
            animate={{
              opacity: [0.15, 1, 0.15],
            }}
            transition={{
              duration: 1.7,
              repeat: Infinity,
            }}
          />

          <motion.div
            className="absolute bottom-[25%] left-[35%] h-2 w-2 rounded-full bg-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.8)]"
            animate={{
              opacity: [0.15, 1, 0.15],
            }}
            transition={{
              duration: 2.4,
              repeat: Infinity,
            }}
          />

          <div className="absolute -bottom-7 left-1/2 -translate-x-1/2 whitespace-nowrap text-[9px] font-semibold tracking-[0.35em] text-cyan-300/[0.45]">
            MARITIME RADAR
          </div>
        </div>

        {/* =====================================================
            SATELLITE
        ===================================================== */}

        <motion.div
          className="absolute right-[7%] top-[12%] hidden md:block"
          animate={{
            y: [0, -18, 0],
            rotateZ: [-2, 2, -2],
          }}
          transition={{
            duration: 7,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          <div className="relative h-40 w-56">

            <div className="absolute left-1/2 top-1/2 h-28 w-28 -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-400/[0.08] blur-2xl" />

            <motion.div
              className="absolute left-1/2 top-1/2 flex h-16 w-20 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-xl border border-cyan-300/[0.55] bg-cyan-400/[0.12] shadow-[0_0_45px_rgba(34,211,238,0.18)]"
              animate={{
                rotateY: [0, 360],
              }}
              transition={{
                duration: 14,
                repeat: Infinity,
                ease: "linear",
              }}
            >
              <Satellite className="h-8 w-8 text-cyan-300/[0.85]" />
            </motion.div>

            <motion.div
              className="absolute left-0 top-1/2 h-12 w-14 -translate-y-1/2 border border-blue-400/[0.45] bg-blue-500/[0.10]"
              animate={{
                rotateY: [0, 360],
              }}
              transition={{
                duration: 14,
                repeat: Infinity,
                ease: "linear",
              }}
            />

            <motion.div
              className="absolute right-0 top-1/2 h-12 w-14 -translate-y-1/2 border border-blue-400/[0.45] bg-blue-500/[0.10]"
              animate={{
                rotateY: [0, 360],
              }}
              transition={{
                duration: 14,
                repeat: Infinity,
                ease: "linear",
              }}
            />

            <motion.div
              className="absolute left-1/2 top-[78%] h-10 w-28 -translate-x-1/2 rounded-full border border-cyan-300/[0.35]"
              animate={{
                scale: [0.7, 1.5],
                opacity: [0.6, 0],
              }}
              transition={{
                duration: 2.5,
                repeat: Infinity,
              }}
            />
          </div>
        </motion.div>

        {/* =====================================================
            SHIP
        ===================================================== */}

        <motion.div
          className="absolute bottom-[15%] left-[6%] hidden md:block"
          animate={{
            x: [-20, 35, -20],
          }}
          transition={{
            duration: 16,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          <div className="opacity-[0.18]">
            <Ship className="h-32 w-32 text-cyan-300" />
          </div>

          <motion.div
            className="absolute -bottom-5 left-[-30px] h-5 w-48 rounded-full border-t border-cyan-400/[0.35]"
            animate={{
              scaleX: [0.8, 1.2, 0.8],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
            }}
          />
        </motion.div>

        {/* =====================================================
            OCEAN WAVES
        ===================================================== */}

        <div className="absolute bottom-0 left-0 right-0 h-40 overflow-hidden">

          <motion.div
            className="absolute bottom-0 h-32 w-[120%] rounded-[50%] border-t border-cyan-300/[0.18]"
            animate={{
              x: ["-5%", "5%", "-5%"],
            }}
            transition={{
              duration: 10,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />

          <motion.div
            className="absolute bottom-[-20px] h-32 w-[120%] rounded-[50%] border-t border-blue-300/[0.14]"
            animate={{
              x: ["5%", "-5%", "5%"],
            }}
            transition={{
              duration: 13,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        </div>

        {/* =====================================================
            DATA PARTICLES
        ===================================================== */}

        {[
          ["18%", "72%"],
          ["27%", "27%"],
          ["73%", "76%"],
          ["82%", "48%"],
          ["62%", "17%"],
          ["90%", "82%"],
          ["12%", "42%"],
        ].map((position, index) => (
          <motion.div
            key={index}
            className="absolute h-1.5 w-1.5 rounded-full bg-cyan-300 shadow-[0_0_12px_rgba(34,211,238,0.8)]"
            style={{
              left: position[0],
              top: position[1],
            }}
            animate={{
              y: [-10, 10, -10],
              opacity: [0.2, 0.9, 0.2],
              scale: [0.7, 1.4, 0.7],
            }}
            transition={{
              duration: 3 + index * 0.4,
              delay: index * 0.3,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        ))}

        {/* Scan line */}

        <motion.div
          className="absolute left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-300/30 to-transparent"
          animate={{
            top: ["0%", "100%"],
          }}
          transition={{
            duration: 9,
            repeat: Infinity,
            ease: "linear",
          }}
        />
      </div>

      {/* =========================================================
          TOP NAV
      ========================================================= */}

      <div className="relative z-20 flex items-center justify-between px-6 py-5 md:px-10">

        <motion.div
          className="flex items-center gap-3"
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <div className="relative flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-400/30 bg-cyan-400/10">

            <Radar className="h-5 w-5 text-cyan-300" />

            <motion.div
              className="absolute inset-0 rounded-xl border border-cyan-400/30"
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.7, 0, 0.7],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
              }}
            />
          </div>

          <div>
            <div className="text-lg font-black tracking-[0.25em]">
              OILTRACE
            </div>

            <div className="text-[8px] tracking-[0.3em] text-cyan-300/50">
              MARITIME INTELLIGENCE
            </div>
          </div>
        </motion.div>

        <motion.div
          className="hidden items-center gap-3 text-[10px] tracking-[0.2em] text-slate-500 sm:flex"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <Activity className="h-3.5 w-3.5 text-emerald-400" />
          SYSTEM OPERATIONAL
          <span className="text-slate-700">|</span>
          {formatTime()} IST
        </motion.div>
      </div>

      {/* =========================================================
          LOGIN
      ========================================================= */}

      <div className="relative z-10 flex min-h-[calc(100vh-90px)] items-center justify-center px-5 pb-10">

        <motion.div
          initial={{
            opacity: 0,
            y: 35,
            scale: 0.96,
          }}
          animate={{
            opacity: 1,
            y: 0,
            scale: 1,
          }}
          transition={{
            duration: 0.8,
            ease: "easeOut",
          }}
          className="w-full max-w-md"
        >

          {/* Label */}

          <div className="mb-4 flex items-center justify-center gap-3 text-[9px] tracking-[0.3em] text-cyan-400/60">
            <span className="h-px w-12 bg-cyan-400/30" />
            SECURE COMMAND ACCESS
            <span className="h-px w-12 bg-cyan-400/30" />
          </div>

          {/* Login card */}

          <div className="relative overflow-hidden rounded-3xl border border-white/[0.12] bg-slate-950/75 p-7 shadow-2xl shadow-black/50 backdrop-blur-2xl md:p-9">

            <motion.div
              className="pointer-events-none absolute inset-0 rounded-3xl border border-cyan-400/20"
              animate={{
                opacity: [0.25, 0.8, 0.25],
              }}
              transition={{
                duration: 4,
                repeat: Infinity,
              }}
            />

            {/* Corner HUD */}

            <div className="absolute left-0 top-0 h-10 w-10 rounded-tl-3xl border-l border-t border-cyan-400/60" />

            <div className="absolute right-0 top-0 h-10 w-10 rounded-tr-3xl border-r border-t border-violet-400/50" />

            <div className="absolute bottom-0 left-0 h-10 w-10 rounded-bl-3xl border-b border-l border-blue-400/50" />

            <div className="absolute bottom-0 right-0 h-10 w-10 rounded-br-3xl border-b border-r border-cyan-400/50" />

            {/* Header */}

            <div className="relative mb-8 text-center">

              <motion.div
                className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl border border-cyan-400/30 bg-gradient-to-br from-cyan-400/20 to-blue-600/10 shadow-[0_0_40px_rgba(34,211,238,0.15)]"
                animate={{
                  y: [0, -4, 0],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                }}
              >
                <Satellite className="h-7 w-7 text-cyan-300" />
              </motion.div>

              <h1 className="text-3xl font-black tracking-tight">
                Welcome to{" "}
                <span className="bg-gradient-to-r from-cyan-300 via-blue-400 to-violet-400 bg-clip-text text-transparent">
                  OILTRACE
                </span>
              </h1>

              <p className="mt-2 text-sm text-slate-400">
                Maritime Intelligence & Oil Spill Attribution Platform
              </p>
            </div>

            {/* Secure status */}

            <div className="mb-6 flex items-center justify-between rounded-xl border border-white/[0.08] bg-white/[0.035] px-4 py-3">

              <div className="flex items-center gap-2">

                <motion.span
                  className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_12px_rgba(52,211,153,0.8)]"
                  animate={{
                    opacity: [0.4, 1, 0.4],
                  }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                  }}
                />

                <span className="text-[10px] font-semibold tracking-[0.15em] text-slate-400">
                  SECURE CHANNEL
                </span>
              </div>

              <div className="flex items-center gap-1.5 text-[9px] tracking-wider text-cyan-400/70">
                <ShieldCheck className="h-3.5 w-3.5" />
                AES-256
              </div>
            </div>

            {/* FORM */}

            <form onSubmit={handleLogin} className="relative space-y-5">

              {/* EMAIL */}

              <div>

                <label className="mb-2 block text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">
                  Analyst Email
                </label>

                <div className="group relative">

                  <Mail className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500 transition-colors group-focus-within:text-cyan-400" />

                  <input
                    type="email"
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value);
                      setError("");
                    }}
                    placeholder="email-oiltrace@gmail.com"
                    className="w-full rounded-xl border border-white/[0.10] bg-black/30 py-3.5 pl-11 pr-4 text-sm text-white outline-none transition-all placeholder:text-slate-600 focus:border-cyan-400/60 focus:bg-cyan-400/[0.04] focus:ring-2 focus:ring-cyan-400/10"
                  />
                </div>
              </div>

              {/* PASSWORD */}

              <div>

                <div className="mb-2 flex items-center justify-between">

                  <label className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">
                    Access Key
                  </label>

                  <button
                    type="button"
                    onClick={() => navigate("/forgot-password")}
                    className="group flex items-center gap-1.5 text-[10px] font-semibold tracking-wide text-cyan-400/70 transition-colors hover:text-cyan-300"
                  >
                    <KeyRound className="h-3 w-3 transition-transform group-hover:rotate-12" />
                    Forgot Password?
                  </button>

                </div>

                <div className="group relative">

                  <Lock className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500 transition-colors group-focus-within:text-cyan-400" />

                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => {
                      setPassword(e.target.value);
                      setError("");
                    }}
                    placeholder="Enter secure access key"
                    className="w-full rounded-xl border border-white/[0.10] bg-black/30 py-3.5 pl-11 pr-12 text-sm text-white outline-none transition-all placeholder:text-slate-600 focus:border-cyan-400/60 focus:bg-cyan-400/[0.04] focus:ring-2 focus:ring-cyan-400/10"
                  />

                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 transition-colors hover:text-cyan-300"
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>

                </div>
              </div>

              {/* ERROR */}

              {error && (
                <motion.div
                  initial={{
                    opacity: 0,
                    y: -5,
                  }}
                  animate={{
                    opacity: 1,
                    y: 0,
                  }}
                  className="rounded-xl border border-red-500/20 bg-red-500/5 px-4 py-3 text-xs text-red-300"
                >
                  {error}
                </motion.div>
              )}

              {/* LOGIN BUTTON */}

              <motion.button
                type="submit"
                disabled={loading}
                whileHover={{
                  scale: 1.01,
                }}
                whileTap={{
                  scale: 0.98,
                }}
                className="group relative mt-2 flex w-full items-center justify-center gap-3 overflow-hidden rounded-xl bg-gradient-to-r from-cyan-500 via-blue-600 to-violet-600 py-4 text-sm font-bold tracking-wide shadow-lg shadow-blue-900/40 transition-all disabled:cursor-not-allowed disabled:opacity-70"
              >

                {/* Button shine */}

                <motion.div
                  className="absolute inset-y-0 -left-20 w-20 skew-x-[-20deg] bg-white/20 blur-md"
                  animate={{
                    x: ["0%", "650%"],
                  }}
                  transition={{
                    duration: 2.8,
                    repeat: Infinity,
                    repeatDelay: 2,
                  }}
                />

                {loading ? (
                  <>
                    <motion.div
                      className="h-4 w-4 rounded-full border-2 border-white/30 border-t-white"
                      animate={{
                        rotate: 360,
                      }}
                      transition={{
                        duration: 0.8,
                        repeat: Infinity,
                        ease: "linear",
                      }}
                    />

                    INITIALIZING...
                  </>
                ) : (
                  <>
                    ENTER COMMAND CENTER
                    <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                  </>
                )}

              </motion.button>
            </form>

            {/* CARD FOOTER */}

            <div className="mt-7 border-t border-white/[0.07] pt-5">

              <div className="flex items-center justify-between text-[9px] uppercase tracking-[0.15em] text-slate-600">

                <div className="flex items-center gap-2">
                  <Globe2 className="h-3.5 w-3.5" />
                  GLOBAL MARITIME NETWORK
                </div>

                <div className="flex items-center gap-2">
                  <Radio className="h-3.5 w-3.5 text-cyan-400/60" />
                  LIVE
                </div>

              </div>
            </div>
          </div>

          {/* Bottom intelligence bar */}

          <motion.div
            className="mt-5 flex items-center justify-center gap-6 text-[8px] tracking-[0.2em] text-slate-600"
            initial={{
              opacity: 0,
            }}
            animate={{
              opacity: 1,
            }}
            transition={{
              delay: 1.2,
            }}
          >

            <span className="flex items-center gap-1.5">
              <ScanLine className="h-3 w-3 text-cyan-500/50" />
              SATELLITE
            </span>

            <span className="h-1 w-1 rounded-full bg-slate-700" />

            <span className="flex items-center gap-1.5">
              <Waves className="h-3 w-3 text-blue-500/50" />
              OCEAN DATA
            </span>

            <span className="h-1 w-1 rounded-full bg-slate-700" />

            <span className="flex items-center gap-1.5">
              <Crosshair className="h-3 w-3 text-violet-500/50" />
              AIS INTELLIGENCE
            </span>

          </motion.div>
        </motion.div>
      </div>

      {/* Bottom HUD */}

      <div className="pointer-events-none absolute bottom-6 left-6 hidden text-[8px] leading-5 tracking-[0.2em] text-slate-700 md:block">
        <div>OT // SECURE TERMINAL</div>
        <div>LAT // 20.5937 N</div>
        <div>LON // 78.9629 E</div>
      </div>

      <div className="pointer-events-none absolute bottom-6 right-6 hidden text-right text-[8px] leading-5 tracking-[0.2em] text-slate-700 md:block">
        <div>ORBITAL LINK // ACTIVE</div>
        <div>ENCRYPTION // AES-256</div>
        <div>NODE // INDIA-01</div>
      </div>

      <motion.div
        className="pointer-events-none absolute right-[32%] top-[30%] hidden md:block"
        animate={{
          rotate: 360,
          scale: [0.8, 1.2, 0.8],
        }}
        transition={{
          rotate: {
            duration: 8,
            repeat: Infinity,
            ease: "linear",
          },
          scale: {
            duration: 2,
            repeat: Infinity,
          },
        }}
      >
        <Sparkles className="h-4 w-4 text-cyan-400/30" />
      </motion.div>

    </div>
  );
};

export default Login;

