"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { resources } from "@/lib/api";
import { MOCK_RESOURCES } from "@/lib/mockData";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

export default function ResourceDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [resource, setResource] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showMindmap, setShowMindmap] = useState(false);

  useEffect(() => {
    async function fetch() {
      try {
        const data = await resources.get(id as string);
        setResource(data);
      } catch {
        setResource(MOCK_RESOURCES.find((r) => r.id === id) || MOCK_RESOURCES[0]);
      } finally {
        setLoading(false);
      }
    }
    fetch();
  }, [id]);

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-2/3 mb-4" />
        <div className="h-4 bg-gray-100 rounded w-full mb-2" />
        <div className="h-4 bg-gray-100 rounded w-5/6 mb-2" />
        <div className="h-64 bg-gray-100 rounded mt-6" />
      </div>
    );
  }

  if (!resource) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12 text-center">
        <span className="text-5xl">🔍</span>
        <h2 className="text-xl font-bold text-gray-900 mt-4">资源未找到</h2>
        <a href="/resources" className="mt-4 inline-block text-indigo-600 hover:text-indigo-700">← 返回资源列表</a>
      </div>
    );
  }

  const isMindmap = resource.resource_type === "mindmap";
  const content = resource.content || "";

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <a href="/resources" className="text-sm text-indigo-600 hover:text-indigo-700 mb-4 inline-block">← 返回资源列表</a>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        <div className="flex items-center gap-3 mb-6">
          <span className={`px-2 py-1 rounded text-xs font-medium ${
            resource.resource_type === "lecture" ? "bg-blue-50 text-blue-600" :
            resource.resource_type === "mindmap" ? "bg-purple-50 text-purple-600" :
            resource.resource_type === "code" ? "bg-green-50 text-green-600" : "bg-gray-50 text-gray-600"
          }`}>
            {resource.resource_type === "lecture" ? "📝 讲义" :
             resource.resource_type === "mindmap" ? "🧠 思维导图" :
             resource.resource_type === "code" ? "💻 代码" : "📄 文档"}
          </span>
          {resource.metadata?.difficulty && (
            <span className="text-sm text-gray-400">{"⭐".repeat(resource.metadata.difficulty)}</span>
          )}
        </div>

        <h1 className="text-2xl font-bold text-gray-900 mb-6">{resource.title}</h1>

        {/* Mindmap view */}
        {isMindmap && (
          <div className="mb-6">
            <button onClick={() => setShowMindmap(!showMindmap)}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700 transition-colors mb-4">
              {showMindmap ? "查看源码" : "渲染思维导图"}
            </button>
            {showMindmap ? (
              <div className="border border-gray-200 rounded-xl p-4 bg-gray-50 overflow-x-auto">
                <pre className="text-sm text-gray-700 font-mono whitespace-pre">{content}</pre>
              </div>
            ) : (
              <div className="border border-gray-200 rounded-xl p-4 bg-white">
                <MermaidRenderer code={content} />
              </div>
            )}
          </div>
        )}

        {/* Markdown content with KaTeX math and code highlighting */}
        {!isMindmap && content && (
          <article className="prose prose-indigo max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkMath]}
              rehypePlugins={[rehypeKatex]}
              components={{
                code({ node, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || "");
                  const language = match ? match[1] : "";
                  const code = String(children).replace(/\n$/, "");
                  const inline = !match;
                  return inline ? (
                    <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm text-pink-600 font-mono" {...props}>
                      {children}
                    </code>
                  ) : (
                    <div className="my-4 rounded-xl overflow-hidden border border-gray-200">
                      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 text-gray-300 text-xs font-mono">
                        <span>{language || "code"}</span>
                      </div>
                      <pre className="bg-gray-900 text-gray-100 p-4 overflow-x-auto text-sm leading-relaxed">
                        <code className={`language-${language}`}>{code}</code>
                      </pre>
                    </div>
                  );
                },
                // Fix LaTeX inline/block rendering
                p({ children }) {
                  return <p className="leading-7 mb-4">{children}</p>;
                },
                h2({ children }) {
                  return <h2 className="text-xl font-bold mt-8 mb-4 text-gray-900">{children}</h2>;
                },
                h3({ children }) {
                  return <h3 className="text-lg font-semibold mt-6 mb-3 text-gray-800">{children}</h3>;
                },
                table({ children }) {
                  return <div className="overflow-x-auto mb-4"><table className="min-w-full border-collapse border border-gray-200">{children}</table></div>;
                },
                th({ children }) {
                  return <th className="border border-gray-200 px-4 py-2 bg-gray-50 text-left text-sm font-medium text-gray-700">{children}</th>;
                },
                td({ children }) {
                  return <td className="border border-gray-200 px-4 py-2 text-sm text-gray-600">{children}</td>;
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

// Simple Mermaid renderer (loads dynamically)
function MermaidRenderer({ code }: { code: string }) {
  const [svg, setSvg] = useState<string>("");
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    import("mermaid").then((mermaid) => {
      mermaid.default.initialize({ startOnLoad: false, theme: "default" });
      mermaid.default.render("mermaid-svg", code).then(({ svg }) => {
        if (!cancelled) setSvg(svg);
      }).catch((e: any) => {
        if (!cancelled) setError(`渲染失败: ${e.message}`);
      });
    }).catch(() => setError("Mermaid 库加载失败"));
    return () => { cancelled = true; };
  }, [code]);

  if (error) return <div className="text-red-500 text-sm">{error}</div>;
  if (!svg) return <div className="text-gray-400 text-sm animate-pulse">渲染中...</div>;
  return <div dangerouslySetInnerHTML={{ __html: svg }} className="flex justify-center" />;
}
