import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "DSALearn - 数据结构与算法个性化学习系统",
  description: "基于大模型的多智能体个性化资源生成与学习系统",
};

const navItems = [
  { href: "/", label: "学习看板", icon: "📊" },
  { href: "/chat", label: "AI 对话", icon: "💬" },
  { href: "/resources", label: "学习资源", icon: "📚" },
  { href: "/learning-path", label: "学习路径", icon: "🗺️" },
  { href: "/exercises", label: "练习中心", icon: "✏️" },
  { href: "/assessment", label: "学习评估", icon: "📈" },
];

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="zh-CN"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-gray-50">
        {/* Top Navigation */}
        <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-14">
              <Link href="/" className="flex items-center gap-2 font-bold text-lg text-indigo-600">
                <span className="text-2xl">🧠</span>
                <span>DSALearn</span>
              </Link>
              <nav className="hidden md:flex items-center gap-1">
                {navItems.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm text-gray-600 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
                  >
                    <span>{item.icon}</span>
                    <span>{item.label}</span>
                  </Link>
                ))}
              </nav>
              {/* Mobile menu placeholder */}
              <div className="md:hidden">
                <button className="p-2 rounded-lg hover:bg-gray-100">
                  <span className="text-xl">🍔</span>
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1">{children}</main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 py-4 text-center text-sm text-gray-500">
          DSALearn — 基于大模型的多智能体个性化学习系统 | 数据结构与算法
        </footer>
      </body>
    </html>
  );
}
