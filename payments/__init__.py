"""Optional payment-boundary integrations for Formal AI Underwriting.

The payment gate is deliberately separate from certification evidence. It
checks a proposed x402 payment before a caller signs it and never signs or
sends the payment itself.

SPDX-License-Identifier: Apache-2.0
"""
