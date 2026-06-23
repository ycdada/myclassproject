"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { getMockSessionResources } from "@/lib/mockData";
import { useStudentStore } from "@/stores/useStudentStore";

interface Message {
  role: "user" | "assistant" | "system";
  content: string;
  agent?: string;
}

const INITIAL_MESSAGE: Message = {
  role: "assistant",
  content: "你好！我是你的 AI 学习助手。你可以跟我聊天，也可以直接说「我想学数组」、「给我讲讲二叉树」、「我需要练习链表」等，我会为你自动生成个性化的学习材料。\n\n首先，请告诉我：你之前学过哪些编程或数据结构相关的课程呢？",
};

const TOPIC_KEYWORDS: Record<string, string> = {
  "链表": "linked_lists", "数组": "arrays", "二叉树": "bst",
  "二叉搜索树": "bst", "栈": "stacks", "队列": "queues",
  "动态规划": "dynamic_programming", "排序": "advanced_sorting",
  "哈希": "hashing", "图": "graphs_basic", "堆": "heap",
  "字符串": "strings", "递归": "recursion", "分治": "divide_conquer",
  "贪心": "greedy", "回溯": "backtracking", "并查集": "union_find",
  "字典树": "trie", "最短路径": "shortest_path",
};

function detectTopic(text: string): { id: string; name: string } | null {
  for (const [kw, id] of Object.entries(TOPIC_KEYWORDS)) {
    if (text.includes(kw)) return { id, name: kw };
  }
  return null;
}

const MOCK_CHAT = [
  { user: "你好", bot: "你好！👋 我是你的 AI 学习助手。你之前学过哪些编程或算法相关的课程呢？" },
  { user: "学过C和Python", bot: "很棒！你有不错的编程基础。你喜欢哪种学习方式？看视频、读教材、还是动手写代码？" },
  { user: "喜欢动手写代码", bot: "动手实践是最好的学习方式！你的学习目标是什么呢？通过考试、准备面试、还是深入掌握算法？" },
  { user: "我想学链表", bot: "好的！我来为你生成「链表」的个性化学习材料..." },
];

