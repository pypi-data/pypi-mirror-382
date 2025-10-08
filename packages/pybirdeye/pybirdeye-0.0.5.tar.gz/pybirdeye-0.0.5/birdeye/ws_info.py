from dataclasses import asdict, dataclass, field
import json
from typing import Any, Literal, Optional, TypedDict
from birdeye.consts import Chain


def ws_params(api_key: str, chain: Chain) -> dict[str, str]:
    return {
        "uri": f"wss://public-api.birdeye.so/socket/{chain}?x-api-key={api_key}",
        "origin": "ws://public-api.birdeye.so",
        "subprotocols": ["echo-protocol"]
    }


# ============================================================
# Types
# ============================================================

QueryType = Literal["simple", "complex"]

# 1s, 15s, 30s only for Solana
IntervalType = Literal["1s", "15s", "30s",
                       "1m", "3m", "5m", "15m", "30m",
                       "1H", "2H", "4H", "6H", "8H", "12H",
                       "1D", "3D", "1W", "1M"]

# Subscribe/Unsubscribe Types
SUBSCRIBE_PRICE = "SUBSCRIBE_PRICE"
SUBSCRIBE_BASE_QUOTE_PRICE = "SUBSCRIBE_BASE_QUOTE_PRICE"
SUBSCRIBE_TXS = "SUBSCRIBE_TXS"
SUBSCRIBE_TOKEN_NEW_LISTING = "SUBSCRIBE_TOKEN_NEW_LISTING"
SUBSCRIBE_NEW_PAIR = "SUBSCRIBE_NEW_PAIR"
SUBSCRIBE_LARGE_TRADE_TXS = "SUBSCRIBE_LARGE_TRADE_TXS"
SUBSCRIBE_WALLET_TXS = "SUBSCRIBE_WALLET_TXS"
SUBSCRIBE_TOKEN_STATS = "SUBSCRIBE_TOKEN_STATS"
UNSUBSCRIBE_PRICE = "UNSUBSCRIBE_PRICE"
UNSUBSCRIBE_BASE_QUOTE_PRICE = "UNSUBSCRIBE_BASE_QUOTE_PRICE"
UNSUBSCRIBE_TXS = "UNSUBSCRIBE_TXS"
UNSUBSCRIBE_TOKEN_NEW_LISTING = "UNSUBSCRIBE_TOKEN_NEW_LISTING"
UNSUBSCRIBE_NEW_PAIR = "UNSUBSCRIBE_NEW_PAIR"
UNSUBSCRIBE_LARGE_TRADE_TXS = "UNSUBSCRIBE_LARGE_TRADE_TXS"
UNSUBSCRIBE_WALLET_TXS = "UNSUBSCRIBE_WALLET_TXS"
UNSUBSCRIBE_TOKEN_STATS = "UNSUBSCRIBE_TOKEN_STATS"


SubUnsubType = Literal[
    SUBSCRIBE_PRICE,
    SUBSCRIBE_BASE_QUOTE_PRICE,
    SUBSCRIBE_TXS,
    SUBSCRIBE_TOKEN_NEW_LISTING,
    SUBSCRIBE_NEW_PAIR,
    SUBSCRIBE_LARGE_TRADE_TXS,
    SUBSCRIBE_WALLET_TXS,
    SUBSCRIBE_TOKEN_STATS,
    UNSUBSCRIBE_PRICE,
    UNSUBSCRIBE_BASE_QUOTE_PRICE,
    UNSUBSCRIBE_TXS,
    UNSUBSCRIBE_TOKEN_NEW_LISTING,
    UNSUBSCRIBE_NEW_PAIR,
    UNSUBSCRIBE_LARGE_TRADE_TXS,
    UNSUBSCRIBE_WALLET_TXS,
    UNSUBSCRIBE_TOKEN_STATS
]

WS_DATA_WELCOME = "WELCOME"
WS_DATA_ERROR = "ERROR"
WS_DATA_PRICE_DATA = "PRICE_DATA"
WS_DATA_TXS_DATA = "TXS_DATA"
WS_DATA_BASE_QUOTE_PRICE_DATA = "BASE_QUOTE_PRICE_DATA"
WS_DATA_TOKEN_NEW_LISTING_DATA = "TOKEN_NEW_LISTING_DATA"
WS_DATA_NEW_PAIR_DATA = "NEW_PAIR_DATA"
WS_DATA_TXS_LARGE_TRADE_DATA = "TXS_LARGE_TRADE_DATA"
WS_DATA_WALLET_TXS_DATA = "WALLET_TXS_DATA"

