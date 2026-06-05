"use client";

const DUMMY_PATH = [
  { id: "dsa_intro", name: "数据结构与算法导论", difficulty: 1, category: "基础", status: "available", order: 1 },
  { id: "complexity_analysis", name: "复杂度分析", difficulty: 2, category: "基础", status: "available", order: 2 },
  { id: "arrays", name: "数组", difficulty: 1, category: "数据结构", status: "available", order: 3 },
  { id: "linked_lists", name: "链表", difficulty: 2, category: "数据结构", status: "locked", order: 4 },
  { id: "stacks", name: "栈", difficulty: 2, category: "数据结构", status: "locked", order: 5 },
  { id: "queues", name: "队列", difficulty: 2, category: "数据结构", status: "locked", order: 6 },
];

export default function LearningPathPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">个性化学习路径</h1>
        <p className="text-gray-600 mt-1">
          依据你的学习画像和知识图谱，为你规划最优学习路径。
        </p>
      </div>

      {/* Path Timeline */}
      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200" />

        <div className="space-y-4">
          {DUMMY_PATH.map((topic) => (
            <div key={topic.id} className="relative flex items-start gap-6">
              {/* Node */}
              <div
                className={`relative z-10 w-16 h-16 rounded-xl flex items-center justify-center text-lg font-bold shadow-sm ${
                  topic.status === "available"
                    ? "bg-indigo-600 text-white"
                    : "bg-gray-200 text-gray-400"
                }`}
              >
                {topic.status === "available" ? topic.order : "🔒"}
              </div>

              {/* Content */}
              <div
                className={`flex-1 p-5 rounded-xl border ${
                  topic.status === "available"
                    ? "bg-white border-gray-200 hover:shadow-md cursor-pointer"
                    : "bg-gray-50 border-gray-200 opacity-60"
                } transition-shadow`}
              >
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-gray-900">{topic.name}</h3>
                  <span className="text-sm text-gray-500">
                    {"⭐".repeat(topic.difficulty)}
                  </span>
                </div>
                <p className="text-sm text-gray-500 mt-1">{topic.category}</p>
                {topic.status === "available" && (
                  <button className="mt-3 text-sm text-indigo-600 hover:text-indigo-700 font-medium">
                    开始学习 →
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-8 text-center">
        <button className="px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors font-medium">
          基于最新画像重新规划
        </button>
      </div>
    </div>
  );
}
