from __future__ import annotations

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from school_agent.demo_engine import answer_student, memory_snapshot


ROOT = Path(__file__).parent
STATIC = ROOT / "static"


class SchoolAgentHandler(SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self.path = "/static/index.html"
        elif path == "/api/memory":
            self._send_json(memory_snapshot())
            return
        super().do_GET()

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/chat":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        message = str(payload.get("message", "")).strip()
        if not message:
            self.send_error(400, "Message is required")
            return

        self._send_json(answer_student(message))

    def translate_path(self, path: str) -> str:
        requested = urlparse(path).path.lstrip("/")
        return str(ROOT / requested)

    def _send_json(self, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    port = 8080
    server = ThreadingHTTPServer(("127.0.0.1", port), SchoolAgentHandler)
    print(f"School Agent UI running at http://127.0.0.1:{port}")
    print("Set GOOGLE_API_KEY before starting to use Gemini responses.")
    server.serve_forever()


if __name__ == "__main__":
    main()

