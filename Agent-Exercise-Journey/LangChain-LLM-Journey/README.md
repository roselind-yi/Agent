# LangChain LLM Journey - Personal Agent

这是一个面向面试可演示的个人智能助理 Agent 项目，覆盖简历中写到的核心能力：竞品分析、Prompt 分层、RAG 知识库、工具调用、FastAPI 服务接口和 Java 客户端跨语言联调。

## 已实现能力

- 知识库问答：内置个人 Agent 产品知识库，支持语义召回和引用来源。
- Agent 编排：意图识别 -> 工具选择 -> RAG 检索 -> 答案生成 -> trace 返回。
- 工具调用：计算器、日程、天气查询三个工具。
- Prompt 分层：系统角色、任务规划、工具选择、答案生成、反思检查。
- API 服务：FastAPI 提供 `/chat`、`/knowledge/search`、`/calendar/events`、`/health`。
- Java 客户端：用 JDK 标准库 `HttpClient` 请求 Python 服务。
- Web 高保真演示：浏览器访问 `/chat`，可直接体验对话、引用和 trace。
- 产品交付文档：竞品分析、PRD、产品方案、架构图、XMind 大纲、原型说明、演示脚本。
- 离线演示：默认使用 `MockLLMProvider`，没有 API Key 也能跑通完整流程。
- 生产扩展：安装依赖后可切到 OpenAI-compatible LLM、LangChain adapter 和 ChromaDB。

## 快速运行

一键启动可展示版本：

```powershell
scripts\start_demo.bat
```

打开：

```text
http://127.0.0.1:8765/chat
```

离线 demo，不需要安装第三方依赖：

```powershell
C:\Users\123\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\run_demo.py
```

启动 API 服务：

```powershell
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

无第三方依赖的本地 HTTP 服务：

```powershell
C:\Users\123\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\serve_stdlib.py --port 8765
```

迁移到 `D:\learn\lover`：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\migrate_to_d_learn_lover.ps1
```

调用接口：

```powershell
curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d "{\"message\":\"结合 RAG 和工具调用说明项目亮点\"}"
```

Java 客户端：

```powershell
cd java-client
javac -encoding UTF-8 -d out src\main\java\com\journey\client\JourneyAgentClient.java
java -cp out com.journey.client.JourneyAgentClient "上海今天天气怎么样？"
```

如果你改用 FastAPI 的 `8000` 端口：

```powershell
$env:JOURNEY_AGENT_BASE_URL="http://127.0.0.1:8000"
java -cp out com.journey.client.JourneyAgentClient "上海今天天气怎么样？"
```

## 真实 LLM 配置

默认环境变量：

```powershell
$env:JOURNEY_LLM_PROVIDER="openai-compatible"
$env:OPENAI_API_KEY="你的 key"
$env:OPENAI_BASE_URL="https://api.openai.com/v1"
$env:OPENAI_MODEL="gpt-4o-mini"
```

未配置时使用确定性的 mock provider，方便演示和测试。

## 面试讲法

一句话版本：

> 我做的是一个个人智能助理 Agent，先把用户需求收敛到知识库问答、日程管理和生活查询三个边界内，再用 Prompt 分层、RAG 检索和工具调用把自然语言变成可执行链路，最后通过 FastAPI 暴露服务给 Java 客户端调用。

技术亮点：

- 产品上先做竞品拆解，明确 Coze/Dify/LangChain 各自强项，再选择个人助理这个更容易闭环的场景。
- 架构上把 LLM 与工具、检索、接口分层解耦，便于从 mock 切到真实模型。
- 体验上返回 `trace` 和 `citations`，方便定位“为什么这么答”，也能支撑 Prompt 迭代。
