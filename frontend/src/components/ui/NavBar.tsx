"use client";

import Link from "next/link";

const navItems = [
  { href: "/", label: "学习看板", icon: "📊" },
  { href: "/chat", label: "AI 对话", icon: "💬" },
  { href: "/resources", label: "学习资源", icon: "📚" },
  { href: "/learning-path", label: "学习路径", icon: "🗺️" },
  { href: "/exercises", label: "练习中心", icon: "✏️" },
  { href: "/assessment", label: "学习评估", icon: "📈" },
];

export function NavBar() {
  return (
    <header className="sticky top-0 z-50 bg-gradient-to-r from-indigo-950 via-indigo-900 to-violet-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-400 to-violet-500 flex items-center justify-center text-lg shadow-lg shadow-indigo-500/25 group-hover:shadow-indigo-500/40 transition-shadow">
              <span className="text-white font-bold text-sm">D</span>
            </div>
            <span className="font-bold text-lg text-white tracking-tight">
              DSA<span className="text-indigo-300 font-medium">Learn</span>
            </span>
          </Link>

          <nav className="hidden md:flex items-center gap-0.5">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-sm font-medium text-indigo-200 hover:text-white hover:bg-white/10 transition-all duration-200"
              >
                <span className="text-base">{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="px-4 py-1.5 rounded-lg bg-white/15 text-indigo-100 hover:bg-white/25 hover:text-white text-sm font-medium transition-all border border-white/10"
            >
              登录
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
