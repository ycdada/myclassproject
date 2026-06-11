"use client";

import { useState, useEffect } from "react";
import { assessment } from "@/lib/api";
import { getMockAssessment } from "@/lib/mockData";

export default function AssessmentPage() {
  const [report, setReport] = useState(getMockAssessment().report);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    async function f() {
      try { const d = await assessment.getReport("demo"); setReport(d.overall_mastery !== undefined ? d : getMockAssessment().report); }
      catch { setReport(getMockAssessment().report); }
      finally { setLoading(false); }
    }
    f();
  }, []);

  const masteryData = [
    { topic: "复杂度分析", score: 50 }, { topic: "数组", score: 30 }, { topic: "链表", score: 15 },
    { topic: "栈与队列", score: 5 }, { topic: "树结构", score: 0 }, { topic: "图算法", score: 0 },
    { topic: "排序算法", score: 0 }, { topic: "哈希表", score: 0 },
  ];

  return (
    <div className="page-enter max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">学习评估</h1>
        <p className="text-sm text-slate-500 mt-1">多维度追踪学习效果，动态优化学习策略</p>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">{[1, 2, 3, 4].map((i) => <div key={i} className="bg-white rounded-2xl border border-slate-100 p-6 animate-pulse"><div className="h-3 bg-slate-100 rounded-lg w-2/3 mb-3" /><div className="h-5 bg-slate-100 rounded-lg w-1/3" /></div>)}</div>
      ) : (
        <>
          {/* Summary */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {[
              { label: "整体掌握度", value: `${Math.round(report.overall_mastery * 100)}%`, gradient: "from-indigo-500 to-blue-600", bar: Math.round(report.overall_mastery * 100) },
              { label: "学习进度", value: `${Math.round(report.learning_velocity * 20)}%`, gradient: "from-emerald-500 to-teal-600", bar: Math.round(report.learning_velocity * 20) },
              { label: "学习投入度", value: `${Math.round(report.engagement_score * 100)}%`, gradient: "from-amber-500 to-orange-600", bar: Math.round(report.engagement_score * 100) },
              { label: "学习速度", value: `${report.learning_velocity?.toFixed(1) || "--"} /周`, gradient: "from-rose-500 to-pink-600", bar: 0 },
            ].map((item) => (
              <div key={item.label} className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5 hover:shadow-md transition-shadow">
                <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-3">{item.label}</p>
                <p className="text-3xl font-bold text-slate-900 tracking-tight">{item.value}</p>
                <div className="mt-3 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                  <div className={`h-full rounded-full bg-gradient-to-r ${item.gradient} transition-all duration-700`} style={{ width: `${item.bar}%` }} />
                </div>
              </div>
            ))}
          </div>

          {/* Mastery */}
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6 mb-8">
            <h2 className="text-base font-bold text-slate-900 mb-5">知识点掌握度</h2>
            <div className="space-y-4">
              {masteryData.map((item) => (
                <div key={item.topic} className="flex items-center gap-4">
                  <span className="w-24 text-xs font-medium text-slate-500 shrink-0">{item.topic}</span>
                  <div className="flex-1 h-2.5 bg-slate-100 rounded-full overflow-hidden">
                    <div className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 transition-all duration-700" style={{ width: `${item.score}%` }} />
                  </div>
                  <span className="w-10 text-xs font-semibold text-slate-400 text-right shrink-0">{item.score}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Strengths & Weaknesses */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6">
              <h2 className="text-sm font-bold text-emerald-700 mb-3">✓ 优势领域</h2>
              {report.strengths?.length ? (
                <ul className="space-y-2">{report.strengths.map((s: string, i: number) => <li key={i} className="flex items-center gap-2 text-sm text-slate-600"><span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0" />{s}</li>)}</ul>
              ) : <p className="text-sm text-slate-400">继续学习以发现优势领域</p>}
            </div>
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6">
              <h2 className="text-sm font-bold text-amber-700 mb-3">↗ 待提升</h2>
              {report.weaknesses?.length ? (
                <ul className="space-y-2">{report.weaknesses.map((w: any, i: number) => <li key={i} className="flex items-center gap-2 text-sm text-slate-600"><span className="w-1.5 h-1.5 rounded-full bg-amber-400 shrink-0" />{w.topic}: {w.gap_description}</li>)}</ul>
              ) : <p className="text-sm text-slate-400">完成更多练习来定位薄弱环节</p>}
            </div>
          </div>

          {/* Recommendations */}
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6">
            <h2 className="text-base font-bold text-slate-900 mb-4">学习建议</h2>
            {report.recommendations?.length ? (
              <div className="space-y-3">
                {report.recommendations.map((rec: any, i: number) => (
                  <div key={i} className="flex items-center gap-4 p-4 rounded-xl bg-gradient-to-r from-indigo-50 to-violet-50 border border-indigo-100">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center text-white text-lg shrink-0 shadow-sm">
                      {rec.action === "review" ? "◈" : "◎"}
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-indigo-800">{rec.action === "review" ? "复习薄弱知识点" : "针对性练习"}</p>
                      <p className="text-xs text-indigo-400">推荐 {rec.resource_type} · 优先级 {rec.priority}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : <p className="text-sm text-slate-400">完成评估后将自动生成个性化建议</p>}
            <button onClick={async () => { setSubmitting(true); try { await assessment.selfEval("demo", "dsa_intro", 0.8); } catch {} finally { setSubmitting(false); alert("已提交"); }}} disabled={submitting}
              className="mt-5 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 text-white rounded-xl text-sm font-medium hover:shadow-md hover:shadow-indigo-200 transition-all disabled:opacity-50">
              {submitting ? "提交中..." : "自我评估掌握度"}
            </button>
          </div>
        </>
      )}
    </div>
  );
}
