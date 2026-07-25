# Java Client

这个客户端使用 JDK 11+ 标准库 `HttpClient` 调用 Python FastAPI 服务。

```powershell
javac -encoding UTF-8 -d out src\main\java\com\journey\client\JourneyAgentClient.java
java -cp out com.journey.client.JourneyAgentClient "上海今天天气怎么样？"
```

默认请求 `http://127.0.0.1:8765`。如果要请求 FastAPI 服务：

```powershell
$env:JOURNEY_AGENT_BASE_URL="http://127.0.0.1:8000"
java -cp out com.journey.client.JourneyAgentClient "上海今天天气怎么样？"
```
