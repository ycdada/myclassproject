# 科大讯飞星火大模型 API 密钥配置指南

## 目录

1. [API 密钥获取](#1-api-密钥获取)
2. [项目中的配置位置](#2-项目中的配置位置)
3. [各密钥用途说明](#3-各密钥用途说明)
4. [配置步骤](#4-配置步骤)
5. [验证配置是否生效](#5-验证配置是否生效)
6. [常见问题排查](#6-常见问题排查)
7. [安全注意事项](#7-安全注意事项)

---

## 1. API 密钥获取

### 1.1 注册与登录

1. 访问 **科大讯飞开放平台**：https://www.xfyun.cn/
2. 点击右上角「注册」，使用手机号或邮箱完成注册
3. 登录后进入「控制台」：https://console.xfyun.cn/

### 1.2 创建应用

1. 在控制台左侧菜单选择「我的应用」→「创建新应用」
2. 填写应用信息：
   - **应用名称**：`DSALearn多智能体学习系统`（可自定义）
   - **应用平台**：Web
   - **应用分类**：教育
   - **应用描述**：基于大模型的数据结构与算法个性化学习多智能体系统
3. 点击「提交」，应用创建成功后会生成 **APPID**

### 1.3 开通所需服务

在应用详情页的「服务管理」中，逐一开通以下服务：

| 服务名称 | API 域名/模型 | 用途 | 价格模式 |
|----------|-------------|------|---------|
| **星火大模型 Pro** | `generalv3.5` | 核心推理、对话画像、辅导答疑 | 按量计费 / 免费额度 |
| **星火大模型 Max** | `generalv4.0` | 长文本生成（讲义、阅读材料） | 按量计费 |
| **星火大模型 Pro 128K** | `pro-128k` | 超长上下文理解（课程规划） | 按量计费 |
| **星火图片生成** | 图片生成API | 算法图解、数据结构可视化 | 按量计费 |
| **语音合成（TTS）** | TTS API | 语音讲解生成 | 按量计费 |
| **语音识别（ASR）** | ASR API | 语音输入转文字 | 按量计费 |

> **提示**：新注册用户通常有免费额度。对于比赛演示，免费额度一般足够使用。

### 1.4 获取认证凭证

开通服务后，在应用详情页顶部可以看到三个关键凭证：

```
┌─────────────────────────────────────────────────────────┐
│  应用 APPID:   1234567a                                  │
│  API Key:      abc123def456...（约32位字符）              │
│  API Secret:   xyz789uvw012...（约32位字符）              │
└─────────────────────────────────────────────────────────┘
```

- **APPID**：应用的唯一标识，格式为短字符串
- **API Key**：用于 API 认证的公钥
- **API Secret**：用于 API 认证的私钥，**必须保密**

---

## 2. 项目中的配置位置

项目通过 **环境变量** 管理所有 API 密钥，涉及的文件：

```
myclassproject/
├── .env                    ← 实际配置文件（从 .env.example 复制，不提交Git）
├── .env.example            ← 配置模板（已提交Git，不含真实密钥）
├── backend/app/config.py   ← 后端读取环境变量的配置类
└── docker-compose.yml      ← Docker容器的环境变量注入
```

### .env.example 模板内容

```bash
# ===========================================
# 科大讯飞星火大模型 API
# ===========================================
SPARK_APP_ID=your_app_id
SPARK_API_KEY=your_api_key
SPARK_API_SECRET=your_api_secret

# ===========================================
# 讯飞 TTS（语音合成）
# ===========================================
SPARK_TTS_APP_ID=your_tts_app_id
SPARK_TTS_API_KEY=your_tts_api_key

# ===========================================
# 讯飞 ASR（语音识别）
# ===========================================
SPARK_ASR_APP_ID=your_asr_app_id

# ===========================================
# 数据库（Docker环境可保持默认值）
# ===========================================
DATABASE_URL=postgresql+asyncpg://dsa_user:dsa_password@localhost:5432/dsa_learning
DATABASE_URL_SYNC=postgresql://dsa_user:dsa_password@localhost:5432/dsa_learning

# ===========================================
# Redis（Docker环境可保持默认值）
# ===========================================
REDIS_URL=redis://localhost:6379/0

# ===========================================
# MinIO 对象存储（Docker环境可保持默认值）
# ===========================================
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_BUCKET=dsa-resources

# ===========================================
# JWT 密钥（必须修改为随机字符串）
# ===========================================
JWT_SECRET_KEY=change-this-to-a-random-secret-key

# ===========================================
# 前端 API 地址
# ===========================================
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 3. 各密钥用途说明

### 3.1 SPARK_APP_ID / SPARK_API_KEY / SPARK_API_SECRET（核心必备）

这三个是最核心的凭证，**每个智能体都依赖它们**。

在代码中的使用路径：

```
用户请求
  │
  ▼
backend/app/api/chat.py          ← POST /api/chat/profile  对话画像
backend/app/api/tutor.py         ← POST /api/tutor/ask     智能辅导
backend/app/api/resources.py     ← POST /api/resources/generate  资源生成
  │
  ▼
backend/app/agents/orchestrator.py   ← LangGraph 编排器
  │
  ├── Profile Analyzer Agent      → Spark Pro  (generalv3.5)
  ├── Curriculum Planner Agent    → Spark Pro 128K (pro-128k)
  ├── Content Generator Agent     → Spark Max  (generalv4.0)
  ├── Exercise Designer Agent     → Spark Max  (generalv4.0)
  ├── Multimedia Creator Agent    → Spark Max  (generalv4.0)
  ├── Code Mentor Agent           → Spark Max  (generalv4.0)
  ├── Tutor Agent                 → Spark Pro  (generalv3.5)
  └── Assessor Agent              → Spark Pro  (generalv3.5)
  │
  ▼
backend/app/services/spark_client.py   ← WebSocket 客户端（实际调用API）
```

### 3.2 图像生成 API（扩展功能）

用于生成算法图解、数据结构可视化图片。可通过 Spark Image API 调用。

### 3.3 TTS 语音合成（扩展功能，加分项）

用于智能辅导时生成语音讲解：

```
Tutor Agent 生成文字解释
  → 讯飞 TTS API → MP3 音频文件
  → 前端播放音频
```

### 3.4 ASR 语音识别（扩展功能，加分项）

用于语音输入提问：

```
学生语音提问
  → 讯飞 ASR API → 文字
  → Tutor Agent 处理
```

---

## 4. 配置步骤

### 步骤 1：复制配置模板

```bash
cd /home/yc_dada/myclassproject
cp .env.example .env
```

### 步骤 2：编辑 .env 文件

用任意编辑器打开 `.env`，填入真实的 API 凭证：

```bash
# 将 your_app_id 等占位符替换为真实值
SPARK_APP_ID=1234567a              # ← 替换为你的APPID
SPARK_API_KEY=abc123def456...      # ← 替换为你的API Key
SPARK_API_SECRET=xyz789uvw012...   # ← 替换为你的API Secret

# 生成一个随机JWT密钥（可以用命令：openssl rand -hex 32）
JWT_SECRET_KEY=a1b2c3d4e5f6...    # ← 改为随机字符串
```

### 步骤 3A：Docker 环境启动

如果使用 Docker Compose（推荐），`docker-compose.yml` 已配置从 `.env` 读取：

```bash
# 启动所有服务
docker-compose up -d

# 查看日志确认无错误
docker-compose logs -f backend
```

### 步骤 3B：本地开发环境启动

如果不使用 Docker，直接本地运行后端：

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 启动后端（.env 会被 config.py 自动加载）
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

```bash
cd frontend

# 安装依赖
npm install

# 启动前端
npm run dev
```

### 步骤 4：确认 .env 不被提交到 Git

`.gitignore` 已包含 `.env`，确认为：

```bash
git status   # 应该看不到 .env 文件
```

---

## 5. 验证配置是否生效

### 5.1 健康检查

```bash
curl http://localhost:8000/api/health
```

期望返回：
```json
{
  "status": "healthy",
  "app": "DSA Learning Multi-Agent System",
  "version": "0.1.0"
}
```

### 5.2 测试 API 连接

后端提供了配置验证逻辑。启动后查看日志：

```bash
# Docker环境
docker-compose logs backend | grep -i spark

# 本地环境
# 控制台输出中查看启动日志
```

正常情况下，日志应显示配置加载成功（无报错）。

### 5.3 发送测试对话请求

```bash
curl -X POST http://localhost:8000/api/chat/profile \
  -H "Content-Type: application/json" \
  -d '{"content": "你好，我学过C语言和Python，对算法比较感兴趣"}'
```

如果 API 密钥配置正确，应该收到 SSE 流式响应（即使返回占位内容，只要不报 API 认证错误就说明配置正确）。

### 5.4 常见验证错误及含义

| 错误信息 | 含义 | 解决方法 |
|----------|------|---------|
| `401 Unauthorized` | API Key/Secret 错误 | 检查凭证是否正确复制 |
| `403 Forbidden` | 服务未开通 | 在控制台开通对应服务 |
| `10001` 或 `10002` | APPID 无效 | 检查 APPID 是否正确 |
| `10104` | 服务额度不足 | 充值或等待免费额度重置 |
| `11200` | 模型授权未通过 | 确保已开通对应模型的权限 |

---

## 6. 常见问题排查

### Q1: 提示 "Connection refused" 或 WebSocket 连接失败？

**原因**：网络环境可能限制了 WebSocket 连接。

**解决**：
1. 确保服务器能访问外网：`curl https://spark-api.xf-yun.com`
2. 检查防火墙是否放行 WebSocket 端口（443）
3. 如果在校园网/公司内网，可能需要配置代理

### Q2: Docker 容器中如何读取 .env？

项目的 `docker-compose.yml` 已配置环境变量映射：

```yaml
backend:
  environment:
    SPARK_APP_ID: ${SPARK_APP_ID:-}     # 从 .env 读取
    SPARK_API_KEY: ${SPARK_API_KEY:-}
    SPARK_API_SECRET: ${SPARK_API_SECRET:-}
```

`${SPARK_APP_ID:-}` 语法：优先从 `.env` 读取，如果不存在则为空。

### Q3: 只需要核心功能（文字对话），需要开通哪些服务？

最少配置：
```
必须：SPARK_APP_ID + SPARK_API_KEY + SPARK_API_SECRET（Spark Pro 文字生成）
可暂不：TTS、ASR、图片生成（这些是扩展加分项）
```

### Q4: 竞赛期间免费额度够用吗？

科大讯飞为开发者提供一定免费额度。以 Spark Pro 为例，新注册通常赠送数十万 tokens。用于竞赛演示（少量资源的生成和对话）完全足够。

建议：
- 开发测试时控制调用频率
- 用低温度参数 (0.3) 和合理的 max_tokens (2048) 节省额度
- 可先用于本地 RAG 管道，减少重复调用

### Q5: 星火API域名/模型版本有变更怎么办？

检查官方文档确认最新域名。在项目中更新以下位置：

- `backend/app/services/spark_client.py` 第 29-33 行：
```python
DOMAIN_URLS = {
    "generalv3.5": f"{BASE_URL}/v3.5/chat",     # Spark Pro
    "generalv4.0": f"{BASE_URL}/v4.0/chat",     # Spark Max
    "pro-128k": f"{BASE_URL}/chat/pro-128k",     # Spark Pro 128K
}
```

---

## 7. 安全注意事项

| ⚠️ 风险 | 正确做法 |
|---------|---------|
| API Secret 泄露 | **永远不要**将 `.env` 提交到 Git（`.gitignore` 已防护） |
| 密钥硬编码 | **永远不要**将密钥直接写死在代码中，必须通过环境变量 |
| 前端暴露密钥 | 密钥**只在后端**使用，前端没有也不应该访问 |
| 演示时屏幕共享 | 提前关闭编辑器，避免展示 `.env` 内容 |
| 提交材料中包含密钥 | 检查提交的源码/文档/截图不含真实密钥 |

### 如果密钥意外泄露

1. 立即登录控制台：https://console.xfyun.cn/
2. 进入应用 → 「API密钥管理」
3. 点击「重置」生成新的 API Secret
4. 更新 `.env` 文件
5. 重启后端服务

---

## 附录：API 认证机制说明

星火大模型使用 **HMAC-SHA256** 签名认证。项目中 `spark_client.py` 已完整实现：

```
1. 构建签名原文：
   host: spark-api.xf-yun.com
   date: {当前GMT时间}
   GET /v3.5/chat HTTP/1.1

2. 用 API Secret 对签名原文做 HMAC-SHA256 → 得到 signature

3. 拼接认证串：
   api_key="{API_KEY}", algorithm="hmac-sha256",
   headers="host date request-line", signature="{signature}"

4. 对认证串做 Base64 编码 → authorization 参数

5. 将 authorization、date、host 作为 WebSocket URL 的查询参数
```

最终 WebSocket 连接 URL 形如：
```
wss://spark-api.xf-yun.com/v3.5/chat?authorization=xxx&date=xxx&host=xxx
```

每次建立 WebSocket 连接时，都会重新生成签名（因为时间戳会变），确保安全性。

---

> **问题反馈**：如遇到本文档未覆盖的配置问题，请查阅 [科大讯飞开放平台文档](https://www.xfyun.cn/doc/) 或在大赛答疑 QQ 群（1072584310）中提问。
