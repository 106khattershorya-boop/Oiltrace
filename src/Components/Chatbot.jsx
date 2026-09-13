import React, {
  useEffect,
  useState,
} from "react";

import {
  Bot,
  Mic,
  Send,
  Sparkles,
  User,
  Volume2,
  X,
} from "lucide-react";

const initialMessages = [
  {
    sender: "bot",
    text:
      "OILTRACE AI online. I can help you navigate spill detection, drift forecasting, AIS correlation and investigation reports.",
  },
];

export default function Chatbot() {

  const [open, setOpen] = useState(false);

  const [messages, setMessages] =
    useState(initialMessages);

  const [input, setInput] =
    useState("");

  useEffect(() => {

    const openChat = () => {
      setOpen(true);
    };

    window.addEventListener(
      "open-oiltrace-chat",
      openChat
    );

    return () => {
      window.removeEventListener(
        "open-oiltrace-chat",
        openChat
      );
    };

  }, []);

  const sendMessage = () => {

    if (!input.trim()) return;

    const text = input.trim();

    setMessages((prev) => [
      ...prev,
      {
        sender: "user",
        text,
      },
      {
        sender: "bot",
        text:
          "I have logged that query. For this prototype, I can guide you through the OILTRACE investigation workflow and explain the intelligence modules.",
      },
    ]);

    setInput("");
  };

  return (
    <>
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className="fixed bottom-6 right-6 z-[100] flex h-14 w-14 items-center justify-center rounded-2xl border border-violet-400/20 bg-gradient-to-br from-cyan-500 to-violet-600 text-white shadow-[0_15px_40px_rgba(139,92,246,.3)] transition hover:scale-105"
        >
          <Sparkles size={22} />

          <span className="absolute inset-0 animate-ping rounded-2xl bg-violet-400/10" />
        </button>
      )}

      {open && (
        <div className="fixed bottom-5 right-5 z-[100] flex h-[540px] w-[360px] flex-col overflow-hidden rounded-3xl border border-white/10 bg-slate-950/95 shadow-2xl backdrop-blur-2xl">

          {/* HEADER */}

          <div className="flex items-center justify-between border-b border-white/[.06] bg-gradient-to-r from-cyan-500/10 to-violet-500/10 px-4 py-4">

            <div className="flex items-center gap-3">

              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-violet-500/10 text-violet-400">
                <Bot size={18} />
              </div>

              <div>

                <p className="text-xs font-bold text-white">
                  OILTRACE AI
                </p>

                <div className="mt-1 flex items-center gap-2">

                  <span className="status-dot" />

                  <span className="text-[9px] text-emerald-400">
                    Online
                  </span>

                </div>

              </div>

            </div>

            <button
              onClick={() => setOpen(false)}
              className="text-slate-500 hover:text-white"
            >
              <X size={18} />
            </button>

          </div>

          {/* MESSAGES */}

          <div className="flex-1 space-y-4 overflow-y-auto p-4">

            {messages.map(
              (message, index) => (
                <div
                  key={index}
                  className={`flex gap-2 ${
                    message.sender === "user"
                      ? "justify-end"
                      : ""
                  }`}
                >

                  {message.sender === "bot" && (
                    <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-violet-500/10 text-violet-400">
                      <Bot size={13} />
                    </div>
                  )}

                  <div
                    className={`max-w-[78%] rounded-2xl px-3 py-2.5 text-[11px] leading-5 ${
                      message.sender === "user"
                        ? "bg-cyan-500/10 text-cyan-100"
                        : "bg-white/[.04] text-slate-300"
                    }`}
                  >
                    {message.text}
                  </div>

                  {message.sender === "user" && (
                    <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-cyan-500/10 text-cyan-400">
                      <User size={13} />
                    </div>
                  )}

                </div>
              )
            )}

          </div>

          {/* INPUT */}

          <div className="border-t border-white/[.06] p-3">

            <div className="flex items-center gap-2">

              <button className="rounded-xl border border-white/10 bg-white/[.03] p-2.5 text-slate-500 hover:text-cyan-400">
                <Mic size={15} />
              </button>

              <input
                value={input}
                onChange={(e) =>
                  setInput(e.target.value)
                }
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    sendMessage();
                  }
                }}
                placeholder="Ask OILTRACE..."
                className="min-w-0 flex-1 rounded-xl border border-white/[.06] bg-white/[.03] px-3 py-2.5 text-xs text-white outline-none placeholder:text-slate-600 focus:border-cyan-400/20"
              />

              <button
                onClick={sendMessage}
                className="rounded-xl bg-cyan-500/10 p-2.5 text-cyan-400 transition hover:bg-cyan-500/20"
              >
                <Send size={15} />
              </button>

            </div>

            <div className="mt-2 flex items-center justify-center gap-1 text-[8px] text-slate-700">
              <Volume2 size={10} />
              AI-assisted intelligence interface
            </div>

          </div>

        </div>
      )}
    </>
  );
}