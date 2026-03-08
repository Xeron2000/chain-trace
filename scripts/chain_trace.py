#!/usr/bin/env python3
"""
Chain Trace - Main Orchestrator

Unified entry point for multi-chain forensics analysis.
Modes: quick (5min), standard (15min), deep (30-60min)
"""

import argparse
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from datetime import datetime
from typing import Dict, Any, Optional

# Import modules
from scripts.config import get_config
from scripts.cache_manager import get_cache
from scripts.rpc_manager import create_rpc_manager
from scripts.evm_explorer_client import EVMExplorerClient
from scripts.solscan_client import SolscanClient
from scripts.holder_analyzer import HolderAnalyzer, Holder
from scripts.suspicious_detector import SuspiciousDetector
from scripts.visualizer import Visualizer


class ChainTrace:
    """Main orchestrator for chain forensics"""

    def __init__(self, chain: str, mode: str = "standard"):
        self.chain = chain
        self.mode = mode
        self.config = get_config()
        self.cache = get_cache() if self.config.cache.enabled else None

        # Initialize RPC manager
        self.rpc_manager = create_rpc_manager(
            chain,
            max_retries=self.config.rpc.max_retries,
            timeout=self.config.rpc.timeout,
            probe_on_init=self.config.rpc.probe_on_init
        )

        # Initialize clients
        if chain in ["eth", "base", "bsc"]:
            self.explorer = EVMExplorerClient(chain=chain)
        elif chain == "solana":
            self.explorer = SolscanClient(prefer_solscan=True)

        self.results = {}
    
    def analyze(self, target: str) -> Dict[str, Any]:
        """
        Run complete analysis.
        
        Args:
            target: Token or wallet address
        
        Returns:
            Analysis results dict
        """
        print(f"[ChainTrace] Starting {self.mode} mode analysis...")
        print(f"[ChainTrace] Target: {target}")
        print(f"[ChainTrace] Chain: {self.chain}\n")
        
        # Phase 1: Basic info
        print("Phase 1: Fetching token info...")
        token_info = self._fetch_token_info(target)
        self.results['token_info'] = token_info
        
        # Phase 2: Holders
        print("Phase 2: Analyzing holders...")
        holders_data = self._fetch_holders(target)
        self.results['holders'] = holders_data
        
        # Phase 3: Suspicious detection
        print("Phase 3: Detecting suspicious patterns...")
        suspicious = self._detect_suspicious(holders_data)
        self.results['suspicious'] = suspicious
        
        # Phase 4: Clustering (standard/deep only)
        if self.mode in ["standard", "deep"]:
            print("Phase 4: Running DBSCAN clustering...")
            clusters = self._analyze_clusters(holders_data, target)
            self.results['clusters'] = clusters
        
        # Phase 5: Origin tracking (deep only)
        if self.mode == "deep":
            print("Phase 5: Tracking holder origins...")
            origins = self._track_origins(holders_data, target)
            self.results['origins'] = origins
        
        # Phase 6: Risk scoring
        print("Phase 6: Calculating risk scores...")
        risk_scores = self._calculate_risk()
        self.results['risk_scores'] = risk_scores

        print("\n[ChainTrace] Analysis complete!")
        return self.results
    
    def _fetch_token_info(self, address: str) -> Dict:
        """Fetch basic token info"""
        if self.chain in ["eth", "base", "bsc"]:
            info = self.explorer.token_info(address)
            return info or {}
        if self.chain == "solana":
            info: Dict[str, Any] = {}

            account_info = getattr(self.explorer, 'account_info', lambda _addr: {})(address) or {}
            token_info = account_info.get('tokenInfo', {})
            metadata = account_info.get('metadata', {}).get('data', {})
            own_extensions = token_info.get('ownExtensions', {})

            info.update({
                'name': metadata.get('name'),
                'symbol': metadata.get('symbol'),
                'decimals': token_info.get('decimals'),
                'mint_authority': token_info.get('tokenAuthority'),
                'freeze_authority': token_info.get('freezeAuthority'),
                'creator': token_info.get('creator'),
                'website': own_extensions.get('website'),
                'twitter': own_extensions.get('twitter'),
                'description': own_extensions.get('description'),
                'created_tx': token_info.get('created_tx'),
                'first_mint_tx': token_info.get('first_mint_tx'),
            })

            holder_stats = getattr(self.explorer, 'token_holders_total', lambda _addr: None)(address)
            if isinstance(holder_stats, dict):
                info['holder_count'] = holder_stats.get('holders')
                info['supply_raw'] = holder_stats.get('supply')
            elif holder_stats is not None:
                info['holder_count'] = holder_stats

            market_info = self._fetch_solana_market_info(address)
            info.update(market_info)

            return info
        return {}

    def _fetch_solana_market_info(self, address: str) -> Dict[str, Any]:
        """Fetch Solana token market info from GeckoTerminal."""
        import requests

        url = f"https://api.geckoterminal.com/api/v2/networks/solana/tokens/{address}"
        try:
            response = requests.get(
                url,
                timeout=20,
                headers={
                    'User-Agent': 'Mozilla/5.0',
                    'Accept': 'application/json',
                },
            )
            response.raise_for_status()
            payload = response.json().get('data', {}).get('attributes', {})
            volume = payload.get('volume_usd', {}) or {}
            return {
                'name': payload.get('name'),
                'symbol': payload.get('symbol'),
                'decimals': payload.get('decimals'),
                'price_usd': float(payload['price_usd']) if payload.get('price_usd') is not None else None,
                'market_cap_usd': float(payload['market_cap_usd']) if payload.get('market_cap_usd') is not None else None,
                'fdv_usd': float(payload['fdv_usd']) if payload.get('fdv_usd') is not None else None,
                'liquidity_usd': float(payload['total_reserve_in_usd']) if payload.get('total_reserve_in_usd') is not None else None,
                'volume_24h_usd': float(volume['h24']) if volume.get('h24') is not None else None,
                'total_supply': float(payload['normalized_total_supply']) if payload.get('normalized_total_supply') is not None else None,
                'coingecko_coin_id': payload.get('coingecko_coin_id'),
                'image_url': payload.get('image_url'),
                'market_source': 'geckoterminal',
            }
        except Exception as e:
            print(f"[ChainTrace] Solana market fetch failed: {e}")
            return {}
    
    def _fetch_holders(self, address: str) -> list:
        """Fetch holder list"""
        if self.chain in ["eth", "base"]:
            data = self.explorer.token_holders(address)
            if data and 'items' in data:
                return data['items'][:50]  # Top 50
        elif self.chain == "solana":
            data = self.explorer.token_holders(address, page_size=50)
            if data and 'accounts' in data:
                holders = []
                for account in data['accounts'][:50]:
                    ui_amount = account.get('uiAmount')
                    if ui_amount is None:
                        ui_amount = account.get('uiAmountString')
                    if ui_amount is None:
                        amount = account.get('amount')
                        decimals = int(account.get('decimals', 0) or 0)
                        try:
                            ui_amount = float(amount) / (10 ** decimals) if amount is not None else 0.0
                        except Exception:
                            ui_amount = 0.0
                    holders.append({
                        'address': {'hash': account.get('address', '')},
                        'value': float(ui_amount or 0.0),
                        'tx_count': 0,
                        'raw': account,
                    })
                return holders
        return []
    
    def _detect_suspicious(self, holders_data: list) -> Dict:
        """Detect suspicious holders"""
        # Convert to detector format
        holders = []
        for h in holders_data:
            holders.append({
                'address': h.get('address', {}).get('hash', ''),
                'balance': float(h.get('value', 0)),
                'balance_pct': 0.0,  # Calculate if total supply known
                'tx_count': h.get('tx_count', 0),
                'bnb_balance': 0.0  # Would need separate query
            })
        
        detector = SuspiciousDetector()
        suspicious = detector.detect(holders)
        
        return {
            'count': len(suspicious),
            'holders': [
                {
                    'address': s.address,
                    'risk_score': s.risk_score,
                    'flags': [f.type for f in s.flags]
                }
                for s in suspicious
            ]
        }
    
    def _analyze_clusters(self, holders_data: list, token_address: str) -> Dict:
        """Run DBSCAN clustering"""
        # Convert to Holder objects
        holders = []
        for h in holders_data:
            holders.append(Holder(
                address=h.get('address', {}).get('hash', ''),
                balance=float(h.get('value', 0)),
                percentage=0.0,
                tx_count=h.get('tx_count', 0)
            ))
        
        analyzer = HolderAnalyzer(chain=self.chain, rpc_manager=self.rpc_manager)
        results = analyzer.analyze_holder_patterns(holders)
        
        return {
            'cluster_count': len(results.get('clusters', [])),
            'anomaly_count': len(results.get('anomalies', [])),
            'risk_score': results.get('risk_score', 0.0)
        }
    
    def _track_origins(self, holders_data: list, token_address: str) -> Dict:
        """Track holder origins (deep mode)"""
        if self.chain == "solana":
            return {
                'tracked_count': 0,
                'coordinated_distributions': 0,
                'note': 'Origin tracking is currently only implemented for EVM chains.'
            }

        # Convert to Holder objects
        holders = []
        for h in holders_data[:10]:  # Top 10 only for deep mode
            holders.append(Holder(
                address=h.get('address', {}).get('hash', ''),
                balance=float(h.get('value', 0)),
                percentage=0.0,
                tx_count=h.get('tx_count', 0)
            ))

        analyzer = HolderAnalyzer(chain=self.chain, rpc_manager=self.rpc_manager)
        origins = analyzer.batch_analyze_origins(holders, token_address)
        coordinated = analyzer.detect_coordinated_distribution(origins)

        return {
            'tracked_count': len(origins),
            'coordinated_distributions': len(coordinated)
        }
    
    def _calculate_risk(self) -> Dict:
        """Calculate overall risk scores"""
        risk = 0
        confidence = 100
        data_gaps = []

        token_info = self.results.get('token_info') or {}
        holders = self.results.get('holders') or []

        if not token_info:
            confidence -= 25
            data_gaps.append('token_info')

        if not holders:
            confidence -= 35
            data_gaps.append('holders')

        if 'suspicious' in self.results:
            risk += self.results['suspicious']['count'] * 10

        if 'clusters' in self.results:
            risk += self.results['clusters'].get('risk_score', 0) * 0.3

        verdict = 'High Risk' if risk > 50 else 'Medium Risk' if risk > 30 else 'Low Risk'
        if 'holders' in data_gaps:
            verdict = 'Unknown'

        return {
            'risk_score': min(risk, 100),
            'confidence_score': max(confidence, 0),
            'verdict': verdict,
            'data_gaps': data_gaps,
        }


    def generate_report(self) -> str:
        """Generate human-readable report with visualizations"""
        visualizer = Visualizer(width=70)

        # Header
        lines = []
        lines.append("=" * 70)
        lines.append(f"Chain Trace Report - {self.chain.upper()}")
        lines.append("=" * 70)
        lines.append(f"Mode: {self.mode}")
        lines.append(f"Timestamp: {datetime.utcnow().isoformat()}Z")
        lines.append("")

        # Use visualizer for rich output
        visual_report = visualizer.generate_full_report(self.results)
        lines.append(visual_report)

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Chain Trace - Multi-chain forensics analysis"
    )
    parser.add_argument("target", help="Token or wallet address")
    parser.add_argument("--chain", "-c", default="bsc",
                        choices=["eth", "base", "bsc", "solana"],
                        help="Blockchain (default: bsc)")
    parser.add_argument("--mode", "-m", default="standard",
                        choices=["quick", "standard", "deep"],
                        help="Analysis mode (default: standard)")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON instead of report")
    parser.add_argument("--output", "-o", help="Save report to file")

    args = parser.parse_args()

    # Run analysis
    tracer = ChainTrace(chain=args.chain, mode=args.mode)
    
    try:
        results = tracer.analyze(args.target)
        
        # Output
        if args.json:
            output = json.dumps(results, indent=2, default=str)
        else:
            output = tracer.generate_report()
        
        # Save or print
        if args.output:
            Path(args.output).write_text(output)
            print(f"Report saved to {args.output}")
        else:
            print("\n" + output)
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
