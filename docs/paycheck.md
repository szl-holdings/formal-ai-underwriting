# Optional x402 payment preflight

The `payments.paycheck` module adds a fail-closed check before an existing x402
caller signs a payment. It uses Python's standard library and does not add a
runtime dependency or a wallet implementation.

The caller supplies the exact endpoint URL, amount, payout wallet and network
from the 402 quote. The adapter sends those fields to Lumière PayCheck and
returns an allow, deny, review or error decision. Only an explicit allow clears
the gate.

```python
from payments.paycheck import PaymentQuote, check_payment, require_allow

quote = PaymentQuote(
    url="https://api.example.com/v1/chat/",
    amount="20000",          # atomic USDC units
    pay_to="0x…",             # exact payout wallet from the quote
    network="eip155:8453",    # Base
)

decision = check_payment(
    quote,
    api_key="pc_free_…",      # optional, use an environment variable
    rules={
        "maxAmount": "50000",
        "allowCaution": False,
        "requireVerified": True,
        "pinPayTo": True,
    },
)
require_allow(decision)

# Call the existing x402 signer only after the gate returns.
```

The adapter never signs or submits a payment. It never receives a prompt or a
model response. It fails closed on a timeout, transport error, HTTP error,
malformed JSON, deny decision or review decision. A team-plan `agent_key` can
be supplied instead of a free-route `api_key` to use `/v1/authorize` and carry
the returned receipt in the bounded decision object.

The command-line entry point is available after installation:

```bash
szl-paycheck-preflight \
  --url https://api.example.com/v1/chat/ \
  --amount 20000 \
  --pay-to 0x… \
  --network eip155:8453 \
  --rules-json '{"maxAmount":"50000","requireVerified":true}'
```

Exit status `0` means allow, `2` means deny or review, and `3` means an input
or service error. JSON output contains the payment fields and reasons. It does
not include the raw PayCheck response.

This adapter supplies payment-endpoint evidence. It does not establish model
lineage, Lean proof status, abstention results, release authorization or a
certification decision. Those remain separate estate evidence axes.

The hosted PayCheck service is an external dependency. Review its current
security, privacy, receipt-key and availability terms before using an agent
key or placing it on a production payment path.

SPDX-License-Identifier: Apache-2.0
