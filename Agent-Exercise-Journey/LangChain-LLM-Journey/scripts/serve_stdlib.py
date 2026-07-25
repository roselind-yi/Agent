from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.agent.engine import JourneyAgent  # noqa: E402


agent = JourneyAgent()
INDEX_HTML = ROOT / "web" / "index.html"


class AgentHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/chat", "/index.html"}:
            body = INDEX_HTML.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/health":
            self._send_json({"status": "ok", "service": "journey-agent-stdlib"})
            return
        if parsed.path == "/api":
            self._send_json(
                {
                    "service": "journey-agent-stdlib",
                    "endpoints": [
                        "GET / or /chat - web demo",
                        "POST /chat - agent chat API",
                        "GET /health - health check",
                        "GET /knowledge/search?q=... - RAG search",
                        "GET /calendar/events - demo calendar events",
                    ],
                }
            )
            return
        if parsed.path == "/knowledge/search":
            params = parse_qs(parsed.query)
            query = params.get("q", [""])[0]
            top_k = int(params.get("top_k", ["3"])[0])
            hits = agent.retriever.search(query, top_k=top_k)
            self._send_json(
                {
                    "query": query,
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
            )
            return
        if parsed.path == "/calendar/events":
            self._send_json({"events": [event.__dict__ for event in agent.calendar.events]})
            return
        self._send_json({"error": "not_found"}, status=404)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/chat":
            self._send_json({"error": "not_found"}, status=404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            payload = json.loads(raw_body) if raw_body else {}
            message = payload.get("message", "")
            user_id = payload.get("user_id", "stdlib-client")
            if not message:
                self._send_json({"error": "message is required"}, status=400)
                return
            self._send_json(agent.answer(message, user_id=user_id).to_dict())
        except json.JSONDecodeError:
            self._send_json({"error": "invalid_json"}, status=400)

    def log_message(self, format: str, *args) -> None:
        print("%s - %s" % (self.address_string(), format % args))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), AgentHandler)
    print(f"Serving Journey Agent on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
