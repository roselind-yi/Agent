# 面试演示脚本

## 30 秒项目介绍

我做的是一个个人智能助理 Agent，目标不是泛聊天，而是把个人用户的高频需求收敛到知识库问答、日程管理和生活查询。系统会先识别意图，再决定检索知识库还是调用工具，最后返回答案、引用来源和执行 trace。

## 2 分钟演示路径

1. 运行 `scripts/run_demo.py`，展示离线 demo。
2. 问“这个 Agent 项目的产品定位是什么？”，展示 RAG 引用。
3. 问“帮我算一下 (128 + 32) / 4”，展示工具调用。
4. 问“明天有什么日程？”，展示日程工具。
5. 打开 `docs/architecture.md`，解释服务、Agent、RAG、工具和 LLM 分层。

如果面试官希望看 API，可以运行：

```powershell
C:\Users\123\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\serve_stdlib.py --port 8765
```

然后请求 `http://127.0.0.1:8765/chat`。

## 可追问回答

### 为什么要返回 trace？

因为 Agent 类产品的核心体验风险是不可解释。Trace 能帮助产品和研发判断：是意图识别错了、检索召回错了，还是生成阶段表达错了。

### 为什么保留 mock LLM？

面试和本地开发环境不一定有 API Key。Mock LLM 让核心链路可测试、可演示；生产环境通过 Provider 抽象切换到真实模型。

### ChromaDB 在哪里？

代码中保留了 `ChromaVectorStore` adapter；本地默认用无依赖 `LocalVectorStore`。这样既说明生产方案，也保证项目可运行。
