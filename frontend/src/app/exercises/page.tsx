"use client";

import { useState, useEffect, useCallback } from "react";
import { exercises } from "@/lib/api";
import { getMockQuestions } from "@/lib/mockData";

const TYPE_CONFIG: Record<string, { label: string; color: string }> = {
  multiple_choice: { label: "选择题", color: "bg-blue-50 text-blue-700 border-blue-200" },
  true_false: { label: "判断题", color: "bg-emerald-50 text-emerald-700 border-emerald-200" },
  coding: { label: "编程题", color: "bg-amber-50 text-amber-700 border-amber-200" },
  short_answer: { label: "简答题", color: "bg-violet-50 text-violet-700 border-violet-200" },
  fill_blank: { label: "填空题", color: "bg-rose-50 text-rose-700 border-rose-200" },
};

export default function ExercisesPage() {
  const [questions, setQuestions] = useState<any[]>([]);
  const [selectedType, setSelectedType] = useState("all");
  const [selectedDifficulty, setSelectedDifficulty] = useState("");
  const [loading, setLoading] = useState(true);
  const [answers, setAnswers] = useState<Record<string, { submitted: boolean; result?: any; hintLevel: number; hint?: string }>>({});

  const fetchQ = useCallback(async () => {
    setLoading(true);
    try {
      const d = await exercises.list({
        question_type: selectedType === "all" ? undefined : selectedType,
        difficulty: selectedDifficulty ? Number(selectedDifficulty) : undefined,
      });
      setQuestions(d.exercises?.length ? d.exercises : getMockQuestions());
    } catch { setQuestions(getMockQuestions(undefined, selectedType === "all" ? undefined : selectedType)); }
    finally { setLoading(false); }
  }, [selectedType, selectedDifficulty]);

  useEffect(() => { fetchQ(); }, [fetchQ]);

  const handleSubmit = async (qId: string, answer: string) => {
    try {
      const r = await exercises.submit({ student_id: "demo", exercise_id: qId, answer });
      setAnswers((p) => ({ ...p, [qId]: { submitted: true, result: r, hintLevel: p[qId]?.hintLevel || 1 } }));
    } catch {
      setAnswers((p) => ({ ...p, [qId]: { submitted: true, result: { is_correct: Math.random() > 0.5, correct_answer: "（演示）", explanation: "演示模式" }, hintLevel: p[qId]?.hintLevel || 1 } }));
    }
  };

  const handleHint = async (qId: string) => {
    const level = (answers[qId]?.hintLevel || 0) + 1;
    try {
      const d = await exercises.getHints(qId, level);
      setAnswers((p) => ({ ...p, [qId]: { ...p[qId], hintLevel: level, hint: d?.hint || "无更多提示" } }));
    } catch {
      const mq = getMockQuestions(); const q = mq.find((x) => x.id === qId);
      const hints = q?.hints || []; const idx = Math.min(level - 1, hints.length - 1);
      setAnswers((p) => ({ ...p, [qId]: { ...p[qId], hintLevel: level, hint: hints[idx] || "无提示" } }));
    }
  };

  return (
    <div className="page-enter max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">练习中心</h1>
        <p className="text-sm text-slate-500 mt-1">多种题型智能匹配，精准巩固薄弱点</p>
      </div>

      <div className="flex flex-wrap gap-3 mb-6">
        <select value={selectedType} onChange={(e) => setSelectedType(e.target.value)}
          className="px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm text-slate-700 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 outline-none shadow-sm">
          <option value="all">全部题型</option>
          <option value="multiple_choice">选择题</option>
          <option value="true_false">判断题</option>
          <option value="coding">编程题</option>
          <option value="short_answer">简答题</option>
          <option value="fill_blank">填空题</option>
        </select>
        <select value={selectedDifficulty} onChange={(e) => setSelectedDifficulty(e.target.value)}
          className="px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm text-slate-700 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 outline-none shadow-sm">
          <option value="">全部难度</option>
          <option value="1">⭐ 基础</option>
          <option value="2">⭐⭐ 入门</option>
          <option value="3">⭐⭐⭐ 进阶</option>
          <option value="4">⭐⭐⭐⭐ 挑战</option>
          <option value="5">⭐⭐⭐⭐⭐ 竞赛</option>
        </select>
      </div>

      {loading ? (
        <div className="space-y-4">{[1, 2, 3].map((i) => <div key={i} className="bg-white rounded-2xl border border-slate-100 p-6 animate-pulse"><div className="h-4 bg-slate-100 rounded-lg w-2/3 mb-3" /><div className="h-3 bg-slate-50 rounded-lg w-full mb-2" /><div className="h-3 bg-slate-50 rounded-lg w-1/2" /></div>)}</div>
      ) : (
        <div className="space-y-4">
          {questions.map((q) => {
            const ans = answers[q.id]; const tc = TYPE_CONFIG[q.question_type] || TYPE_CONFIG.multiple_choice;
            return (
              <div key={q.id} className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6 hover:shadow-md transition-shadow">
                <div className="flex items-center gap-2.5 mb-4">
                  <span className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold tracking-wide border ${tc.color}`}>{tc.label}</span>
                  <span className="text-[11px] text-slate-400 font-medium">{"⭐".repeat(q.difficulty || 1)}</span>
                  <span className="text-[11px] text-slate-300">·</span>
                  <span className="text-[11px] text-slate-400">{q.topic || "数据结构"}</span>
                </div>
                <p className="text-sm font-semibold text-slate-800 mb-4 leading-relaxed">{q.question_text}</p>

                {q.options && (
                  <div className="space-y-2 mb-4">
                    {q.options.map((opt: any) => (
                      <label key={opt.key} className="flex items-center gap-3 p-3.5 rounded-xl border border-slate-100 hover:bg-slate-50 cursor-pointer transition-colors">
                        <div className="w-5 h-5 rounded-full border-2 border-slate-200 flex items-center justify-center shrink-0">
                          <input type="radio" name={`q-${q.id}`} className="sr-only peer" />
                          <div className="w-2.5 h-2.5 rounded-full bg-indigo-500 opacity-0 peer-checked:opacity-100 transition-opacity" />
                        </div>
                        <span className="text-sm text-slate-600">{opt.key}. {opt.value}</span>
                      </label>
                    ))}
                  </div>
                )}

                {q.question_type === "true_false" && (
                  <div className="flex gap-3 mb-4">
                    {["正确", "错误"].map((l) => (
                      <label key={l} className="flex items-center gap-2.5 px-5 py-3 rounded-xl border border-slate-100 hover:bg-slate-50 cursor-pointer text-sm text-slate-600">
                        <div className="w-5 h-5 rounded-full border-2 border-slate-200 flex items-center justify-center"><input type="radio" name={`q-${q.id}`} className="sr-only peer" /><div className="w-2.5 h-2.5 rounded-full bg-indigo-500 opacity-0 peer-checked:opacity-100" /></div>
                        {l}
                      </label>
                    ))}
                  </div>
                )}

                {(q.question_type === "short_answer" || q.question_type === "fill_blank" || q.question_type === "coding") && (
                  <textarea className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 outline-none mb-4 resize-none" rows={q.question_type === "coding" ? 5 : 2} placeholder="输入你的答案..." />
                )}

                {ans?.submitted && ans?.result && (
                  <div className={`mb-4 p-4 rounded-xl text-sm ${ans.result.is_correct ? "bg-emerald-50 border border-emerald-100 text-emerald-800" : "bg-red-50 border border-red-100 text-red-800"}`}>
                    <p className="font-semibold">{ans.result.is_correct ? "✓ 回答正确" : "✗ 回答错误"}</p>
                    {ans.result.correct_answer && <p className="mt-1 text-xs opacity-75">正确答案: {ans.result.correct_answer}</p>}
                    {ans.result.explanation && <p className="mt-1.5 text-xs opacity-80">{ans.result.explanation}</p>}
                  </div>
                )}

                {ans?.hint && (
                  <div className="mb-4 p-4 rounded-xl bg-amber-50 border border-amber-100 text-amber-800 text-sm">
                    <span className="font-semibold">💡 提示:</span> {ans.hint}
                  </div>
                )}

                <div className="flex gap-3">
                  <button onClick={() => handleSubmit(q.id, "answer")} className="px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 text-white rounded-xl text-sm font-medium hover:shadow-md hover:shadow-indigo-200 transition-all active:scale-95">提交答案</button>
                  <button onClick={() => handleHint(q.id)} className="px-5 py-2.5 bg-white border border-slate-200 text-slate-600 rounded-xl text-sm font-medium hover:bg-slate-50 transition-colors">显示提示</button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
