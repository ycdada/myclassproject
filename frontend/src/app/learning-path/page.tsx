"use client";

import { useState, useEffect } from "react";
import { learningPath } from "@/lib/api";
import { getMockLearningPath } from "@/lib/mockData";

const statusConfig: Record<string, { bg: string; dot: string; label: string }> = {
  completed: { bg: "bg-emerald-50", dot: "bg-emerald-500", label: "已完成" },
  in_progress: { bg: "bg-indigo-50", dot: "bg-indigo-600", label: "进行中" },
  available: { bg: "bg-white", dot: "bg-slate-300", label: "待开始" },
  locked: { bg: "bg-slate-50", dot: "bg-slate-200", label: "待解锁" },
};

export default function LearningPathPage() {
  const [topics, setTopics] = useState<any[]>(getMockLearningPath());
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    async function f() {
      try { const d = await learningPath.getCurrent("demo"); setTopics(d.topics_sequence?.length ? d.topics_sequence : getMockLearningPath()); }
      catch { setTopics(getMockLearningPath()); }
      finally { setLoading(false); }
    }
    f();
  }, []);

  const handleRegen = async () => {
    setGenerating(true);
    try { const d = await learningPath.generate("demo"); setTopics(d.topics_sequence || getMockLearningPath()); }
    catch { setTopics(getMockLearningPath()); }
    finally { setGenerating(false); }
  };

  return (
    <div className="page-enter max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">个性化学习路径</h1>
        <p className="text-sm text-slate-500 mt-1">基于知识图谱与学习画像，为你规划最优路径</p>
      </div>

      {loading ? (
        <div className="space-y-4">{Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="bg-white rounded-2xl border border-slate-100 p-6 animate-pulse">
            <div className="h-4 bg-slate-100 rounded-lg w-1/3 mb-2" />
            <div className="h-3 bg-slate-50 rounded-lg w-1/2" />
          </div>
        ))}</div>
      ) : (
        <div className="relative pl-10">
          <div className="absolute left-[19px] top-3 bottom-3 w-0.5 bg-slate-100 rounded-full" />
          <div className="space-y-3">
            {topics.map((topic: any, idx: number) => {
              const cfg = statusConfig[topic.status] || statusConfig.available;
              const isDone = topic.status === "completed";
              const isActive = topic.status === "in_progress";
              return (
                <div key={topic.topic_id || idx} className="relative flex items-start gap-5">
                  <div className={`absolute -left-[31px] top-3 w-6 h-6 rounded-full border-2 flex items-center justify-center z-10 ${isDone ? "border-emerald-500 bg-emerald-500" : isActive ? "border-indigo-600 bg-indigo-600 shadow-sm shadow-indigo-200" : "border-slate-200 bg-white"}`}>
                    {isDone ? <span className="text-white text-[10px] font-bold">✓</span> :
                     isActive ? <span className="text-white text-[10px] font-bold">▶</span> :
                     <span className="w-2 h-2 rounded-full bg-slate-300" />}
                  </div>
                  <div className={`flex-1 p-5 rounded-2xl border transition-all duration-200 ${cfg.bg} ${topic.status === "locked" ? "opacity-40" : "hover:shadow-sm cursor-pointer"}`}>
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">第 {idx + 1} 步</span>
                        <h3 className="font-bold text-slate-800 mt-1">{topic.topic_name}</h3>
                      </div>
                      <span className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold tracking-wide ${isDone ? "bg-emerald-100 text-emerald-700" : isActive ? "bg-indigo-100 text-indigo-700" : "bg-slate-100 text-slate-400"}`}>
                        {cfg.label}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-2 flex items-center gap-3">
                      <span>{"⭐".repeat(topic.difficulty || 1)}</span>
                      <span>预计 {topic.estimated_hours || 2}h</span>
                    </p>
                    {topic.status === "available" || topic.status === "in_progress" ? (
                      <a href="/resources" className="mt-3 inline-block text-sm font-medium text-indigo-600 hover:text-indigo-700">开始学习 →</a>
                    ) : null}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="mt-8 flex justify-center">
        <button onClick={handleRegen} disabled={generating}
          className="px-6 py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 text-white rounded-xl font-medium text-sm hover:shadow-md hover:shadow-indigo-200 disabled:opacity-50 transition-all active:scale-95">
          {generating ? "规划中..." : "基于最新画像重新规划"}
        </button>
      </div>
    </div>
  );
}
