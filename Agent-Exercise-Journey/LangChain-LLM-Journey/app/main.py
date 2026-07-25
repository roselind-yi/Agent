from __future__ import annotations

from app.agent.engine import JourneyAgent


agent = JourneyAgent()


def create_app():
    try:
        from fastapi import FastAPI
        from fastapi.responses import HTMLResponse
        from pydantic import BaseModel, Field
    except ImportError as exc:
        raise RuntimeError("Install dependencies with `pip install -r requirements.txt`.") from exc

    class ChatRequest(BaseModel):
        message: str = Field(..., min_length=1)
        user_id: str = "demo-user"
        session_id: str = "demo-session"

    app = FastAPI(title="Journey Personal Agent", version="1.0.0")

    @app.get("/", response_class=HTMLResponse)
    @app.get("/chat", response_class=HTMLResponse)
    def web_demo() -> str:
        return (agent.settings.data_dir.parent / "web" / "index.html").read_text(encoding="utf-8")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "journey-agent"}

    @app.post("/chat")
    def chat(request: ChatRequest) -> dict[str, object]:
        response = agent.answer(request.message, user_id=request.user_id)
        return response.to_dict()

    @app.get("/knowledge/search")
    def search(q: str, top_k: int = 3) -> dict[str, object]:
        hits = agent.retriever.search(q, top_k=top_k)
        return {
            "query": q,
            "hits": [
                {
                    "id": hit.document.id,
                    "title": hit.document.title,
                    "content": hit.document.content,
                    "score": round(hit.score, 4),
                    "tags": hit.document.tags,
                }
                for hit in hits
            ],
        }

    @app.get("/calendar/events")
    def list_events() -> dict[str, object]:
        return {"events": [event.__dict__ for event in agent.calendar.events]}

    return app


app = create_app()