WsDataType = Literal[
    WS_DATA_WELCOME,
    WS_DATA_ERROR,
    WS_DATA_PRICE_DATA,
    WS_DATA_TXS_DATA,
    WS_DATA_BASE_QUOTE_PRICE_DATA,
    WS_DATA_TOKEN_NEW_LISTING_DATA,
    WS_DATA_NEW_PAIR_DATA,
    WS_DATA_TXS_LARGE_TRADE_DATA,
    WS_DATA_WALLET_TXS_DATA
]

CurrencyType = Literal["usd", "pair"]

# ============================================================
# Sub/Unsub Data Classes
# ============================================================

@dataclass
class SubUnsubData[D = object | None]:
    type: SubUnsubType
    data: Optional[D] = None
    
    def payload(self) -> str:
        if isinstance(self.data, SubDataLargeTradeTxs):
            return json.dumps(asdict(self.data))
        return json.dumps({
            "type": self.type,
            "data": asdict(self.data)
        })


@dataclass
class SubDataComplex(TypedDict):
    queryType: QueryType
    query: str
    

def merge_query(queries: list[str]) -> str:
    return " OR ".join(queries)


@dataclass
class SubDataPrice:
    address: str
    chartType: IntervalType
    currency: CurrencyType = "usd"
    queryType: QueryType = "simple"
    
    def query(self) -> str:
        return f"(address={self.address} AND chartType={self.chartType} AND currency={self.currency} AND queryType={self.queryType})"
    
    def sub_payload(self) -> str:
        return json.dumps({
            "type": SUBSCRIBE_PRICE,
            "data": {
                "address": self.address,
                "chartType": self.chartType,
                "currency": self.currency,
                "queryType": self.queryType
            }
        })
        

def prices_complex_sub_payload(prices: list[SubDataPrice]) -> str:
    queries = [price.query() for price in prices]
    return json.dumps({
        "type": SUBSCRIBE_PRICE,
        "data": {
            "queryType": "complex",
            "query": merge_query(queries)
        }
    })
    

@dataclass
class SubDataTxs:
    address: Optional[str] = None
    pairAddress: Optional[str] = None
    queryType: QueryType = "simple"
    
    def query(self) -> Optional[str]:
        if self.address is not None:
            return f"address={self.address}"
        if self.pairAddress is not None:
            return f"pairAddress={self.pairAddress}"
        return None
    
    def sub_payload(self) -> str:
        data = {
            "type": SUBSCRIBE_TXS,
            "data": {
                "queryType": self.queryType
            }
        }
        if self.address is not None:
            data["data"]["address"] = self.address
        elif self.pairAddress is not None:
            data["data"]["pairAddress"] = self.pairAddress
        return json.dumps(data)
    

def txs_complex_sub_payload(txs: list[SubDataTxs]) -> str:
    queries = [tx.query() for tx in txs]
    return json.dumps({
        "type": SUBSCRIBE_TXS,
        "data": {
            "queryType": "complex",
            "query": merge_query(queries)
        }
    })
    

@dataclass
class SubDataBaseQuotePrice:
    baseAddress: str
    quoteAddress: str
    chartType: IntervalType
    
    def sub_payload(self) -> str:
        return json.dumps({
            "type": SUBSCRIBE_BASE_QUOTE_PRICE,
            "data": {
                "baseAddress": self.baseAddress,
                "quoteAddress": self.quoteAddress,
                "chartType": self.chartType
            }
        })
    
    
    
@dataclass
class SubDataTokenNewListing:
    meme_plateform_enabled: Optional[bool] = None
    min_liquidity: Optional[float] = None
    max_liquidity: Optional[float] = None
    
    def sub_payload(self) -> str:
        data = {
            "type": SUBSCRIBE_TOKEN_NEW_LISTING,
            "data": {
            }
        }
        if self.meme_plateform_enabled is not None:
            data["data"]["meme_plateform_enabled"] = self.meme_plateform_enabled
        if self.min_liquidity is not None:
            data["data"]["min_liquidity"] = self.min_liquidity
        if self.max_liquidity is not None:
            data["data"]["max_liquidity"] = self.max_liquidity
        return json.dumps(data)
    
    
