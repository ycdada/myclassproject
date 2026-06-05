"use client";

import { useState } from "react";

export default function Home() {
  const [studentName] = useState("同学");

  const stats = [
    { label: "已完成知识点", value: "0 / 30", icon: "📚", color: "bg-blue-50 text-blue-700" },
    { label: "已生成资源", value: "0", icon: "📄", color: "bg-green-50 text-green-700" },
    { label: "练习正确率", value: "--", icon: "✅", color: "bg-purple-50 text-purple-700" },
    { label: "学习时长", value: "0 分钟", icon: "⏱️", color: "bg-orange-50 text-orange-700" },
  ];

  const recentTopics = [
    { name: "数组", difficulty: 1, category: "数据结构", status: "recommended" },
    { name: "复杂度分析", difficulty: 2, category: "基础", status: "recommended" },
    { name: "链表", difficulty: 2, category: "数据结构", status: "locked" },
    { name: "栈与队列", difficulty: 2, category: "数据结构", status: "locked" },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          你好，{studentName} 👋
        </h1>
        <p className="mt-2 text-gray-600">
          欢迎来到数据结构与算法个性化学习系统。让我们开始今天的学习之旅！
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{stat.label}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
              </div>
              <div className={`w-10 h-10 rounded-lg ${stat.color} flex items-center justify-center text-xl`}>
                {stat.icon}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Learning Path Preview */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">推荐学习路径</h2>
            <a href="/learning-path" className="text-sm text-indigo-600 hover:text-indigo-700">
              查看全部 →
            </a>
          </div>
          <div className="space-y-3">
            {recentTopics.map((topic, idx) => (
              <div
                key={topic.name}
                className={`flex items-center gap-4 p-4 rounded-lg border ${
                  topic.status === "recommended"
                    ? "border-indigo-200 bg-indigo-50"
                    : "border-gray-200 bg-gray-50 opacity-60"
                }`}
              >
                <div className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center text-sm font-bold">
                  {idx + 1}
                </div>
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{topic.name}</p>
                  <p className="text-sm text-gray-500">
                    {topic.category} · 难度 {"⭐".repeat(topic.difficulty)}
                  </p>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-medium ${
                    topic.status === "recommended"
                      ? "bg-indigo-100 text-indigo-700"
                      : "bg-gray-200 text-gray-500"
                  }`}
                >
                  {topic.status === "recommended" ? "推荐学习" : "待解锁"}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">快速操作</h2>
          <div className="space-y-3">
            <a
              href="/chat"
              className="flex items-center gap-3 p-4 rounded-lg border border-gray-200 hover:border-indigo-300 hover:bg-indigo-50 transition-colors"
            >
              <span className="text-2xl">💬</span>
              <div>
                <p className="font-medium text-gray-900">构建学习画像</p>
                <p className="text-sm text-gray-500">通过对话让系统了解你</p>
              </div>
            </a>
            <a
              href="/resources"
              className="flex items-center gap-3 p-4 rounded-lg border border-gray-200 hover:border-indigo-300 hover:bg-indigo-50 transition-colors"
            >
              <span className="text-2xl">📚</span>
              <div>
                <p className="font-medium text-gray-900">浏览学习资源</p>
                <p className="text-sm text-gray-500">查看个性化生成的学习材料</p>
              </div>
            </a>
            <a
              href="/exercises"
              className="flex items-center gap-3 p-4 rounded-lg border border-gray-200 hover:border-indigo-300 hover:bg-indigo-50 transition-colors"
            >
              <span className="text-2xl">✏️</span>
              <div>
                <p className="font-medium text-gray-900">开始练习</p>
                <p className="text-sm text-gray-500">通过练习巩固知识点</p>
              </div>
            </a>
            <a
              href="/assessment"
              className="flex items-center gap-3 p-4 rounded-lg border border-gray-200 hover:border-indigo-300 hover:bg-indigo-50 transition-colors"
            >
              <span className="text-2xl">📈</span>
              <div>
                <p className="font-medium text-gray-900">查看评估报告</p>
                <p className="text-sm text-gray-500">了解你的学习进展</p>
              </div>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
