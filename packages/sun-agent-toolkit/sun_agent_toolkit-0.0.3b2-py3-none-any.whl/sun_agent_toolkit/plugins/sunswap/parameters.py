from pydantic import BaseModel, Field


class SwapTokensParameters(BaseModel):
    fromToken: str = Field(description="Input token address (Base58)")
    toToken: str = Field(description="Output token address (Base58)")
    amountIn: str = Field(description="Exact input amount in base units (sun)")
    slippageTolerance: float | None = Field(default=0.005, description="Slippage tolerance (default 0.5%)")


class RouterParameters(BaseModel):
    fromToken: str = Field(description="fromToken address (Base58)")
    toToken: str = Field(description="toToken address (Base58)")
    amountIn: str = Field(description="Exact input amount in base units (sun)")
