import json
import logging
from collections.abc import Awaitable, Callable
from decimal import Decimal
from typing import Any, cast

from tronpy import Tron, keys
from tronpy.keys import PrivateKey

from sun_agent_toolkit.core.classes.wallet_client_base import Balance, Signature
from sun_agent_toolkit.core.types.token import Token

from .abi import TRC20_ABI
from .tokens import TronToken
from .tron_wallet_base import TronWalletBase
from .types import TronReadRequest, TronReadResult, TronTransaction

logger = logging.getLogger(__name__)


class TronWalletClient(TronWalletBase):
    """Concrete implementation of TRON wallet client."""

    def __init__(
        self,
        private_key: str | None = None,
        *,
        public_key: str | None = None,
        network: str = "mainnet",
        tokens: list[TronToken] | None = None,
        enable_send: bool = True,
        send_func: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]] | None = None,
        sign_func: Callable[[bytes], Awaitable[dict[str, Any]]] | None = None,
    ):
        """Initialize the TRON wallet implementation.

        Args:
            private_key: Private key in hex format (without 0x prefix)
            public_key: Base58 TRON address to operate in read-only mode when private key is unavailable
            network: TRON network ("mainnet", "shasta", "nile")
            tokens: List of token configurations
            enable_send: Whether to enable send functionality
        """
        if (private_key is None) == (public_key is None):
            raise ValueError("Exactly one of private_key or public_key must be provided")

        can_sign = private_key is not None or send_func is not None
        effective_enable_send = enable_send and can_sign

        super().__init__(tokens, effective_enable_send)
        if enable_send and not can_sign:
            logger.warning("Disabling send functionality because no private key was provided")

        self.network = network

        # Initialize TRON client; 标注为 Any 以屏蔽库未注解成员访问的告警
        self.tron: Any = Tron(network=network)

        # Setup private key
        self.priv_key: PrivateKey | None = None
        self._address: str | None = None

        if private_key is not None:
            pk_hex = private_key[2:] if private_key.startswith("0x") else private_key
            try:
                self.priv_key = PrivateKey(bytes.fromhex(pk_hex))
            except Exception as e:
                raise ValueError(f"Invalid private key format: {e}") from e

            pk_pub: Any = self.priv_key.public_key
            self._address = pk_pub.to_base58check_address()
        else:
            # public_key 限定为 Base58 地址
            assert public_key is not None
            pub_input = public_key.strip()
            try:
                hex_addr = keys.to_hex_address(pub_input)
                self._address = keys.to_base58check_address(hex_addr)
            except Exception as e:
                raise ValueError("Invalid TRON address provided as public_key") from e
        self.send_func = send_func
        self.sign_func = sign_func

        logger.info(f"Initialized TRON wallet: {self._address} on {network}")

    def get_address(self) -> str:
        """Get the wallet's public address."""
        assert self._address is not None
        return self._address

    def get_network_id(self) -> str:
        """Get the network ID (e.g., 'mainnet', 'shasta', 'nile')."""
        return self.network

    async def sign_message(self, message: str) -> Signature:
        """Sign a message with the wallet's private key."""
        if not self.enable_send:
            raise ValueError("Private key is required to sign messages")
        try:
            message_bytes = message.encode("utf-8")
            if self.priv_key:
                signature = self.priv_key.sign_msg(message_bytes)
                return {"signature": signature.hex()}
            else:
                assert self.sign_func is not None
                res = await self.sign_func(message_bytes)
                success = bool(res.get("success"))
                signature = res.get("signature")
                if success and isinstance(signature, str):
                    return {"signature": signature}
                else:
                    raise RuntimeError(res.get("error", "unknown error"))
        except Exception as e:
            logger.error(f"Message signing failed: {e}")
            raise ValueError(f"Failed to sign message: {str(e)}") from e

    async def sign_typed_data(
        self, types: dict[str, Any], primary_type: str, domain: dict[str, Any], value: dict[str, Any]
    ) -> Signature:
        """Sign typed data with the wallet's private key (TRON equivalent of EIP-712)."""
        if not self.enable_send:
            raise ValueError("Private key is required to sign typed data")
        try:
            structured_message = {"types": types, "primaryType": primary_type, "domain": domain, "message": value}
            message_str = str(structured_message)
            return await self.sign_message(message_str)
        except Exception as e:
            logger.error(f"Typed data signing failed: {e}")
            raise ValueError(f"Failed to sign typed data: {str(e)}") from e

    async def send_transaction(self, transaction: TronTransaction) -> dict[str, str]:
        """Send a transaction on the TRON chain."""
        if not self.enable_send:
            raise ValueError("Private key is required to send transactions")
        try:
            step_any: Any = None
            txn: Any = None
            # Decide fee limit once (SUN); default 500 TRX
            fee_limit_raw: Any = transaction.get("feeLimit", 500_000_000)
            fee_limit_opt = int(fee_limit_raw) if isinstance(fee_limit_raw, int | str) else 500_000_000
            if "functionName" in transaction:
                # Smart contract interaction: load contract and set ABI if provided
                contract: Any = self.tron.get_contract(transaction["to"])  # tronpy 未注解，类型为 Any
                abi_opt = transaction.get("abi")
                if abi_opt is not None:
                    # 显式设置 ABI，支持 ABIEncoderV2 的编码
                    contract.abi = abi_opt

                if transaction["functionName"] == "transfer":
                    # TRC20 transfer
                    args = transaction.get("args", [])
                    recipient, amount = args[0], args[1]
                    step_any = contract.functions.transfer(recipient, amount).with_owner(self._address)
                    step_any = step_any.fee_limit(fee_limit_opt)
                    txn = step_any.build()
                elif transaction["functionName"] == "approve":
                    # TRC20 approve
                    args = transaction.get("args", [])
                    spender, amount = args[0], args[1]
                    step_any = contract.functions.approve(spender, amount).with_owner(self._address)
                    step_any = step_any.fee_limit(fee_limit_opt)
                    txn = step_any.build()
                else:
                    # Generic contract call
                    method: Any = getattr(contract.functions, transaction["functionName"])  # ContractMethod
                    call_args = transaction.get("args", [])
                    value_opt = int(transaction.get("value", 0) or 0)
                    # For payable methods, attach native TRX via with_transfer before invoking
                    if value_opt > 0:
                        method = method.with_transfer(value_opt)
                    step_any = method(*call_args).with_owner(self._address)
                    step_any = step_any.fee_limit(fee_limit_opt)
                    txn = step_any.build()
            else:
                # Native TRX transfer - must build before signing
                value = int(transaction.get("value", 0))
                step_any = self.tron.trx.transfer(self._address, transaction["to"], value)
                step_any = step_any.fee_limit(fee_limit_opt)
                txn = step_any.build()

            if self.send_func is not None:
                res = await self.send_func(txn.to_json())
                status = res.get("success")
                if not status:
                    raise RuntimeError(res.get("error", "unknown error"))
                return {"hash": res.get("txid", "unknown"), "status": status}
            # Sign and broadcast
            signed_txn: Any = txn.sign(self.priv_key)
            result: Any = signed_txn.broadcast()

            # Wait for confirmation
            receipt: Any = result.wait()

            # Extract transaction ID from receipt - support multiple shapes
            tx_id: str | None = None
            if isinstance(receipt, dict):
                rec_dict = cast(dict[str, Any], receipt)
                tx_id = rec_dict.get("txid") or rec_dict.get("transaction_id") or rec_dict.get("id")
            else:
                tx_id = getattr(receipt, "txid", None) or getattr(receipt, "transaction_id", None)

            # Fallback to signed transaction's txid
            if not tx_id and hasattr(signed_txn, "txid"):
                tx_id = signed_txn.txid

            # Final fallback
            if not tx_id:
                tx_id = "unknown"

            logger.info(f"Transaction completed: {tx_id}")

            # Check transaction status from receipt
            status = "success"  # Default assumption
            if isinstance(receipt, dict):
                # Check for failure indicators in receipt
                rec_any: dict[str, Any] = cast(dict[str, Any], receipt)
                if rec_any.get("result") == "FAILED" or rec_any.get("ret", [{}])[0].get("contractRet") == "REVERT":
                    status = "failed"

            return {"hash": tx_id, "status": status}

        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            raise ValueError(f"Failed to send transaction: {str(e)}") from e

    def _apply_transaction_options(self, builder_any: Any, options: dict[str, Any] | None) -> Any:
        """Apply optional transaction builder settings such as fee limit, memo, permission, expiration."""
        if not options:
            return builder_any

        fee_limit_opt = options.get("feeLimit") or options.get("fee_limit")
        if fee_limit_opt is not None:
            builder_any = builder_any.fee_limit(int(fee_limit_opt))

        memo_opt = options.get("memo")
        if memo_opt:
            builder_any = builder_any.memo(memo_opt)

        permission_opt = options.get("permissionId") or options.get("permission_id")
        if permission_opt is not None:
            builder_any = builder_any.permission_id(int(permission_opt))

        expiration_opt = options.get("expiration")
        if expiration_opt is not None:
            builder_any = builder_any.expiration(int(expiration_opt))

        return builder_any

    def _normalize_transaction_payload(self, payload: dict[str, Any] | str) -> dict[str, Any]:
        """Convert tool input into a transaction JSON dictionary."""
        if isinstance(payload, dict):
            return payload

        if not isinstance(payload, str):
            raise TypeError("transaction payload must be dict or JSON string")

        text = payload.strip()
        if not text:
            raise ValueError("transaction payload is empty")

        try:
            return cast(dict[str, Any], json.loads(text))
        except json.JSONDecodeError as exc:
            raise ValueError("transaction payload string must be valid JSON") from exc

    def _hex_address(self) -> str:
        if self._address is None:
            raise ValueError("Wallet address is not initialized")
        return keys.to_hex_address(self._address)

    def get_account_resource_info(self) -> dict[str, Any]:
        res: Any = self.tron.get_account_resource(self._address)
        return cast(dict[str, Any], res)

    def get_pending_reward(self) -> int:
        res = cast(
            dict[str, Any], self.tron.provider.make_request("wallet/getReward", {"address": self._hex_address()})
        )
        reward_any = res.get("reward", 0)
        try:
            return int(reward_any)
        except Exception:
            return 0

    def get_votes(self) -> dict[str, int]:
        acct = cast(dict[str, Any], self.tron.get_account(self._address))

        # 已用票数
        votes_list = cast(list[dict[str, Any]] | None, acct.get("votes")) or []
        used_votes = 0
        for v in votes_list:
            try:
                used_votes += int(v.get("voteCount") or v.get("vote_count") or 0)
            except Exception:
                continue

        # 总票数
        frozen_v2 = cast(list[dict[str, Any]] | None, acct.get("frozenV2")) or []
        total_sun = 0
        for f in frozen_v2:
            try:
                total_sun += int(f.get("amount") or 0)
            except Exception:
                continue
        total_votes = total_sun // 1_000_000

        available = total_votes - used_votes
        if available < 0:
            available = 0

        return {
            "totalVotes": int(total_votes),
            "availableVotes": int(available),
        }

    def read(self, request: TronReadRequest) -> TronReadResult:
        """Read data from a smart contract."""
        try:
            # Validate contract address format
            contract_addr = request["address"]
            if not contract_addr or len(contract_addr) != 34 or not contract_addr.startswith("T"):
                raise ValueError(f"Invalid TRON contract address format: {contract_addr}")

            contract = self.tron.get_contract(contract_addr)

            # Get the function from the contract
            func = getattr(contract.functions, request["functionName"])

            # Call the function with provided arguments
            call_args = request.get("args", [])
            func_result = func(*call_args)
            # Some functions return direct values, others return callable objects
            if hasattr(func_result, "call"):
                result = func_result.call()
            else:
                result = func_result

            return {"value": result}

        except Exception as e:
            logger.error(f"Contract read failed for {request.get('address', 'unknown')}: {e}")
            # Check if it's a specific problematic contract on testnet
            if "bad base58check format" in str(e) and request.get("address") == "TFbqCqAJtoJGNqKxcJrHpj7dPNPyaUwrLn":
                raise ValueError(
                    f"Contract {request['address']} appears to be invalid or non-existent on {self.network} network"
                ) from e
            raise ValueError(f"Failed to read from contract: {str(e)}") from e

    def get_native_balance(self) -> int:
        """Get the native balance of the wallet in SUN."""
        return self.get_native_balance_of(self._address)

    def get_native_balance_of(self, address: str | None) -> int:
        """Get the native balance of given wallet address in SUN."""
        try:
            account = cast(dict[str, Any], self.tron.get_account(address))
            balance_sun = account.get("balance", 0)
            return balance_sun
        except Exception as e:
            logger.error(f"Failed to get native balance: {e}")
            raise ValueError(f"Failed to fetch native balance: {str(e)}") from e

    def balance_of(self, address: str, token_address: str | None = None) -> Balance:
        """Get the balance of an address for native or TRC20 tokens.

        Args:
            address: The address to check balance for
            token_address: Optional TRC20 token address

        Returns:
            Balance information
        """
        if token_address:
            try:
                balance_result = self.read(
                    {
                        "address": token_address,
                        "abi": TRC20_ABI,
                        "functionName": "balanceOf",
                        "args": [address],
                    }
                )
                balance_in_base_units = str(balance_result["value"])

                token_info = self.get_token_info_by_address(token_address)

                # Use proper decimal arithmetic to avoid precision loss
                divisor = Decimal(10) ** token_info["decimals"]
                balance_value = str(Decimal(balance_in_base_units) / divisor)

                return {
                    "decimals": token_info["decimals"],
                    "symbol": token_info["symbol"],
                    "name": token_info["name"],
                    "value": balance_value,
                    "in_base_units": balance_in_base_units,
                }
            except Exception as e:
                raise ValueError(f"Failed to fetch token balance: {str(e)}") from e
        else:
            try:
                balance_in_sun = self.get_native_balance_of(address)
                decimals = 6
                balance_value = str(Decimal(balance_in_sun) / (10**decimals))

                return {
                    "decimals": decimals,
                    "symbol": "TRX",
                    "name": "TRON",
                    "value": balance_value,
                    "in_base_units": str(balance_in_sun),
                }
            except Exception as e:
                raise ValueError(f"Failed to fetch native balance: {str(e)}") from e

    def get_token_info_by_address(self, address: str | None) -> Token:
        """Get token information by token address.

        Args:
            address: The token base58 address, None for native token

        Returns:
            Token information
        """
        chain = self.get_chain()
        network = cast(str, chain["network"])

        if address is None or address == "T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb":
            return {
                "symbol": "TRX",
                "decimals": 6,
                "name": "TRON",
                "address": "T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb",
            }

        for token in self.tokens:
            if network not in token["networks"] or token["networks"][network]["contractAddress"] != address:
                continue
            return {
                "symbol": token["symbol"],
                "decimals": token["decimals"],
                "name": token["name"],
                "address": address,
            }

        try:
            decimals_result = self.read({"address": address, "abi": TRC20_ABI, "functionName": "decimals", "args": []})
            name_result = self.read({"address": address, "abi": TRC20_ABI, "functionName": "name", "args": []})
            symbol_result = self.read({"address": address, "abi": TRC20_ABI, "functionName": "symbol", "args": []})
            return {
                "symbol": str(symbol_result["value"]),
                "decimals": int(decimals_result["value"]),
                "name": str(name_result["value"]),
                "address": address,
            }
        except Exception as e:
            logger.error(f"Failed to get token info {e}")
            raise ValueError(f"Token with address {address} not found") from e

    def get_token_info_by_ticker(self, ticker: str) -> Token:
        """Get token information by ticker symbol.

        Args:
            ticker: The token ticker symbol (e.g., USDT, USDC)

        Returns:
            Token information
        """
        chain = self.get_chain()
        network = cast(str, chain["network"])
        upper_ticker = ticker.upper()

        if upper_ticker == "TRX":
            return {
                "symbol": "TRX",
                "decimals": 6,
                "name": "TRON",
                "address": "T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb",
            }

        for token in self.tokens:
            if token["symbol"].upper() == upper_ticker:
                if network in token["networks"]:
                    return {
                        "symbol": token["symbol"],
                        "decimals": token["decimals"],
                        "name": token["name"],
                        "address": token["networks"][network]["contractAddress"],
                    }

        # TODO: deal with sunio & sunpump token

        raise ValueError(f"Token with ticker {ticker} not found for network {network}")

    # ----- Stake 2.0 & Governance implementations -----

    async def _finalize_transaction(self, builder_any: Any) -> dict[str, str]:
        """Helper to build, sign, broadcast and wait a transaction, returning a uniform receipt dict."""
        try:
            txn: Any = builder_any.build()
            if self.send_func is not None:
                res = await self.send_func(txn.to_json())
                status = res.get("success")
                if not status:
                    raise RuntimeError(res.get("error", "unknown error"))
                return {"hash": res.get("txid", "unknown"), "status": status}
            signed_txn: Any = txn.sign(self.priv_key)
            result: Any = signed_txn.broadcast()
            receipt: Any = result.wait()

            tx_id: str | None = None
            if isinstance(receipt, dict):
                rec_dict = cast(dict[str, Any], receipt)
                tx_id = rec_dict.get("txid") or rec_dict.get("transaction_id") or rec_dict.get("id")
            else:
                tx_id = getattr(receipt, "txid", None) or getattr(receipt, "transaction_id", None)
            if not tx_id and hasattr(signed_txn, "txid"):
                tx_id = signed_txn.txid
            if not tx_id:
                tx_id = "unknown"

            status = "success"
            if isinstance(receipt, dict):
                rec_any: dict[str, Any] = cast(dict[str, Any], receipt)
                if rec_any.get("result") == "FAILED" or rec_any.get("ret", [{}])[0].get("contractRet") == "REVERT":
                    status = "failed"
            logger.info(f"Transaction completed: {tx_id}")
            return {"hash": tx_id, "status": status}
        except Exception as e:
            logger.error(f"Finalizing transaction failed: {e}")
            raise

    async def freeze_balance(self, params: dict[str, Any]) -> dict[str, str]:
        """Freeze TRX to obtain ENERGY or BANDWIDTH (Stake 2.0)."""
        try:
            amount = int(params["amountInSun"])
            resource = params["resource"]
            builder_any: Any = self.tron.trx.freeze_balance(self._address, amount, resource)
            builder_any = builder_any.with_owner(self._address)
            return await self._finalize_transaction(builder_any)
        except Exception as e:
            logger.error(f"freeze_balance failed: {e}")
            raise ValueError(f"Failed to freeze balance: {str(e)}") from e

    async def unfreeze_balance(self, params: dict[str, Any]) -> dict[str, str]:
        """Unstake TRX (Stake 2.0)."""
        try:
            resource = params["resource"]
            amount_opt = int(params.get("amountInSun", "0"))
            if amount_opt == 0:
                raise RuntimeError("Can't unfreeze balance amount 0")
            builder_any = self.tron.trx.unfreeze_balance(
                owner=self._address, resource=resource, unfreeze_balance=amount_opt
            )
            builder_any = builder_any.with_owner(self._address)
            return await self._finalize_transaction(builder_any)
        except Exception as e:
            logger.error(f"unfreeze_balance failed: {e}")
            raise ValueError(f"Failed to unfreeze balance: {str(e)}") from e

    async def withdraw_stake_balance(self, params: dict[str, Any]) -> dict[str, str]:
        """Withdraw expired unstaked TRX after cool-down period (Stake 2.0)."""
        del params  # unused
        try:
            # TronPy API: withdraw_stake_balance(owner)
            builder_any: Any = self.tron.trx.withdraw_stake_balance(self._address)
            builder_any = builder_any.with_owner(self._address)
            return await self._finalize_transaction(builder_any)
        except Exception as e:
            logger.error(f"withdraw_stake_balance failed: {e}")
            raise ValueError(f"Failed to withdraw expired unstake: {str(e)}") from e

    async def delegate_resource(self, params: dict[str, Any]) -> dict[str, str]:
        """Delegate ENERGY/BANDWIDTH to another address (Stake 2.0)."""
        try:
            receiver = params["receiver"]
            amount = int(params["amountInSun"])
            resource = params["resource"]
            lock = params["lock"]
            lock_period = params.get("lock_period")
            builder_any: Any = self.tron.trx.delegate_resource(
                self._address, receiver, amount, resource, lock=lock, lock_period=lock_period
            )
            builder_any = builder_any.with_owner(self._address)
            return await self._finalize_transaction(builder_any)
        except Exception as e:
            logger.error(f"delegate_resource failed: {e}")
            raise ValueError(f"Failed to delegate resource: {str(e)}") from e

    async def undelegate_resource(self, params: dict[str, Any]) -> dict[str, str]:
        """Cancel delegation of ENERGY/BANDWIDTH (Stake 2.0)."""
        try:
            receiver = params["receiver"]
            amount = int(params["amountInSun"])
            resource = params["resource"]
            builder_any: Any = self.tron.trx.undelegate_resource(self._address, receiver, amount, resource)
            builder_any = builder_any.with_owner(self._address)
            return await self._finalize_transaction(builder_any)
        except Exception as e:
            logger.error(f"undelegate_resource failed: {e}")
            raise ValueError(f"Failed to undelegate resource: {str(e)}") from e

    async def vote_witness(self, params: dict[str, Any]) -> dict[str, str]:
        """Vote for witnesses (governance)."""
        try:
            votes_param = params["votes"]
            # Expect list of {witnessAddress, voteCount}
            votes_list: list[tuple[str, int]] = []
            for v in votes_param:
                addr = cast(str, v.get("witnessAddress"))
                count = int(cast(int, v.get("voteCount")))
                votes_list.append((addr, count))
            builder_any: Any = self.tron.trx.vote_witness(self._address, *votes_list)
            builder_any = builder_any.with_owner(self._address)
            return await self._finalize_transaction(builder_any)
        except Exception as e:
            logger.error(f"vote_witness failed: {e}")
            raise ValueError(f"Failed to vote witnesses: {str(e)}") from e

    async def withdraw_rewards(self, params: dict[str, Any]) -> dict[str, str]:
        """Withdraw voting rewards."""
        del params  # unused
        try:
            builder_any: Any = self.tron.trx.withdraw_rewards(self._address)
            builder_any = builder_any.with_owner(self._address)
            return await self._finalize_transaction(builder_any)
        except Exception as e:
            logger.error(f"withdraw_rewards failed: {e}")
            raise ValueError(f"Failed to withdraw rewards: {str(e)}") from e
