import json
import logging
import urllib.parse
import urllib.request
from decimal import Decimal
from itertools import groupby
from typing import Any, cast

from sun_agent_toolkit.core.decorators.tool import Tool
from sun_agent_toolkit.wallets.tron.abi import SUNSWAP_SMART_ROUTER_ABI
from sun_agent_toolkit.wallets.tron.tron_wallet_base import TronWalletBase
from sun_agent_toolkit.wallets.tron.types import TronTransaction

from .parameters import (
    RouterParameters,
    SwapTokensParameters,
)


class _CalcServiceClient:
    def __init__(self, base_url: str | None = None) -> None:
        if not base_url:
            raise ValueError("SunSwap CalculationService base_url is required")
        self.base_url = base_url.rstrip("/")

    def _get_json(self, params: dict[str, Any]) -> dict[str, Any]:
        query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        url = f"{self.base_url}?{query}" if query else self.base_url
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
            },
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8")
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError as e:
                raise ValueError(f"CalculationService invalid JSON: {body}") from e
            if resp.status < 200 or resp.status >= 300:
                if isinstance(parsed, dict):
                    err = cast(dict[str, Any], parsed).get("errorCode")
                else:
                    err = parsed
                raise ValueError(f"CalculationService error {resp.status}: {err}")
            if not isinstance(parsed, dict):
                raise ValueError("Unexpected CalculationService response format (expected object)")
            return cast(dict[str, Any], parsed)

    def get_router(self, *, fromToken: str, toToken: str, amountIn: str) -> dict[str, Any]:
        params: dict[str, Any] = {
            "fromToken": fromToken,
            "toToken": toToken,
            "amountIn": amountIn,
        }
        return self._get_json(params)


def select_best_route(route_result: dict[str, Any]) -> dict[str, Any]:
    code = route_result.get("code")
    if code != 0:
        raise RuntimeError(f"get_route failed: {route_result.get('message')}")
    routes = cast(list[dict[str, Any]] | None, route_result.get("data")) or []
    if not routes:
        raise RuntimeError("no routes returned")

    # 直接返回第一个路由
    best: dict[str, Any] = routes[0]
    return best


