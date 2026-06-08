"use client";

import { useState, useEffect, useCallback } from "react";
import { exercises } from "@/lib/api";
import { getMockQuestions } from "@/lib/mockData";

const TYPE_LABELS: Record<string, string> = {
  multiple_choice: "选择题", true_false: "判断题", coding: "编程题",
  short_answer: "简答题", fill_blank: "填空题",
};

export default function ExercisesPage() {
  const [questions, setQuestions] = useState<any[]>([]);
  const [selectedType, setSelectedType] = useState("all");
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [answers, setAnswers] = useState<Record<string, { submitted: boolean; result?: any; hintLevel: number; hint?: string }>>({});

  const fetchQuestions = useCallback(async () => {
    setLoading(true);
    try {
      const data = await exercises.list({
        question_type: selectedType === "all" ? undefined : selectedType,
        difficulty: selectedDifficulty ? Number(selectedDifficulty) : undefined,
      });
      setQuestions(data.exercises?.length ? data.exercises : getMockQuestions());
    } catch {
      setQuestions(getMockQuestions(undefined, selectedType === "all" ? undefined : selectedType));
    } finally {
      setLoading(false);
    }
  }, [selectedType, selectedDifficulty]);

  useEffect(() => {
    fetchQuestions();
  }, [fetchQuestions]);

  const handleSubmit = async (qId: string, answer: string) => {
    try {
      const result = await exercises.submit({ student_id: "demo", exercise_id: qId, answer });
      setAnswers((prev) => ({ ...prev, [qId]: { submitted: true, result, hintLevel: prev[qId]?.hintLevel || 1 } }));
    } catch {
      setAnswers((prev) => ({
        ...prev,
        [qId]: { submitted: true, result: { is_correct: Math.random() > 0.5, correct_answer: "（演示模式）", explanation: "演示模式下的模拟结果" }, hintLevel: prev[qId]?.hintLevel || 1 },
      }));
    }
  };

  const handleShowHint = async (qId: string) => {
    const currentLevel = (answers[qId]?.hintLevel || 0) + 1;
    try {
      const data = await exercises.getHints(qId, currentLevel);
      const hint = data?.hint || "暂无更多提示";
      setAnswers((prev) => ({
        ...prev,
        [qId]: { ...prev[qId], hintLevel: currentLevel, hint },
      }));
    } catch {
      const mockQs = getMockQuestions();
      const q = mockQs.find((mq) => mq.id === qId);
      const hints = q?.hints || [];
      const idx = Math.min(currentLevel - 1, hints.length - 1);
      setAnswers((prev) => ({
        ...prev,
        [qId]: { ...prev[qId], hintLevel: currentLevel, hint: hints[idx] || "暂无提示" },
      }));
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">练习中心</h1>
        <p className="text-gray-600 mt-1">通过多种类型的练习巩固知识点。</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-6">
        <select value={selectedType} onChange={(e) => setSelectedType(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none">
          <option value="all">全部题型</option>
          <option value="multiple_choice">选择题</option>
          <option value="true_false">判断题</option>
          <option value="coding">编程题</option>
          <option value="short_answer">简答题</option>
          <option value="fill_blank">填空题</option>
        </select>
        <select value={selectedDifficulty} onChange={(e) => setSelectedDifficulty(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none">
          <option value="">全部难度</option>
          <option value="1">⭐ 基础</option>
          <option value="2">⭐⭐ 入门</option>
          <option value="3">⭐⭐⭐ 进阶</option>
          <option value="4">⭐⭐⭐⭐ 挑战</option>
          <option value="5">⭐⭐⭐⭐⭐ 竞赛</option>
        </select>
      </div>

      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-xl border border-gray-200 p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-2/3 mb-3" />
              <div className="h-3 bg-gray-100 rounded w-full mb-2" />
              <div className="h-3 bg-gray-100 rounded w-1/2" />
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {questions.map((q) => {
            const ans = answers[q.id];
            return (
              <div key={q.id} className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-md transition-shadow">
                <div className="flex items-center gap-3 mb-3">
                  <span className="px-2 py-1 bg-indigo-50 text-indigo-600 text-xs font-medium rounded">
                    {TYPE_LABELS[q.question_type] || q.question_type}
                  </span>
                  <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded">
                    难度 {"⭐".repeat(q.difficulty || 1)}
                  </span>
                  <span className="px-2 py-1 bg-green-50 text-green-600 text-xs font-medium rounded">
                    {q.topic || "数据结构"}
                  </span>
                </div>
                <p className="text-gray-900 font-medium mb-4">{q.question_text}</p>

                {/* Multiple choice options */}
                {q.options && (
                  <div className="space-y-2 mb-4">
                    {q.options.map((opt: any) => (
                      <label key={opt.key} className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer">
                        <input type="radio" name={`q-${q.id}`} className="text-indigo-600" />
                        <span className="text-sm text-gray-700">{opt.key}. {opt.value}</span>
                      </label>
                    ))}
                  </div>
                )}

                {/* True/false */}
                {q.question_type === "true_false" && (
                  <div className="flex gap-4 mb-4">
                    {["正确", "错误"].map((label) => (
                      <label key={label} className="flex items-center gap-2 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer">
                        <input type="radio" name={`q-${q.id}`} className="text-indigo-600" /> {label}
                      </label>
                    ))}
                  </div>
                )}

                {/* Short answer / fill blank */}
                {(q.question_type === "short_answer" || q.question_type === "fill_blank" || q.question_type === "coding") && (
                  <textarea className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none mb-4"
                    rows={q.question_type === "coding" ? 5 : 2}
                    placeholder={q.question_type === "coding" ? "请输入你的代码..." : "请输入你的答案..."} />
                )}

                {/* Result display */}
                {ans?.submitted && ans?.result && (
                  <div className={`mb-4 p-3 rounded-lg text-sm ${ans.result.is_correct ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
                    <p className="font-medium">{ans.result.is_correct ? "✅ 回答正确！" : "❌ 回答错误"}</p>
                    {ans.result.correct_answer && <p className="mt-1">正确答案: {ans.result.correct_answer}</p>}
                    {ans.result.explanation && <p className="mt-1 text-xs">{ans.result.explanation}</p>}
                  </div>
                )}

                {/* Hint display */}
                {ans?.hint && (
                  <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-700">
                    💡 提示: {ans.hint}
                  </div>
                )}

                <div className="flex gap-3">
                  <button onClick={() => handleSubmit(q.id, "answer")}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 transition-colors">
                    提交答案
                  </button>
                  <button onClick={() => handleShowHint(q.id)}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm hover:bg-gray-50 transition-colors">
                    显示提示
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
