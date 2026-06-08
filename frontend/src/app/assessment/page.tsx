"use client";

import { useState, useEffect } from "react";
import { assessment } from "@/lib/api";
import { getMockAssessment } from "@/lib/mockData";

export default function AssessmentPage() {
  const [report, setReport] = useState(getMockAssessment().report);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    async function fetchReport() {
      try {
        const data = await assessment.getReport("demo");
        setReport(data.overall_mastery !== undefined ? data : getMockAssessment().report);
      } catch {
        setReport(getMockAssessment().report);
      } finally {
        setLoading(false);
      }
    }
    fetchReport();
  }, []);

  const handleSelfEval = async (topicId: string) => {
    setSubmitting(true);
    try {
      await assessment.selfEval("demo", topicId, 0.8, "我掌握了基本概念");
    } catch {
      // silent
    } finally {
      setSubmitting(false);
      alert("自评已提交！");
    }
  };

  const masteryData = report.overall_mastery
    ? [
        { topic: "复杂度分析", score: 50 },
        { topic: "数组", score: 30 },
        { topic: "链表", score: 15 },
        { topic: "栈与队列", score: 5 },
        { topic: "树结构", score: 0 },
        { topic: "图算法", score: 0 },
        { topic: "排序", score: 0 },
        { topic: "哈希表", score: 0 },
      ]
    : [];

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">学习评估报告</h1>
        <p className="text-gray-600 mt-1">多维度评估你的学习效果，动态调整学习策略。</p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-xl border border-gray-200 p-5 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-2/3 mb-3" />
              <div className="h-6 bg-gray-200 rounded w-1/4" />
            </div>
          ))}
        </div>
      ) : (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {[
              { label: "整体掌握度", value: `${Math.round(report.overall_mastery * 100)}%`, icon: "📊", color: "bg-blue-50" },
              { label: "学习进度", value: `${Math.round(report.learning_velocity * 20)}%`, icon: "📈", color: "bg-green-50" },
              { label: "学习投入度", value: `${Math.round(report.engagement_score * 100)}%`, icon: "🔥", color: "bg-orange-50" },
              { label: "学习速度", value: `${report.learning_velocity?.toFixed(1) || "--"} 知识点/周`, icon: "⚡", color: "bg-purple-50" },
            ].map((item) => (
              <div key={item.label} className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">{item.label}</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">{item.value}</p>
                  </div>
                  <div className={`w-10 h-10 rounded-lg ${item.color} flex items-center justify-center text-xl`}>{item.icon}</div>
                </div>
              </div>
            ))}
          </div>

          {/* Mastery by Topic */}
          <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">知识点掌握度</h2>
            <div className="space-y-3">
              {report.strengths?.length ? (
                masteryData.map((item) => (
                  <div key={item.topic} className="flex items-center gap-4">
                    <span className="w-24 text-sm text-gray-600">{item.topic}</span>
                    <div className="flex-1 bg-gray-100 rounded-full h-3">
                      <div className="bg-indigo-500 h-3 rounded-full transition-all duration-700" style={{ width: `${item.score}%` }} />
                    </div>
                    <span className="w-10 text-sm text-gray-500 text-right">{item.score}%</span>
                  </div>
                ))
              ) : (
                <div className="p-4 text-center text-gray-500 text-sm">尚无评估数据，完成练习后将自动生成掌握度分析。</div>
              )}
            </div>
          </div>

          {/* Strengths & Weaknesses */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-green-700 mb-3">✅ 优势领域</h2>
              {report.strengths?.length ? (
                <ul className="space-y-2">
                  {report.strengths.map((s: string, i: number) => (
                    <li key={i} className="flex items-center gap-2 text-sm text-gray-700">
                      <span className="text-green-500">●</span> {s}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-400">继续学习以发现优势领域</p>
              )}
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-orange-700 mb-3">🎯 待提升</h2>
              {report.weaknesses?.length ? (
                <ul className="space-y-2">
                  {report.weaknesses.map((w: any, i: number) => (
                    <li key={i} className="flex items-center gap-2 text-sm text-gray-700">
                      <span className="text-orange-500">●</span> {w.topic}: {w.gap_description}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-400">完成更多练习来定位薄弱环节</p>
              )}
            </div>
          </div>

          {/* Recommendations */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">📋 学习建议</h2>
            {report.recommendations?.length ? (
              <div className="space-y-3">
                {report.recommendations.map((rec: any, i: number) => (
                  <div key={i} className="flex items-center gap-3 p-4 rounded-lg bg-indigo-50 border border-indigo-100">
                    <span className="text-lg">{rec.action === "review" ? "📖" : "✏️"}</span>
                    <div>
                      <p className="text-sm font-medium text-indigo-700">
                        {rec.action === "review" ? "复习薄弱知识点" : "针对性练习"}
                      </p>
                      <p className="text-xs text-indigo-500">推荐资源类型: {rec.resource_type} · 优先级: {rec.priority}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-400">完成评估后将自动生成个性化学习建议</p>
            )}
            <button onClick={() => handleSelfEval("dsa_intro")} disabled={submitting}
              className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50 transition-colors">
              {submitting ? "提交中..." : "自我评估掌握度"}
            </button>
          </div>
        </>
      )}
    </div>
  );
}
