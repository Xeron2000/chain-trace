#!/usr/bin/env python3
"""
Solscan Client - 优先使用逆向的 $200/月 API，降级到公共 RPC

基于 https://github.com/paoloanzn/free-solscan-api 逆向工程
"""

import json
import time
from typing import Optional, Dict, Any, List

try:
    import free_solscan_api
    SOLSCAN_AVAILABLE = True
except ImportError:
    SOLSCAN_AVAILABLE = False

# Fallback: 公共 RPC 池
SOLANA_RPCS = [
    "https://api.mainnet-beta.solana.com",
    "https://api.mainnet.solana.com",
    "https://solana-rpc.publicnode.com",
    "https://solana.drpc.org",
]


class SolscanClient:
    """Solana 数据客户端，优先 Solscan 逆向 API，降级公共 RPC"""

    def __init__(self, prefer_solscan: bool = True):
        self.prefer_solscan = prefer_solscan and SOLSCAN_AVAILABLE
        self._router = None
        self._rpc_index = 0
        self._rpc_fails: Dict[str, int] = {}

        if self.prefer_solscan:
            self._router = free_solscan_api.Router(free_solscan_api.solscan_endpoints)

    @property
    def source(self) -> str:
        return "solscan_reversed" if self.prefer_solscan else "public_rpc"

    # ========== Solscan API 方法 ==========

    def transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """获取交易详情"""
        if self.prefer_solscan:
            try:
                return self._router.transaction(tx_hash)
            except Exception as e:
                print(f"[Solscan] transaction failed: {e}, falling back to RPC")
        return self._rpc_get_transaction(tx_hash)

    def transactions(self, address: str, page: int = 1, page_size: int = 40) -> Optional[Dict[str, Any]]:
        """获取地址交易列表"""
        if self.prefer_solscan:
            try:
                return self._router.transactions(address, page=page, page_size=page_size)
            except Exception as e:
                print(f"[Solscan] transactions failed: {e}, falling back to RPC")
        return self._rpc_get_signatures(address, limit=page_size)

    def account_info(self, address: str) -> Optional[Dict[str, Any]]:
        """获取账户信息"""
        if self.prefer_solscan:
            try:
                return self._router.account_info(address)
            except Exception as e:
                print(f"[Solscan] account_info failed: {e}, falling back to RPC")
        return self._rpc_get_account_info(address)

    def token_holders(self, mint: str, page: int = 1, page_size: int = 100) -> Optional[Dict[str, Any]]:
        """获取代币持有者列表"""
        if self.prefer_solscan:
            try:
                return self._router.token_holders(mint, page=page, page_size=page_size)
            except Exception as e:
                print(f"[Solscan] token_holders failed: {e}")
        return None  # 公共 RPC 无此功能

    def token_holders_total(self, mint: str) -> Optional[int]:
        """获取代币持有者总数"""
        if self.prefer_solscan:
            try:
                return self._router.token_holders_total(mint)
            except Exception as e:
                print(f"[Solscan] token_holders_total failed: {e}")
        return None

    def transfers(self, address: str, page: int = 1, page_size: int = 100,
                  remove_spam: bool = True, exclude_amount_zero: bool = True) -> Optional[Dict[str, Any]]:
        """获取转账记录"""
        if self.prefer_solscan:
            try:
                return self._router.transfers(
                    address,
                    remove_spam=remove_spam,
                    exclude_amount_zero=exclude_amount_zero,
                    page=page,
                    page_size=page_size
                )
            except Exception as e:
                print(f"[Solscan] transfers failed: {e}")
        return None

    def defi_activities(self, address: str, page: int = 1, page_size: int = 100) -> Optional[Dict[str, Any]]:
        """获取 DeFi 活动"""
        if self.prefer_solscan:
            try:
                return self._router.defi_activities(address, page=page, page_size=page_size)
            except Exception as e:
                print(f"[Solscan] defi_activities failed: {e}")
        return None

    def portfolio(self, address: str, token_type: str = "token",
                  page: int = 1, page_size: int = 100, hide_zero: bool = True) -> Optional[Dict[str, Any]]:
        """获取钱包投资组合"""
        if self.prefer_solscan:
            try:
                return self._router.portfolio(
                    address,
                    type=token_type,
                    page=page,
                    page_size=page_size,
                    hide_zero=hide_zero
                )
            except Exception as e:
                print(f"[Solscan] portfolio failed: {e}")
        return None

    def balance_history(self, address: str) -> Optional[Dict[str, Any]]:
        """获取余额历史"""
        if self.prefer_solscan:
            try:
                return self._router.balance_history(address)
            except Exception as e:
                print(f"[Solscan] balance_history failed: {e}")
        return None

    def top_address_transfers(self, address: str, range_days: int = 7) -> Optional[Dict[str, Any]]:
        """获取地址的 Top 转账"""
        if self.prefer_solscan:
            try:
                return self._router.top_address_transfers(address, range_days=range_days)
            except Exception as e:
                print(f"[Solscan] top_address_transfers failed: {e}")
        return None

    def token_data(self, mint: str = "So11111111111111111111111111111111111111112") -> Optional[Dict[str, Any]]:
        """获取代币数据"""
        if self.prefer_solscan:
            try:
                return self._router.token_data(token_address=mint)
            except Exception as e:
                print(f"[Solscan] token_data failed: {e}")
        return self._rpc_get_token_supply(mint)

    # ========== 公共 RPC Fallback ==========

    def _get_rpc(self) -> str:
        """轮换获取可用 RPC"""
        for _ in range(len(SOLANA_RPCS)):
            rpc = SOLANA_RPCS[self._rpc_index]
            if self._rpc_fails.get(rpc, 0) < 3:
                return rpc
            self._rpc_index = (self._rpc_index + 1) % len(SOLANA_RPCS)
        # 全部失败，重置
        self._rpc_fails.clear()
        return SOLANA_RPCS[0]

    def _rpc_call(self, method: str, params: list) -> Optional[Dict[str, Any]]:
        """执行 RPC 调用"""
        import urllib.request

        rpc = self._get_rpc()
        payload = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }).encode()

        for attempt in range(3):
            try:
                req = urllib.request.Request(
                    rpc,
                    data=payload,
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=12) as resp:
                    result = json.loads(resp.read().decode())
                    if "result" in result:
                        self._rpc_fails[rpc] = 0
                        return result["result"]
                    if "error" in result:
                        print(f"[RPC] {method} error: {result['error']}")
                        return None
            except Exception as e:
                self._rpc_fails[rpc] = self._rpc_fails.get(rpc, 0) + 1
                if attempt < 2:
                    time.sleep(1 << attempt)
                    self._rpc_index = (self._rpc_index + 1) % len(SOLANA_RPCS)
                    rpc = self._get_rpc()
        return None

    def _rpc_get_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        return self._rpc_call("getTransaction", [tx_hash, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}])

    def _rpc_get_signatures(self, address: str, limit: int = 50) -> Optional[Dict[str, Any]]:
        sigs = self._rpc_call("getSignaturesForAddress", [address, {"limit": limit}])
        return {"signatures": sigs} if sigs else None

    def _rpc_get_account_info(self, address: str) -> Optional[Dict[str, Any]]:
        return self._rpc_call("getAccountInfo", [address, {"encoding": "jsonParsed"}])

    def _rpc_get_token_supply(self, mint: str) -> Optional[Dict[str, Any]]:
        supply = self._rpc_call("getTokenSupply", [mint])
        return {"supply": supply} if supply else None


