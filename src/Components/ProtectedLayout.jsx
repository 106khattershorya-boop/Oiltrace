import React, { useState } from "react";
import { Navigate, Outlet } from "react-router-dom";

import Navbar from "./Navbar";
import Sidebar from "./Sidebar";
import Chatbot from "./Chatbot";

export default function ProtectedLayout() {
  const isLoggedIn =
    localStorage.getItem("isLoggedIn") === "true";

  const [sidebarOpen, setSidebarOpen] = useState(false);

  if (!isLoggedIn) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen w-full bg-[#020617] text-white">

      {/* NAVBAR */}
      <Navbar
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
      />

      {/* DESKTOP SIDEBAR */}
      <aside
        className="
          fixed
          left-0
          top-16
          z-40
          hidden
          h-[calc(100vh-4rem)]
          w-64
          lg:block
        "
      >
        <Sidebar />
      </aside>

      {/* MOBILE OVERLAY */}
      {sidebarOpen && (
        <button
          type="button"
          aria-label="Close sidebar"
          className="
            fixed
            inset-0
            z-[70]
            cursor-default
            bg-black/70
            backdrop-blur-sm
            lg:hidden
          "
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* MOBILE SIDEBAR */}
      <aside
        className={`
          fixed
          left-0
          top-16
          z-[80]
          h-[calc(100vh-4rem)]
          w-72
          transition-transform
          duration-300
          ease-in-out
          lg:hidden
          ${
            sidebarOpen
              ? "translate-x-0"
              : "-translate-x-full"
          }
        `}
      >
        <Sidebar
          closeSidebar={() => setSidebarOpen(false)}
        />
      </aside>

      {/* MAIN */}
      <main
        className="
          min-h-screen
          w-full
          pt-16
          lg:ml-64
          lg:w-[calc(100%-16rem)]
        "
      >
        <div
          className="
            min-h-[calc(100vh-4rem)]
            w-full
            min-w-0
            px-4
            py-5
            sm:px-6
            sm:py-6
            lg:px-8
            lg:py-7
            xl:px-10
          "
        >
          <Outlet />
        </div>
      </main>

      {/* CHATBOT */}
      <Chatbot />

    </div>
  );
}