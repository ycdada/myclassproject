"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useSSE } from "@/lib/useSSE";
import type { SSEEvent } from "@/lib/useSSE";
import { getMockChatScript, isDemoMode } from "@/lib/mockData";

interface Message {
  role: "user" | "assistant" | "system";
  content: string;
  agent?: string;
}

const INITIAL_MESSAGE: Message = {
  role: "assistant",
  content: "你好！我是你的 AI 学习助手。让我们通过对话来了解你的学习情况，为你构建个性化的学习画像。首先，请告诉我：你之前学过哪些编程或数据结构相关的课程呢？",
};

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([INITIAL_MESSAGE]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const [chatRound, setChatRound] = useState(0);
  const [useMockFallback, setUseMockFallback] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  const handleSSEMessage = useCallback((event: SSEEvent) => {
    switch (event.event) {
      case "content_chunk":
        setStreamingText((prev) => prev + (event.data?.text || ""));
        break;
      case "profile_update":
        if (event.data?.profile) console.log("[Chat] Profile updated:", event.data.profile);
        break;
      case "error":
        setIsStreaming(false); setStreamingText("");
        setMessages((prev) => [...prev, { role: "system", content: `⚠️ ${event.data?.message || "连接失败，已切换到演示模式。"}` }]);
        setUseMockFallback(true);
        break;
      case "done":
        setStreamingText((current) => { if (current) setMessages((prev) => [...prev, { role: "assistant", content: current, agent: "DSALearn AI" }]); return ""; });
        setIsStreaming(false);
        break;
    }
  }, []);

  const { connect } = useSSE("/api/chat/profile", {
    onMessage: handleSSEMessage,
    onComplete: () => { setIsStreaming(false); setStreamingText(""); },
    onError: () => { setIsStreaming(false); setStreamingText(""); setUseMockFallback(true); },
  });

  useEffect(() => { scrollToBottom(); }, [messages, streamingText, scrollToBottom]);

  const runMockChat = useCallback((userMessage: string) => {
    const scripts = getMockChatScript();
    const round = Math.min(chatRound, scripts.length - 1);
    const script = scripts[round];
    setTimeout(() => {
      setMessages((prev) => [...prev, { role: "assistant", content: script.assistant, agent: "DSALearn AI" }]);
      setIsStreaming(false);
      if (userMessage.length > 2) setChatRound((r) => Math.min(r + 1, scripts.length - 1));
    }, 800 + Math.random() * 1200);
  }, [chatRound]);

  const handleSend = () => {
    if (!input.trim() || isStreaming) return;
    const msg = input.trim();
    setMessages((prev) => [...prev, { role: "user", content: msg }]);
    setInput(""); setIsStreaming(true); setStreamingText("");
    if (isDemoMode() || useMockFallback) runMockChat(msg);
    else connect({ content: msg });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  return (
    <div className="page-enter max-w-3xl mx-auto px-4 py-6 h-[calc(100vh-8rem)] flex flex-col">
      {/* Header */}
      <div className="mb-4">
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">AI 学习对话</h1>
        <p className="text-sm text-slate-500 mt-0.5">通过对话构建你的专属学习画像</p>
        {(isDemoMode() || useMockFallback) && (
          <div className="mt-2 px-3 py-1.5 rounded-lg bg-amber-50 border border-amber-200 text-amber-700 text-xs inline-flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" /> 演示模式
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto rounded-2xl bg-white border border-slate-100 shadow-sm p-5 space-y-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
              msg.role === "user"
                ? "bg-gradient-to-br from-indigo-600 to-violet-600 text-white shadow-sm shadow-indigo-200"
                : msg.role === "system"
                ? "bg-amber-50 border border-amber-100 text-amber-800"
                : "bg-slate-50 text-slate-700"
            }`}>
              {msg.agent && <div className="text-[11px] font-semibold text-indigo-500 mb-1 tracking-wide">DSALearn AI</div>}
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}
        {streamingText && (
          <div className="flex justify-start">
            <div className="max-w-[80%] bg-slate-50 rounded-2xl px-4 py-3">
              <p className="text-sm text-slate-700 whitespace-pre-wrap">{streamingText}<span className="inline-block w-1.5 h-4 bg-indigo-500 animate-pulse ml-0.5 rounded-sm" /></p>
            </div>
          </div>
        )}
        {isStreaming && !streamingText && (
          <div className="flex justify-start">
            <div className="bg-slate-50 rounded-2xl px-4 py-3 flex items-center gap-1.5">
              <div className="w-2 h-2 bg-slate-300 rounded-full animate-bounce" />
              <div className="w-2 h-2 bg-slate-300 rounded-full animate-bounce [animation-delay:0.12s]" />
              <div className="w-2 h-2 bg-slate-300 rounded-full animate-bounce [animation-delay:0.24s]" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex gap-2.5 mt-3">
        <div className="flex-1 relative">
          <input type="text" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={handleKeyDown}
            placeholder="输入你的回答..."
            disabled={isStreaming}
            className="w-full px-4 py-3 bg-white border border-slate-200 rounded-2xl text-sm text-slate-800 placeholder-slate-400 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 outline-none transition-all disabled:opacity-50 shadow-sm"
          />
        </div>
        <button onClick={handleSend} disabled={isStreaming || !input.trim()}
          className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-violet-600 text-white rounded-2xl font-medium text-sm hover:from-indigo-700 hover:to-violet-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-sm shadow-indigo-200 hover:shadow-md active:scale-95">
          发送
        </button>
      </div>
    </div>
  );
}
