"use client";

import { useState, useEffect } from "react";
import { resources } from "@/lib/api";
import { MOCK_RESOURCES } from "@/lib/mockData";

const RESOURCE_TYPES = [
  { id: "all", label: "全部", icon: "📋" },
  { id: "lecture", label: "课程讲义", icon: "📝" },
  { id: "mindmap", label: "思维导图", icon: "🧠" },
  { id: "exercise", label: "练习题", icon: "✏️" },
  { id: "reading", label: "拓展阅读", icon: "📖" },
  { id: "code", label: "代码案例", icon: "💻" },
];

export default function ResourcesPage() {
  const [activeType, setActiveType] = useState("all");
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError("");
      try {
        const data = await resources.list({
          resource_type: activeType === "all" ? undefined : activeType,
        });
        setItems(data.resources.length ? data.resources : MOCK_RESOURCES);
      } catch {
        setItems(MOCK_RESOURCES.filter((r) => activeType === "all" || r.resource_type === activeType));
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [activeType]);

  const handleViewResource = (res: any) => {
    // Show content in a simple alert for demo, or could navigate to detail page
    if (res.content) {
      const win = window.open("", "_blank", "width=800,height=600");
      if (win) {
        win.document.write(`<html><head><title>${res.title}</title>
          <meta charset="utf-8"><style>body{font-family:sans-serif;max-width:720px;margin:2rem auto;padding:1rem;line-height:1.7;}pre{background:#f5f5f5;padding:1rem;border-radius:8px;overflow-x:auto;}code{font-size:0.9em;}</style></head>
          <body>${res.content.replace(/\n/g, "<br>").replace(/\$\$(.*?)\$\$/g, "<em>$1</em>")}</body></html>`);
      }
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">学习资源</h1>
        <p className="text-gray-600 mt-1">浏览和搜索系统为你个性化生成的学习资源。</p>
      </div>

      <div className="flex flex-wrap gap-2 mb-6">
        {RESOURCE_TYPES.map((type) => (
          <button key={type.id} onClick={() => setActiveType(type.id)}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeType === type.id
                ? "bg-indigo-600 text-white"
                : "bg-white text-gray-600 border border-gray-200 hover:border-indigo-300 hover:text-indigo-600"
            }`}>
            <span>{type.icon}</span><span>{type.label}</span>
          </button>
        ))}
      </div>

      {/* Loading / Error / Empty states */}
      {loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-xl border border-gray-200 p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-3" />
              <div className="h-3 bg-gray-100 rounded w-full mb-2" />
              <div className="h-3 bg-gray-100 rounded w-2/3" />
            </div>
          ))}
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
          <span className="text-3xl">⚠️</span>
          <p className="mt-2 text-red-700">{error}</p>
          <button onClick={() => window.location.reload()} className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm">重试</button>
        </div>
      )}

      {!loading && !error && items.length === 0 && (
        <div className="bg-white rounded-xl border border-dashed border-gray-300 p-12 text-center">
          <span className="text-5xl">📚</span>
          <h3 className="mt-4 text-lg font-medium text-gray-900">还没有学习资源</h3>
          <p className="mt-2 text-gray-500">完成学习画像构建后，系统将为你自动生成个性化的学习资源。</p>
          <a href="/chat" className="mt-4 inline-block px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">开始构建画像 →</a>
        </div>
      )}

      {!loading && !error && items.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map((res: any) => (
            <div key={res.id} onClick={() => handleViewResource(res)}
              className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-md hover:border-indigo-200 transition-all cursor-pointer group">
              <div className="flex items-start justify-between mb-3">
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  res.resource_type === "lecture" ? "bg-blue-50 text-blue-600" :
                  res.resource_type === "mindmap" ? "bg-purple-50 text-purple-600" :
                  res.resource_type === "exercise" ? "bg-orange-50 text-orange-600" :
                  res.resource_type === "code" ? "bg-green-50 text-green-600" :
                  res.resource_type === "reading" ? "bg-teal-50 text-teal-600" :
                  "bg-gray-50 text-gray-600"
                }`}>
                  {RESOURCE_TYPES.find((t) => t.id === res.resource_type)?.icon}{" "}
                  {RESOURCE_TYPES.find((t) => t.id === res.resource_type)?.label || res.resource_type}
                </span>
                {res.metadata?.difficulty && (
                  <span className="text-xs text-gray-400">{"⭐".repeat(res.metadata.difficulty)}</span>
                )}
              </div>
              <h3 className="font-semibold text-gray-900 mb-2 group-hover:text-indigo-600 transition-colors">{res.title}</h3>
              <p className="text-sm text-gray-500 line-clamp-2">
                {res.resource_type === "lecture" ? "包含概念定义、算法步骤、代码示例和常见误区的完整讲义" :
                 res.resource_type === "mindmap" ? "可视化的知识结构思维导图" :
                 res.resource_type === "exercise" ? `${res.metadata?.question_count || 10} 道精选练习题` :
                 res.resource_type === "code" ? "可运行的代码实现与测试用例" :
                 "深入拓展阅读材料"}
              </p>
              {res.metadata?.estimated_time && (
                <p className="text-xs text-gray-400 mt-3">⏱️ 预计学习: {res.metadata.estimated_time}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
