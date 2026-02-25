# chain-trace

Zero-key crypto forensics for ETH / Base / BSC / Solana.

## Features

- Multi-chain support (ETH, Base, BSC, Solana)
- Zero API keys required
- Automated suspicious holder detection
- Holder clustering & origin tracking
- Snapshot comparison
- ASCII visualizations
- Continuous monitoring

## Quick Start

```bash
# Install
npx skills add https://github.com/Xeron2000/chain-trace

# Basic analysis
/chain-trace <token_or_wallet>

# Deep analysis with snapshot
/chain-trace <target> --chain bsc --mode deep --snapshot

# Monitor suspicious address
python scripts/monitor.py add 0x... --chain bsc --reason "suspicious"
python scripts/monitor.py run --interval 300
```

## Modes

- `quick` (5min): Basic info + suspicious detection
- `standard` (15min): + DBSCAN clustering
- `deep` (30-60min): + Origin tracking + coordinated distribution

## Data Sources

- **Solana**: Reversed Solscan API + Public RPC
- **Base/ETH**: Blockscout API + Public RPC
- **BSC**: Etherscan searchHandler + Public RPC
- **Market**: DexScreener, GeckoTerminal, Jupiter
- **Security**: GoPlus, Honeypot.is

## Standalone Scripts

```bash
cd ~/.claude/skills/chain-trace

# Config
python scripts/config.py --init

# Analysis
python scripts/chain_trace.py 0x... --chain bsc --mode deep

# Snapshots
python scripts/snapshot_manager.py list --chain bsc
python scripts/snapshot_manager.py compare OLD_ID NEW_ID

# Monitor
python scripts/monitor.py add 0x... --chain bsc
python scripts/monitor.py run --interval 300

# Tests
python tests/test_all.py
```

## License

MIT
