"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import Link from "next/link";
import { useSSE } from "@/lib/useSSE";
import type { SSEEvent } from "@/lib/useSSE";
import { getMockChatScript, getMockSessionResources, isDemoMode } from "@/lib/mockData";
import { useStudentStore } from "@/stores/useStudentStore";

interface Message {
  role: "user" | "assistant" | "system";
  content: string;
  agent?: string;
}

interface ResourceCard {
  id: string;
  topic_id: string;
  resource_type: string;
  title: string;
  content?: string;
  mindmap?: string;
  questions?: any[];
  hints?: string[];
  solution?: string;
}

const INITIAL_MESSAGE: Message = {
  role: "assistant",
  content:
    "你好！我是你的 AI 学习助手。你可以跟我聊天，也可以直接说「我想学数组」、「给我讲讲二叉树」、「我需要练习链表」等，我会为你自动生成个性化的学习材料。\n\n首先，请告诉我：你之前学过哪些编程或数据结构相关的课程呢？",
};

const TYPE_ICONS: Record<string, string> = {
  lecture: "📝", mindmap: "🧠", exercise: "✏️", code: "💻", reading: "📖",
};

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([INITIAL_MESSAGE]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const [chatRound, setChatRound] = useState(0);
  const [useMockFallback, setUseMockFallback] = useState(false);
  const [generatedResources, setGeneratedResources] = useState<ResourceCard[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const addSessionResource = useStudentStore((s) => s.addSessionResource);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  const handleSSEMessage = useCallback((event: SSEEvent) => {
    switch (event.event) {
      case "content_chunk":
        setStreamingText((prev) => prev + (event.data?.text || ""));
        break;
      case "message":
        if (event.data?.text) {
          setMessages((prev) => [...prev, { role: "assistant", content: event.data.text, agent: event.data.agent }]);
        }
        break;
      case "profile_update":
        if (event.data?.profile) console.log("[Chat] Profile updated");
        break;
      case "progress":
        if (event.data?.step) {
          setMessages((prev) => [...prev, { role: "system", content: `🔄 ${event.data.step}` }]);
        }
        break;
      case "resource_ready": {
        const res: ResourceCard = {
          id: event.data?.id || "",
          topic_id: event.data?.topic_id || "",
          resource_type: event.data?.resource_type || "lecture",
          title: event.data?.title || "",
          content: event.data?.content || "",
          mindmap: event.data?.mindmap || "",
          questions: event.data?.questions || [],
          hints: event.data?.hints || [],
          solution: event.data?.solution || "",
        };
        setGeneratedResources((prev) => {
          if (prev.find((r) => r.id === res.id)) return prev;
          return [...prev, res];
        });
        addSessionResource(res);
        break;
      }
      case "error":
        setIsStreaming(false); setStreamingText("");
        setMessages((prev) => [...prev, { role: "system", content: `⚠️ ${event.data?.message || "连接失败，已切换到演示模式。"}` }]);
        setUseMockFallback(true);
        break;
      case "done":
        setStreamingText((current) => {
          if (current.trim()) {
            setMessages((prev) => [...prev, { role: "assistant", content: current, agent: "DSALearn AI" }]);
          }
          return "";
        });
        setIsStreaming(false);
        break;
    }
  }, [addSessionResource]);

  const { connect } = useSSE("/api/chat/session", {
    onMessage: handleSSEMessage,
    onComplete: () => { setIsStreaming(false); setStreamingText(""); },
    onError: () => { setIsStreaming(false); setStreamingText(""); setUseMockFallback(true); },
  });

  useEffect(() => { scrollToBottom(); }, [messages, streamingText, generatedResources, scrollToBottom]);

  // Demo mock: simulate topic detection + resource generation
  const runMockChat = useCallback(
    (userMessage: string) => {
      const scripts = getMockChatScript();
      const round = Math.min(chatRound, scripts.length - 1);
      const script = scripts[round];

      // Detect topic keywords
      const topicMap: Record<string, string> = {
        "链表": "linked_lists", "数组": "arrays", "二叉树": "bst",
        "二叉搜索树": "bst", "栈": "stacks", "队列": "queues",
        "动态规划": "dynamic_programming", "排序": "advanced_sorting",
        "哈希": "hashing", "图": "graphs_basic",
      };
      let detectedTopic: string | undefined;
      let detectedName: string | undefined;
      for (const [kw, id] of Object.entries(topicMap)) {
        if (userMessage.includes(kw)) { detectedTopic = id; detectedName = kw; break; }
      }

      setTimeout(() => {
        if (detectedTopic && chatRound >= 1) {
          // Show generation progress + resources
          setMessages((prev) => [
            ...prev,
            { role: "assistant", content: `好的！我来为你生成「${detectedName}」的个性化学习材料，请稍候...`, agent: "DSALearn AI" },
            { role: "system", content: `🔄 正在为「${detectedName}」生成个性化学习材料...` },
          ]);

          setTimeout(() => {
            const mockResources = getMockSessionResources(detectedTopic);
            setGeneratedResources(mockResources);
            mockResources.forEach((r) => addSessionResource(r));
            setMessages((prev) => [
              ...prev,
              { role: "system", content: `🔄 生成完成: lecture → exercise → code → mindmap (质量检查通过)` },
              { role: "assistant", content: `✅ 已为你生成「${detectedName}」的学习材料！包括课程讲义、思维导图、练习题和代码案例。你可以切换到学习资源页面查看完整内容。`, agent: "DSALearn AI" },
            ]);
            setIsStreaming(false);
          }, 1500);
        } else {
          setMessages((prev) => [...prev, { role: "assistant", content: script.assistant, agent: "DSALearn AI" }]);
          setIsStreaming(false);
        }
        if (userMessage.length > 2) setChatRound((r) => Math.min(r + 1, scripts.length - 1));
      }, 800 + Math.random() * 1200);
    },
    [chatRound, addSessionResource]
  );

  const handleSend = () => {
    if (!input.trim() || isStreaming) return;
    const msg = input.trim();
    setMessages((prev) => [...prev, { role: "user", content: msg }]);
    setInput(""); setIsStreaming(true); setStreamingText(""); setGeneratedResources([]);

    if (isDemoMode() || useMockFallback) {
      runMockChat(msg);
    } else {
      connect({ content: msg, student_id: "demo" });
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  return (
    <div className="page-enter max-w-3xl mx-auto px-4 py-6 h-[calc(100vh-8rem)] flex flex-col">
      <div className="mb-4">
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">AI 学习对话</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          与我对话，或直接说「想学 XX 知识点」触发资源生成
        </p>
        {(isDemoMode() || useMockFallback) && (
          <div className="mt-2 px-3 py-1.5 rounded-lg bg-amber-50 border border-amber-200 text-amber-700 text-xs inline-flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" /> 演示模式
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto rounded-2xl bg-white border border-slate-100 shadow-sm p-5 space-y-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[82%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
              msg.role === "user"
                ? "bg-gradient-to-br from-indigo-600 to-violet-600 text-white shadow-sm shadow-indigo-200"
                : msg.role === "system"
                ? "bg-indigo-50 border border-indigo-100 text-indigo-700 text-xs"
                : "bg-slate-50 text-slate-700"
            }`}>
              {msg.agent && <div className="text-[11px] font-semibold text-indigo-500 mb-1 tracking-wide">{msg.agent}</div>}
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}

        {/* Generated resource cards */}
        {generatedResources.length > 0 && (
          <div className="flex justify-start">
            <div className="max-w-[90%] space-y-3">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider pl-1">📦 已生成学习资源</div>
              {generatedResources.map((res) => (
                <Link key={res.id} href={`/resources/${res.id}`}
                  className="flex items-center gap-3 p-3.5 rounded-xl bg-white border border-indigo-200 hover:border-indigo-400 hover:shadow-sm transition-all group"
                >
                  <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center text-white text-sm shrink-0">
                    {TYPE_ICONS[res.resource_type] || "📄"}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-slate-800 group-hover:text-indigo-600 transition-colors truncate">{res.title}</p>
                    <p className="text-[10px] text-slate-400 mt-0.5">{res.resource_type === "lecture" ? "课程讲义 · Markdown + LaTeX" : res.resource_type === "mindmap" ? "思维导图 · 可视化结构" : res.resource_type === "exercise" ? "练习题 · 5种题型" : res.resource_type === "code" ? "代码案例 · 可运行" : "学习材料"}</p>
                  </div>
                  <span className="text-slate-300 group-hover:text-indigo-400 group-hover:translate-x-0.5 transition-all">→</span>
                </Link>
              ))}
            </div>
          </div>
        )}

        {streamingText && (
          <div className="flex justify-start">
            <div className="max-w-[82%] bg-slate-50 rounded-2xl px-4 py-3">
              <p className="text-sm text-slate-700 whitespace-pre-wrap">{streamingText}<span className="inline-block w-1.5 h-4 bg-indigo-500 animate-pulse ml-0.5 rounded-sm" /></p>
            </div>
          </div>
        )}
        {isStreaming && !streamingText && generatedResources.length === 0 && (
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

      <div className="flex gap-2.5 mt-3">
        <div className="flex-1 relative">
          <input type="text" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={handleKeyDown}
            placeholder="试试说「我想学链表」或「给我讲讲二叉树」..."
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