@dataclass
class SubDataNewPair:
    min_liquidity: Optional[float] = None
    max_liquidity: Optional[float] = None
    
    def sub_payload(self) -> str:
        data = {
            "type": SUBSCRIBE_NEW_PAIR,
            "data": {
            }
        }
        if self.min_liquidity is not None:
            data["data"]["min_liquidity"] = self.min_liquidity
        if self.max_liquidity is not None:
            data["data"]["max_liquidity"] = self.max_liquidity
        return json.dumps(data)
    
    
@dataclass
class SubDataLargeTradeTxs:
    min_volume: float = 0
    max_volume: Optional[float] = None
    type: SubUnsubType = SUBSCRIBE_LARGE_TRADE_TXS
    
    
    def sub_payload(self) -> str:
        data = {
            "type": SUBSCRIBE_LARGE_TRADE_TXS,
            "min_volume": self.min_volume
        }
        if self.max_volume is not None:
            data["max_volume"] = self.max_volume
        return json.dumps(data)
    
    
@dataclass
class SubDataWalletTxs:
    address: str
    def sub_payload(self) -> str:
        return json.dumps({
            "type": SUBSCRIBE_WALLET_TXS,
            "data": {
                "address": self.address
            }
        })
        
        
@dataclass
class TokenStatsSelectTradeData:
    volume: bool = True
    trade: bool = True
    price_history: bool = True
    volume_history: bool = True
    price_change: bool = True
    trade_history: bool = True
    trade_change: bool = True
    volume_change: bool = True
    unique_wallet: bool = True
    unique_wallet_change: bool = False
    intervals: list[IntervalType] = field(default_factory=lambda: ["30m", "1h", "2h", "4h", "8h", "24h"])


@dataclass
class TokenStatsSelect:
    price: bool = True
    trade_data: TokenStatsSelectTradeData = field(default_factory=TokenStatsSelectTradeData)
    fdv: bool = True
    marketcap: bool = True
    supply: bool = True
    last_trade: bool = True
    liquidity: bool = True


@dataclass
class SubDataTokenStats:
    address: str
    select: TokenStatsSelect = field(default_factory=TokenStatsSelect)
    
    def sub_payload(self) -> str:
        data = {
            "type": SUBSCRIBE_TOKEN_STATS,
            "data": {
                "address": self.address,
                "select": asdict(self.select)
            }
        }
        return json.dumps(data)

    
# ============================================================
# Data Classes
# ============================================================

class WsData[D = dict | str](TypedDict):
    """
    If has error, data is a string
    """
    type: WsDataType
    data: D


class WsDataPrice(TypedDict):
    """Response type for price data from websocket.
    
    Example:
        {
            "o": 24.586420063533236,  # Open price
            "h": 24.586420063533236,  # High price
            "l": 24.586420063533236,  # Low price 
            "c": 24.586420063533236,  # Close price
            "eventType": "ohlcv",
            "type": "1m",
            "unixTime": 1675506000,
            "v": 32.928421816,        # Volume
            "symbol": "SOL",
            "address": "So11111111111111111111111111111111111111112"
        }
    """
    o: float  # Open price
    h: float  # High price
    l: float  # Low price
    c: float  # Close price
    eventType: Literal["ohlcv"]
    type: str  # Interval type
    unixTime: int
    v: float  # Volume
    symbol: str
    address: str


