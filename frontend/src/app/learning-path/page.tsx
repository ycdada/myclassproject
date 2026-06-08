"use client";

import { useState, useEffect } from "react";
import { learningPath } from "@/lib/api";
import { getMockLearningPath } from "@/lib/mockData";

export default function LearningPathPage() {
  const [topics, setTopics] = useState<any[]>(getMockLearningPath());
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    async function fetchPath() {
      try {
        const data = await learningPath.getCurrent("demo");
        setTopics(data.topics_sequence?.length ? data.topics_sequence : getMockLearningPath());
      } catch {
        setTopics(getMockLearningPath());
      } finally {
        setLoading(false);
      }
    }
    fetchPath();
  }, []);

  const handleRegenerate = async () => {
    setGenerating(true);
    try {
      const data = await learningPath.generate("demo");
      setTopics(data.topics_sequence || getMockLearningPath());
    } catch {
      setTopics(getMockLearningPath());
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">个性化学习路径</h1>
        <p className="text-gray-600 mt-1">依据你的学习画像和知识图谱，为你规划最优学习路径。</p>
      </div>

      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="bg-white rounded-xl border border-gray-200 p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/3 mb-2" />
              <div className="h-3 bg-gray-100 rounded w-1/2" />
            </div>
          ))}
        </div>
      ) : (
        <div className="relative">
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200" />
          <div className="space-y-4">
            {topics.map((topic: any) => (
              <div key={topic.topic_id || topic.order} className="relative flex items-start gap-6">
                <div className={`relative z-10 w-16 h-16 rounded-xl flex items-center justify-center text-lg font-bold shadow-sm ${
                  topic.status === "completed" ? "bg-green-500 text-white" :
                  topic.status === "in_progress" ? "bg-indigo-600 text-white" :
                  topic.status === "available" ? "bg-blue-500 text-white" :
                  "bg-gray-200 text-gray-400"
                }`}>
                  {topic.status === "completed" ? "✓" :
                   topic.status === "in_progress" ? "▶" :
                   topic.status === "available" ? topic.order : "🔒"}
                </div>
                <div className={`flex-1 p-5 rounded-xl border ${
                  topic.status === "completed" || topic.status === "in_progress" || topic.status === "available"
                    ? "bg-white border-gray-200 hover:shadow-md cursor-pointer"
                    : "bg-gray-50 border-gray-200 opacity-60"
                } transition-shadow`}>
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-gray-900">{topic.topic_name}</h3>
                    <span className="text-sm text-gray-500">{"⭐".repeat(topic.difficulty || 1)}</span>
                  </div>
                  <p className="text-sm text-gray-500 mt-1">
                    {topic.category || "数据结构"} · 预计 {topic.estimated_hours || 2} 小时
                  </p>
                  {topic.status === "available" || topic.status === "in_progress" ? (
                    <a href="/resources" className="mt-3 inline-block text-sm text-indigo-600 hover:text-indigo-700 font-medium">
                      开始学习 →
                    </a>
                  ) : null}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-8 text-center">
        <button onClick={handleRegenerate} disabled={generating}
          className="px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-colors font-medium">
          {generating ? "重新规划中..." : "基于最新画像重新规划"}
        </button>
      </div>
    </div>
  );
}
