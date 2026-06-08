"use client";

import { useState, useEffect } from "react";
import { assessment, learningPath } from "@/lib/api";
import { MOCK_ASSESSMENT, MOCK_LEARNING_PATH } from "@/lib/mockData";

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
      } catch {
        // Already initialized with mock data
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const stats = [
    { label: "已完成知识点", value: `${dashboard.topics_completed} / ${dashboard.total_topics}`, icon: "📚", color: "bg-blue-50 text-blue-700" },
    { label: "已生成资源", value: `${dashboard.resources_generated || 4}`, icon: "📄", color: "bg-green-50 text-green-700" },
    { label: "练习正确率", value: dashboard.exercises_attempted ? `${Math.round((dashboard.exercises_correct / dashboard.exercises_attempted) * 100)}%` : "--", icon: "✅", color: "bg-purple-50 text-purple-700" },
    { label: "学习时长", value: `${dashboard.total_study_time_minutes} 分钟`, icon: "⏱️", color: "bg-orange-50 text-orange-700" },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">你好，同学 👋</h1>
        <p className="mt-2 text-gray-600">欢迎来到数据结构与算法个性化学习系统。让我们开始今天的学习之旅！</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((stat) => (
          <div key={stat.label} className={`bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow ${loading ? "animate-pulse" : ""}`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{stat.label}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
              </div>
              <div className={`w-10 h-10 rounded-lg ${stat.color} flex items-center justify-center text-xl`}>{stat.icon}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Learning Path Preview */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">推荐学习路径</h2>
            <a href="/learning-path" className="text-sm text-indigo-600 hover:text-indigo-700">查看全部 →</a>
          </div>
          <div className="space-y-3">
            {pathPreview.map((topic: any, idx: number) => (
              <div key={topic.topic_id || idx}
                className={`flex items-center gap-4 p-4 rounded-lg border ${
                  topic.status === "completed" || topic.status === "in_progress"
                    ? "border-indigo-200 bg-indigo-50"
                    : topic.status === "available"
                    ? "border-gray-200 bg-white"
                    : "border-gray-200 bg-gray-50 opacity-60"
                }`}
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                  topic.status === "completed" ? "bg-green-500 text-white" :
                  topic.status === "in_progress" ? "bg-indigo-600 text-white" :
                  "bg-gray-200 text-gray-500"
                }`}>
                  {topic.status === "completed" ? "✓" : topic.status === "in_progress" ? "▶" : idx + 1}
                </div>
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{topic.topic_name}</p>
                  <p className="text-sm text-gray-500">
                    {topic.category || "数据结构"} · 难度 {"⭐".repeat(topic.difficulty || 1)}
                  </p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  topic.status === "completed" ? "bg-green-100 text-green-700" :
                  topic.status === "in_progress" ? "bg-indigo-100 text-indigo-700" :
                  topic.status === "available" ? "bg-blue-100 text-blue-700" :
                  "bg-gray-200 text-gray-500"
                }`}>
                  {topic.status === "completed" ? "已完成" : topic.status === "in_progress" ? "学习中" : topic.status === "available" ? "可学习" : "待解锁"}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">快速操作</h2>
          <div className="space-y-3">
            {[
              { href: "/chat", icon: "💬", title: "构建学习画像", desc: "通过对话让系统了解你" },
              { href: "/resources", icon: "📚", title: "浏览学习资源", desc: "查看个性化生成的学习材料" },
              { href: "/exercises", icon: "✏️", title: "开始练习", desc: "通过练习巩固知识点" },
              { href: "/assessment", icon: "📈", title: "查看评估报告", desc: "了解你的学习进展" },
            ].map((item) => (
              <a key={item.href} href={item.href}
                className="flex items-center gap-3 p-4 rounded-lg border border-gray-200 hover:border-indigo-300 hover:bg-indigo-50 transition-colors">
                <span className="text-2xl">{item.icon}</span>
                <div>
                  <p className="font-medium text-gray-900">{item.title}</p>
                  <p className="text-sm text-gray-500">{item.desc}</p>
                </div>
              </a>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
