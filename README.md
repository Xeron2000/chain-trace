# chain-trace

**Public crypto forensics skill for ETH / Base / BSC / Solana investigations.**

Zero API keys required. Uses reversed premium APIs and public data sources to provide institutional-grade chain analysis for free.

---

## 🎯 What it does

- **Entity Graph Construction**: Maps on-chain + off-chain relationships (wallets, contracts, websites, social accounts)
- **Official Identity Verification**: Canonical CA matrix with P0/P1/P2 evidence levels
- **Funding Path Tracing**: Tracks money flow from CEX deposits to final destinations
- **Holder Analysis**: Top holder concentration, LP depth, insider/bundle detection
- **Automated Cluster Detection**: Discovers coordinated wallet groups via co-funding, co-timing, shared exits
- **Insider Trading Signals**: Pre-announcement accumulation, synchronized dumps, rat trading patterns
- **Contract Security**: Honeypot detection, dangerous permissions, tax analysis
- **Cross-Chain Support**: ETH, Base, BSC (EVM), Solana
- **Off-Chain Intelligence**: Website forensics, Twitter graph analysis, domain age, historical snapshots
- **Comprehensive Reporting**: Evidence IDs (EID), UTC timelines, risk/confidence scoring, scenario valuation

---

## 🚀 Data Sources (No API Keys)

