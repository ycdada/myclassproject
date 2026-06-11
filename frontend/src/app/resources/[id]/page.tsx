"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { resources } from "@/lib/api";
import { MOCK_RESOURCES } from "@/lib/mockData";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

export default function ResourceDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [resource, setResource] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function f() {
      try { const d = await resources.get(id as string); setResource(d); }
      catch { setResource(MOCK_RESOURCES.find((r) => r.id === id) || MOCK_RESOURCES[0]); }
      finally { setLoading(false); }
    }
    f();
  }, [id]);

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12 animate-pulse space-y-4">
        <div className="h-6 bg-slate-100 rounded-lg w-1/4" />
        <div className="h-8 bg-slate-100 rounded-lg w-2/3" />
        <div className="h-4 bg-slate-50 rounded-lg w-full" />
        <div className="h-4 bg-slate-50 rounded-lg w-5/6" />
        <div className="h-64 bg-slate-50 rounded-2xl mt-6" />
      </div>
    );
  }

  if (!resource) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <span className="text-5xl">🔍</span>
        <h2 className="text-xl font-bold text-slate-800 mt-4">资源未找到</h2>
        <Link href="/resources" className="mt-4 inline-block text-sm text-indigo-600 hover:text-indigo-700">← 返回资源列表</Link>
      </div>
    );
  }

  const isMindmap = resource.resource_type === "mindmap";
  const content = resource.content || "";

  const typeConfig: Record<string, { label: string; color: string }> = {
    lecture: { label: "课程讲义", color: "bg-blue-50 text-blue-700" },
    mindmap: { label: "思维导图", color: "bg-violet-50 text-violet-700" },
    code: { label: "代码案例", color: "bg-emerald-50 text-emerald-700" },
    reading: { label: "拓展阅读", color: "bg-rose-50 text-rose-700" },
  };
  const tc = typeConfig[resource.resource_type] || { label: resource.resource_type, color: "bg-slate-50 text-slate-600" };

  return (
    <div className="page-enter max-w-3xl mx-auto px-4 py-8">
      <Link href="/resources" className="text-sm font-medium text-indigo-600 hover:text-indigo-700 mb-6 inline-flex items-center gap-1">← 返回资源列表</Link>

      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-8">
        <div className="flex items-center gap-3 mb-6">
          <span className={`px-3 py-1 rounded-lg text-xs font-semibold ${tc.color}`}>{tc.label}</span>
          {resource.metadata?.difficulty && (
            <span className="text-xs text-slate-300 font-medium">{"◇".repeat(resource.metadata.difficulty)}</span>
          )}
          {resource.metadata?.estimated_time && (
            <span className="text-xs text-slate-300">{resource.metadata.estimated_time}</span>
          )}
        </div>

        <h1 className="text-2xl font-bold text-slate-900 mb-8 tracking-tight">{resource.title}</h1>

        {isMindmap ? (
          <div className="border border-slate-100 rounded-2xl p-6 bg-slate-50 overflow-x-auto">
            <pre className="text-sm text-slate-600 font-mono leading-relaxed">{content}</pre>
          </div>
        ) : (
          <article className="prose prose-slate max-w-none prose-headings:font-bold prose-headings:text-slate-900 prose-h2:text-xl prose-h2:mt-8 prose-h2:mb-4 prose-h3:text-lg prose-h3:mt-6 prose-h3:mb-3 prose-p:text-sm prose-p:leading-7 prose-p:text-slate-600 prose-code:text-pink-600 prose-code:bg-slate-50 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-xs prose-pre:rounded-2xl prose-pre:border prose-pre:border-slate-100 prose-table:text-sm prose-th:bg-slate-50 prose-th:px-4 prose-th:py-2 prose-td:px-4 prose-td:py-2">
            <ReactMarkdown
              remarkPlugins={[remarkMath]}
              rehypePlugins={[rehypeKatex]}
              components={{
                code({ className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || "");
                  const code = String(children).replace(/\n$/, "");
                  const isInline = !match;
                  return isInline ? (
                    <code className="text-pink-600 bg-slate-50 px-1.5 py-0.5 rounded text-xs">{children}</code>
                  ) : (
                    <div className="my-5 rounded-2xl overflow-hidden border border-slate-200">
                      <div className="flex items-center justify-between px-4 py-2.5 bg-slate-800 text-slate-300 text-xs">
                        <span className="font-mono font-semibold">{match?.[1] || "code"}</span>
                      </div>
                      <pre className="bg-slate-900 text-slate-100 p-5 overflow-x-auto text-sm leading-relaxed"><code className={`language-${match?.[1] || ""}`}>{code}</code></pre>
                    </div>
                  );
                },
              }}
            >
              {content}
            </ReactMarkdown>
          </article>
        )}
      </div>
    </div>
  );
}
