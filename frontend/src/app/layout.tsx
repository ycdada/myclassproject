import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { NavBar } from "@/components/ui/NavBar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "DSALearn — 数据结构与算法个性化学习系统",
  description: "基于大模型的多智能体个性化资源生成与学习系统",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="zh-CN"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <body className="min-h-full flex flex-col bg-slate-50">
        <NavBar />
        <main className="flex-1 overflow-x-hidden">{children}</main>
        <footer className="border-t border-slate-100 bg-white/80 backdrop-blur-sm py-4 text-center text-xs text-slate-400 tracking-wide">
          DSALearn — 基于大模型的多智能体个性化学习系统 · 数据结构与算法
        </footer>
      </body>
    </html>
  );
}
