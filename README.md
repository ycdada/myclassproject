# DSALearn — 基于大模型的个性化资源生成与学习多智能体系统

第十五届中国软件杯大赛 A3 赛题 | 科大讯飞股份有限公司

## 项目简介

DSALearn 是一个面向**数据结构与算法**课程的个性化学习多智能体系统。系统通过 9 个协同 AI 智能体，为学生自动生成个性化学习资源，规划最优学习路径，并提供智能辅导服务。

### 核心功能

- 🗣️ **对话式学习画像** — 通过自然语言对话自动构建 8 维动态学生画像
- 🤖 **多智能体协同** — 9 个角色智能体协作生成 5+ 种个性化资源类型
- 🗺️ **个性化学习路径** — 基于知识图谱 + 学生画像的拓扑路径规划
- 💡 **智能辅导** — 多模态答疑（文字 + 图解 + 语音）
- 📊 **学习效果评估** — 多维度追踪 + 动态策略调整

### 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Next.js 14, React 18, TailwindCSS, Zustand |
| 后端 | FastAPI (Python 3.12), LangGraph, LangChain |
| 大模型 | 科大讯飞星火 Spark Pro/Max |
| 数据库 | PostgreSQL 16 + pgvector |
| 向量检索 | sentence-transformers (MiniLM) |
| 缓存 | Redis 7 |
| 存储 | MinIO |
| 部署 | Docker Compose + Nginx |

## 快速开始

### 1. 配置 API 密钥

```bash
cp .env.example .env
# 编辑 .env 填入科大讯飞星火 API 凭证
# 详见 docs/API密钥配置指南.md
```

### 2. 启动系统

```bash
# Docker 环境
docker-compose up -d

# 或本地开发
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload &
cd frontend && npm install && npm run dev
```

### 3. 演示模式

无需后端直接体验：

```bash
cd frontend
NEXT_PUBLIC_DEMO_MODE=true npm run dev
# 访问 http://localhost:3000/login → 点击"演示模式一键登录"
```

## 目录结构

```
myclassproject/
├── frontend/          # Next.js 前端 SPA
├── backend/           # FastAPI 后端 + 多智能体系统
│   ├── app/
│   │   ├── agents/    # 9 个智能体 (LangGraph)
│   │   ├── api/       # REST + SSE 路由
│   │   ├── services/  # 星火 API, RAG, TTS
│   │   ├── models/    # SQLAlchemy + pgvector
│   │   ├── knowledge_graph/  # DSA 知识图谱 (30+ 知识点)
│   │   └── safety/    # 防幻觉 + 内容安全
├── docs/              # 竞赛文档
├── docker-compose.yml
└── nginx.conf
```

## 文档

| 文档 | 说明 |
|------|------|
| [API 密钥配置指南](docs/API密钥配置指南.md) | 讯飞星火 API 凭证获取与配置 |
| [系统开发说明书](docs/系统开发说明书.md) | 系统架构、技术实现、创新点详解 |
| [测试说明书](docs/测试说明书.md) | 测试策略、用例设计、性能指标 |
| [部署指南](docs/部署指南.md) | Docker 部署、环境配置、运维说明 |
| [AI Coding 工具说明](docs/AI_Coding工具说明.md) | AI 辅助开发工具使用情况 |

## License

本项目为第十五届中国软件杯大赛参赛作品。
