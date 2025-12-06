from __future__ import annotations

import json
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Iterator, List

import requests

from src.application.llm import LLMClient
from src.application.respond_on_reviews import respond_on_reviews
from src.infra.clients.wildberries import WildberriesClient
from src.infra.config.settings import WildberriesSettings
from src.infra.logger import init_logger
from src.infra.prompt import PromptBuilder
from src.infra.reply_generator import LLMReplyGenerator


@dataclass
class FakeWBState:
    reviews: List[dict]
    published_payloads: List[dict] = field(default_factory=list)


@dataclass
class FakeLLMState:
    reply_text: str
    prompts: List[str] = field(default_factory=list)


class InlineSettings:
    """Minimal settings stub that satisfies WildberriesClient."""

    def __init__(self, *, base_url: str):
        self.wildberries = WildberriesSettings(
            api_token="fake-token",
            base_url=base_url.rstrip("/"),
            request_timeout=1,
            batch_size=10,
        )


class FakeHTTPLLMClient(LLMClient):
    """LLM client that forwards prompts to an HTTP endpoint (used only in tests)."""

    def __init__(self, *, base_url: str, **kwargs):
        super().__init__(**kwargs)
        self.base_url = base_url.rstrip("/")

    def generate_reply(self, prompt: str) -> str:
        response = requests.post(
            f"{self.base_url}/reply",
            json={"prompt": prompt},
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["text"]


def make_wb_handler(state: FakeWBState):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            if self.path.startswith("/api/v1/feedbacks"):
                payload = {"data": {"feedbacks": state.reviews}}
                body = json.dumps(payload).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            self.send_error(404)

        def do_POST(self):  # noqa: N802
            if self.path == "/api/v1/feedbacks/answer":
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length)
                payload = json.loads(body.decode("utf-8"))
                state.published_payloads.append(payload)
                self.send_response(200)
                self.end_headers()
                return
            self.send_error(404)

        def log_message(self, format: str, *args):  # noqa: A003
            return

    return Handler


def make_llm_handler(state: FakeLLMState):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):  # noqa: N802
            if self.path == "/reply":
                length = int(self.headers.get("Content-Length", 0))
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                state.prompts.append(payload["prompt"])
                body = json.dumps({"text": state.reply_text}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            self.send_error(404)

        def log_message(self, format: str, *args):  # noqa: A003
            return

    return Handler


@contextmanager
def run_http_server(handler_cls) -> Iterator[str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_e2e_flow_with_fake_wildberries_and_llm_endpoints():
    review_payload = {
        "id": "wb-1",
        "productId": "SKU-1",
        "userName": "Alice",
        "productValuation": 5,
        "text": "Сумка отличная, спасибо!",
        "pros": "Быстрая доставка",
        "cons": "",
        "createdDate": "2024-08-01T12:00:00Z",
    }
    wb_state = FakeWBState(reviews=[review_payload])
    llm_state = FakeLLMState(reply_text="Благодарим за отзыв и рады, что всё понравилось!")

    prompt_builder = PromptBuilder(template="Ответь дружелюбно на отзыв Wildberries.")
    logger = init_logger()

    with run_http_server(make_wb_handler(wb_state)) as wb_base_url:
        with run_http_server(make_llm_handler(llm_state)) as llm_base_url:
            wildberries_client = WildberriesClient(InlineSettings(base_url=wb_base_url))
            llm_client = FakeHTTPLLMClient(
                base_url=llm_base_url,
                temperature=0.1,
                max_tokens=200,
                instructions="Ответь кратко",
                timeout=2,
            )
            reply_generator = LLMReplyGenerator(prompt_builder, llm_client)

            respond_on_reviews(
                review_fetcher=wildberries_client,
                reply_generator=reply_generator,
                review_publisher=wildberries_client,
                logger=logger,
            )

    assert len(llm_state.prompts) == 1
    assert review_payload["text"] in llm_state.prompts[0]

    assert wb_state.published_payloads == [
        {"id": review_payload["id"], "text": llm_state.reply_text},
    ]