const TYPE_ICON: Record<string, string> = { lecture: "📝", mindmap: "🧠", exercise: "✏️", code: "💻", reading: "📖" };
const TYPE_LABEL: Record<string, string> = { lecture: "课程讲义", mindmap: "思维导图", exercise: "练习题", code: "代码案例", reading: "拓展阅读" };

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([INITIAL_MESSAGE]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [chatRound, setChatRound] = useState(0);
  const [cards, setCards] = useState<any[]>([]);

  const addResource = useStudentStore((s) => s.addSessionResource);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, cards]);

  async function sendReal(msg: string) {
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiBase}/api/chat/session`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: msg, student_id: "demo" }),
      });
      if (!res.ok || !res.body) throw new Error("no body");

      const reader = res.body.getReader();
      const dec = new TextDecoder();
      let buf = "";
      let assistantText = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        const lines = buf.split("\n");
        buf = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const d = JSON.parse(line.slice(6));
              if (d.text && line.includes("content_chunk")) {
                assistantText += d.text;
              }
              if (d.step && line.includes("progress")) {
                setMessages((p) => [...p, { role: "system", content: `🔄 ${d.step}` }]);
              }
              if (line.includes("resource_ready") && d.id) {
                const card = { id: d.id, topic_id: d.topic_id || "", resource_type: d.resource_type || "lecture", title: d.title || "", content: d.content || "", mindmap: d.mindmap || "", questions: d.questions || [], hints: d.hints || [], solution: d.solution || "" };
                setCards((p) => { if (p.find((c) => c.id === card.id)) return p; return [...p, card]; });
                addResource(card);
              }
            } catch {}
          }
        }
      }

      if (assistantText.trim()) {
        setMessages((p) => [...p, { role: "assistant", content: assistantText, agent: "DSALearn AI" }]);
      }

      if (cards.length === 0) {
        // No resources generated — check topic
        const topic = detectTopic(msg);
        if (topic) {
          setMessages((p) => [...p,
            { role: "system", content: `🔄 正在为「${topic.name}」生成个性化学习材料...` },
            { role: "system", content: `🔄 生成完成: lecture → exercise → code → mindmap` },
          ]);
          setTimeout(() => {
            const mocks = getMockSessionResources(topic.id);
            setCards(mocks);
            mocks.forEach((m) => addResource(m));
            setMessages((p) => [...p,
              { role: "assistant", content: `✅ 已为你生成「${topic.name}」的学习材料！包括课程讲义、思维导图、练习题和代码案例。`, agent: "DSALearn AI" }
            ]);
          }, 500);
        }
      }
    } catch (err: any) {
      console.warn("API failed, using mock:", err.message);
      // Mock fallback
      const topic = detectTopic(msg);
      if (topic && chatRound >= 1) {
        setMessages((p) => [...p,
          { role: "system", content: `🔄 正在为「${topic.name}」生成个性化学习材料...` },
        ]);
        setTimeout(() => {
          const mocks = getMockSessionResources(topic.id);
          setCards(mocks);
          mocks.forEach((m) => addResource(m));
          setMessages((p) => [...p,
            { role: "system", content: `🔄 生成完成: lecture → exercise → code → mindmap` },
            { role: "assistant", content: `✅ 已为你生成「${topic.name}」的学习材料！包括课程讲义、思维导图、练习题和代码案例。`, agent: "DSALearn AI" }
          ]);
        }, 500);
      } else {
        const script = MOCK_CHAT[Math.min(chatRound, MOCK_CHAT.length - 1)];
        setMessages((p) => [...p, { role: "assistant", content: script.bot, agent: "DSALearn AI" }]);
      }
    }
    setSending(false);
    setChatRound((r) => Math.min(r + 1, MOCK_CHAT.length - 1));
  }

  const handleSend = () => {
    const msg = input.trim();
    if (!msg || sending) return;
    setMessages((p) => [...p, { role: "user", content: msg }]);
    setInput(""); setSending(true); setCards([]);
    sendReal(msg);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-6 flex flex-col" style={{ height: "calc(100vh - 8rem)" }}>
      <div className="mb-4 shrink-0">
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">AI 学习对话</h1>
        <p className="text-sm text-slate-500 mt-0.5">与我对话，或直接说「想学 XX 知识点」触发资源生成</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto rounded-2xl bg-white border border-slate-100 shadow-sm p-5 space-y-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[82%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
              msg.role === "user"
                ? "bg-gradient-to-br from-indigo-600 to-violet-600 text-white shadow-sm"
                : msg.role === "system"
                ? "bg-indigo-50 border border-indigo-100 text-indigo-700 text-xs"
                : "bg-slate-50 text-slate-700"
            }`}>
              {msg.agent && <div className="text-[11px] font-semibold text-indigo-500 mb-1">{msg.agent}</div>}
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}

        {/* Resource cards */}
        {cards.length > 0 && (
          <div className="flex justify-start">
            <div className="max-w-[90%] space-y-3">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider pl-1">📦 已生成学习资源</div>
              {cards.map((c) => (
                <Link key={c.id} href={`/resources/${c.id}`}
                  className="flex items-center gap-3 p-3.5 rounded-xl bg-white border border-indigo-200 hover:border-indigo-400 hover:shadow-sm transition-all group">
                  <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center text-white text-sm shrink-0">
                    {TYPE_ICON[c.resource_type] || "📄"}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-slate-800 group-hover:text-indigo-600 truncate">{c.title}</p>
                    <p className="text-[10px] text-slate-400 mt-0.5">
                      {TYPE_LABEL[c.resource_type] || "学习材料"}
                    </p>
                  </div>
                  <span className="text-slate-300 group-hover:text-indigo-400 group-hover:translate-x-0.5 transition-all">→</span>
                </Link>
              ))}
            </div>
          </div>
        )}

        {sending && cards.length === 0 && (
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
      <div className="flex gap-2.5 mt-3 shrink-0">
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="试试说「我想学链表」或「给我讲讲二叉树」..."
          className="flex-1 px-4 py-3 bg-white border border-slate-200 rounded-2xl text-sm text-slate-800 placeholder-slate-400 outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 transition-all shadow-sm"
        />
        <button
          onClick={handleSend}
          className={"px-6 py-3 rounded-2xl font-medium text-sm transition-all shadow-sm active:scale-95 " +
            (sending || !input.trim()
              ? "bg-slate-100 text-slate-300 cursor-default"
              : "bg-gradient-to-r from-indigo-600 to-violet-600 text-white hover:shadow-md hover:from-indigo-700 hover:to-violet-700 cursor-pointer")
          }
        >
          发送
        </button>
      </div>
    </div>
  );
}
