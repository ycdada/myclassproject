"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { auth } from "@/lib/api";
import { useStudentStore } from "@/stores/useStudentStore";

export default function LoginPage() {
  const router = useRouter();
  const setAuth = useStudentStore((s) => s.setAuth);
  const [mode, setMode] = useState<"login" | "register">("login");
  const [form, setForm] = useState({ username: "", email: "", password: "", major: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const h = (f: string) => (e: React.ChangeEvent<HTMLInputElement>) => { setForm((p) => ({ ...p, [f]: e.target.value })); setError(""); };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setError(""); setLoading(true);
    if (!form.username || !form.password) { setError("用户名和密码不能为空"); setLoading(false); return; }
    if (mode === "register" && !form.email) { setError("邮箱不能为空"); setLoading(false); return; }
    try {
      const r = mode === "login"
        ? await auth.login({ username: form.username, password: form.password })
        : await auth.register({ username: form.username, email: form.email, password: form.password, major: form.major || undefined });
      setAuth(r.user_id, r.username, r.access_token);
      localStorage.setItem("token", r.access_token);
      router.push("/");
    } catch (err: any) { setError(err?.message || "操作失败"); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center mx-auto shadow-lg shadow-indigo-200">
            <span className="text-3xl">🧠</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900 mt-4 tracking-tight">DSALearn</h1>
          <p className="text-sm text-slate-400 mt-1">数据结构与算法个性化学习系统</p>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-8">
          {/* Tabs */}
          <div className="flex mb-6 bg-slate-100 rounded-xl p-1">
            {(["login", "register"] as const).map((m) => (
              <button key={m} onClick={() => setMode(m)}
                className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${
                  mode === m ? "bg-white text-indigo-600 shadow-sm" : "text-slate-400 hover:text-slate-600"
                }`}>
                {m === "login" ? "登录" : "注册"}
              </button>
            ))}
          </div>

          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-500 mb-1.5 uppercase tracking-wider">用户名</label>
              <input type="text" value={form.username} onChange={h("username")}
                className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 focus:bg-white outline-none transition-all" placeholder="请输入用户名" />
            </div>
            {mode === "register" && (
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1.5 uppercase tracking-wider">邮箱</label>
                <input type="email" value={form.email} onChange={h("email")}
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 focus:bg-white outline-none transition-all" placeholder="请输入邮箱" />
              </div>
            )}
            <div>
              <label className="block text-xs font-semibold text-slate-500 mb-1.5 uppercase tracking-wider">密码</label>
              <input type="password" value={form.password} onChange={h("password")}
                className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 focus:bg-white outline-none transition-all" placeholder="请输入密码" />
            </div>
            {mode === "register" && (
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1.5 uppercase tracking-wider">专业（选填）</label>
                <input type="text" value={form.major} onChange={h("major")}
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 focus:bg-white outline-none transition-all" placeholder="如：计算机科学与技术" />
              </div>
            )}
            {error && <div className="px-4 py-2 bg-red-50 border border-red-100 rounded-xl text-xs text-red-600">{error}</div>}
            <button type="submit" disabled={loading}
              className="w-full py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 text-white rounded-xl font-medium text-sm hover:shadow-md hover:shadow-indigo-200 disabled:opacity-50 transition-all active:scale-[0.99]">
              {loading ? "处理中..." : mode === "login" ? "登录" : "注册"}
            </button>
          </form>

          <div className="mt-6 pt-4 border-t border-slate-100">
            <p className="text-[10px] text-center text-slate-300 uppercase tracking-wider mb-3">无需注册，直接体验</p>
            <button onClick={() => { setAuth("demo_user_001", "demo_student", "mock_token_demo"); localStorage.setItem("token", "mock_token_demo"); router.push("/"); }}
              className="w-full py-2.5 bg-amber-50 border border-amber-200 text-amber-700 rounded-xl font-medium text-sm hover:bg-amber-100 transition-colors">
              🎭 演示模式一键登录
            </button>
          </div>
        </div>

        <p className="mt-4 text-center text-[11px] text-slate-300">演示账号: demo_student / demo123</p>
      </div>
    </div>
  );
}
