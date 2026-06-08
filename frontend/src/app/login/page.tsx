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

  const handleChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
    setError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    if (!form.username || !form.password) {
      setError("用户名和密码不能为空");
      setLoading(false);
      return;
    }

    if (mode === "register" && !form.email) {
      setError("邮箱不能为空");
      setLoading(false);
      return;
    }

    try {
      let result;
      if (mode === "login") {
        result = await auth.login({ username: form.username, password: form.password });
      } else {
        result = await auth.register({
          username: form.username,
          email: form.email,
          password: form.password,
          major: form.major || undefined,
        });
      }

      setAuth(result.user_id, result.username, result.access_token);
      localStorage.setItem("token", result.access_token);
      router.push("/");
    } catch (err: any) {
      setError(err?.message || "操作失败，请重试");
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = () => {
    setAuth("demo_user_001", "demo_student", "mock_token_demo");
    localStorage.setItem("token", "mock_token_demo");
    router.push("/");
  };

  return (
    <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">🧠 DSALearn</h1>
          <p className="mt-2 text-gray-600">数据结构与算法个性化学习系统</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          {/* Mode Tabs */}
          <div className="flex mb-6 bg-gray-100 rounded-lg p-1">
            {(["login", "register"] as const).map((m) => (
              <button key={m} onClick={() => setMode(m)}
                className={`flex-1 py-2 text-sm font-medium rounded-md transition-colors ${
                  mode === m ? "bg-white text-indigo-600 shadow-sm" : "text-gray-500 hover:text-gray-700"
                }`}>
                {m === "login" ? "登录" : "注册"}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">用户名</label>
              <input type="text" value={form.username} onChange={handleChange("username")}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none text-sm"
                placeholder="请输入用户名" />
            </div>

            {mode === "register" && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
                <input type="email" value={form.email} onChange={handleChange("email")}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none text-sm"
                  placeholder="请输入邮箱" />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">密码</label>
              <input type="password" value={form.password} onChange={handleChange("password")}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none text-sm"
                placeholder="请输入密码" />
            </div>

            {mode === "register" && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">专业（选填）</label>
                <input type="text" value={form.major} onChange={handleChange("major")}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none text-sm"
                  placeholder="如：计算机科学与技术" />
              </div>
            )}

            {error && (
              <div className="px-4 py-2 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">{error}</div>
            )}

            <button type="submit" disabled={loading}
              className="w-full py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors font-medium text-sm">
              {loading ? "处理中..." : mode === "login" ? "登录" : "注册"}
            </button>
          </form>

          <div className="mt-6 pt-4 border-t border-gray-200">
            <p className="text-xs text-center text-gray-400 mb-3">无需注册，直接体验</p>
            <button onClick={handleDemoLogin}
              className="w-full py-2.5 bg-yellow-50 border border-yellow-200 text-yellow-700 rounded-lg hover:bg-yellow-100 transition-colors font-medium text-sm">
              🎭 演示模式一键登录
            </button>
          </div>
        </div>

        <p className="mt-4 text-center text-xs text-gray-400">
          演示账号: demo_student / demo123
        </p>
      </div>
    </div>
  );
}
