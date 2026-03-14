from __future__ import annotations

import json
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .enforcement import PolicyViolationError, validate_intent
from .execution import execute_transfer
from .models import Intent, Policy
from .reasoning import ReasoningError, parse_intent_from_text

ROOT = Path(__file__).resolve().parent.parent
POLICY_FILE = ROOT / "data" / "policies.json"
FRONTEND_DIR = ROOT / "frontend"


def load_policies() -> dict[str, Policy]:
    raw = json.loads(POLICY_FILE.read_text(encoding="utf-8"))
    return {name: Policy.from_dict(payload) for name, payload in raw.items()}


def process_request_text(request_text: str, policy_name: str) -> dict[str, Any]:
    policies = load_policies()
    if policy_name not in policies:
        raise KeyError(f"Unknown policy '{policy_name}'. Available: {list(policies.keys())}")

    intent = parse_intent_from_text(request_text)
    policy = policies[policy_name]
    trace = validate_intent(intent, policy)
    receipt_path = execute_transfer(intent)

    return {
        "decision": "allowed",
        "policy": policy_name,
        "policy_snapshot": asdict(policy),
        "intent": asdict(intent),
        "trace": trace,
        "receipt_file": str(receipt_path.relative_to(ROOT)),
    }


class FArmorHandler(BaseHTTPRequestHandler):
    def _json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, path: Path, content_type: str) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return
        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        if self.path in {"/", "/index.html"}:
            self._serve_file(FRONTEND_DIR / "index.html", "text/html; charset=utf-8")
            return
        if self.path == "/styles.css":
            self._serve_file(FRONTEND_DIR / "styles.css", "text/css; charset=utf-8")
            return
        if self.path == "/app.js":
            self._serve_file(FRONTEND_DIR / "app.js", "application/javascript; charset=utf-8")
            return
        if self.path == "/api/policies":
            policies = {k: asdict(v) for k, v in load_policies().items()}
            self._json(HTTPStatus.OK, {"policies": policies})
            return
        if self.path == "/api/examples":
            self._json(
                HTTPStatus.OK,
                {
                    "examples": [
                        "I am the DevOps Bot, pay $400 to AWS for hosting.",
                        "I am the Engineer, pay $900 to AWS for a surprise bill.",
                        "I am the Bot, pay $500 to AWS for delegated hosting request.",
                    ]
                },
            )
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Route not found")

    def do_POST(self) -> None:
        if self.path != "/api/execute":
            self.send_error(HTTPStatus.NOT_FOUND, "Route not found")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length)
        try:
            payload = json.loads(raw.decode("utf-8"))
            request_text = str(payload.get("request_text", ""))
            policy_name = str(payload.get("policy_name", "default"))

            result = process_request_text(request_text, policy_name)
            self._json(HTTPStatus.OK, result)
        except (ReasoningError, ValueError, KeyError) as err:
            self._json(
                HTTPStatus.BAD_REQUEST,
                {
                    "decision": "blocked",
                    "reason": str(err),
                },
            )
        except PolicyViolationError as err:
            self._json(
                HTTPStatus.FORBIDDEN,
                {
                    "decision": "blocked",
                    "reason": str(err),
                },
            )


def run_server(host: str = "127.0.0.1", port: int = 8080) -> None:
    server = ThreadingHTTPServer((host, port), FArmorHandler)
    print(f"FArmor server listening at http://{host}:{port}")
    print("Open / in your browser to use the frontend demo.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.server_close()


if __name__ == "__main__":
    run_server()
