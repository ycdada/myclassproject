"use client";

import { useState, useEffect } from "react";
import { assessment, learningPath } from "@/lib/api";
import { MOCK_ASSESSMENT, MOCK_LEARNING_PATH } from "@/lib/mockData";
import { useStudentStore } from "@/stores/useStudentStore";

const statDefs = [
  { label: "已完成知识点", valueKey: "completed", totalKey: "total", icon: "📚", gradient: "from-indigo-500 to-blue-600", unit: "" },
  { label: "已生成资源", valueKey: "resources", icon: "📄", gradient: "from-emerald-500 to-teal-600", unit: " 个" },
  { label: "练习正确率", valueKey: "accuracy", icon: "✅", gradient: "from-amber-500 to-orange-600", unit: "%" },
  { label: "学习时长", valueKey: "minutes", icon: "⏱️", gradient: "from-rose-500 to-pink-600", unit: " 分钟" },
];

const quickLinks = [
  { href: "/chat", title: "AI 学习画像", desc: "对话式构建你的专属学习画像", icon: "💬", gradient: "from-indigo-500 to-violet-500" },
  { href: "/resources", title: "浏览资源库", desc: "个性化生成的讲义、习题与代码", icon: "📚", gradient: "from-emerald-500 to-teal-500" },
  { href: "/exercises", title: "开始练习", desc: "多种题型智能匹配，巩固知识点", icon: "✏️", gradient: "from-amber-500 to-orange-500" },
  { href: "/assessment", title: "查看评估", desc: "多维度掌握度分析与学习建议", icon: "📈", gradient: "from-rose-500 to-pink-500" },
];

export default function Home() {
  const [dashboard, setDashboard] = useState(MOCK_ASSESSMENT.dashboard);
  const [pathPreview, setPathPreview] = useState(MOCK_LEARNING_PATH.slice(0, 4));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [dashData, pathData] = await Promise.all([
          assessment.getDashboard("demo"),
          learningPath.getCurrent("demo"),
        ]);
        setDashboard(dashData);
        setPathPreview((pathData.topics_sequence || MOCK_LEARNING_PATH).slice(0, 4));
      } catch {} finally { setLoading(false); }
    }
    fetchData();
  }, []);

  const sessionCount = useStudentStore((s) => s.sessionResources.length);
  const statValues = {
    completed: dashboard.topics_completed,
    total: dashboard.total_topics,
    resources: (dashboard.resources_generated || 4) + sessionCount,
    accuracy: dashboard.exercises_attempted
      ? Math.round((dashboard.exercises_correct / dashboard.exercises_attempted) * 100) : "--",
    minutes: dashboard.total_study_time_minutes,
  };

  return (
    <div className="page-enter">
      {/* Hero */}
      <div className="bg-gradient-to-br from-slate-900 via-indigo-950 to-violet-950 border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
          <div className="flex items-center gap-4 mb-2">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-400 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/30">
              <span className="text-2xl">🧠</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">你好，同学 👋</h1>
              <p className="text-indigo-200 text-sm mt-0.5">
                欢迎回来 · 学习之旅第 3 天 · 继续保持！
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {statDefs.map((stat, i) => (
            <div key={stat.label}
              className={`relative overflow-hidden rounded-2xl bg-white p-5 shadow-sm border border-slate-100 hover:shadow-md transition-all duration-300 group ${loading ? "animate-pulse" : ""}`}
            >
              <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${stat.gradient}`} />
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">{stat.label}</p>
              <p className="text-3xl font-bold text-slate-900 tracking-tight">
                {stat.label === "已完成知识点"
                  ? `${statValues.completed} / ${statValues.total}`
                  : statValues[stat.valueKey as keyof typeof statValues]}{stat.unit}
              </p>
              <div className={`absolute -bottom-4 -right-4 w-20 h-20 rounded-full bg-gradient-to-br ${stat.gradient} opacity-5 group-hover:opacity-10 transition-opacity`} />
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Learning Path */}
          <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-bold text-slate-900 tracking-tight">推荐学习路径</h2>
              <a href="/learning-path" className="text-sm font-medium text-indigo-600 hover:text-indigo-700 transition-colors">
                查看全部 →
              </a>
            </div>
            <div className="space-y-2.5">
              {pathPreview.map((topic: any, idx: number) => {
                const done = topic.status === "completed";
                const active = topic.status === "in_progress";
                return (
                  <div key={topic.topic_id || idx}
                    className={`flex items-center gap-4 p-4 rounded-xl transition-all duration-200 ${
                      done ? "bg-emerald-50 border border-emerald-100" :
                      active ? "bg-indigo-50 border border-indigo-100" :
                      topic.status === "available" ? "bg-white border border-slate-100 hover:border-indigo-200 hover:bg-indigo-50/30" :
                      "bg-slate-50 border border-slate-100 opacity-50"
                    }`}
                  >
                    <div className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold shrink-0 ${
                      done ? "bg-emerald-500 text-white" :
                      active ? "bg-indigo-600 text-white shadow-sm shadow-indigo-200" :
                      topic.status === "available" ? "bg-white border-2 border-indigo-300 text-indigo-500" :
                      "bg-slate-200 text-slate-400"
                    }`}>
                      {done ? "✓" : active ? "▶" : idx + 1}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className={`font-semibold text-sm ${done ? "text-emerald-800" : active ? "text-indigo-900" : "text-slate-700"}`}>
                        {topic.topic_name}
                      </p>
                      <p className="text-xs text-slate-400 mt-0.5">
                        难度 {"⭐".repeat(topic.difficulty || 1)} · {topic.estimated_hours || 2}h
                      </p>
                    </div>
                    <span className={`px-2.5 py-1 rounded-full text-[11px] font-semibold tracking-wide shrink-0 ${
                      done ? "bg-emerald-100 text-emerald-700" :
                      active ? "bg-indigo-100 text-indigo-700" :
                      topic.status === "available" ? "bg-indigo-50 text-indigo-500" :
                      "bg-slate-100 text-slate-400"
                    }`}>
                      {done ? "已完成" : active ? "进行中" : topic.status === "available" ? "可学习" : "待解锁"}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="space-y-3">
            <h2 className="text-lg font-bold text-slate-900 tracking-tight px-1">快速操作</h2>
            {quickLinks.map((item) => (
              <a key={item.href} href={item.href}
                className="flex items-center gap-4 p-4 rounded-xl bg-white border border-slate-100 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 group"
              >
                <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${item.gradient} flex items-center justify-center text-white text-lg shadow-sm group-hover:scale-110 transition-transform`}>
                  {item.icon}
                </div>
                <div>
                  <p className="font-semibold text-sm text-slate-800">{item.title}</p>
                  <p className="text-xs text-slate-400 mt-0.5">{item.desc}</p>
                </div>
                <span className="ml-auto text-slate-300 group-hover:text-indigo-400 group-hover:translate-x-0.5 transition-all">→</span>
              </a>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