class WsDataTxs(TypedDict):
    """Response type for transaction data from websocket.
    
    Example:
        {
            "blockUnixTime": 1747307828,
            "owner": "Dc9jiLSNN8qwEciwd55HmZhroswZ4XvcvKeRXHWCnwbP",
            "source": "zerofi",
            "txHash": "3L4BWQxgpF7SyH13bbEH53ZXYFNdRcK5dtMXreeGviaWFKes3fod5cQWsQ3oRHXcdUaemoiEXLaUit1Syw5FdCP1",
            "side": "sell",
            "tokenAddress": "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
            "alias": Optional[str],
            "isTradeOnBe": False,
            "platform": "Jupiter",
            "pricePair": 0.49898781541961984,
            "volumeUSD": 86.16813238056157,
            "from": {
                "address": str,
                "amount": int,
                "changeAmount": int,
                "decimals": int,
                "nearestPrice": float,
                "price": Optional[float],
                "symbol": str,
                "type": str,
                "typeSwap": str,
                "uiAmount": float,
                "uiChangeAmount": float
            },
            "to": {
                "address": str,
                "amount": int,
                "changeAmount": int,
                "decimals": int,
                "feeInfo": Optional[dict],
                "nearestPrice": float,
                "price": Optional[float],
                "symbol": str,
                "type": str,
                "typeSwap": str,
                "uiAmount": float,
                "uiChangeAmount": float
            },
            "priceMark": bool,
            "tokenPrice": float,
            "network": str,
            "poolId": str
        }
    """
    class TokenInfo(TypedDict):
        """Token information in a transaction"""
        address: str
        amount: int
        changeAmount: int
        decimals: int
        nearestPrice: float
        price: Optional[float]
        symbol: str
        type: str
        typeSwap: str
        uiAmount: float
        uiChangeAmount: float
        feeInfo: Optional[dict]

    blockUnixTime: int
    owner: str
    source: str
    txHash: str
    side: Literal["buy", "sell"]
    tokenAddress: str
    alias: Optional[str]
    isTradeOnBe: bool
    platform: str
    pricePair: float
    volumeUSD: float
    from_: TokenInfo  # type: ignore
    to: TokenInfo
    priceMark: bool
    tokenPrice: float
    network: str
    poolId: str

 
class WsDataBaseQuotePrice(TypedDict):
    """OHLCV price data for a base/quote token pair.
    
    Example:
        {
            "o": 153.00668789866964,
            "h": 153.0229060481432, 
            "l": 152.88823226160142,
            "c": 152.89094335479908,
            "eventType": "ohlcv",
            "type": "1m",
            "unixTime": 1729158060,
            "v": 0,
            "baseAddress": "So11111111111111111111111111111111111111112",
            "quoteAddress": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        }
    """
    o: float  # Open price
    h: float  # High price
    l: float  # Low price 
    c: float  # Close price
    eventType: Literal["ohlcv"]
    type: str  # Time interval
    unixTime: int  # Unix timestamp
    v: float  # Volume
    baseAddress: str  # Base token address
    quoteAddress: str  # Quote token address
    

class WsDataTokenNewListing(TypedDict):
    """New token listing data.
    
    Example:
        {
            "address": "BkQfwVktcbWmxePJN5weHWJZgReWbiz8gzTdFa2w7Uds",
            "decimals": 6,
            "name": "Worker Cat", 
            "symbol": "$MCDCAT",
            "liquidity": "12120.155172280874",
            "liquidityAddedAt": 1720155863
        }
    """
    address: str  # Token contract address
    decimals: int  # Token decimals
    name: str  # Token name
    symbol: str  # Token symbol
    liquidity: str  # Initial liquidity amount
    liquidityAddedAt: int  # Unix timestamp when liquidity was added


class WsDataNewPair(TypedDict):
    """New trading pair listing data.
    
    Example:
        {
            "address": "CXV4S8CxSppJeGzMFv8YQjsGZJif8d1Fqz9EtJRovmJY",
            "name": "$JESUSPUMP-SOL", 
            "source": "pump_dot_fun",
            "base": {
                "address": "AoMBAxc82xinKTnEBGvuJaFb7occsyyBD6GmELrypump",
                "name": "JESUS PUMP",
                "symbol": "$JESUSPUMP", 
                "decimals": 6
            },
            "quote": {
                "address": "So11111111111111111111111111111111111111112",
                "name": "Wrapped SOL",
                "symbol": "SOL",
                "decimals": 9
            },
            "txHash": "3CzXpuUJV9KryVDMN5nFAqH87TfueWG6sUiksbf3Akh9eqGNJW1CJtYbrELJixXC77Dyutz8CfT3eP1uJ3LP3iy5",
            "blockTime": 1720156781
        }
    """
    class TokenInfo(TypedDict):
        """Token information in a trading pair"""
        address: str
        name: str 
        symbol: str
        decimals: int

    address: str  # Pool address
    name: str  # Trading pair name
    source: str  # Source platform
    base: TokenInfo  # Base token info
    quote: TokenInfo  # Quote token info
    txHash: str  # Transaction hash
    blockTime: int  # Unix timestamp


