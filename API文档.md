# 全模态 AI 混合输出系统 API 文档

## 1. 系统概述

全模态 AI 混合输出系统是一个 AI 应用生成与编排运行时（AI Application Runtime），支持：
- 解析自然语言需求
- 规划执行任务
- 生成多模态内容
- 生成可运行应用
- 输出结构化页面描述

## 2. API 端点

### 2.1 健康检查

- **URL**: `/api/v1/health`
- **方法**: GET
- **描述**: 检查系统健康状态
- **响应**: 
  ```json
  {
    "status": "ok",
    "version": "1.0.0"
  }
  ```

### 2.2 聊天

- **URL**: `/api/v1/chat`
- **方法**: POST
- **描述**: 处理用户聊天请求
- **请求体**:
  ```json
  {
    "message": "你好，告诉我关于人工智能的信息",
    "session_id": "optional-session-id"
  }
  ```
- **响应**: 结构化响应，包含文本、图像、SVG、图表和Artifact块

### 2.3 生成应用

- **URL**: `/api/v1/generate-app`
- **方法**: POST
- **描述**: 生成可运行的应用
- **请求体**:
  ```json
  {
    "message": "生成一个BMI计算器应用"
  }
  ```
- **响应**: 结构化响应，包含生成的应用信息

### 2.4 执行任务

- **URL**: `/api/v1/execute-task`
- **方法**: POST
- **描述**: 执行特定任务
- **请求体**:
  ```json
  {
    "agent": "text_generator",
    "action": "execute",
    "input_data": {
      "prompt": "生成一段关于人工智能的介绍"
    }
  }
  ```
- **响应**:
  ```json
  {
    "success": true,
    "output": {
      "text": "生成的文本内容"
    },
    "error": null,
    "execution_time": 1.234
  }
  ```

### 2.5 生成多模态内容

- **URL**: `/api/v1/generate-multimodal`
- **方法**: POST
- **描述**: 生成多模态内容，支持文本、图像、SVG、图表和应用
- **请求体**:
  ```json
  {
    "message": "讲解微分中值定理并可视化，生成相关图表和示例应用",
    "session_id": "optional-session-id"
  }
  ```
- **响应**: 结构化响应，包含多种类型的内容块

### 2.6 会话管理

- **URL**: `/api/v1/sessions/{session_id}`
- **方法**: GET
- **描述**: 获取会话信息
- **响应**: 会话详细信息

- **URL**: `/api/v1/sessions/{session_id}`
- **方法**: DELETE
- **描述**: 删除会话
- **响应**:
  ```json
  {
    "status": "deleted",
    "session_id": "session-id"
  }
  ```

### 2.7 Agent 管理

- **URL**: `/api/v1/agents`
- **方法**: GET
- **描述**: 获取所有可用的Agent列表
- **响应**:
  ```json
  {
    "agents": [
      {
        "name": "code_agent",
        "type": "system",
        "description": "代码生成助手",
        "capabilities": ["生成Python代码", "生成JavaScript代码", ...]
      },
      ...
    ]
  }
  ```

- **URL**: `/api/v1/agents/reload`
- **方法**: POST
- **描述**: 重新加载技能Agent
- **响应**:
  ```json
  {
    "status": "success",
    "reloaded_skills": 6
  }
  ```

### 2.8 带技能支持的聊天

- **URL**: `/api/v1/chat-with-skills`
- **方法**: POST
- **描述**: 使用技能进行聊天
- **请求体**:
  ```json
  {
    "message": "使用代码技能生成一个Python函数",
    "session_id": "optional-session-id"
  }
  ```
- **响应**: 结构化响应，包含技能执行结果

## 3. 结构化响应格式

系统返回的结构化响应包含以下类型的块：

### 3.1 文本块 (text_blocks)

```json
{
  "type": "text",
  "content": "文本内容",
  "metadata": {
    "priority": 1
  }
}
```

### 3.2 图像块 (image_blocks)

```json
{
  "type": "image",
  "url": "/images/image-id.png",
  "alt_text": "图像描述",
  "metadata": {
    "priority": 2
  }
}
```