# ========== CLI 测试 ==========

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Solscan Client - 测试逆向 API")
    parser.add_argument("--address", "-a", help="Solana 地址")
    parser.add_argument("--tx", "-t", help="交易哈希")
    parser.add_argument("--mint", "-m", help="代币 Mint 地址")
    parser.add_argument("--method", default="account_info",
                        choices=["account_info", "transactions", "transaction", "token_holders",
                                 "transfers", "defi_activities", "portfolio", "token_data"])
    parser.add_argument("--no-solscan", action="store_true", help="禁用 Solscan，仅用公共 RPC")
    args = parser.parse_args()

    client = SolscanClient(prefer_solscan=not args.no_solscan)
    print(f"[Source] {client.source}")
    print(f"[Solscan Available] {SOLSCAN_AVAILABLE}")

    result = None

    if args.method == "account_info" and args.address:
        result = client.account_info(args.address)
    elif args.method == "transactions" and args.address:
        result = client.transactions(args.address)
    elif args.method == "transaction" and args.tx:
        result = client.transaction(args.tx)
    elif args.method == "token_holders" and args.mint:
        result = client.token_holders(args.mint)
    elif args.method == "transfers" and args.address:
        result = client.transfers(args.address)
    elif args.method == "defi_activities" and args.address:
        result = client.defi_activities(args.address)
    elif args.method == "portfolio" and args.address:
        result = client.portfolio(args.address)
    elif args.method == "token_data" and args.mint:
        result = client.token_data(args.mint)
    else:
        print("请提供必要参数，例如：")
        print("  --address <地址> --method account_info")
        print("  --tx <交易哈希> --method transaction")
        print("  --mint <代币地址> --method token_holders")

    if result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
