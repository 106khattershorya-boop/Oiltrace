import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  ArrowRight,
  Mail,
  Lock,
  Eye,
  EyeOff,
  ShieldCheck,
  Satellite,
  CheckCircle2,
  AlertCircle,
  KeyRound,
} from "lucide-react";

const AUTH_EMAIL = "email-oiltrace@gmail.com";

export default function ForgotPassword() {
  const navigate = useNavigate();

  const [step, setStep] = useState(1);

  const [email, setEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] =
    useState("");

  const [showPassword, setShowPassword] =
    useState(false);

  const [showConfirmPassword, setShowConfirmPassword] =
    useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [loading, setLoading] = useState(false);

  // ==========================================
  // STEP 1 - VERIFY EMAIL
  // ==========================================

  const handleVerifyEmail = (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    const enteredEmail =
      email.trim().toLowerCase();

    if (!enteredEmail) {
      setError("Please enter your email address.");
      return;
    }

    if (enteredEmail !== AUTH_EMAIL) {
      setError(
        "This email is not registered with OILTRACE."
      );
      return;
    }

    setLoading(true);

    setTimeout(() => {
      setLoading(false);
      setStep(2);
    }, 700);
  };

  // ==========================================
  // STEP 2 - RESET PASSWORD
  // ==========================================

  const handleResetPassword = (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    if (!newPassword || !confirmPassword) {
      setError("Please fill in both password fields.");
      return;
    }

    if (newPassword.length < 8) {
      setError(
        "Password must contain at least 8 characters."
      );
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    setTimeout(() => {

      // Save the new password.
      // Login.jsx reads exactly this same key.
      localStorage.setItem(
        "oiltracePassword",
        newPassword
      );

      // Make sure user is logged out after password reset.
      localStorage.removeItem("isLoggedIn");

      setLoading(false);
      setSuccess(
        "Password updated successfully."
      );

      setStep(3);

    }, 800);
  };

  // ==========================================
  // STEP 3 - GO TO LOGIN
  // ==========================================

  const handleContinueToLogin = () => {
    navigate("/login", { replace: true });
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#020617] text-white">

      {/* ================= BACKGROUND ================= */}

      <div className="pointer-events-none absolute inset-0">

        <div
          className="
            absolute inset-0 opacity-[0.07]
            [background-image:linear-gradient(rgba(56,189,248,0.35)_1px,transparent_1px),linear-gradient(90deg,rgba(56,189,248,0.35)_1px,transparent_1px)]
            [background-size:60px_60px]
          "
        />

        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.15, 0.25, 0.15],
          }}
          transition={{
            duration: 7,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="
            absolute
            -left-40
            -top-40
            h-[500px]
            w-[500px]
            rounded-full
            bg-cyan-500/20
            blur-[120px]
          "
        />

        <motion.div
          animate={{
            scale: [1, 1.25, 1],
            opacity: [0.12, 0.22, 0.12],
          }}
          transition={{
            duration: 9,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="
            absolute
            -bottom-40
            -right-40
            h-[550px]
            w-[550px]
            rounded-full
            bg-violet-600/20
            blur-[130px]
          "
        />

        <motion.div
          animate={{
            y: ["-100%", "100vh"],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "linear",
          }}
          className="
            absolute
            left-0
            right-0
            h-px
            bg-gradient-to-r
            from-transparent
            via-cyan-400/30
            to-transparent
          "
        />

      </div>

      {/* ================= MAIN ================= */}

      <div className="relative z-10 flex min-h-screen items-center justify-center px-5 py-10">

        <motion.div
          initial={{
            opacity: 0,
            y: 25,
            scale: 0.97,
          }}
          animate={{
            opacity: 1,
            y: 0,
            scale: 1,
          }}
          transition={{ duration: 0.6 }}
          className="w-full max-w-md"
        >

          {/* BACK TO LOGIN */}

          <button
            type="button"
            onClick={() => navigate("/login")}
            className="
              mb-6
              flex
              items-center
              gap-2
              text-sm
              font-semibold
              text-slate-400
              transition-colors
              hover:text-cyan-300
            "
          >
            <ArrowLeft size={17} />
            Back to Login
          </button>

          {/* BRAND */}

          <div className="mb-7 text-center">

            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{
                type: "spring",
                stiffness: 180,
              }}
              className="
                mx-auto
                mb-5
                flex
                h-16
                w-16
                items-center
                justify-center
                rounded-2xl
                border
                border-cyan-400/20
                bg-cyan-400/[0.08]
                shadow-[0_0_45px_rgba(34,211,238,0.15)]
              "
            >
              <Satellite
                size={31}
                className="text-cyan-300"
              />
            </motion.div>

            <h1
              className="
                text-4xl
                font-black
                tracking-tight
                bg-gradient-to-r
                from-cyan-300
                via-blue-400
                to-violet-400
                bg-clip-text
                text-transparent
              "
            >
              OILTRACE
            </h1>

            <p className="mt-2 text-sm text-slate-400">
              Account Recovery
            </p>

          </div>

          {/* ================= CARD ================= */}

          <div
            className="
              rounded-3xl
              border
              border-white/[0.09]
              bg-[#06101d]/90
              p-6
              shadow-[0_30px_100px_rgba(0,0,0,0.45)]
              backdrop-blur-2xl
              sm:p-8
            "
          >

            {/* ================= PROGRESS ================= */}

            <div className="mb-8 flex items-center">

              <div className="flex items-center">

                <div
                  className={`
                    flex
                    h-9
                    w-9
                    items-center
                    justify-center
                    rounded-full
                    text-xs
                    font-bold
                    transition-all
                    duration-300
                    ${
                      step >= 1
                        ? "bg-cyan-500 text-white shadow-[0_0_20px_rgba(34,211,238,0.25)]"
                        : "bg-white/[0.06] text-slate-500"
                    }
                  `}
                >
                  {step > 1 ? (
                    <CheckCircle2 size={17} />
                  ) : (
                    "1"
                  )}
                </div>

              </div>

              <div
                className={`
                  mx-2
                  h-px
                  flex-1
                  transition-all
                  duration-500
                  ${
                    step >= 2
                      ? "bg-cyan-400/50"
                      : "bg-white/[0.08]"
                  }
                `}
              />

              <div
                className={`
                  flex
                  h-9
                  w-9
                  items-center
                  justify-center
                  rounded-full
                  text-xs
                  font-bold
                  transition-all
                  duration-300
                  ${
                    step >= 2
                      ? "bg-cyan-500 text-white shadow-[0_0_20px_rgba(34,211,238,0.25)]"
                      : "bg-white/[0.06] text-slate-500"
                  }
                `}
              >
                {step > 2 ? (
                  <CheckCircle2 size={17} />
                ) : (
                  "2"
                )}
              </div>

              <div
                className={`
                  mx-2
                  h-px
                  flex-1
                  transition-all
                  duration-500
                  ${
                    step >= 3
                      ? "bg-cyan-400/50"
                      : "bg-white/[0.08]"
                  }
                `}
              />

              <div
                className={`
                  flex
                  h-9
                  w-9
                  items-center
                  justify-center
                  rounded-full
                  text-xs
                  font-bold
                  transition-all
                  duration-300
                  ${
                    step >= 3
                      ? "bg-emerald-500 text-white shadow-[0_0_20px_rgba(16,185,129,0.25)]"
                      : "bg-white/[0.06] text-slate-500"
                  }
                `}
              >
                <CheckCircle2
                  size={17}
                  className={
                    step >= 3
                      ? ""
                      : "opacity-30"
                  }
                />
              </div>

            </div>

            {/* ================= ERROR ================= */}

            {error && (
              <motion.div
                initial={{
                  opacity: 0,
                  y: -8,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                }}
                className="
                  mb-5
                  flex
                  items-center
                  gap-3
                  rounded-xl
                  border
                  border-red-400/20
                  bg-red-500/[0.08]
                  px-4
                  py-3
                  text-sm
                  text-red-300
                "
              >
                <AlertCircle size={18} />
                <span>{error}</span>
              </motion.div>
            )}

            {/* ================= STEP 1 ================= */}

            {step === 1 && (
              <motion.div
                initial={{
                  opacity: 0,
                  x: -15,
                }}
                animate={{
                  opacity: 1,
                  x: 0,
                }}
              >

                <div className="mb-6">

                  <div
                    className="
                      mb-4
                      flex
                      h-11
                      w-11
                      items-center
                      justify-center
                      rounded-xl
                      bg-cyan-400/[0.08]
                      text-cyan-400
                    "
                  >
                    <Mail size={21} />
                  </div>

                  <h2 className="text-xl font-bold">
                    Verify your email
                  </h2>

                  <p className="mt-2 text-sm leading-6 text-slate-400">
                    Enter your registered OILTRACE email
                    address to continue with password
                    recovery.
                  </p>

                </div>

                <form
                  onSubmit={handleVerifyEmail}
                  className="space-y-5"
                >

                  <div>

                    <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-400">
                      Registered Email
                    </label>

                    <div className="relative">

                      <Mail
                        size={18}
                        className="
                          absolute
                          left-4
                          top-1/2
                          -translate-y-1/2
                          text-slate-500
                        "
                      />

                      <input
                        type="email"
                        value={email}
                        onChange={(e) => {
                          setEmail(e.target.value);
                          setError("");
                        }}
                        placeholder="Enter your email"
                        autoComplete="email"
                        className="
                          w-full
                          rounded-xl
                          border
                          border-white/[0.09]
                          bg-[#030914]
                          py-3.5
                          pl-11
                          pr-4
                          text-sm
                          text-white
                          outline-none
                          placeholder:text-slate-600
                          transition-all
                          duration-300
                          hover:border-cyan-400/20
                          focus:border-cyan-400/40
                          focus:ring-2
                          focus:ring-cyan-400/10
                        "
                      />

                    </div>

                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="
                      flex
                      w-full
                      items-center
                      justify-center
                      gap-3
                      rounded-xl
                      bg-gradient-to-r
                      from-cyan-500
                      via-blue-600
                      to-violet-600
                      px-5
                      py-3.5
                      text-sm
                      font-bold
                      text-white
                      shadow-[0_12px_35px_rgba(37,99,235,0.25)]
                      transition-all
                      duration-300
                      hover:scale-[1.01]
                      hover:shadow-[0_15px_45px_rgba(34,211,238,0.2)]
                      disabled:cursor-not-allowed
                      disabled:opacity-70
                    "
                  >
                    {loading ? (
                      <>
                        <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                        Verifying...
                      </>
                    ) : (
                      <>
                        Continue
                        <ArrowRight size={18} />
                      </>
                    )}
                  </button>

                </form>

              </motion.div>
            )}

            {/* ================= STEP 2 ================= */}

            {step === 2 && (
              <motion.div
                initial={{
                  opacity: 0,
                  x: 15,
                }}
                animate={{
                  opacity: 1,
                  x: 0,
                }}
              >

                <div className="mb-6">

                  <div
                    className="
                      mb-4
                      flex
                      h-11
                      w-11
                      items-center
                      justify-center
                      rounded-xl
                      bg-violet-400/[0.08]
                      text-violet-400
                    "
                  >
                    <KeyRound size={21} />
                  </div>

                  <h2 className="text-xl font-bold">
                    Create new password
                  </h2>

                  <p className="mt-2 text-sm leading-6 text-slate-400">
                    Create a new password for your OILTRACE
                    account.
                  </p>

                </div>

                <form
                  onSubmit={handleResetPassword}
                  className="space-y-5"
                >

                  {/* NEW PASSWORD */}

                  <div>

                    <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-400">
                      New Password
                    </label>

                    <div className="relative">

                      <Lock
                        size={18}
                        className="
                          absolute
                          left-4
                          top-1/2
                          -translate-y-1/2
                          text-slate-500
                        "
                      />

                      <input
                        type={
                          showPassword
                            ? "text"
                            : "password"
                        }
                        value={newPassword}
                        onChange={(e) => {
                          setNewPassword(
                            e.target.value
                          );
                          setError("");
                        }}
                        placeholder="Minimum 8 characters"
                        autoComplete="new-password"
                        className="
                          w-full
                          rounded-xl
                          border
                          border-white/[0.09]
                          bg-[#030914]
                          py-3.5
                          pl-11
                          pr-12
                          text-sm
                          text-white
                          outline-none
                          placeholder:text-slate-600
                          transition-all
                          duration-300
                          focus:border-cyan-400/40
                          focus:ring-2
                          focus:ring-cyan-400/10
                        "
                      />

                      <button
                        type="button"
                        onClick={() =>
                          setShowPassword(
                            (prev) => !prev
                          )
                        }
                        className="
                          absolute
                          right-3
                          top-1/2
                          flex
                          h-9
                          w-9
                          -translate-y-1/2
                          items-center
                          justify-center
                          rounded-lg
                          text-slate-500
                          hover:text-slate-300
                        "
                      >
                        {showPassword ? (
                          <EyeOff size={18} />
                        ) : (
                          <Eye size={18} />
                        )}
                      </button>

                    </div>

                  </div>

                  {/* CONFIRM PASSWORD */}

                  <div>

                    <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-400">
                      Confirm Password
                    </label>

                    <div className="relative">

                      <Lock
                        size={18}
                        className="
                          absolute
                          left-4
                          top-1/2
                          -translate-y-1/2
                          text-slate-500
                        "
                      />

                      <input
                        type={
                          showConfirmPassword
                            ? "text"
                            : "password"
                        }
                        value={confirmPassword}
                        onChange={(e) => {
                          setConfirmPassword(
                            e.target.value
                          );
                          setError("");
                        }}
                        placeholder="Re-enter your password"
                        autoComplete="new-password"
                        className="
                          w-full
                          rounded-xl
                          border
                          border-white/[0.09]
                          bg-[#030914]
                          py-3.5
                          pl-11
                          pr-12
                          text-sm
                          text-white
                          outline-none
                          placeholder:text-slate-600
                          transition-all
                          duration-300
                          focus:border-cyan-400/40
                          focus:ring-2
                          focus:ring-cyan-400/10
                        "
                      />

                      <button
                        type="button"
                        onClick={() =>
                          setShowConfirmPassword(
                            (prev) => !prev
                          )
                        }
                        className="
                          absolute
                          right-3
                          top-1/2
                          flex
                          h-9
                          w-9
                          -translate-y-1/2
                          items-center
                          justify-center
                          rounded-lg
                          text-slate-500
                          hover:text-slate-300
                        "
                      >
                        {showConfirmPassword ? (
                          <EyeOff size={18} />
                        ) : (
                          <Eye size={18} />
                        )}
                      </button>

                    </div>

                  </div>

                  {/* RESET BUTTON */}

                  <button
                    type="submit"
                    disabled={loading}
                    className="
                      flex
                      w-full
                      items-center
                      justify-center
                      gap-3
                      rounded-xl
                      bg-gradient-to-r
                      from-cyan-500
                      via-blue-600
                      to-violet-600
                      px-5
                      py-3.5
                      text-sm
                      font-bold
                      text-white
                      shadow-[0_12px_35px_rgba(37,99,235,0.25)]
                      transition-all
                      duration-300
                      hover:scale-[1.01]
                      disabled:cursor-not-allowed
                      disabled:opacity-70
                    "
                  >

                    {loading ? (
                      <>
                        <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                        Updating Password...
                      </>
                    ) : (
                      <>
                        Update Password
                        <ArrowRight size={18} />
                      </>
                    )}

                  </button>

                </form>

              </motion.div>
            )}

            {/* ================= STEP 3 ================= */}

            {step === 3 && (
              <motion.div
                initial={{
                  opacity: 0,
                  scale: 0.95,
                }}
                animate={{
                  opacity: 1,
                  scale: 1,
                }}
                className="text-center"
              >

                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{
                    type: "spring",
                    stiffness: 180,
                  }}
                  className="
                    mx-auto
                    mb-5
                    flex
                    h-16
                    w-16
                    items-center
                    justify-center
                    rounded-full
                    bg-emerald-400/[0.1]
                    text-emerald-400
                    shadow-[0_0_35px_rgba(16,185,129,0.15)]
                  "
                >
                  <CheckCircle2 size={34} />
                </motion.div>

                <h2 className="text-2xl font-bold">
                  Password Updated
                </h2>

                <p className="mx-auto mt-3 max-w-sm text-sm leading-6 text-slate-400">
                  {success ||
                    "Your OILTRACE password has been updated successfully."}
                </p>

                <div
                  className="
                    mt-6
                    rounded-xl
                    border
                    border-emerald-400/10
                    bg-emerald-400/[0.05]
                    px-4
                    py-3
                    text-xs
                    text-emerald-300
                  "
                >
                  You can now sign in using your new
                  password.
                </div>

                <button
                  type="button"
                  onClick={handleContinueToLogin}
                  className="
                    mt-6
                    flex
                    w-full
                    items-center
                    justify-center
                    gap-3
                    rounded-xl
                    bg-gradient-to-r
                    from-cyan-500
                    via-blue-600
                    to-violet-600
                    px-5
                    py-3.5
                    text-sm
                    font-bold
                    text-white
                    shadow-[0_12px_35px_rgba(37,99,235,0.25)]
                    transition-all
                    duration-300
                    hover:scale-[1.01]
                  "
                >
                  Continue to Login
                  <ArrowRight size={18} />
                </button>

              </motion.div>
            )}

            {/* SECURITY */}

            <div className="mt-7 border-t border-white/[0.07] pt-5">

              <div className="flex items-center gap-3">

                <div
                  className="
                    flex
                    h-9
                    w-9
                    items-center
                    justify-center
                    rounded-lg
                    bg-emerald-400/[0.08]
                    text-emerald-400
                  "
                >
                  <ShieldCheck size={18} />
                </div>

                <div>

                  <p className="text-xs font-semibold text-slate-300">
                    Secure Recovery
                  </p>

                  <p className="text-[11px] text-slate-500">
                    OILTRACE account security protocol
                  </p>

                </div>

              </div>

            </div>

          </div>

          <p className="mt-6 text-center text-[10px] tracking-wide text-slate-600">
            OILTRACE • Maritime Intelligence & Oil Spill Attribution
          </p>

        </motion.div>

      </div>
    </div>
  );
}