### 3.3 SVG块 (svg_blocks)

```json
{
  "type": "svg",
  "content": "<svg>...</svg>",
  "metadata": {
    "priority": 2
  }
}
```

### 3.4 图表块 (chart_blocks)

```json
{
  "type": "chart",
  "config": {
    "title": {
      "text": "图表标题",
      "left": "center"
    },
    "tooltip": {
      "trigger": "axis"
    },
    "xAxis": {
      "type": "category",
      "data": ["一月", "二月", ...]
    },
    "yAxis": {
      "type": "value"
    },
    "series": [
      {
        "name": "数据",
        "type": "bar",
        "data": [100, 200, ...]
      }
    ]
  },
  "metadata": {
    "priority": 2
  }
}
```

### 3.5 Artifact块 (artifact_blocks)

```json
{
  "type": "artifact",
  "artifact_id": "app-id",
  "name": "应用名称",
  "description": "应用描述",
  "url": "/apps/app-id",
  "metadata": {
    "priority": 3
  }
}
```

### 3.6 后续问题块 (follow_up_blocks)

```json
{
  "type": "follow_up",
  "questions": [
    "你对生成的内容满意吗？",
    "需要对内容进行哪些修改？",
    "还需要生成其他类型的内容吗？"
  ],
  "metadata": {
    "priority": 1
  }
}
```

## 4. 使用示例

### 4.1 生成多模态内容

```python
import requests
import json

url = "http://localhost:8002/api/v1/generate-multimodal"
data = {
    "message": "讲解微分中值定理并可视化，生成相关图表和示例应用"
}

response = requests.post(url, json=data)
result = response.json()

print("文本内容:")
for text_block in result.get("text_blocks", []):
    print(text_block["content"])

print("\n图像:")
for image_block in result.get("image_blocks", []):
    print(image_block["url"])

print("\n图表:")
for chart_block in result.get("chart_blocks", []):
    print(chart_block["config"]["title"]["text"])

print("\n应用:")
for artifact_block in result.get("artifact_blocks", []):
    print(f"{artifact_block['name']}: {artifact_block['url']}")
```

### 4.2 生成应用

```python
import requests
import json

url = "http://localhost:8002/api/v1/generate-app"
data = {
    "message": "生成一个BMI计算器应用"
}

response = requests.post(url, json=data)
result = response.json()

print("生成的应用:")
for artifact_block in result.get("artifact_blocks", []):
    print(f"名称: {artifact_block['name']}")
    print(f"描述: {artifact_block['description']}")
    print(f"URL: {artifact_block['url']}")
```

## 5. 能力模块

系统支持以下能力模块：

- **text_generator**: 生成文本内容
- **image_generator**: 生成图像
- **svg_generator**: 生成SVG图表和diagrams
- **flash_app_generator**: 生成可运行的Flash应用
- **chart_generator**: 生成ECharts图表配置
- **data_processor**: 处理和分析数据（支持Pandas/NumPy）
- **search_retriever**: 搜索和检索信息

## 6. 异步渲染机制

系统返回的响应块包含优先级信息，前端可以根据优先级进行异步加载：

1. **优先级 1**: 文本和后续问题（立即加载）
2. **优先级 2**: 图像、SVG和图表（次优先加载）
3. **优先级 3**: 应用（最后加载）

这样可以提升用户体验，让用户先看到文本内容，然后是可视化内容，最后是应用。

## 7. 部署建议

- **静态文件托管**: 可以使用CDN加速静态文件的访问
- **API服务**: 可以部署在云服务器上，使用负载均衡提高可用性
- **存储**: 生成的应用和资源可以存储在对象存储服务中
- **监控**: 建议添加监控和日志系统，以便及时发现和解决问题

## 8. 错误处理

系统会返回适当的HTTP状态码和错误信息：

- **404**: 资源不存在
- **500**: 服务器内部错误
- **400**: 请求参数错误

错误响应格式：

```json
{
  "detail": "错误描述"
}
```