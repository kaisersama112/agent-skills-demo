# 灵光 Lite 后端

基于技术方案文档实现的后端系统。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置:

```bash
cp .env.example .env
# 编辑 .env 文件，设置 OPENAI_API_KEY
```

### 3. 启动服务

```bash
uvicorn main:app --reload --port 8000
```

### 4. 访问 API

- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/api/v1/health

## API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/v1/health | 健康检查 |
| POST | /api/v1/chat | 聊天接口 |
| POST | /api/v1/generate-app | 生成应用 |
| POST | /api/v1/execute-task | 执行任务 |
| GET | /api/v1/sessions/{session_id} | 获取会话 |
| DELETE | /api/v1/sessions/{session_id} | 删除会话 |

## 技术架构

- **API层**: FastAPI
- **LLM层**: OpenAI (可替换为 DeepSeek/Qwen)
- **Agent系统**: 自研 Agent Runtime
- **运行时**: Docker Sandbox (可选)
