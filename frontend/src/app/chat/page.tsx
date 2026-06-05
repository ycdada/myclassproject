"use client";

import { useState, useRef, useEffect } from "react";
import { useSSE } from "@/lib/useSSE";
import type { SSEEvent } from "@/lib/useSSE";

interface Message {
  role: "user" | "assistant" | "system";
  content: string;
  agent?: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "你好！我是你的AI学习助手。让我们通过对话来了解你的学习情况，为你构建个性化的学习画像。首先，请告诉我：你之前学过哪些编程或数据结构相关的课程呢？",
    },
  ]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleSSEMessage = (event: SSEEvent) => {
    switch (event.event) {
      case "agent_thinking":
        // Show agent thinking status
        break;
      case "message":
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: event.data.content, agent: event.data.agent },
        ]);
        break;
      case "profile_update":
        // Profile dimension updated
        break;
      case "done":
        setIsStreaming(false);
        break;
    }
  };

  const { connect } = useSSE("/api/chat/profile", {
    onMessage: handleSSEMessage,
    onComplete: () => setIsStreaming(false),
    onError: () => setIsStreaming(false),
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim() || isStreaming) return;
    const userMessage = input.trim();
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setInput("");
    setIsStreaming(true);
    connect({ content: userMessage });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 h-[calc(100vh-8rem)] flex flex-col">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">AI 对话</h1>
        <p className="text-gray-600 mt-1">
          通过与AI助手对话，系统将自动构建你的学习画像，并为你提供个性化学习建议。
        </p>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto bg-white rounded-xl border border-gray-200 p-6 mb-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-xl px-4 py-3 ${
                msg.role === "user"
                  ? "bg-indigo-600 text-white"
                  : msg.role === "system"
                  ? "bg-yellow-50 border border-yellow-200 text-gray-700"
                  : "bg-gray-100 text-gray-900"
              }`}
            >
              {msg.agent && (
                <div className="text-xs font-medium text-indigo-500 mb-1">
                  🤖 {msg.agent}
                </div>
              )}
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}
        {isStreaming && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-xl px-4 py-3">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.1s]" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.2s]" />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="flex gap-3">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入你的回答..."
          disabled={isStreaming}
          className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none disabled:opacity-50"
        />
        <button
          onClick={handleSend}
          disabled={isStreaming || !input.trim()}
          className="px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
        >
          发送
        </button>
      </div>
    </div>
  );
}
