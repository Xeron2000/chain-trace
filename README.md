# chain-trace

Zero-key crypto forensics for ETH / Base / BSC / Solana.

## Features

- Multi-chain support (ETH, Base, BSC, Solana)
- Zero API keys required
- Automated suspicious holder detection
- Holder clustering & origin tracking
- ASCII visualizations

## Quick Start

```bash
# Install
npx skills add https://github.com/Xeron2000/chain-trace

# Basic analysis
/chain-trace <token_or_wallet>

# Deep analysis
/chain-trace <target> --chain bsc --mode deep
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

# Threshold calibration
python scripts/calibrate_thresholds.py --input templates/calibration_dataset.example.json

# Tests
python tests/test_all.py
```

## License

MIT
