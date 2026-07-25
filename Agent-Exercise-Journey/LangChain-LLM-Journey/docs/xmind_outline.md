# 产品架构图 XMind 大纲

可直接复制到 XMind / ProcessOn / 飞书思维导图中生成产品架构图。

- Journey Personal Agent
  - 用户入口
    - Web Demo
    - Java Client
    - FastAPI / Stdlib HTTP
  - Agent 编排层
    - 意图识别
    - 任务拆解
    - 工具路由
    - 反思修正
  - Prompt 分层
    - System Role
    - Task Planning
    - Tool Selection
    - Answer Generation
    - Reflection
  - RAG 知识库
    - 文档导入
    - 向量化
    - TopK 检索
    - 引用返回
    - ChromaDB 生产扩展
  - 工具能力
    - Calculator
    - Calendar
    - Weather
  - 可观测性
    - Trace
    - Citations
    - Used Tools
  - 面试展示
    - 竞品分析
    - PRD
    - 架构图
    - API 示例
    - 演示脚本

