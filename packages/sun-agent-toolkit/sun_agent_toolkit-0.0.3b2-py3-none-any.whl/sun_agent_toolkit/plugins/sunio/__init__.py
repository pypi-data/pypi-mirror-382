from __future__ import annotations

import os
from dataclasses import dataclass

from sun_agent_toolkit.core.classes.plugin_base import PluginBase
from sun_agent_toolkit.core.classes.wallet_client_base import WalletClientBase
from sun_agent_toolkit.core.types.chain import Chain

from .service import SunIOService


@dataclass
class SunIOPluginOptions:
    """Options for the SunIOPlugin."""

    api_key: str | None  # API key for external service integration
    base_url: str  # Base URL for SunIO API

    @staticmethod
    def from_env() -> SunIOPluginOptions:
        """从环境变量创建 Azure OpenAI 配置"""
        base_url = os.getenv("SUNIO_OPENAPI_BASE_URL")
        if base_url is None:
            raise ValueError("环境变量 'SUNIO_OPENAPI_BASE_URL' 未设置")
        return SunIOPluginOptions(api_key=os.getenv("SUNIO_OPENAPI_KEY"), base_url=base_url)


class SunIOPlugin(PluginBase[WalletClientBase]):
    """SunIO plugin for token swaps on supported EVM chains."""

    def __init__(self, options: SunIOPluginOptions):
        super().__init__("sunio", [SunIOService(options.api_key, options.base_url)])

    def supports_chain(self, chain: Chain) -> bool:
        """Check if the chain is supported by SunIO."""

        chain_type = chain.get("type")
        if chain_type == "tron":
            return True
        chain_id = chain.get("id")
        return isinstance(chain_id, str) and chain_id.startswith("tron")


def sunio(options: SunIOPluginOptions) -> SunIOPlugin:
    """Create a new instance of the SunIO plugin.

    Args:
        options: Configuration options for the plugin

    Returns:
        A configured SunIOPlugin instance
    """
    return SunIOPlugin(options)
