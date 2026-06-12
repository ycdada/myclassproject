"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { resources } from "@/lib/api";
import { MOCK_RESOURCES } from "@/lib/mockData";
import { useStudentStore } from "@/stores/useStudentStore";

const RESOURCE_TYPES = [
  { id: "all", label: "全部", icon: "📋", gradient: "from-slate-500 to-slate-600" },
  { id: "lecture", label: "课程讲义", icon: "📝", gradient: "from-blue-500 to-indigo-600" },
  { id: "mindmap", label: "思维导图", icon: "🧠", gradient: "from-violet-500 to-purple-600" },
  { id: "exercise", label: "练习题", icon: "✏️", gradient: "from-amber-500 to-orange-600" },
  { id: "code", label: "代码案例", icon: "💻", gradient: "from-emerald-500 to-teal-600" },
  { id: "reading", label: "拓展阅读", icon: "📖", gradient: "from-rose-500 to-pink-600" },
];

export default function ResourcesPage() {
  const [activeType, setActiveType] = useState("all");
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const sessionResources = useStudentStore((s) => s.sessionResources);

  useEffect(() => {
    async function fetchData() {
      setLoading(true); setError("");
      try {
        const data = await resources.list({ resource_type: activeType === "all" ? undefined : activeType });
        const apiRes = data.resources.length ? data.resources : MOCK_RESOURCES;
        // Merge session-generated resources
        const sessionRes = sessionResources.filter((r) =>
          activeType === "all" || r.resource_type === activeType
        );
        const merged = [...sessionRes, ...apiRes.filter((r: any) =>
          !sessionRes.find((s) => s.id === r.id)
        )];
        setItems(merged);
      } catch {
        const base = MOCK_RESOURCES.filter((r) => activeType === "all" || r.resource_type === activeType);
        const sessionRes = sessionResources.filter((r) => activeType === "all" || r.resource_type === activeType);
        setItems([...sessionRes, ...base.filter((r) => !sessionRes.find((s) => s.id === r.id))]);
      } finally { setLoading(false); }
    }
    fetchData();
  }, [activeType, sessionResources]);

  return (
    <div className="page-enter max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">学习资源</h1>
        <p className="text-sm text-slate-500 mt-1">个性化生成的学习材料，为你量身定制</p>
      </div>

      {/* Filter tabs */}
      <div className="flex flex-wrap gap-2 mb-6">
        {RESOURCE_TYPES.map((t) => (
          <button key={t.id} onClick={() => setActiveType(t.id)}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
              activeType === t.id
                ? `bg-gradient-to-r ${t.gradient} text-white shadow-sm`
                : "bg-white text-slate-500 border border-slate-200 hover:border-slate-300 hover:text-slate-700"
            }`}
          >
            <span className="text-base">{t.icon}</span>
            <span>{t.label}</span>
          </button>
        ))}
      </div>

      {/* States */}
      {loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-2xl border border-slate-100 p-6 animate-pulse">
              <div className="h-3 bg-slate-100 rounded-full w-1/4 mb-4" />
              <div className="h-4 bg-slate-100 rounded-lg w-3/4 mb-3" />
              <div className="h-3 bg-slate-50 rounded-lg w-full mb-2" />
              <div className="h-3 bg-slate-50 rounded-lg w-2/3" />
            </div>
          ))}
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-100 rounded-2xl p-8 text-center">
          <span className="text-4xl">⚠</span>
          <p className="mt-3 text-red-600 text-sm">{error}</p>
          <button onClick={() => window.location.reload()} className="mt-4 px-5 py-2 bg-red-600 text-white rounded-xl text-sm font-medium hover:bg-red-700 transition-colors">重试</button>
        </div>
      )}

      {!loading && !error && items.length === 0 && (
        <div className="bg-white rounded-2xl border border-dashed border-slate-200 p-16 text-center">
          <div className="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">📚</span>
          </div>
          <h3 className="text-lg font-bold text-slate-800">还没有学习资源</h3>
          <p className="text-sm text-slate-400 mt-1.5 max-w-sm mx-auto">完成学习画像构建后，系统将为你自动生成个性化的学习资源。</p>
          <a href="/chat" className="mt-5 inline-block px-6 py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 text-white rounded-xl text-sm font-medium hover:shadow-md hover:shadow-indigo-200 transition-all">开始构建画像 →</a>
        </div>
      )}

      {!loading && !error && items.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map((res: any) => {
            const rt = RESOURCE_TYPES.find((t) => t.id === res.resource_type);
            return (
              <Link key={res.id} href={`/resources/${res.id}`}
                className="block bg-white rounded-2xl border border-slate-100 p-6 shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-200 group"
              >
                <div className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-semibold tracking-wide mb-4 bg-gradient-to-r ${rt?.gradient || "from-slate-500 to-slate-600"} text-white`}>
                  {rt?.icon} {rt?.label || res.resource_type}
                </div>
                <h3 className="font-bold text-slate-800 mb-2 group-hover:text-indigo-600 transition-colors leading-snug">{res.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed line-clamp-2">
                  {res.resource_type === "mindmap" ? "可视化知识结构，一目了然" :
                   res.resource_type === "code" ? "可运行代码 + 测试用例" :
                   "包含概念定义、算法步骤与常见误区"}
                </p>
                {res.metadata?.difficulty && (
                  <div className="flex items-center gap-2 mt-4 pt-3 border-t border-slate-50">
                    <span className="text-[10px] text-slate-400">{"⭐".repeat(res.metadata.difficulty)}{"☆".repeat(Math.max(0, 5 - res.metadata.difficulty))}</span>
                    <span className="text-[10px] text-slate-300">{res.metadata.estimated_time || "20 min"}</span>
                  </div>
                )}
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