class WsDataLargeTradeTxs(TypedDict):
    """Response type for large trade transaction data from websocket.
    
    Example:
        {
            "blockUnixTime": 1734345250,
            "blockHumanTime": "2024-12-16T10:34:10", 
            "owner": "7wWGFsrUnCjDS5mSxSZVgqqX2KBvS7muUTgAyB3pZQ4s",
            "source": "lifinity",
            "poolAddress": "Gkt4BpMRFxhhrrVMQsewM74ggriAbxyN2yUYDD9qt1NV",
            "txHash": "5TDU8rdEYXzmiJmGB6xeB9VsmQGXrQvefsto65jXJfgb2dZu19zt2nWxxTuhdKUCGyHPbBfyPhyuxpDgfP5Qfd3d",
            "volumeUSD": 12903.754274606412,
            "network": "solana",
            "from": {
                "symbol": "SOL",
                "decimals": 9,
                "address": "So11111111111111111111111111111111111111112", 
                "uiAmount": 59.283968522,
                "price": null,
                "nearestPrice": 217.64374028102003,
                "uiChangeAmount": -59.283968522
            },
            "to": {
                "symbol": "USDC",
                "decimals": 6,
                "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                "uiAmount": 12904.206438,
                "price": null,
                "nearestPrice": 0.99996496,
                "uiChangeAmount": 12904.206438
            }
        }
    """
    class TokenInfo(TypedDict):
        """Token information in a large trade"""
        symbol: str
        decimals: int
        address: str
        uiAmount: float
        price: Optional[float]
        nearestPrice: float
        uiChangeAmount: float

    blockUnixTime: int
    blockHumanTime: str
    owner: str
    source: str
    poolAddress: str
    txHash: str
    volumeUSD: float
    network: str
    from_: TokenInfo
    to: TokenInfo
    
    
class WsDataWalletMintAddLiquidityTx(TypedDict):
    """Response type for wallet transaction data from websocket.
    
    Example:
        {
            "type": "mint_add_liquidity",
            "blockUnixTime": 1733821667,
            "blockHumanTime": "2024-12-10T09:07:47",
            "owner": "0xae2Fc483527B8EF99EB5D9B44875F005ba1FaE13",
            "source": "0x0A0b2c28470bF68A6144DF04b08360559fb4aAf1",
            "txHash": "0xd80eaabb9c185313c8258ac54eea8bd75eadfb904dec85f887b7f47c58bdb59e",
            "volumeUSD": 2635.811230294149,
            "network": "ethereum",
            "base": {
                "symbol": "WETH",
                "decimals": 18,
                "address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                "uiAmount": 0.09992862476596062
            },
            "quote": {
                "symbol": "TRVL", 
                "decimals": 18,
                "address": "0xd47bDF574B4F76210ed503e0EFe81B58Aa061F3d",
                "uiAmount": 39214.96224535667
            }
        }
    """
    class TokenInfo(TypedDict):
        """Token information in a wallet transaction"""
        symbol: str
        decimals: int
        address: str
        uiAmount: float

    type: str
    blockUnixTime: int
    blockHumanTime: str
    owner: str
    source: str
    txHash: str
    volumeUSD: float
    network: str
    base: TokenInfo
    quote: TokenInfo
    
    
