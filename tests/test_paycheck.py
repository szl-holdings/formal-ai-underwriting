#!/usr/bin/env python3
"""Regression tests for the fail-closed PayCheck adapter."""

from __future__ import annotations

import base64
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from payments.paycheck import (
    PaymentBlockedError,
    PaymentQuote,
    QuoteError,
    check_payment,
    fetch_payment_quote,
    payment_quote_from_header,
    require_allow,
)


class _Handler(BaseHTTPRequestHandler):
    payload: dict[str, object] = {"allow": True, "outcome": "allow", "reasons": ["test allow"]}
    requests: list[tuple[str, dict[str, str], dict[str, object]]] = []
    quote_header: str | None = None

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("content-length", "0"))
        body = json.loads(self.rfile.read(length))
        headers = {key.lower(): value for key, value in self.headers.items()}
        self.__class__.requests.append((self.path, headers, body))
        raw = json.dumps(self.__class__.payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802
        headers = {key.lower(): value for key, value in self.headers.items()}
        self.__class__.requests.append((self.path, headers, {}))
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/v1/completions")
            self.end_headers()
            return
        self.send_response(402)
        if self.__class__.quote_header is not None:
            self.send_header("PAYMENT-REQUIRED", self.__class__.quote_header)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, *_args: object) -> None:
        return


class TestPayCheckAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.api_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.thread.join(timeout=5)

    def setUp(self) -> None:
        _Handler.requests.clear()
        _Handler.payload = {"allow": True, "outcome": "allow", "reasons": ["test allow"]}
        _Handler.quote_header = None

    def payment(self) -> PaymentQuote:
        return PaymentQuote(
            "https://api.example.test/v1/chat/",
            "20000",
            "0xabc",
            "eip155:8453",
        )

    def test_allow_sends_exact_quote_and_rules(self) -> None:
        decision = check_payment(
            self.payment(),
            api_url=self.api_url,
            api_key="pc_free_test",
            rules={"maxAmount": "50000", "pinPayTo": True},
        )
        self.assertTrue(decision.allow)
        self.assertEqual(decision.outcome, "allow")
        self.assertEqual(len(_Handler.requests), 1)
        path, headers, body = _Handler.requests[0]
        self.assertEqual(path, "/v1/check-payment")
        self.assertEqual(headers["x-paycheck-key"], "pc_free_test")
        self.assertEqual(body, {
            "url": "https://api.example.test/v1/chat/",
            "amount": "20000",
            "payTo": "0xabc",
            "network": "eip155:8453",
            "rules": {"maxAmount": "50000", "pinPayTo": True},
        })

    def test_agent_route_is_fail_closed_until_allow(self) -> None:
        _Handler.payload = {"outcome": "review", "reasons": ["human review required"], "decision": "d-1"}
        decision = check_payment(self.payment(), api_url=self.api_url, agent_key="agent_secret")
        self.assertFalse(decision.allow)
        self.assertEqual(decision.outcome, "review")
        self.assertEqual(_Handler.requests[0][0], "/v1/authorize")
        self.assertEqual(_Handler.requests[0][1]["authorization"], "Bearer agent_secret")

    def test_denial_raises_before_signing(self) -> None:
        _Handler.payload = {"allow": False, "outcome": "deny", "reasons": ["wallet changed"]}
        decision = check_payment(self.payment(), api_url=self.api_url)
        with self.assertRaises(PaymentBlockedError):
            require_allow(decision)

    def test_invalid_json_blocks(self) -> None:
        original = _Handler.do_POST

        def invalid_json(handler: _Handler) -> None:
            length = int(handler.headers.get("content-length", "0"))
            handler.rfile.read(length)
            raw = b"not-json"
            handler.send_response(200)
            handler.send_header("Content-Type", "text/plain")
            handler.send_header("Content-Length", str(len(raw)))
            handler.end_headers()
            handler.wfile.write(raw)

        _Handler.do_POST = invalid_json  # type: ignore[method-assign]
        try:
            decision = check_payment(self.payment(), api_url=self.api_url)
        finally:
            _Handler.do_POST = original  # type: ignore[method-assign]
        self.assertFalse(decision.allow)
        self.assertEqual(decision.outcome, "error")

    def test_transport_failure_blocks(self) -> None:
        decision = check_payment(self.payment(), api_url="http://127.0.0.1:1", timeout=0.2)
        self.assertFalse(decision.allow)
        self.assertEqual(decision.outcome, "error")

    def test_quote_validation_rejects_non_decimal_amount(self) -> None:
        with self.assertRaises(ValueError):
            PaymentQuote("https://api.example.test/v1/chat/", "0.02", "0xabc")

    def test_fetch_payment_quote_parses_unpaid_x402_header(self) -> None:
        url = f"{self.api_url}/v1/completions"
        payload = {
            "x402Version": 2,
            "resource": {"url": url},
            "accepts": [{
                "scheme": "exact",
                "network": "eip155:8453",
                "amount": "20000",
                "payTo": "0xabc",
                "asset": "0xusdc",
            }],
        }
        _Handler.quote_header = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
        quote = fetch_payment_quote(url, network="eip155:8453")
        self.assertEqual(quote, PaymentQuote(url, "20000", "0xabc", "eip155:8453"))
        self.assertNotIn("x-payment", _Handler.requests[0][1])

    def test_quote_parser_rejects_resource_mismatch(self) -> None:
        payload = {
            "x402Version": 2,
            "resource": {"url": "https://other.example.test/v1/completions"},
            "accepts": [{"scheme": "exact", "network": "eip155:8453", "amount": "1", "payTo": "0xabc"}],
        }
        header = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
        with self.assertRaisesRegex(QuoteError, "resource URL"):
            payment_quote_from_header("https://api.example.test/v1/completions", header)

    def test_quote_fetch_rejects_missing_payment_required_header(self) -> None:
        with self.assertRaisesRegex(QuoteError, "PAYMENT-REQUIRED"):
            fetch_payment_quote(f"{self.api_url}/v1/completions")

    def test_quote_fetch_does_not_follow_redirects(self) -> None:
        with self.assertRaisesRegex(QuoteError, "HTTP 302"):
            fetch_payment_quote(f"{self.api_url}/redirect")

    def test_quote_parser_rejects_invalid_base64(self) -> None:
        with self.assertRaisesRegex(QuoteError, "invalid PAYMENT-REQUIRED"):
            payment_quote_from_header("https://api.example.test/v1/completions", "%%%")


if __name__ == "__main__":
    unittest.main()
