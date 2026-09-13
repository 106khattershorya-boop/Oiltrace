import React, { useEffect } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import ProtectedLayout from "./Components/ProtectedLayout";

// Authentication
import Login from "./pages/Login";
import ForgotPassword from "./pages/ForgotPassword";

// Main Dashboard
import Dashboard from "./pages/Dashboard";

// Analysis
import NewAnalysis from "./pages/NewAnalysis";
import SpillAnalysis from "./pages/SpillAnalysis";
import DriftPrediction from "./pages/DriftPrediction";
import VesselAttribution from "./pages/VesselAttribution";

// Intelligence
import History from "./pages/History";
import Analytics from "./pages/Analytics";

// Reports
import Reports from "./Pages/Reports";
import ReportPreview from "./Pages/ReportPreview";

// Other
import Settings from "./pages/Settings";
import Help from "./pages/Help";

// Storage
import { seedDemoData } from "./utils/storage";


// ======================================================
// 404 PAGE
// ======================================================

function NotFound() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#020617] px-6 text-white">

      <div className="text-center">

        <div
          className="
            mb-4
            text-7xl
            font-black
            bg-gradient-to-r
            from-cyan-400
            via-blue-500
            to-violet-500
            bg-clip-text
            text-transparent
          "
        >
          404
        </div>

        <h1 className="text-2xl font-bold">
          Signal Lost
        </h1>

        <p className="mt-2 text-sm text-slate-400">
          The requested OILTRACE intelligence node
          could not be located.
        </p>

        <button
          type="button"
          onClick={() =>
            (window.location.href = "/dashboard")
          }
          className="
            mt-6
            inline-flex
            items-center
            rounded-xl
            bg-gradient-to-r
            from-cyan-500
            via-blue-600
            to-violet-600
            px-6
            py-3
            text-sm
            font-semibold
            transition-all
            duration-300
            hover:scale-105
            hover:shadow-[0_0_30px_rgba(34,211,238,0.2)]
          "
        >
          Return to Command Center
        </button>

      </div>

    </div>
  );
}


// ======================================================
// APP
// ======================================================

export default function App() {

  // ----------------------------------------------------
  // Initialize demo/local storage data
  // ----------------------------------------------------

  useEffect(() => {
    try {
      seedDemoData();
    } catch (error) {
      console.error(
        "OILTRACE demo data initialization failed:",
        error
      );
    }
  }, []);


  return (
    <BrowserRouter>

      <Routes>

        {/* =================================================
            AUTHENTICATION ROUTES
        ================================================= */}

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/forgot-password"
          element={<ForgotPassword />}
        />


        {/* =================================================
            PROTECTED APPLICATION ROUTES

            ProtectedLayout handles:
            - Navbar
            - Sidebar
            - Mobile hamburger
            - Chatbot
            - Authentication check
            - Main page layout
        ================================================= */}

        <Route
          element={<ProtectedLayout />}
        >

          {/* ===============================================
              COMMAND CENTER
          =============================================== */}

          <Route
            path="/dashboard"
            element={<Dashboard />}
          />


          {/* ===============================================
              ANALYSIS
          =============================================== */}

          <Route
            path="/analysis/new"
            element={<NewAnalysis />}
          />

          <Route
            path="/analysis/spill"
            element={<SpillAnalysis />}
          />

          <Route
            path="/analysis/drift"
            element={<DriftPrediction />}
          />

          <Route
            path="/analysis/vessels"
            element={<VesselAttribution />}
          />


          {/* ===============================================
              INTELLIGENCE
          =============================================== */}

          <Route
            path="/history"
            element={<History />}
          />

          <Route
            path="/analytics"
            element={<Analytics />}
          />


          {/* ===============================================
              REPORTS
          =============================================== */}

          <Route
            path="/reports"
            element={<Reports />}
          />

          <Route
            path="/reports/view/:id"
            element={<ReportPreview />}
          />


          {/* ===============================================
              SETTINGS & HELP
          =============================================== */}

          <Route
            path="/settings"
            element={<Settings />}
          />

          <Route
            path="/help"
            element={<Help />}
          />

        </Route>


        {/* =================================================
            ROOT ROUTE
        ================================================= */}

        <Route
          path="/"
          element={
            <Navigate
              to="/dashboard"
              replace
            />
          }
        />


        {/* =================================================
            404
        ================================================= */}

        <Route
          path="*"
          element={<NotFound />}
        />

      </Routes>

    </BrowserRouter>
  );
}