class WsDataWalletSwapTx(TypedDict):
    """Response type for wallet swap transaction data from websocket.
    
    Example:
        {
            "type": "swap",
            "blockUnixTime": 1759849618,
            "blockHumanTime": "2025-10-07T15:06:58",
            "owner": "0x64B23c2987AcA16b3d3C55ad6F694058783c72Ea",
            "source": "PancakeSwap",
            "poolAddress": "0x70ab2bd596893153887032D20e1e542872249Ce9",
            "txHash": "0xa34275a10d30c57514b20cd6f0b1b6a352ed7434521e1f966b16df142fbc16c8",
            "volumeUSD": 640.2648748948124,
            "network": "bsc",
            "from": {
                "symbol": "WBNB",
                "decimals": 18,
                "address": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
                "uiAmount": 0.495,
                "amount": 495000000000000000,
                "price": 1293.4643937268936,
                "nearestPrice": 1293.4643937268936,
                "uiChangeAmount": -0.495
            },
            "to": {
                "symbol": "CZINTERN",
                "decimals": 18,
                "address": "0x89a39e9f4FF38Cb0df35B0Cb98432ADAc3F64444",
                "uiAmount": 27952489.5237955,
                "amount": 2.79524895237955e+25,
                "price": 2.2905468736506107e-05,
                "nearestPrice": 2.154756979291976e-05,
                "uiChangeAmount": 27952489.5237955
            },
            "interactedProgramId": "0x1de460f363AF910f51726DEf188F9004276Bf4bc",
            "logIndex": 398,
            "insIndex": 5,
            "blockNumber": 63800381
        }
    """
    class TokenInfo(TypedDict):
        """Token information in a wallet swap transaction"""
        symbol: str
        decimals: int
        address: str
        uiAmount: float
        amount: int
        price: float
        nearestPrice: float
        uiChangeAmount: float

    type: str
    blockUnixTime: int
    blockHumanTime: str
    owner: str
    source: str
    poolAddress: str
    txHash: str
    volumeUSD: float
    network: str
    from_: TokenInfo  # from is a reserved keyword
    to: TokenInfo
    interactedProgramId: str
    logIndex: int
    insIndex: int
    blockNumber: int


    

class WsDataTokenStats(TypedDict):
    """Response type for token statistics data from websocket.
    
    Example:
        {
            "price": 0.61249,
            "last_trade_human_time": "2025-07-21T10:47:21",
            "last_trade_unix_time": 1753094841,
            "circulating_supply": 3266503718.50,
            "total_supply": 6999203720.02,
            "fdv": 4286950419.35,
            "marketcap": 2000704658.13,
            "liquidity": 14376190.77,
            "volume_30m_usd": 1366829.36,
            "volume_30m": 2257825.69,
            "volume_buy_30m": 1172585.03,
            "volume_buy_30m_usd": 706769.62,
            "volume_sell_30m": 1085240.66,
            "volume_sell_30m_usd": 660059.73,
            "trade_30m": 6961,
            "buy_30m": 3542,
            "sell_30m": 3419,
            "volume_history_30m": 1891967.98,
            "volume_history_30m_usd": 1151063.25,
            "volume_sell_history_30m_usd": 542627.18,
            "volume_buy_history_30m_usd": 608436.06,
            "price_change_30m_percent": 0.70,
            "trade_history_30m": 7300,
            "buy_history_30m": 3746,
            "sell_history_30m": 3554,
            "trade_30m_change_percent": -4.64,
            "buy_30m_change_percent": -5.44,
            "sell_30m_change_percent": -3.79,
            "volume_30m_change_percent": 19.33,
            "volume_buy_30m_change_percent": 17.35,
            "volume_sell_30m_change_percent": 21.55,
            "unique_wallet_30m": 872
        }
    """
    price: float
    last_trade_human_time: str
    last_trade_unix_time: int
    circulating_supply: float
    total_supply: float
    fdv: float
    marketcap: float
    liquidity: float
    volume_30m_usd: float
    volume_30m: float
    volume_buy_30m: float
    volume_buy_30m_usd: float
    volume_sell_30m: float
    volume_sell_30m_usd: float
    trade_30m: int
    buy_30m: int
    sell_30m: int
    volume_history_30m: float
    volume_history_30m_usd: float
    volume_sell_history_30m_usd: float
    volume_buy_history_30m_usd: float
    price_change_30m_percent: float
    trade_history_30m: int
    buy_history_30m: int
    sell_history_30m: int
    trade_30m_change_percent: float
    buy_30m_change_percent: float
    sell_30m_change_percent: float
    volume_30m_change_percent: float
    volume_buy_30m_change_percent: float
    volume_sell_30m_change_percent: float
    unique_wallet_30m: int


