"use client";

import { useState } from "react";

const SAMPLE_QUESTIONS = [
  {
    id: "1",
    type: "multiple_choice",
    difficulty: 2,
    question: "在长度为n的数组中按值查找元素，时间复杂度是多少？",
    options: ["O(1)", "O(log n)", "O(n)", "O(n²)"],
    topic: "数组",
  },
  {
    id: "2",
    type: "true_false",
    difficulty: 1,
    question: "链表的插入和删除操作时间复杂度始终为O(1)。",
    topic: "链表",
  },
  {
    id: "3",
    type: "coding",
    difficulty: 3,
    question: "实现一个函数，反转一个单链表。",
    topic: "链表",
  },
];

const TYPE_LABELS: Record<string, string> = {
  multiple_choice: "选择题",
  true_false: "判断题",
  coding: "编程题",
  short_answer: "简答题",
  fill_blank: "填空题",
};

export default function ExercisesPage() {
  const [selectedType, setSelectedType] = useState<string>("all");
  const [selectedDifficulty, setSelectedDifficulty] = useState<number | null>(null);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">练习中心</h1>
        <p className="text-gray-600 mt-1">通过多种类型的练习巩固知识点。</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-6">
        <select
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
        >
          <option value="all">全部题型</option>
          <option value="multiple_choice">选择题</option>
          <option value="true_false">判断题</option>
          <option value="coding">编程题</option>
          <option value="short_answer">简答题</option>
          <option value="fill_blank">填空题</option>
        </select>
        <select
          value={selectedDifficulty || ""}
          onChange={(e) => setSelectedDifficulty(e.target.value ? Number(e.target.value) : null)}
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
        >
          <option value="">全部难度</option>
          <option value="1">⭐ 基础</option>
          <option value="2">⭐⭐ 入门</option>
          <option value="3">⭐⭐⭐ 进阶</option>
          <option value="4">⭐⭐⭐⭐ 挑战</option>
          <option value="5">⭐⭐⭐⭐⭐ 竞赛</option>
        </select>
      </div>

      {/* Questions List */}
      <div className="space-y-4">
        {SAMPLE_QUESTIONS.map((q) => (
          <div key={q.id} className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center gap-3 mb-3">
              <span className="px-2 py-1 bg-indigo-50 text-indigo-600 text-xs font-medium rounded">
                {TYPE_LABELS[q.type] || q.type}
              </span>
              <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded">
                难度 {"⭐".repeat(q.difficulty)}
              </span>
              <span className="px-2 py-1 bg-green-50 text-green-600 text-xs font-medium rounded">
                {q.topic}
              </span>
            </div>
            <p className="text-gray-900 font-medium mb-4">{q.question}</p>
            {q.options && (
              <div className="space-y-2">
                {q.options.map((opt, idx) => (
                  <label
                    key={idx}
                    className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer"
                  >
                    <input type="radio" name={`q-${q.id}`} className="text-indigo-600" />
                    <span className="text-sm text-gray-700">
                      {String.fromCharCode(65 + idx)}. {opt}
                    </span>
                  </label>
                ))}
              </div>
            )}
            <div className="mt-4 flex gap-3">
              <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 transition-colors">
                提交答案
              </button>
              <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm hover:bg-gray-50 transition-colors">
                显示提示
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
