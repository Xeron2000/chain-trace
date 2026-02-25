# chain-trace

**Zero-key crypto forensics for ETH / Base / BSC / Solana.**

Reversed premium APIs + public data sources = institutional-grade analysis for free.

---

## 🎯 Features

- **Multi-Chain**: ETH, Base, BSC, Solana
- **Zero API Keys**: Uses reversed APIs and public endpoints
- **Insider Detection**: Automated wallet clustering, pre-pump accumulation, coordinated dumps
- **Full Reports**: Evidence IDs, UTC timelines, risk/confidence scoring, scenario valuation
- **Off-Chain Intel**: Website forensics, Twitter analysis, domain history

---

## 🚀 Data Sources

### Solana
- **Reversed Solscan API** ($200/mo → $0): Price, holder count, balance history
- **Public RPC**: Fallback with multi-endpoint rotation

### Base / ETH
- **Blockscout API** (Free): Full token/holder/transfer data
- **Public RPC**: 5+ endpoints with auto-failover

### BSC
- **Etherscan searchHandler** (Free): Basic token info
- **Public RPC**: 20+ Binance endpoints

### Market & Security (All Chains)
- **DexScreener**, **GeckoTerminal**, **Jupiter Lite**
- **GoPlus**, **Honeypot.is**

---

## 📦 Installation

```bash
npx skills add https://github.com/Xeron2000/chain-trace
```

---

## 📖 Usage

```bash
# Basic analysis
/chain-trace <token_or_wallet>

# Chain-specific
/chain-trace <target> --chain base

# Deep investigation (insider trading, clusters)
/chain-trace <target> --deep --auto-link --insider --bundle
```

---

## 🔧 Standalone Scripts

**Solana (Solscan)**
```bash
cd ~/.claude/skills/chain-trace

# Token price/market cap
uv run python scripts/solscan_client.py --mint <mint> --method token_data

# Holder count
uv run python scripts/solscan_client.py --mint <mint> --method token_holders_total
```

**EVM (Blockscout)**
```bash
# Base token info
uv run python scripts/evm_explorer_client.py --chain base --token <address> --method info

# Base holders
uv run python scripts/evm_explorer_client.py --chain base --token <address> --method holders
```

**Twitter (Auto-Camofox)**
```bash
# Single tweet (no Camofox)
uv run python scripts/fetch_twitter.py --url https://x.com/user/status/123456

# User timeline (auto-starts Camofox)
uv run python scripts/fetch_twitter.py --user username --limit 50
```

---

## ⚠️ Known Limitations

**Solscan API**
- ❌ Holder list, transfers, DeFi activities, portfolio (endpoints broken)
- ✅ Price, holder count, balance history

**Twitter ([x-tweet-fetcher](https://github.com/ythx-101/x-tweet-fetcher))**
- Single tweet: Requires full URL
- Timeline/replies: Auto-starts Camofox (requires Node.js)

**Rate Limits**
- Public RPCs may return 429/403
- Auto-retry with exponential backoff

---

## 📊 Report Structure

**Standard Mode (A~N)**
- Executive Summary (Risk/Confidence scores)
- Evidence Inventory (EID)
- Timeline (≥8 events, ≥3 turning points)
- On-Chain Evidence (holders, clusters, insider signals)
- Off-Chain Evidence (website, Twitter)
- Cross-Validation (2-of-3 identity check)
- Scenario Valuation (Bear/Base/Bull)

**Deep Mode (+O)**
- Address profile cards
- Decoded transactions (≥25)
- Funding path diagrams
- Dispute analysis

---

## 🔗 Related

- [paoloanzn/free-solscan-api](https://github.com/paoloanzn/free-solscan-api) - Reversed Solscan
- [ythx-101/x-tweet-fetcher](https://github.com/ythx-101/x-tweet-fetcher) - Twitter scraper
- [Blockscout](https://github.com/blockscout/blockscout) - Open-source explorer

---

## ⚠️ Disclaimer

- For research/risk analysis only
- Not investment advice
- Reversed APIs may violate ToS

---

## 📝 License

MIT