### Solana
**Priority 1: Reversed Solscan API** ($200/mo → **$0**)
- Token holders, DeFi activities, portfolio data
- Based on [paoloanzn/free-solscan-api](https://github.com/paoloanzn/free-solscan-api)
- Auto-fallback to public RPC on failure

**Priority 2: Public RPC**
- `api.mainnet-beta.solana.com` + 5 backup endpoints
- Multi-endpoint rotation with rate-limit handling

### Base / ETH
**Priority 1: Blockscout API** (Free, no key)
- Full REST API: tokens, holders, transfers, transactions
- Base: `base.blockscout.com/api/v2`
- ETH: `eth.blockscout.com/api/v2`

**Priority 2: Etherscan searchHandler** (Free, no key)
- Basic token info via `/searchHandler` endpoint
- Works on BSCScan, BaseScan, Etherscan

**Priority 3: Public RPC**
- 5+ endpoints per chain with automatic failover

### BSC
**Priority 1: Etherscan searchHandler** (Free, no key)
- Token search and basic info

**Priority 2: Public RPC**
- 20+ Binance official + community endpoints

### Market Data (All Chains)
- **DexScreener**: Price, liquidity, volume, pairs
- **GeckoTerminal**: Token info, pools, market data
- **Jupiter Lite API** (Solana): Price feeds, token search

### Security (All Chains)
- **GoPlus**: Honeypot detection, tax analysis, contract risks
- **Honeypot.is**: EVM honeypot verification

---

## 📊 Report Structure

### Standard Mode (A~N sections)
```
A. Executive Summary (Risk/Confidence scores, verdict)
B. Scope & Method
C. Entity Graph Snapshot
D. Evidence Inventory (EID)
E. Chronology Timeline (≥8 events)
E2. Timeline Turning Points (≥3 critical moments)
F. On-Chain Evidence (holders, liquidity, authority, clusters)
G. Off-Chain Evidence (website, Twitter, domain)
H. Claim Resolution Matrix (Confirmed/Unverified/Contradicted)
I. Cross-Validation (2-of-3 identity check, CA matrix)
J. Scenario Valuation (Bear/Base/Bull + EV)
K. Red Flags Checklist
L. Data Quality & Unknowns
M. Final Action Guidance
N. Appendix (Raw Extracts)
```

### Deep Mode (adds O section)
```
O. Deep-Dive Annex
   - Address profile cards (deployer, treasury, fee receiver)
   - Decoded transaction details (≥25 txs)
   - Multi-tier funding path diagrams
   - Dispute point analysis
   - Unresolved questions + next steps
```

---

## 🛠️ Installation

```bash
npx skills add https://github.com/Xeron2000/chain-trace
```

Or manually:
```bash
git clone https://github.com/Xeron2000/chain-trace ~/.claude/skills/chain-trace
cd ~/.claude/skills/chain-trace
uv sync --locked
```

---

## 📖 Usage

### Basic Analysis
```bash
/chain-trace <token_address_or_wallet>
```

### Chain-Specific
```bash
/chain-trace <target> --chain eth
/chain-trace <target> --chain base
/chain-trace <target> --chain bsc
/chain-trace <target> --chain solana
```

### Deep Investigation
```bash
# Full deep dive with all sources
/chain-trace <target> --deep --all-sources --evidence-graph

# Auto-discover insider trading & coordinated wallets
/chain-trace <target> --deep --auto-link --insider --bundle --evidence-graph
```

### Standalone Scripts

**Test Solscan Client (Solana)**
```bash
cd ~/.claude/skills/chain-trace

# Token data (price, market cap)
uv run python scripts/solscan_client.py \
  --mint So11111111111111111111111111111111111111112 \
  --method token_data

# Token holders
uv run python scripts/solscan_client.py \
  --mint <token_mint> \
  --method token_holders

# Disable Solscan, use public RPC only
uv run python scripts/solscan_client.py \
  --address <address> \
  --method account_info \
  --no-solscan
```

**Test EVM Explorer Client (Base/BSC/ETH)**
```bash
# Base token info (via Blockscout)
uv run python scripts/evm_explorer_client.py \
  --chain base \
  --token 0x4200000000000000000000000000000000000006 \
  --method info

# Base token holders
uv run python scripts/evm_explorer_client.py \
  --chain base \
  --token 0x4200000000000000000000000000000000000006 \
  --method holders

# BSC token search (via searchHandler)
uv run python scripts/evm_explorer_client.py \
  --chain bsc \
  --address 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c \
  --method search
```

---

## 🔍 Key Features

### Insider Trading Detection
Automatically identifies:
- **Pre-announcement accumulation**: Wallets buying before official announcements
- **Coordinated clusters**: Groups sharing funding sources, timing, exit paths
- **Synchronized dumps**: Multiple wallets selling at the same time
- **Rat trading patterns**: Early access + quick exits

Scoring system:
- `insider_score ≥ 0.70`: High probability insider trading
- `relation_score ≥ 0.75`: Strong wallet cluster linkage
- Deterministic signals (shared funder, shared sink) weighted higher than heuristics

### Canonical CA Verification
Multi-level evidence matrix:
- **P0**: Official website/docs/Twitter statements
- **P1**: On-chain endorsement (official wallet holds/signs)
- **P2**: DEX/aggregator/media listings

Verdict:
- `Official`: ≥1 P0 + ≥1 P1, no conflicts
- `Unverified`: Missing P0 or P1
- `Contradicted`: Official denial exists

### Risk Scoring
```
Risk = 0.30×funding + 0.25×clusters + 0.20×liquidity + 0.15×permissions + 0.10×off-chain
Confidence = 0.40×coverage + 0.40×agreement + 0.20×freshness
```

---

## 🧪 Example Output

```markdown
## Token Forensics Report: WETH [Base]

### A. Executive Summary
- Risk Score: 12/100 (Low)
- Confidence Score: 95/100 (Very High)
- Verdict: Low Risk
- Canonical CA Status: Official

Why:
1. Official Base L2 predeploy contract (base.org confirmed)
2. 4.16M+ holders, $454M circulating market cap
3. Top holders = verified DeFi protocols (Morpho, Uniswap, Aave)
4. No dangerous permissions (buy_tax=0, sell_tax=0, no honeypot)
5. $50M+ liquidity across multiple DEXs

### F. On-Chain Evidence
Top Holders (net):
| Rank | Address | Name | Balance | % |
|------|---------|------|---------|---|
| 1 | 0xBBBB...FFCb | Morpho | 44,440 WETH | 18.1% |
| 2 | 0x6c56...1372 | UniswapV3Pool | 21,917 WETH | 8.9% |

Authority / Security:
✅ is_honeypot: 0
✅ buy_tax: 0
✅ sell_tax: 0
✅ can_take_back_ownership: 0

### K. Red Flags Checklist
Red Flags: 0/8 ✅
```

---

## 🔧 Technical Details

### Reversed APIs
- **Solscan**: Bypasses $200/mo paywall via internal API reverse engineering
  - Auth token = random string with `B9dls0fK` inserted at random position
  - Uses `cloudscraper` to bypass Cloudflare protection
- **Blockscout**: Official public API, no authentication needed
- **Etherscan searchHandler**: Undocumented JSON endpoint, requires `X-Requested-With: XMLHttpRequest`

### Rate Limit Handling
- Multi-endpoint pools (5-20 endpoints per chain)
- Exponential backoff with jitter
- Automatic failover on 429/403/1010 errors
- Per-endpoint cooldown tracking

### Dependencies
```toml
[dependencies]
free-solscan-api = { url = "https://github.com/paoloanzn/free-solscan-api/releases/download/0.0.4/free_solscan_api-0.0.4-py3-none-any.whl" }
```

---

## ⚠️ Disclaimer

- **For research and risk analysis only**
- **Not investment advice**
- Reversed APIs may violate ToS (use at your own risk)
- Data accuracy depends on public source availability
- Rate limits may affect completeness

---

## 📝 License

MIT

---

## 🤝 Contributing

PRs welcome! Especially:
- New chain support (Arbitrum, Optimism, Polygon)
- Additional free data sources
- Improved cluster detection algorithms
- Better report templates

---

## 🔗 Related Projects

- [paoloanzn/free-solscan-api](https://github.com/paoloanzn/free-solscan-api) - Reversed Solscan API
- [Blockscout](https://github.com/blockscout/blockscout) - Open-source block explorer
- [GoPlus Security](https://gopluslabs.io/) - Token security API
