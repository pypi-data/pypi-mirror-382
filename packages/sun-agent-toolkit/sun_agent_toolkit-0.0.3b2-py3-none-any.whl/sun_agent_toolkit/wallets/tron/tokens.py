from typing import TypedDict, cast

from sun_agent_toolkit.core.types.token import Token as CoreToken


class TronTokenChainInfo(TypedDict):
    """TRON token information for specific network"""

    contractAddress: str


class TronToken(CoreToken):
    """TRON token with network-specific contract addresses"""

    networks: dict[str, TronTokenChainInfo]  # network -> token info


# TRON mainnet tokens
USDT_TRC20: TronToken = cast(
    TronToken,
    {
        "name": "Tether USD",
        "symbol": "USDT",
        "decimals": 6,
        "networks": {
            "mainnet": {"contractAddress": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"},
            "shasta": {"contractAddress": "TG3XXyExBkPp9nzdajDZsozEu4BkaSJozs"},  # Testnet USDT
            "nile": {"contractAddress": "TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj"},  # Nile testnet USDT
        },
    },
)

USDC_TRC20: TronToken = cast(
    TronToken,
    {
        "name": "USD Coin",
        "symbol": "USDC",
        "decimals": 6,
        "networks": {
            "mainnet": {"contractAddress": "TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8"},
            # "shasta": {"contractAddress": "TFbqCqAJtoJGNqKxcJrHpj7dPNPyaUwrLn"},  # Disabled: invalid contract
            "nile": {"contractAddress": "TUpMhErZL2fhh4sVNULAbNKLokS4GjC1F4"},  # Nile testnet USDC
        },
    },
)

BTT_TRC20: TronToken = cast(
    TronToken,
    {
        "name": "BitTorrent Token",
        "symbol": "BTT",
        "decimals": 18,
        "networks": {
            "mainnet": {"contractAddress": "TAFjULxiVgT4qWk6UZwjqwZXTSaGaqnVp4"},
        },
    },
)

JST_TRC20: TronToken = cast(
    TronToken,
    {
        "name": "JUST",
        "symbol": "JST",
        "decimals": 18,
        "networks": {
            "mainnet": {"contractAddress": "TCFLL5dx5ZJdKnWuesXxi1VPwjLVmWZZy9"},
        },
    },
)

SUN_TRC20: TronToken = cast(
    TronToken,
    {
        "name": "SUN Token",
        "symbol": "SUN",
        "decimals": 18,
        "networks": {
            "mainnet": {"contractAddress": "TSSMHYeV2uE9qYH95DqyoCuNCzEL1NvU3S"},
        },
    },
)

WIN_TRC20: TronToken = cast(
    TronToken,
    {
        "name": "WINkLink",
        "symbol": "WIN",
        "decimals": 6,
        "networks": {
            "mainnet": {"contractAddress": "TLa2f6VPqDgRE67v1736s7bJ8Ray5wYjU7"},
        },
    },
)

# Predefined tokens list
PREDEFINED_TOKENS: list[TronToken] = [
    USDT_TRC20,
    USDC_TRC20,
    BTT_TRC20,
    JST_TRC20,
    SUN_TRC20,
    WIN_TRC20,
]


def get_token_by_symbol(symbol: str, network: str = "mainnet") -> TronToken | None:
    """Get token by symbol for specific network"""
    for token in PREDEFINED_TOKENS:
        if token["symbol"] == symbol and network in token["networks"]:
            return token
    return None


def get_token_by_address(address: str, network: str = "mainnet") -> TronToken | None:
    """Get token by contract address for specific network"""
    for token in PREDEFINED_TOKENS:
        if network in token["networks"] and token["networks"][network]["contractAddress"] == address:
            return token
    return None
