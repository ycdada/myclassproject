"use client";

import { useState } from "react";

const RESOURCE_TYPES = [
  { id: "all", label: "全部", icon: "📋" },
  { id: "lecture", label: "课程讲义", icon: "📝" },
  { id: "mindmap", label: "思维导图", icon: "🧠" },
  { id: "exercise", label: "练习题", icon: "✏️" },
  { id: "reading", label: "拓展阅读", icon: "📖" },
  { id: "video", label: "教学视频", icon: "🎬" },
  { id: "code", label: "代码案例", icon: "💻" },
];

export default function ResourcesPage() {
  const [activeType, setActiveType] = useState("all");

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">学习资源</h1>
        <p className="text-gray-600 mt-1">
          浏览和搜索系统为你个性化生成的学习资源。
        </p>
      </div>

      {/* Resource Type Filter */}
      <div className="flex flex-wrap gap-2 mb-6">
        {RESOURCE_TYPES.map((type) => (
          <button
            key={type.id}
            onClick={() => setActiveType(type.id)}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeType === type.id
                ? "bg-indigo-600 text-white"
                : "bg-white text-gray-600 border border-gray-200 hover:border-indigo-300 hover:text-indigo-600"
            }`}
          >
            <span>{type.icon}</span>
            <span>{type.label}</span>
          </button>
        ))}
      </div>

      {/* Resources Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Empty state */}
        <div className="col-span-full bg-white rounded-xl border border-dashed border-gray-300 p-12 text-center">
          <span className="text-5xl">📚</span>
          <h3 className="mt-4 text-lg font-medium text-gray-900">还没有学习资源</h3>
          <p className="mt-2 text-gray-500">
            完成学习画像构建后，系统将为你自动生成个性化的学习资源。
          </p>
          <a
            href="/chat"
            className="mt-4 inline-block px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            开始构建画像 →
          </a>
        </div>
      </div>
    </div>
  );
}
