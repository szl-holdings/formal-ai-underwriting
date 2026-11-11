#!/usr/bin/env python3
"""Fail-closed x402 pre-payment checks through Lumière PayCheck.

This module is a small standard-library-only adapter for callers that already
have an x402 payment quote. It asks PayCheck whether the exact endpoint,
amount, payout wallet, and network may be paid. The caller remains responsible
for signing and submitting the payment after :func:`require_allow` returns.

The adapter never signs a wallet transaction, sends a prompt, or reports a
response body. A timeout, malformed response, unavailable service, denied
decision, or review decision blocks the payment.

SPDX-License-Identifier: Apache-2.0
"""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import sys
from dataclasses import dataclass
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener, urlopen


DEFAULT_API_URL = "https://lumierepaycheck.org"
USER_AGENT = "formal-ai-underwriting-paycheck/0.1.0"
MAX_RESPONSE_BYTES = 256 * 1024
MAX_REQUEST_BYTES = 1024 * 1024
_OUTCOMES = {"allow", "deny", "review", "error"}


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, *_args: Any, **_kwargs: Any) -> None:
        return None


_QUOTE_OPENER = build_opener(_NoRedirectHandler)


@dataclass(frozen=True)
class PaymentQuote:
    """The exact fields selected from an x402 402 quote."""

    url: str
    amount: str
    pay_to: str
    network: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.url, str):
            raise ValueError("url must be an absolute HTTP(S) URL")
        if not isinstance(self.amount, str):
            raise ValueError("amount must be a non-negative decimal string")
        if not isinstance(self.pay_to, str):
            raise ValueError("pay_to must be non-empty")
        if self.network is not None and not isinstance(self.network, str):
            raise ValueError("network must be a string when supplied")
        parsed = urlsplit(self.url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("url must be an absolute HTTP(S) URL")
        if not self.amount.isdigit():
            raise ValueError("amount must be a non-negative decimal string")
        if not self.pay_to.strip():
            raise ValueError("pay_to must be non-empty")

    def as_payload(self) -> dict[str, str]:
        payload = {
            "url": self.url,
            "amount": self.amount,
            "payTo": self.pay_to,
        }
        if self.network:
            payload["network"] = self.network
        return payload


class QuoteError(ValueError):
    """Raised when an endpoint does not provide a usable x402 quote."""


def _decode_payment_required(header_value: str) -> Any:
    if not isinstance(header_value, str) or not header_value.strip():
        raise QuoteError("endpoint returned an empty PAYMENT-REQUIRED header")
    try:
        encoded = header_value.strip()
        padding = "=" * (-len(encoded) % 4)
        raw = base64.b64decode((encoded + padding).encode("ascii"), altchars=b"-_", validate=True)
    except (UnicodeEncodeError, ValueError, binascii.Error) as error:
        raise QuoteError("endpoint returned an invalid PAYMENT-REQUIRED header") from error
    if len(raw) > MAX_RESPONSE_BYTES:
        raise QuoteError("PAYMENT-REQUIRED header exceeded the size limit")
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise QuoteError("endpoint returned non-JSON PAYMENT-REQUIRED data") from error


def payment_quote_from_header(
    url: str,
    header_value: str,
    *,
    network: str | None = None,
) -> PaymentQuote:
    """Parse one x402 v2 ``PAYMENT-REQUIRED`` header without accepting payment data."""

    parsed_url = urlsplit(url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise QuoteError("url must be an absolute HTTP(S) URL")
    payload = _decode_payment_required(header_value)
    if not isinstance(payload, dict) or payload.get("x402Version") != 2:
        raise QuoteError("endpoint did not return an x402 v2 quote")
    resource = payload.get("resource")
    if not isinstance(resource, dict) or resource.get("url") != url:
        raise QuoteError("x402 quote resource URL does not match the requested URL")
    accepts = payload.get("accepts")
    if not isinstance(accepts, list) or not accepts:
        raise QuoteError("x402 quote has no payment options")
    candidates = []
    for option in accepts:
        if not isinstance(option, dict) or option.get("scheme") != "exact":
            continue
        if network is not None and option.get("network") != network:
            continue
        candidates.append(option)
    if len(candidates) != 1:
        if not candidates:
            detail = f" for network {network!r}" if network else ""
            raise QuoteError(f"x402 quote has no exact payment option{detail}")
        raise QuoteError("x402 quote has multiple exact payment options; specify a network")
    option = candidates[0]
    amount = option.get("amount")
    pay_to = option.get("payTo")
    selected_network = option.get("network")
    if not isinstance(amount, str) or not amount.isdigit():
        raise QuoteError("x402 quote amount must be a non-negative decimal string")
    if not isinstance(pay_to, str) or not pay_to.strip():
        raise QuoteError("x402 quote payTo must be non-empty")
    if not isinstance(selected_network, str) or not selected_network:
        raise QuoteError("x402 quote network must be a non-empty string")
    return PaymentQuote(url, amount, pay_to, selected_network)


def fetch_payment_quote(
    url: str,
    *,
    network: str | None = None,
    method: str = "GET",
    data: bytes | None = None,
    headers: Mapping[str, str] | None = None,
    timeout: float = 8.0,
) -> PaymentQuote:
    """Fetch and parse a quote without sending a payment or reading a response body.

    The request is unpaid. A redirect to a different URL, a missing or malformed
    x402 header, and every HTTP status other than 402 fail closed.
    """

    if timeout <= 0:
        raise ValueError("timeout must be positive")
    parsed_url = urlsplit(url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise ValueError("url must be an absolute HTTP(S) URL")
    if not isinstance(method, str) or not method.strip() or not method.strip().isalpha():
        raise ValueError("method must be a non-empty string")
    if data is not None and not isinstance(data, bytes):
        raise ValueError("data must be bytes when supplied")
    if data is not None and len(data) > MAX_REQUEST_BYTES:
        raise ValueError("request body exceeded the size limit")
    request_headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    if headers is not None:
        if not isinstance(headers, Mapping):
            raise ValueError("headers must be a mapping")
        for key, value in headers.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValueError("headers must contain string names and values")
            if key.casefold() in {"x-payment", "payment-signature"}:
                raise ValueError("fetch_payment_quote never accepts a payment header")
            request_headers[key] = value
    request = Request(url, data=data, headers=request_headers, method=method.upper())
    try:
        with _QUOTE_OPENER.open(request, timeout=timeout) as response:
            status = int(response.status)
            response_url = response.geturl()
            header_value = response.headers.get("PAYMENT-REQUIRED")
    except HTTPError as error:
        status = error.code
        response_url = error.geturl()
        header_value = error.headers.get("PAYMENT-REQUIRED")
    except (OSError, URLError, TimeoutError) as error:
        raise QuoteError(f"could not reach x402 endpoint: {error.__class__.__name__}") from error
    if response_url != url:
        raise QuoteError("x402 endpoint redirected to a different URL")
    if status != 402:
        raise QuoteError(f"x402 endpoint answered HTTP {status}, expected 402")
    return payment_quote_from_header(url, header_value, network=network)


@dataclass(frozen=True)
class PayCheckDecision:
    """A bounded PayCheck result safe to log without raw response data."""

    allow: bool
    outcome: str
    reasons: tuple[str, ...]
    payment: PaymentQuote
    status: int | None = None
    receipt: str | None = None
    decision_id: str | None = None

    def __post_init__(self) -> None:
        if self.outcome not in _OUTCOMES:
            raise ValueError(f"unsupported outcome {self.outcome!r}")
        if self.allow and self.outcome != "allow":
            raise ValueError("only an allow outcome may allow a payment")

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "allow": self.allow,
            "outcome": self.outcome,
            "reasons": list(self.reasons),
            "payment": self.payment.as_payload(),
        }
        if self.status is not None:
            result["status"] = self.status
        if self.receipt is not None:
            result["receipt"] = self.receipt
        if self.decision_id is not None:
            result["decision_id"] = self.decision_id
        return result


class PaymentBlockedError(RuntimeError):
    """Raised when a payment cannot clear the pre-payment gate."""

    def __init__(self, decision: PayCheckDecision) -> None:
        self.decision = decision
        reason = "; ".join(decision.reasons) or "no reason returned"
        super().__init__(f"PayCheck blocked payment ({decision.outcome}): {reason}")


def _error_decision(payment: PaymentQuote, reason: str, status: int | None = None) -> PayCheckDecision:
    return PayCheckDecision(
        allow=False,
        outcome="error",
        reasons=(reason,),
        payment=payment,
        status=status,
    )


def _response_decision(payment: PaymentQuote, payload: Any, status: int) -> PayCheckDecision:
    if not isinstance(payload, dict):
        return _error_decision(payment, "PayCheck returned a non-object JSON response", status)

    raw_outcome = payload.get("outcome")
    outcome = raw_outcome if raw_outcome in _OUTCOMES else ("allow" if payload.get("allow") is True else "deny")
    reasons_value = payload.get("reasons", [])
    if not isinstance(reasons_value, list) or not all(isinstance(item, str) for item in reasons_value):
        return _error_decision(payment, "PayCheck returned invalid reasons", status)
    reasons = tuple(reasons_value) or (("PayCheck allowed the payment" if outcome == "allow" else "PayCheck denied the payment"),)

    receipt = payload.get("receipt")
    if receipt is not None and not isinstance(receipt, str):
        return _error_decision(payment, "PayCheck returned an invalid receipt", status)
    decision_id = payload.get("decision")
    if decision_id is not None and not isinstance(decision_id, str):
        return _error_decision(payment, "PayCheck returned an invalid decision id", status)

    allow = payload.get("allow") is True and outcome == "allow"
    if outcome == "allow" and not allow:
        return _error_decision(payment, "PayCheck returned an inconsistent allow decision", status)
    return PayCheckDecision(
        allow=allow,
        outcome=outcome,
        reasons=reasons,
        payment=payment,
        status=status,
        receipt=receipt,
        decision_id=decision_id,
    )


def check_payment(
    payment: PaymentQuote,
    *,
    api_url: str = DEFAULT_API_URL,
    api_key: str | None = None,
    agent_key: str | None = None,
    rules: Mapping[str, object] | None = None,
    timeout: float = 8.0,
) -> PayCheckDecision:
    """Ask PayCheck whether ``payment`` may be signed.

    The free route uses ``/v1/check-payment``. A supplied ``agent_key`` uses
    the team route ``/v1/authorize`` and receives any signed receipt returned
    by PayCheck. Both routes fail closed on transport, HTTP, and schema errors.
    """

    if timeout <= 0:
        raise ValueError("timeout must be positive")
    base = api_url.rstrip("/")
    if not base:
        raise ValueError("api_url must be non-empty")
    if rules is not None and not isinstance(rules, Mapping):
        raise ValueError("rules must be a mapping")

    path = "/v1/authorize" if agent_key else "/v1/check-payment"
    body: dict[str, object] = payment.as_payload()
    if agent_key is None and rules:
        body["rules"] = dict(rules)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }
    if api_key and agent_key is None:
        headers["x-paycheck-key"] = api_key
    if agent_key:
        headers["Authorization"] = f"Bearer {agent_key}"

    request = Request(
        f"{base}{path}",
        data=json.dumps(body, separators=(",", ":")).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            status = int(response.status)
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except HTTPError as error:
        return _error_decision(payment, f"PayCheck answered HTTP {error.code}", error.code)
    except (OSError, URLError, TimeoutError) as error:
        return _error_decision(payment, f"could not reach PayCheck: {error.__class__.__name__}")

    if len(raw) > MAX_RESPONSE_BYTES:
        return _error_decision(payment, "PayCheck response exceeded the size limit", status)

    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return _error_decision(payment, "PayCheck returned invalid JSON", status)
    return _response_decision(payment, payload, status)


def require_allow(decision: PayCheckDecision) -> PayCheckDecision:
    """Return an allowed decision or raise before a wallet signer is called."""

    if not decision.allow:
        raise PaymentBlockedError(decision)
    return decision


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a fail-closed x402 PayCheck preflight")
    parser.add_argument("--url", required=True, help="absolute x402 endpoint URL")
    parser.add_argument("--amount", required=True, help="quoted amount in atomic units")
    parser.add_argument("--pay-to", required=True, dest="pay_to", help="quoted payout wallet")
    parser.add_argument("--network", help="x402 network identifier")
    parser.add_argument("--api-url", default=DEFAULT_API_URL)
    parser.add_argument("--api-key", help="optional free-route API key")
    parser.add_argument("--agent-key", help="optional team-plan agent key")
    parser.add_argument("--rules-json", help="optional JSON object of free-route rules")
    parser.add_argument("--timeout", type=float, default=8.0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    rules: Mapping[str, object] | None = None
    if args.rules_json:
        try:
            parsed = json.loads(args.rules_json)
        except json.JSONDecodeError as error:
            print(json.dumps({"allow": False, "outcome": "error", "reasons": [f"invalid --rules-json: {error.msg}"]}))
            return 3
        if not isinstance(parsed, dict):
            print(json.dumps({"allow": False, "outcome": "error", "reasons": ["--rules-json must be a JSON object"]}))
            return 3
        rules = parsed

    try:
        payment = PaymentQuote(args.url, args.amount, args.pay_to, args.network)
        decision = check_payment(
            payment,
            api_url=args.api_url,
            api_key=args.api_key,
            agent_key=args.agent_key,
            rules=rules,
            timeout=args.timeout,
        )
    except ValueError as error:
        print(json.dumps({"allow": False, "outcome": "error", "reasons": [str(error)]}))
        return 3

    print(json.dumps(decision.as_dict(), sort_keys=True))
    return 0 if decision.allow else (3 if decision.outcome == "error" else 2)


if __name__ == "__main__":
    sys.exit(main())
