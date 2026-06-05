"use client";

export default function AssessmentPage() {
  const masteryData = [
    { topic: "复杂度分析", score: 0 },
    { topic: "数组", score: 0 },
    { topic: "链表", score: 0 },
    { topic: "栈与队列", score: 0 },
    { topic: "树结构", score: 0 },
    { topic: "图算法", score: 0 },
    { topic: "排序", score: 0 },
    { topic: "哈希表", score: 0 },
  ];

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">学习评估报告</h1>
        <p className="text-gray-600 mt-1">
          多维度评估你的学习效果，动态调整学习策略。
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[
          { label: "整体掌握度", value: "--", icon: "📊", color: "bg-blue-50" },
          { label: "学习进度", value: "0%", icon: "📈", color: "bg-green-50" },
          { label: "学习投入度", value: "--", icon: "🔥", color: "bg-orange-50" },
          { label: "学习速度", value: "--", icon: "⚡", color: "bg-purple-50" },
        ].map((item) => (
          <div key={item.label} className={`${item.color} rounded-xl p-5 border border-gray-200`}>
            <span className="text-2xl">{item.icon}</span>
            <p className="text-2xl font-bold text-gray-900 mt-2">{item.value}</p>
            <p className="text-sm text-gray-500">{item.label}</p>
          </div>
        ))}
      </div>

      {/* Mastery by Topic */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">知识点掌握度</h2>
        <div className="space-y-3">
          {masteryData.map((item) => (
            <div key={item.topic} className="flex items-center gap-4">
              <span className="w-24 text-sm text-gray-600">{item.topic}</span>
              <div className="flex-1 bg-gray-100 rounded-full h-3">
                <div
                  className="bg-indigo-500 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${item.score}%` }}
                />
              </div>
              <span className="w-10 text-sm text-gray-500 text-right">{item.score}%</span>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">学习建议</h2>
        <div className="p-8 text-center text-gray-500">
          <span className="text-4xl">🔍</span>
          <p className="mt-3">完成画像构建和初步学习后，系统将为你生成个性化的学习建议。</p>
        </div>
      </div>
    </div>
  );
}
