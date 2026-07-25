# Functional Test Report

- Base URL: `http://127.0.0.1:8766`
- Timestamp: 2026-07-25T15:43:16
- Total cases: 27
- Passed: 27
- Failed: 0

## Results
- [PASS] Health endpoint: status=200, payload={'status': 'ok', 'service': 'journey-agent-stdlib'}
- [PASS] Web demo page: status=200, has_page=True
- [PASS] API discovery: status=200, payload={'service': 'journey-agent-stdlib', 'endpoints': ['GET / or /chat - web demo', 'POST /chat - agent chat API', 'GET /health - health check', 'GET /knowledge/search?q=... - RAG search', 'GET /calendar/events - demo calendar events']}
- [PASS] Knowledge search: status=200, top_hit=product-positioning
- [PASS] Weather 北京: city=北京, answer=工具结果：北京、北京市、中国：雷阵雨、温度 28.5°C、体感 33.0°C、湿度 74%、风速 8.1km/h、更新 2026-07-25T15:30

本次识别意图：weather。
- [PASS] Weather 上海: city=上海, answer=工具结果：上海、上海市、中国：晴朗、温度 35.8°C、体感 39.8°C、湿度 50%、风速 15.4km/h、更新 2026-07-25T15:30

本次识别意图：weather。
- [PASS] Weather 杭州: city=杭州, answer=工具结果：杭州、浙江、中国：多云、温度 38.8°C、体感 41.3°C、湿度 36%、风速 12.7km/h、更新 2026-07-25T15:30

本次识别意图：weather。
- [PASS] Weather 深圳: city=深圳, answer=工具结果：深圳、广东、中国：中等毛雨、温度 27.4°C、体感 33.2°C、湿度 92%、风速 10.4km/h、更新 2026-07-25T15:30

本次识别意图：weather。
- [PASS] Weather 广州: city=广州, answer=工具结果：广州、广东、中国：雷阵雨伴冰雹、温度 31.5°C、体感 37.1°C、湿度 68%、风速 10.5km/h、更新 2026-07-25T15:30

本次识别意图：weather。
- [PASS] Weather 成都: city=成都, answer=工具结果：成都、四川、中国：多云、温度 41.3°C、体感 42.8°C、湿度 22%、风速 8.6km/h、更新 2026-07-25T15:30

本次识别意图：weather。
- [PASS] Weather 武汉: city=武汉, answer=工具结果：武汉、湖北、中国：多云转晴、温度 34.9°C、体感 40.4°C、湿度 55%、风速 6.6km/h、更新 2026-07-25T15:30

本次识别意图：weather。
- [PASS] Weather 西安: city=西安, answer=工具结果：西安、陕西、中国：阴天、温度 35.6°C、体感 39.3°C、湿度 45%、风速 7.8km/h、更新 2026-07-25T15:30

本次识别意图：weather。
- [PASS] Weather 重庆: city=重庆, answer=工具结果：重庆、重庆市、中国：多云、温度 39.0°C、体感 41.0°C、湿度 31%、风速 14.6km/h、更新 2026-07-25T15:30

本次识别意图：weather。
- [PASS] Weather 苏州: city=苏州, answer=工具结果：苏州、江苏、中国：晴朗、温度 35.4°C、体感 40.2°C、湿度 54%、风速 13.1km/h、更新 2026-07-25T15:30

本次识别意图：weather。
- [PASS] Calculator one: intent=calculator, tools=['calculator'], citations=0
- [PASS] Calculator two: intent=calculator, tools=['calculator'], citations=0
- [PASS] Calendar today: intent=calendar, tools=['calendar'], citations=0
- [PASS] Calendar tomorrow: intent=calendar, tools=['calendar'], citations=0
- [PASS] Calendar day after tomorrow: intent=calendar, tools=['calendar'], citations=0
- [PASS] Calendar create event: before=3, after=4, answer=工具结果：已创建日程：用户临时安排 2026-07-25T17:43:10-2026-07-25T18:28:10

本次识别意图：calendar。
- [PASS] Knowledge product: intent=knowledge, tools=[], citations=3
- [PASS] Knowledge prompt: intent=knowledge, tools=[], citations=3
- [PASS] Knowledge rag: intent=knowledge, tools=[], citations=3
- [PASS] Knowledge competitor: intent=knowledge, tools=[], citations=3
- [PASS] Multi tool: intent=multi_tool, tools=['calendar', 'weather'], citations=0
- [PASS] General chat: intent=general_chat, tools=[], citations=0
- [PASS] Java client: {"answer": "工具结果：上海、上海市、中国：晴朗、温度 35.8°C、体感 39.8°C、湿度 50%、风速 15.4km/h、更新 2026-07-25T15:30\n\n本次识别意图：weather。", "intent": "weather", "used_tools": ["weather"], "citations": [], "trace": [{"name": "classify_intent", "input": "上海今天天气怎么样？", "output": "weather"}, {"name": "weather", "input": "上海今天天气怎么样？", "output": "上海、上海市、中国：晴朗、温度 35.8°C、体感 39.8°C、湿度 50%、风速 15.4km/h、更新 2026-07-25T15:30"}, {"name": "generate_answer", "input": "上海、上海市、中国：晴朗、温度 35.8°C、体感 39.8°C、湿度 50%、风速 15.4km/h、更新 2026-07-25T15:30", "output": "工具结果：上海、上海市、中国：晴朗、温度 35.8°C、体感 39.8°C、湿度 50%、风速 15.4km/h、更新 2026-07-25T15:30\n\n本次识别意图：weather。"}]}