class SunSwapService:
    def __init__(self) -> None:
        pass

    def _resolve_client(self, wallet_client: TronWalletBase) -> _CalcServiceClient:
        # 根据钱包网络选择固定网关
        network = wallet_client.get_network_id()
        # 固定映射：mainnet/nile 有网关，shasta 不支持
        if network == "mainnet":
            url = "https://rot.endjgfsv.link/swap/router"
        elif network == "nile":
            url = "https://tnrouter.endjgfsv.link/swap/router"
        else:
            raise ValueError(f"不支持的网络: {network}")

        return _CalcServiceClient(url)

    @Tool(
        {
            "description": "获取智能路由报价",
            "parameters_schema": RouterParameters,
        }
    )
    def get_route(self, params: dict[str, Any], wallet_client: TronWalletBase) -> dict[str, Any]:
        from_token = cast(str, params["fromToken"])
        to_token = cast(str, params["toToken"])
        # 入参 amountIn 为 human，这里统一转换为 base（sun）；原生判断已在钱包实现
        amount_in_human = cast(str, params["amountIn"])
        amount_in_base = wallet_client.convert_to_base_units(
            {
                "amount": amount_in_human,
                "tokenAddress": from_token,
            }
        )
        client = self._resolve_client(wallet_client)
        result = client.get_router(fromToken=from_token, toToken=to_token, amountIn=amount_in_base)
        return result

    @Tool(
        {
            "description": "执行代币交换",
            "parameters_schema": SwapTokensParameters,
        }
    )
    async def swap_tokens(self, params: dict[str, Any], wallet_client: TronWalletBase) -> dict[str, Any]:
        from_token = cast(str, params["fromToken"])
        to_token = cast(str, params["toToken"])
        amount_in_human = cast(str, params["amountIn"])
        slippage_tolerance = cast(float, params.get("slippageTolerance", 0.005))  # 默认 0.5%

        # 1. 获取路由信息
        route_result = self.get_route(
            {
                "fromToken": from_token,
                "toToken": to_token,
                "amountIn": amount_in_human,
            },
            wallet_client,
        )

        best_route = select_best_route(route_result)
        # 调试：打印最佳路由
        logging.debug("[SunSwapService] best_route: %s", best_route)

        # 4. 获取智能路由合约地址
        network = wallet_client.get_network_id()
        if network == "mainnet":
            router_address = "TCFNp179Lg46D16zKoumd4Poa2WFFdtqYj"
        elif network == "nile":
            # 官网文档 https://docs.sun.io/DEVELOPERS/Swap/SmartRouter/Contract
            # router_address = "TDAQGC5Ekd683GjekSaLzCaeg7jGsGSmbh"
            router_address = "TB6xBCixqRPUSKiXb45ky1GhChFJ7qrfFj"
        else:
            raise ValueError(f"不支持的网络: {network}")

        # 5. 准备交易参数
        user_address = wallet_client.get_address()

        # 6. 将 best_route 转为合约调用参数（path/pool_version/version_len/fees/swap_data）
        contract_args = self._build_swap_contract_args(
            best_route=best_route,
            to_address=user_address,
            wallet_client=wallet_client,
            slippage_tolerance=slippage_tolerance,
        )

        from_token_symbol = best_route["symbols"][0]
        # 8. 检查并处理代币授权
        if from_token_symbol.lower() != "trx":  # TRX 不需要授权
            await self._ensure_token_approval(wallet_client, from_token, router_address, amount_in_human)

        # 9. 发送交易
        try:
            tx_payload: dict[str, Any] = {
                "to": router_address,
                "abi": SUNSWAP_SMART_ROUTER_ABI,
                "functionName": "swapExactInput",
                "args": contract_args,
                "feeLimit": 1000_000_000,  # 1000 TRX
            }
            # 如果路径起点是 TRX，需附带原生 value，与 amountIn 保持一致
            if from_token_symbol.lower() == "trx":
                # 使用基于 best_route 计算得到的 amountIn（swap_data 第 1 位）
                tx_payload["value"] = int(contract_args[4][0])

            tx_result = await wallet_client.send_transaction(cast(TronTransaction, tx_payload))

            # 兼容多种返回形态的 tx 哈希与状态
            tx_hash = (
                tx_result.get("hash") or tx_result.get("txid") or tx_result.get("transaction_id") or tx_result.get("id")
            )
            status = tx_result.get("status", "unknown")

            return {
                "success": status == "success",
                "txHash": tx_hash,
                "status": status,
                "amountIn": str(contract_args[4][0]),
                "amountOutExpected": str(best_route.get("amountOut")),
                "amountOutMinBase": str(contract_args[4][1]),
                "route": best_route,
                "rawReceipt": tx_result,
            }

        except Exception as e:
            raise ValueError(f"交易执行失败: {str(e)}") from e

    async def _ensure_token_approval(
        self, wallet_client: TronWalletBase, token_address: str, spender: str, amount: str
    ) -> None:
        user_address = wallet_client.get_address()
        current_allowance = wallet_client.get_token_allowance(
            {"tokenAddress": token_address, "owner": user_address, "spender": spender}
        )

        # 将 human 数量转换为 base（sun）后再比较
        amount_base = wallet_client.convert_to_base_units(
            {
                "amount": amount,
                "tokenAddress": token_address,
            }
        )

        # 如果授权不足，进行授权
        if int(current_allowance) < int(amount_base):
            # 授权一个较大的数量以减少频繁授权
            max_uint256 = "115792089237316195423570985008687907853269984665640564039457584007913129639935"
            await wallet_client.approve({"tokenAddress": token_address, "spender": spender, "amount": max_uint256})

    def _get_current_timestamp(self) -> int:
        """获取当前时间戳。"""
        import time

        return int(time.time())

    def _build_swap_contract_args(
        self,
        *,
        best_route: dict[str, Any],
        to_address: str,
        wallet_client: TronWalletBase,
        slippage_tolerance: float,
    ) -> list[Any]:
        path = cast(list[str], best_route["tokens"])
        pool_version = cast(list[str], best_route["poolVersions"])

        runs = [len(list(g)) for _, g in groupby(pool_version)]
        version_len: list[int] = [runs[0] + 1] + runs[1:] if runs else [len(path)]

        # 规范化 fees 为整型列表，并确保最后一个为 0
        fees_raw = cast(list[Any], best_route["poolFees"])
        fees: list[int] = [int(f) if f != "" else 0 for f in fees_raw]
        if fees:
            fees[-1] = 0

        amount_in_human = str(best_route["amountIn"])  # human-readable
        amount_out_human = str(best_route["amountOut"])  # human-readable

        # 若路径标注了 symbols，可用来识别是否为原生 TRX
        symbols = cast(list[str] | None, best_route.get("symbols"))

        def _to_base_units(amount_human: str, token_addr: str, symbol: str | None) -> str:
            if symbol and symbol.upper() == "TRX":
                # 原生 TRX 固定 6 位
                return str(int(Decimal(amount_human) * Decimal(1_000_000)))
            return wallet_client.convert_to_base_units(
                {
                    "amount": amount_human,
                    "tokenAddress": token_addr,
                }
            )

        amount_in_base = _to_base_units(amount_in_human, path[0], symbols[0] if symbols else None)
        min_out_human = str(Decimal(amount_out_human) * Decimal(1 - slippage_tolerance))
        amount_out_min_base = _to_base_units(min_out_human, path[-1], symbols[-1] if symbols else None)

        # 统一设置 deadline 为当前时间 + 30 分钟
        deadline = int(self._get_current_timestamp()) + 1800

        swap_data = [
            int(amount_in_base),
            int(amount_out_min_base),
            to_address,
            int(deadline),
        ]

        return [path, pool_version, version_len, fees, swap_data]
