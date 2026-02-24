# chain-trace

Public crypto forensics skill for **ETH / Base / BSC / Solana** investigations.

Uses public data sources only (no API key required by default).

## What it does

- Builds an **entity graph** across on-chain + off-chain signals
- Verifies official identity with a **canonical CA matrix (P0/P1/P2)**
- Traces funding path, holders, liquidity, authority, and insider/bundle signals
- Supports EVM + Solana workflows with chain-specific public RPC fallback and anti-rate-limit probing
- Investigates website/domain/Twitter evidence and contradiction points
- Outputs a full report with:
  - **Evidence IDs (EID)**
  - **Clear UTC timeline + turning points**
  - **Risk/Confidence scoring**
  - **Scenario valuation (Bear/Base/Bull + EV)**

## Output standard

- Default: full report template (A~N)
- Deep mode: includes **O. Deep-Dive Annex**

## Install

```bash
npx skills add https://github.com/Xeron2000/chain-trace
```

## Usage

```bash
/chain-trace <token_or_wallet>
/chain-trace <target> --chain eth
/chain-trace <target> --chain base
/chain-trace <target> --chain bsc
/chain-trace <target> --chain solana
/chain-trace <target> --deep --all-sources --evidence-graph
/chain-trace <target> --deep --auto-link --insider --bundle --evidence-graph
```

## Notes

- This skill is for investigation/risk analysis only.
- Not investment advice.
