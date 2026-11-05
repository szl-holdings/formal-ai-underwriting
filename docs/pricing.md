# SZL Holdings API Pricing

All endpoints use x402 per-call pricing. No signup, no API key.
**The payment IS the credential.**

## Model Inference

| Endpoint | Price (all agents) | Price (verified bots) |
|---|---|---|
| `/v1/inference` | $0.05/call | $0.10/call |
| `/v1/chat` | $0.02/call | — |

## MCP Tool Calls (hatun-mcp)

| Endpoint | Price (all agents) | Price (verified bots) |
|---|---|---|
| `/mcp/*` | $0.01/tool call | $0.05/tool call |

## Premium APIs

| Endpoint | Price (verified bots) |
|---|---|
| `/api/a11oy/v1/mesh/*` | $0.05/call |
| `/api/a11oy/v1/attest/*` | $0.03/call |
| `/api/a11oy/v1/experimental/*` | $0.01/call |

## Web Traffic

| Surface | Price (verified bots) |
|---|---|
| Non-API pages | $1.00/visit |

## How to pay

1. Get an x402 client (https://x402.org)
2. Send a request to `api.a-11-oy.com/v1/inference`
3. Receive HTTP 402 with payment requirements
4. Pay via x402 (stablecoins)
5. Retry with payment attached
6. Get your inference

**No account. No API key. No subscription. The payment IS the credential.**

## Settlement

All payments settle peer-to-peer to:
`0x50E9B335ac233fcc5e87404367E7De253A63D460`

## Proof receipts

Every model available via this API carries a cryptographic proof receipt showing:
- Which datasets trained it
- When the training ran
- What hyperparameters were used
- The heartbeat log from the training run

See: https://huggingface.co/SZLHOLDINGS (all models with proof banners)
