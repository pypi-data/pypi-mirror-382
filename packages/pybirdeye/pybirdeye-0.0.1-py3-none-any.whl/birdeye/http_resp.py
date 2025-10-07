"""
Response type definitions for Birdeye API.

This module contains all TypedDict definitions for API response types.
"""

from typing import Any, Literal, Optional, TypedDict
from birdeye.consts import Chain

# ============================================================================
# Response Type Definitions
# ============================================================================

class RespTokenPrice(TypedDict):
    """Response type for token price endpoints.
    
    Example:
        {
            "isScaledUiToken": false,
            "value": 0.38622452197470425,
            "updateUnixTime": 1745058945,
            "updateHumanTime": "2025-04-19T10:35:45", 
            "priceChange24h": 1.933391934259418,
            "priceInNative": 0.0027761598581298626,
            "liquidity": 10854103.37938592
        }
    """
    isScaledUiToken: bool
    value: float  
    updateUnixTime: int
    updateHumanTime: str
    priceChange24h: float
    priceInNative: float
    liquidity: float


class RespTokenTxs(TypedDict):
    class RespTokenTxsItem(TypedDict):
        """
        Response type for token trade data.
        
        Example:
            {
                "quote": {
                    "symbol": "SHIPE",
                    "decimals": 6,
                    "address": "9K78h3XEb7qqRu4XEaAEhe3qXaAeN1XyHa65bLwKXaNp",
                    "amount": 3000940514830,
                    "uiAmount": 3000940.51483,
                    "price": 0.00008920248678973954,
                    "nearestPrice": 0.00008879906452142359,
                    "changeAmount": 3000940514830,
                    "uiChangeAmount": 3000940.51483,
                    "isScaledUiToken": False,
                    "multiplier": None
                },
                "base": {
                    "symbol": "SOL", 
                    "decimals": 9,
                    "address": "So11111111111111111111111111111111111111112",
                    "amount": 1452043321,
                    "uiAmount": 1.452043321,
                    "price": 184.35493814782487,
                    "nearestPrice": 184.35493814782487,
                    "changeAmount": -1452043321,
                    "uiChangeAmount": -1.452043321,
                    "isScaledUiToken": False,
                    "multiplier": None
                },
                "basePrice": 184.35493814782487,
                "quotePrice": 0.00008920248678973954,
                "txHash": "NLiBctRYuhibKZCJPkPxGhDKi9pCo2fx818H1UBJ82gD5DKddvufzf5DAPVKkLgejQ4EezcgE72FUrf327VQGaV",
                "source": "pump_amm",
                "blockUnixTime": 1754883867,
                "txType": "swap",
                "owner": "5V7aauQjnizwXAPGcJnjC7mbpenbiQZBfBSxW3n7NGCD",
                "side": "sell",
                "alias": null,
                "pricePair": 2066701.7790924432,
                "from": {...},  # Same structure as quote/base
                "to": {...},    # Same structure as quote/base
                "tokenPrice": 184.35493814782487,
                "poolId": "7LfK73yHk16kaSqa4FDB8t1oU445zzSsgMMC3at4eCFR"
            }
    
        """
    
        class RespTokenTradeToken(TypedDict):
            """Token details in a trade response"""
            symbol: str
            decimals: int
            address: str
            amount: int
            uiAmount: float
            price: float
            nearestPrice: float
            changeAmount: int
            uiChangeAmount: float
            isScaledUiToken: bool
            multiplier: Optional[float]
    
        quote: RespTokenTradeToken
        base: RespTokenTradeToken
        basePrice: float
        quotePrice: float
        txHash: str
        source: str
        blockUnixTime: int
        txType: Literal["swap", "add", "remove"]
        owner: str
        side: Literal["buy", "sell"]
        alias: Optional[str]
        pricePair: float
        from_: RespTokenTradeToken  # from is a reserved keyword
        to: RespTokenTradeToken
        tokenPrice: float
        poolId: str

    items: list[RespTokenTxsItem]
    hasNext: bool


class RespPairTxs(TypedDict):
    class RespPairTxsItem(TypedDict):
        """Transaction details for a trading pair.
        
        Example:
            {
                "txHash": "2s27V8t3HANqUA572KLqBNXFvGyqvYobFX2Cn3c5puoWbHSNCebjT6PDX7gixe5HjdNhuG7SuHpDroJXFrBpAFn1",
                "source": "phoenix",
                "blockUnixTime": 1754882843,
                "txType": "swap",
                "address": "4DoNfFBfF7UokCC2FQzriy7yHK6DY6NVdYpuekQ5pRgg",
                "owner": "MfDuWeqSHEqTFVYZ7LoexgAK9dxk7cy4DFJWjWMGVWa",
                "from": {
                    "symbol": "USDC",
                    "decimals": 6,
                    "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                    "amount": 4000129768,
                    "type": "log",
                    "typeSwap": "from",
                    "uiAmount": 4000.129768,
                    "price": 0.99986,
                    "nearestPrice": 0.99986,
                    "changeAmount": -4000129768,
                    "uiChangeAmount": -4000.129768,
                    "isScaledUiToken": false,
                    "multiplier": null
                },
                "to": {
                    "symbol": "SOL", 
                    "decimals": 9,
                    "address": "So11111111111111111111111111111111111111112",
                    "amount": 21638000000,
                    "type": "log",
                    "typeSwap": "to",
                    "uiAmount": 21.638,
                    "price": 184.67395202659998,
                    "nearestPrice": 184.67395202659998,
                    "changeAmount": 21638000000,
                    "uiChangeAmount": 21.638,
                    "isScaledUiToken": false,
                    "multiplier": null
                }
            }
        """
        class TokenTradeToken(TypedDict):
            """Token trade information in a transaction."""
            symbol: str
            decimals: int
            address: str
            amount: int
            type: str
            typeSwap: str
            uiAmount: float
            price: float
            nearestPrice: float
            changeAmount: int
            uiChangeAmount: float
            isScaledUiToken: bool
            multiplier: Optional[float]
    
        txHash: str
        source: str
        blockUnixTime: int
        txType: Literal["swap", "add", "remove"]
        address: str
        owner: str
        from_: TokenTradeToken  # from is a reserved keyword
        to: TokenTradeToken

    items: list[RespPairTxsItem]
    hasNext: bool


class RespTokenTxsByTime(TypedDict):
    items: list[RespTokenTxs.RespTokenTxsItem]
    hasNext: bool


class RespPairTxsByTime(TypedDict):
    items: list[RespPairTxs.RespPairTxsItem]
    hasNext: bool


class RespAllTxsV3(TypedDict):
    class RespAllTxsItemV3(TypedDict):
        """Response type for all transactions v3 endpoint.
        
        Example:
            {
                "base": {
                    "symbol": "CLIPPY",
                    "address": "GCLTmivKZfxYi8SV17FrpqH8HZtJauoePQPRHxJxBAGS", 
                    "decimals": 9,
                    "price": 0.00026036603447282113,
                    "amount": "24285885836773",
                    "ui_amount": 24285.885836773,
                    "ui_change_amount": 24285.885836773,
                    "type_swap": "to",
                    "is_scaled_ui_token": false,
                    "multiplier": null
                },
                "quote": {
                    "symbol": "SOL",
                    "address": "So11111111111111111111111111111111111111112",
                    "decimals": 9, 
                    "price": 185.6186502639611,
                    "amount": "34118151",
                    "ui_amount": 0.034118151,
                    "ui_change_amount": -0.034118151,
                    "type_swap": "from",
                    "is_scaled_ui_token": false,
                    "multiplier": null
                },
                "tx_type": "swap",
                "tx_hash": "4z62PXFvbo52qY66XAMhsaKSfNH9MoBinFQtsjoZcjRTc2gCGP2o86yTUdaHpnYozHxNkiATX3KRGPfFb7CyjoPW",
                "ins_index": 0,
                "inner_ins_index": 3,
                "block_unix_time": 1754885184,
                "block_number": 359262879,
                "volume_usd": 6.332965138122014,
                "volume": 24285.885836773,
                "owner": "7dGrdJRYtsNR8UYxZ3TnifXGjGc9eRYLq9sELwYpuuUu",
                "signers": ["7dGrdJRYtsNR8UYxZ3TnifXGjGc9eRYLq9sELwYpuuUu"],
                "source": "meteora_dlmm",
                "interacted_program_id": "King7ki4SKMBPb3iupnQwTyjsq294jaXsgLmJo8cb7T",
                "pool_id": "6LR2pDMBbYZNhj1iF86b4X5zRYyX7BNrhpzRDEZYNam9"
            }
        """
        
        class RespAllTxsTokenV3(TypedDict):
            """Token details in an all transactions v3 response"""
            symbol: str
            address: str
            decimals: int
            price: float
            amount: str
            ui_amount: float
            ui_change_amount: float
            type_swap: Literal["from", "to"]
            is_scaled_ui_token: bool
            multiplier: Optional[float]
    
        base: RespAllTxsTokenV3
        quote: RespAllTxsTokenV3
        tx_type: Literal["swap", "add", "remove"]
        tx_hash: str
        ins_index: int
        inner_ins_index: int
        block_unix_time: int
        block_number: int
        volume_usd: float
        volume: float
        owner: str
        signers: list[str]
        source: str
        interacted_program_id: str
        pool_id: str

    items: list[RespAllTxsItemV3]
    hasNext: bool


class RespTokenTxsV3(TypedDict):
    class RespTokenTxsItemV3(TypedDict):
        """Response type for token transaction data (v3 API).
        
        Example:
            {
                "tx_type": "buy",
                "tx_hash": "3fqsirN8vbhBLHS2cVAaCXTdsCcCua75LgcBX6Z2G2yupM9cDEsmo2TP5AhXvEUBZ91xyy3KWiuDdHxoFVnp1R88",
                "ins_index": 2,
                "inner_ins_index": 0, 
                "block_unix_time": 1740380278,
                "block_number": 322728531,
                "volume_usd": 0.0005729458359923133,
                "volume": 1733.23946,
                "owner": "8bP4FJNXwN5Q4a6EybtHwsiAnxFFWb93sY38mYdo6Pr2",
                "signers": ["8bP4FJNXwN5Q4a6EybtHwsiAnxFFWb93sY38mYdo6Pr2"],
                "source": "raydium",
                "side": "buy",
                "alias": null,
                "price_pair": 486318591.4702581,
                "from": {
                    "symbol": "PEPEAI",
                    "address": "7nM97F8takLArrKLJdT62L54jTtX1e7h7qPSjtBrsMQA",
                    "decimals": 6,
                    "price": 3.5071289483955604e-7,
                    "amount": "1733239460",
                    "ui_amount": 1733.23946,
                    "ui_change_amount": -1733.23946
                },
                "to": {
                    "symbol": "SOL", 
                    "address": "So11111111111111111111111111111111111111112",
                    "decimals": 9,
                    "price": 160.7592132413898,
                    "amount": "3564",
                    "ui_amount": 0.000003564,
                    "ui_change_amount": 0.000003564
                },
                "pool_id": "8aTXVUjPcUSwSLAbUegaKTQdB6SaNosSKQkURvpbLCNC"
            }
        """
        class TokenInfo(TypedDict):
            """Token information in a transaction"""
            symbol: str
            address: str
            decimals: int
            price: float
            amount: str
            ui_amount: float
            ui_change_amount: float
    
        tx_type: Literal["buy", "sell", "swap", "add", "remove"]
        tx_hash: str
        ins_index: int
        inner_ins_index: int
        block_unix_time: int
        block_number: int
        volume_usd: float
        volume: float
        owner: str
        signers: list[str]
        source: str
        side: Literal["buy", "sell"]
        alias: Optional[str]
        price_pair: float
        from_: TokenInfo  # from is a reserved keyword
        to: TokenInfo
        pool_id: str

    items: list[RespTokenTxsItemV3]
    hasNext: bool


class RespRecentTxsV3(TypedDict):
    class RespRecentTxsItemV3(TypedDict):
        """Response type for recent transactions v3.
        
        Example:
            {
                "base": {
                    "symbol": "CLIPPY",
                    "address": "GCLTmivKZfxYi8SV17FrpqH8HZtJauoePQPRHxJxBAGS", 
                    "decimals": 9,
                    "price": 0.00026036603447282113,
                    "amount": "24285885836773",
                    "ui_amount": 24285.885836773,
                    "ui_change_amount": 24285.885836773,
                    "type_swap": "to",
                    "is_scaled_ui_token": false,
                    "multiplier": null
                },
                "quote": {
                    "symbol": "SOL",
                    "address": "So11111111111111111111111111111111111111112",
                    "decimals": 9, 
                    "price": 185.6186502639611,
                    "amount": "34118151",
                    "ui_amount": 0.034118151,
                    "ui_change_amount": -0.034118151,
                    "type_swap": "from",
                    "is_scaled_ui_token": false,
                    "multiplier": null
                },
                "tx_type": "swap",
                "tx_hash": "4z62PXFvbo52qY66XAMhsaKSfNH9MoBinFQtsjoZcjRTc2gCGP2o86yTUdaHpnYozHxNkiATX3KRGPfFb7CyjoPW",
                "ins_index": 0,
                "inner_ins_index": 3,
                "block_unix_time": 1754885184,
                "block_number": 359262879,
                "volume_usd": 6.332965138122014,
                "volume": 24285.885836773,
                "owner": "7dGrdJRYtsNR8UYxZ3TnifXGjGc9eRYLq9sELwYpuuUu",
                "signers": ["7dGrdJRYtsNR8UYxZ3TnifXGjGc9eRYLq9sELwYpuuUu"],
                "source": "meteora_dlmm",
                "interacted_program_id": "King7ki4SKMBPb3iupnQwTyjsq294jaXsgLmJo8cb7T",
                "pool_id": "6LR2pDMBbYZNhj1iF86b4X5zRYyX7BNrhpzRDEZYNam9"
            }
        """
        
        class RespRecentTxsTokenV3(TypedDict):
            """Token details in a recent transactions v3 response"""
            symbol: str
            address: str
            decimals: int
            price: float
            amount: str
            ui_amount: float
            ui_change_amount: float
            type_swap: Literal["from", "to"]
            is_scaled_ui_token: bool
            multiplier: Optional[float]
    
        base: RespRecentTxsTokenV3
        quote: RespRecentTxsTokenV3
        tx_type: Literal["swap", "add", "remove"]
        tx_hash: str
        ins_index: int
        inner_ins_index: int
        block_unix_time: int
        block_number: int
        volume_usd: float
        volume: float
        owner: str
        signers: list[str]
        source: str
        interacted_program_id: str
        pool_id: str

    items: list[RespRecentTxsItemV3]
    hasNext: bool


class RespTokenOHLCVs(TypedDict):
    """OHLCV response for a token.
    
    Example:
        {
            "isScaledUiToken": false,
            "items": [
                {
                    "o": 128.27328370924414,  # open price
                    "h": 128.6281001340782,   # high price 
                    "l": 127.91200927364626,  # low price
                    "c": 127.97284640184616,  # close price
                    "v": 58641.16636665621,   # volume
                    "unixTime": 1726670700,   # unix timestamp
                    "address": "So11111111111111111111111111111111111111112",
                    "type": "15m",            # interval type
                    "currency": "usd"         # price currency
                },
                ...
            ]
        }
    """
    
    class RespTokenOHLCVItem(TypedDict):
        """OHLCV data point for a token."""
        o: float
        h: float
        l: float
        c: float
        v: float
        unixTime: int
        address: str
        type: Literal["1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "8H", "12H", "1D", "3D", "1W", "1M"]  # Time interval
        currency: str

    isScaledUiToken: bool
    items: list[RespTokenOHLCVItem]


class RespPairOHLCVItem(TypedDict):
    """OHLCV data point for a trading pair.
    
    Example:
        {
            "address": "Czfq3xZZDmsdGdUyrNLtRhGc47cXcZtLG4crryfu44zE",
            "c": 131.98629958196778,
            "h": 132.23482213379438, 
            "l": 131.51590533656915,
            "o": 131.51590533656915,
            "type": "15m",
            "unixTime": 1726700400,
            "v": 6156.155046497001
        }
    """
    address: str
    c: float  # Close price
    h: float  # High price
    l: float  # Low price 
    o: float  # Open price
    type: Literal["1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "8H", "12H", "1D", "3D", "1W", "1M"]  # Time interval
    type: str  # Time interval
    unixTime: int  # Unix timestamp
    v: float  # Volume


class RespOHLCVBaseQuote(TypedDict):
    """OHLCV response for a base/quote token pair.
    
    Example:
        {
            "items": [
                {
                    "o": 128.2848293438851,
                    "c": 127.98180512820512, 
                    "h": 128.64650816293124,
                    "l": 127.91584674904873,
                    "vBase": 58641.16636665621,
                    "vQuote": 4362436.09417201,
                    "unixTime": 1726670700
                },
                {
                    "o": 127.98180512820512,
                    "c": 128.0549796460581,
                    "h": 128.51250171609132,
                    "l": 127.89610078074669,
                    "vBase": 47861.13031539581,
                    "vQuote": 3913815.120231004,
                    "unixTime": 1726671600
                }
            ],
            "baseAddress": "So11111111111111111111111111111111111111112",
            "quoteAddress": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "isScaledUiTokenBase": false,
            "isScaledUiTokenQuote": false,
            "type": "15m"
        }
    """
    
    class Item(TypedDict):
        """OHLCV data point for a base/quote token pair."""
        o: float  # Open price
        c: float  # Close price 
        h: float  # High price
        l: float  # Low price
        vBase: float  # Volume in base token
        vQuote: float  # Volume in quote token
        unixTime: int  # Unix timestamp in seconds

    items: list[Item]
    baseAddress: str
    quoteAddress: str 
    isScaledUiTokenBase: bool
    isScaledUiTokenQuote: bool
    type: Literal["1m", "3m", "5m", "15m", "30m",
                  "1H", "2H", "4H", "6H", "8H", "12H",
                  "1D", "3D", "1W", "1M"]


class RespTokenOHLCVsV3(TypedDict):
    """OHLCV V3 response for a token.
    
    Example:
        {
            "is_scaled_ui_token": false,
            "items": [
                {
                    "o": 128.27328370924414,  # open price
                    "h": 128.6281001340782,   # high price
                    "l": 127.91200927364626,  # low price
                    "c": 127.97284640184616,  # close price
                    "v": 58641.16636665621,   # volume
                    "v_usd": 7506048,         # volume in USD
                    "unix_time": 1726670700,  # unix timestamp
                    "address": "So11111111111111111111111111111111111111112",
                    "type": "15m",           # interval type
                    "currency": "usd"        # price currency
                },
                ...
            ]
        }
    """
    
    class RespTokenOHLCVItemV3(TypedDict):
        """OHLCV V3 data point for a token."""
        o: float
        h: float
        l: float
        c: float
        v: float
        v_usd: float
        unix_time: int
        address: str
        type: Literal["1s", "15s", "1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "8H", "12H", "1D", "3D", "1W", "1M"]
        currency: str

    is_scaled_ui_token: bool
    items: list[RespTokenOHLCVItemV3]


class RespPairOHLCVItemV3(TypedDict):
    """OHLCV V3 data point for a trading pair.
    
    Example:
        {
            "address": "9wFFyRfZBsuAha4YcuxcXLKwMxJR43S7fPfQLusDBzvT",
            "h": 210,
            "o": 210, 
            "l": 210,
            "c": 210,
            "type": "15m",
            "v": 0,
            "unix_time": 1726670700,
            "v_usd": 1000
        }
    """
    address: str
    h: float  # High price
    o: float  # Open price
    l: float  # Low price
    c: float  # Close price
    type: Literal["1s", "15s", "1m", "3m", "5m", "15m", "30m",
                  "1H", "2H", "4H", "6H", "8H", "12H",
                  "1D", "3D", "1W", "1M"]  # Time interval
    v: float  # Volume
    unix_time: int  # Unix timestamp
    v_usd: float  # Volume in USD


class RespTokenPriceHistories(TypedDict):
    """Response type for token price history.
    
    Example:
        {
            "isScaledUiToken": false,
            "items": [
                {
                    "unixTime": 1726670700,
                    "value": 127.97284640184616
                },
                {
                    "unixTime": 1726671600, 
                    "value": 128.04188346328968
                },
                {
                    "unixTime": 1726672500,
                    "value": 127.40223856228901
                }
            ]
        }
    """
    class RespPriceHistoryItem(TypedDict):
        """Individual price history data point"""
        unixTime: int
        value: float

    isScaledUiToken: bool 
    items: list[RespPriceHistoryItem]


class RespTokenPriceHistoryByTime(TypedDict):
    """Price history for a token at a specific time.
    
    Example:
        {
            "isScaledUiToken": false,
            "value": 128.09276765626564,
            "updateUnixTime": 1726675897,
            "priceChange24h": -4.924324221890145
        }
    """
    isScaledUiToken: bool
    value: float
    updateUnixTime: int # unix time in seconds
    priceChange24h: float


class RespTokenPriceVolume(TypedDict):
    """Response type for token price and volume data.
    
    Example:
        {
            "isScaledUiToken": false,
            "price": 128.70426432642992,
            "updateUnixTime": 1726678569,
            "updateHumanTime": "2024-09-18T16:56:09",
            "volumeUSD": 755004403.5277437,
            "volumeChangePercent": -6.0377419970263055,
            "priceChangePercent": -2.6091746792986936
        }
    """
    isScaledUiToken: bool
    price: float
    updateUnixTime: int # unix time in seconds
    updateHumanTime: str
    volumeUSD: float
    volumeChangePercent: float
    priceChangePercent: float


class RespPairOverview(TypedDict):
    """Overview data for a trading pair.
    
    Example:
        {
            "address": "4DoNfFBfF7UokCC2FQzriy7yHK6DY6NVdYpuekQ5pRgg",
            "base": {
                "address": "So11111111111111111111111111111111111111112",
                "decimals": 9,
                "icon": "https://...",
                "symbol": "SOL",
                "is_scaled_ui_token": false,
                "multiplier": 1
            },
            "quote": {
                "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", 
                "decimals": 6,
                "icon": "https://...",
                "symbol": "USDC",
                "is_scaled_ui_token": false,
                "multiplier": 1
            },
            "name": "SOL-USDC",
            "source": "Phoenix",
            "created_at": "2023-02-28T03:00:02.253Z",
            "liquidity": 2798754.646440928,
            "price": 185.2259461756374,
            "volume_24h": 3960934.260889339,
            "volume_24h_base": 21735.928,
            "volume_24h_quote": 3961073.7718080003,
            ...
        }
    """
    class TokenInfo(TypedDict):
        """Token information in pair overview"""
        address: str
        decimals: int
        icon: str
        symbol: str
        is_scaled_ui_token: bool
        multiplier: float

    address: str
    base: TokenInfo
    quote: TokenInfo
    name: str
    source: str
    created_at: str
    liquidity: float
    liquidity_change_percentage_24h: Optional[float]
    price: float
    
    trade_24h: int
    trade_12h: int
    trade_8h: int
    trade_4h: int
    trade_2h: int
    trade_1h: int
    trade_30m: int
    
    trade_24h_change_percent: float
    trade_12h_change_percent: float
    trade_8h_change_percent: float
    trade_4h_change_percent: float
    trade_2h_change_percent: float
    trade_1h_change_percent: float
    trade_30m_change_percent: float
    
    trade_history_24h: int
    trade_history_12h: int
    trade_history_8h: int
    trade_history_4h: int
    trade_history_2h: int
    trade_history_1h: int
    trade_history_30m: int
    
    unique_wallet_24h: int
    unique_wallet_12h: int
    unique_wallet_8h: int
    unique_wallet_4h: int
    unique_wallet_2h: int
    unique_wallet_1h: int
    unique_wallet_30m: int
    
    unique_wallet_24h_change_percent: float
    unique_wallet_12h_change_percent: float
    unique_wallet_8h_change_percent: float
    unique_wallet_4h_change_percent: float
    unique_wallet_2h_change_percent: float
    unique_wallet_1h_change_percent: float
    unique_wallet_30m_change_percent: float
    
    volume_24h: float
    volume_12h: float
    volume_8h: float
    volume_4h: float
    volume_2h: float
    volume_1h: float
    volume_30m: float
    
    volume_24h_base: float
    volume_12h_base: float
    volume_8h_base: float
    volume_4h_base: float
    volume_2h_base: float
    volume_1h_base: float
    volume_30m_base: float
    
    volume_24h_quote: float
    volume_12h_quote: float
    volume_8h_quote: float
    volume_4h_quote: float
    volume_2h_quote: float
    volume_1h_quote: float
    volume_30m_quote: float
    
    volume_24h_change_percentage_24h: Optional[float]


class RespTokenPriceStats(TypedDict):
    """Price statistics response for a token.
    
    Example:
        {
            "address": "So11111111111111111111111111111111111111112",
            "is_scaled_ui_token": false,
            "data": [
                {
                    "unix_time_update_price": 1751419434,
                    "time_frame": "1m", 
                    "price": 147.37122560933628,
                    "price_change_percent": -0.023923362896247174,
                    "high": 147.48709093365915,
                    "low": 147.31438207414254
                }
            ]
        }
    """
    class PriceStatsData(TypedDict):
        """Price statistics data point."""
        unix_time_update_price: int
        time_frame: Literal["1m", "5m", "30m", "1h", "2h", "4h", "8h", "24h", "2d", "3d", "7d"]
        price: float
        price_change_percent: float
        high: float
        low: float

    address: str
    is_scaled_ui_token: bool
    data: list[PriceStatsData]


class RespTokenListV1(TypedDict):
    """Token list v1 response.
    
    Example:
        {
            "updateUnixTime": 1754885276,
            "updateTime": "2025-08-11T04:07:56.945Z", 
            "tokens": [
                {
                    "isScaledUiToken": false,
                    "multiplier": null,
                    "address": "So11111111111111111111111111111111111111112",
                    "decimals": 9,
                    "price": 185.45023454574132,
                    "lastTradeUnixTime": 1754885221,
                    "liquidity": 23349538049.2037,
                    "logoURI": "https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/So11111111111111111111111111111111111111112/logo.png",
                    "mc": 100058305776.50261,
                    "name": "Wrapped SOL", 
                    "symbol": "SOL",
                    "v24hChangePercent": -1.4820129368250423,
                    "v24hUSD": 9515832024.915321
                }
            ],
            "total": 298068
        }
    """
    class RespTokenListV1Token(TypedDict):
        """Token details in a token list v1 response."""
        isScaledUiToken: bool
        multiplier: Optional[float]
        address: str
        decimals: int
        price: float
        lastTradeUnixTime: int
        liquidity: float
        logoURI: str
        mc: float  # Market cap
        name: str
        symbol: str
        v24hChangePercent: float
        v24hUSD: float

    updateUnixTime: int
    updateTime: str
    tokens: list[RespTokenListV1Token]
    total: int


class RespTokenListV3(TypedDict):
    """Token list V3 response.
    
    Example:
        {
            "items": [
                {
                    "address": "So11111111111111111111111111111111111111112",
                    "logo_uri": "https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/So11111111111111111111111111111111111111112/logo.png",
                    "name": "Wrapped SOL",
                    "symbol": "SOL",
                    "decimals": 9,
                    "extensions": {
                        "coingecko_id": "solana",
                        "website": "https://solana.com/",
                        "telegram": null,
                        "twitter": "https://twitter.com/solana",
                        "description": "Wrapped Solana",
                        "discord": "https://discordapp.com/invite/pquxPsq",
                        "medium": "https://medium.com/solana-labs"
                    },
                    "market_cap": 100119664431.51688,
                    "fdv": 112672175707.38792,
                    "total_supply": 607331645.8349773,
                    "circulating_supply": 539665463.3820738,
                    "liquidity": 23353595552.52654,
                    "last_trade_unix_time": 1754885383,
                    "volume_1h_usd": 443688491.34178054,
                    "volume_1h_change_percent": -1.714504394496686,
                    "volume_2h_usd": 861291542.4427114,
                    "volume_2h_change_percent": -3.5864189799692134,
                    "volume_4h_usd": 1747234746.548523,
                    "volume_4h_change_percent": -8.826330954721023,
                    "volume_8h_usd": 3423287365.9121313,
                    "volume_8h_change_percent": 8.888103083472839,
                    "volume_24h_usd": 9530159635.659721,
                    "volume_24h_change_percent": -1.3364377681566488,
                    "trade_1h_count": 1535608,
                    "trade_2h_count": 2948829,
                    "trade_4h_count": 5684776,
                    "trade_8h_count": 11119027,
                    "trade_24h_count": 31542138,
                    "buy_24h": 13941877,
                    "buy_24h_change_percent": -2.1854401371296177,
                    "volume_buy_24h_usd": 4728527789.759392,
                    "volume_buy_24h_change_percent": -1.6920149268570155,
                    "sell_24h": 17600261,
                    "sell_24h_change_percent": -3.143992919930877,
                    "volume_sell_24h_usd": 4801631845.900329,
                    "volume_sell_24h_change_percent": -0.9837807096207587,
                    "unique_wallet_24h": 1262031,
                    "unique_wallet_24h_change_percent": -26.286938857043396,
                    "price": 185.56395800803165,
                    "price_change_1h_percent": 0.4114972388399392,
                    "price_change_2h_percent": 0.4575777911423116,
                    "price_change_4h_percent": 1.8680908355708248,
                    "price_change_8h_percent": 1.3798037663979583,
                    "price_change_24h_percent": 0.5817906810497413,
                    "holder": 3472550,
                    "recent_listing_time": null,
                    "is_scaled_ui_token": false,
                    "multiplier": null
                }
            ],
            "hasNext": true
        }
    """
    
    class Extensions(TypedDict, total=False):
        """Token extension metadata."""
        coingecko_id: Optional[str]
        serum_v3_usdc: Optional[str]
        serum_v3_usdt: Optional[str]
        website: Optional[str]
        telegram: Optional[str]
        twitter: Optional[str]
        description: Optional[str]
        discord: Optional[str]
        medium: Optional[str]

    class TokenItem(TypedDict):
        """Individual token details."""
        address: str
        logo_uri: str
        name: str
        symbol: str
        decimals: int
        extensions: "RespTokenListV3.Extensions"
        market_cap: float
        fdv: float
        total_supply: float
        circulating_supply: float
        liquidity: float
        last_trade_unix_time: int
        volume_1h_usd: float
        volume_1h_change_percent: float
        volume_2h_usd: float
        volume_2h_change_percent: float
        volume_4h_usd: float
        volume_4h_change_percent: float
        volume_8h_usd: float
        volume_8h_change_percent: float
        volume_24h_usd: float
        volume_24h_change_percent: float
        trade_1h_count: int
        trade_2h_count: int
        trade_4h_count: int
        trade_8h_count: int
        trade_24h_count: int
        buy_24h: int
        buy_24h_change_percent: float
        volume_buy_24h_usd: float
        volume_buy_24h_change_percent: float
        sell_24h: int
        sell_24h_change_percent: float
        volume_sell_24h_usd: float
        volume_sell_24h_change_percent: float
        unique_wallet_24h: int
        unique_wallet_24h_change_percent: float
        price: float
        price_change_1h_percent: float
        price_change_2h_percent: float
        price_change_4h_percent: float
        price_change_8h_percent: float
        price_change_24h_percent: float
        holder: int
        recent_listing_time: Optional[int]
        is_scaled_ui_token: bool
        multiplier: Optional[float]

    items: list[TokenItem]
    hasNext: bool


class RespTokenListV3Scroll(TypedDict):
    """Token list v3 scroll response.
    
    Example:
        {
            "items": [
                {
                    "address": "So11111111111111111111111111111111111111112",
                    "logo_uri": "https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/So11111111111111111111111111111111111111112/logo.png",
                    "name": "Wrapped SOL",
                    "symbol": "SOL", 
                    "decimals": 9,
                    "extensions": {
                        "coingecko_id": "solana",
                        "website": "https://solana.com/",
                        "telegram": null,
                        "twitter": "https://twitter.com/solana",
                        "description": "Wrapped Solana",
                        "discord": "https://discordapp.com/invite/pquxPsq",
                        "medium": "https://medium.com/solana-labs"
                    },
                    "market_cap": 100119664431.51688,
                    "fdv": 112672175707.38792,
                    "total_supply": 607331645.8349773,
                    "circulating_supply": 539665463.3820738,
                    "liquidity": 23353595552.52654,
                    "last_trade_unix_time": 1754885383,
                    "volume_1h_usd": 443688491.34178054,
                    "volume_1h_change_percent": -1.714504394496686,
                    "volume_2h_usd": 861291542.4427114,
                    "volume_2h_change_percent": -3.5864189799692134,
                    "volume_4h_usd": 1747234746.548523,
                    "volume_4h_change_percent": -8.826330954721023,
                    "volume_8h_usd": 3423287365.9121313,
                    "volume_8h_change_percent": 8.888103083472839,
                    "volume_24h_usd": 9530159635.659721,
                    "volume_24h_change_percent": -1.3364377681566488,
                    "trade_1h_count": 1535608,
                    "trade_2h_count": 2948829,
                    "trade_4h_count": 5684776,
                    "trade_8h_count": 11119027,
                    "trade_24h_count": 31542138,
                    "buy_24h": 13941877,
                    "buy_24h_change_percent": -2.1854401371296177,
                    "volume_buy_24h_usd": 4728527789.759392,
                    "volume_buy_24h_change_percent": -1.6920149268570155,
                    "sell_24h": 17600261,
                    "sell_24h_change_percent": -3.143992919930877,
                    "volume_sell_24h_usd": 4801631845.900329,
                    "volume_sell_24h_change_percent": -0.9837807096207587,
                    "unique_wallet_24h": 1262031,
                    "unique_wallet_24h_change_percent": -26.286938857043396,
                    "price": 185.56395800803165,
                    "price_change_1h_percent": 0.4114972388399392,
                    "price_change_2h_percent": 0.4575777911423116,
                    "price_change_4h_percent": 1.8680908355708248,
                    "price_change_8h_percent": 1.3798037663979583,
                    "price_change_24h_percent": 0.5817906810497413,
                    "holder": 3472550,
                    "recent_listing_time": null,
                    "is_scaled_ui_token": false,
                    "multiplier": null
                }
            ],
            "hasNext": true
        }
    """
    class TokenExtensions(TypedDict, total=False):
        """Token extension metadata."""
        coingecko_id: Optional[str]
        serum_v3_usdc: Optional[str]
        serum_v3_usdt: Optional[str]
        website: Optional[str]
        telegram: Optional[str]
        twitter: Optional[str]
        description: Optional[str]
        discord: Optional[str]
        medium: Optional[str]

    class TokenItem(TypedDict):
        """Token details in a token list v3 scroll response."""
        address: str
        logo_uri: str
        name: str
        symbol: str
        decimals: int
        extensions: "RespTokenListV3Scroll.TokenExtensions"
        market_cap: float
        fdv: float
        total_supply: float
        circulating_supply: float
        liquidity: float
        last_trade_unix_time: int
        volume_1h_usd: float
        volume_1h_change_percent: float
        volume_2h_usd: float
        volume_2h_change_percent: float
        volume_4h_usd: float
        volume_4h_change_percent: float
        volume_8h_usd: float
        volume_8h_change_percent: float
        volume_24h_usd: float
        volume_24h_change_percent: float
        trade_1h_count: int
        trade_2h_count: int
        trade_4h_count: int
        trade_8h_count: int
        trade_24h_count: int
        buy_24h: int
        buy_24h_change_percent: float
        volume_buy_24h_usd: float
        volume_buy_24h_change_percent: float
        sell_24h: int
        sell_24h_change_percent: float
        volume_sell_24h_usd: float
        volume_sell_24h_change_percent: float
        unique_wallet_24h: int
        unique_wallet_24h_change_percent: float
        price: float
        price_change_1h_percent: float
        price_change_2h_percent: float
        price_change_4h_percent: float
        price_change_8h_percent: float
        price_change_24h_percent: float
        holder: int
        recent_listing_time: Optional[int]
        is_scaled_ui_token: bool
        multiplier: Optional[float]

    items: list[TokenItem]
    hasNext: bool


class RespTokenOverview(TypedDict):
    """Token overview response including price, volume and trading statistics.
    
    Example:
        {
            "address": "So11111111111111111111111111111111111111112",
            "decimals": 9,
            "symbol": "SOL", 
            "name": "Wrapped SOL",
            "marketCap": 100263084724.62823,
            "fdv": 112833577331.7062,
            "extensions": {
                "coingeckoId": "solana",
                "serumV3Usdc": "9wFFyRfZBsuAha4YcuxcXLKwMxJR43S7fPfQLusDBzvT",
                "website": "https://solana.com/",
                "twitter": "https://twitter.com/solana"
            },
            "logoURI": "https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/So11111111111111111111111111111111111111112/logo.png",
            "liquidity": 23353595552.52654,
            "price": 185.82977629057913,
            "volume_24h": 9537454514.524822,
            "holder": 3472782
        }
    """
    address: str
    decimals: int
    symbol: str
    name: str
    marketCap: float
    fdv: float
    extensions: RespTokenListV3.Extensions
    logoURI: str
    liquidity: float
    lastTradeUnixTime: int
    lastTradeHumanTime: str
    price: float
    totalSupply: float
    circulatingSupply: float
    holder: int
    numberMarkets: int
    isScaledUiToken: bool
    multiplier: Optional[float]

    # Price history and changes
    history1mPrice: float
    priceChange1mPercent: float
    history5mPrice: float 
    priceChange5mPercent: float
    history30mPrice: float
    priceChange30mPercent: float
    history1hPrice: float
    priceChange1hPercent: float
    history2hPrice: float
    priceChange2hPercent: float
    history4hPrice: float
    priceChange4hPercent: float
    history6hPrice: float
    priceChange6hPercent: float
    history8hPrice: float
    priceChange8hPercent: float
    history12hPrice: float
    priceChange12hPercent: float
    history24hPrice: float
    priceChange24hPercent: float

    # Unique wallet stats
    uniqueWallet1m: int
    uniqueWalletHistory1m: int
    uniqueWallet1mChangePercent: float
    uniqueWallet5m: int
    uniqueWalletHistory5m: int
    uniqueWallet5mChangePercent: float
    uniqueWallet30m: int
    uniqueWalletHistory30m: int
    uniqueWallet30mChangePercent: float
    uniqueWallet1h: int
    uniqueWalletHistory1h: int
    uniqueWallet1hChangePercent: float
    uniqueWallet2h: int
    uniqueWalletHistory2h: int
    uniqueWallet2hChangePercent: float
    uniqueWallet4h: int
    uniqueWalletHistory4h: int
    uniqueWallet4hChangePercent: float
    uniqueWallet8h: int
    uniqueWalletHistory8h: int
    uniqueWallet8hChangePercent: float
    uniqueWallet24h: int
    uniqueWalletHistory24h: int
    uniqueWallet24hChangePercent: float

    # Trade counts
    trade1m: int
    tradeHistory1m: int
    trade1mChangePercent: float
    trade5m: int
    tradeHistory5m: int
    trade5mChangePercent: float
    trade30m: int
    tradeHistory30m: int
    trade30mChangePercent: float
    trade1h: int
    tradeHistory1h: int
    trade1hChangePercent: float
    trade2h: int
    tradeHistory2h: int
    trade2hChangePercent: float
    trade4h: int
    tradeHistory4h: int
    trade4hChangePercent: float
    trade8h: int
    tradeHistory8h: int
    trade8hChangePercent: float
    trade24h: int
    tradeHistory24h: int
    trade24hChangePercent: float

    # Buy/sell counts
    sell1m: int
    sellHistory1m: int
    sell1mChangePercent: float
    buy1m: int
    buyHistory1m: int
    buy1mChangePercent: float
    sell5m: int
    sellHistory5m: int
    sell5mChangePercent: float
    buy5m: int
    buyHistory5m: int
    buy5mChangePercent: float
    sell30m: int
    sellHistory30m: int
    sell30mChangePercent: float
    buy30m: int
    buyHistory30m: int
    buy30mChangePercent: float
    sell1h: int
    sellHistory1h: int
    sell1hChangePercent: float
    buy1h: int
    buyHistory1h: int
    buy1hChangePercent: float
    sell2h: int
    sellHistory2h: int
    sell2hChangePercent: float
    buy2h: int
    buyHistory2h: int
    buy2hChangePercent: float
    sell4h: int
    sellHistory4h: int
    sell4hChangePercent: float
    buy4h: int
    buyHistory4h: int
    buy4hChangePercent: float
    sell8h: int
    sellHistory8h: int
    sell8hChangePercent: float
    buy8h: int
    buyHistory8h: int
    buy8hChangePercent: float
    sell24h: int
    sellHistory24h: int
    sell24hChangePercent: float
    buy24h: int
    buyHistory24h: int
    buy24hChangePercent: float

    # Volume stats
    v1m: float
    v1mUSD: float
    vHistory1m: float
    vHistory1mUSD: float
    v1mChangePercent: float
    vBuy1m: float
    vBuy1mUSD: float
    vBuyHistory1m: float
    vBuyHistory1mUSD: float
    vBuy1mChangePercent: float
    vSell1m: float
    vSell1mUSD: float
    vSellHistory1m: float
    vSellHistory1mUSD: float
    vSell1mChangePercent: float
    v5m: float
    v5mUSD: float
    vHistory5m: float
    vHistory5mUSD: float
    v5mChangePercent: float
    vBuy5m: float
    vBuy5mUSD: float
    vBuyHistory5m: float
    vBuyHistory5mUSD: float
    vBuy5mChangePercent: float
    vSell5m: float
    vSell5mUSD: float
    vSellHistory5m: float
    vSellHistory5mUSD: float
    vSell5mChangePercent: float
    v30m: float
    v30mUSD: float
    vHistory30m: float
    vHistory30mUSD: float
    v30mChangePercent: float
    vBuy30m: float
    vBuy30mUSD: float
    vBuyHistory30m: float
    vBuyHistory30mUSD: float
    vBuy30mChangePercent: float
    vSell30m: float
    vSell30mUSD: float
    vSellHistory30m: float
    vSellHistory30mUSD: float
    vSell30mChangePercent: float
    v1h: float
    v1hUSD: float
    vHistory1h: float
    vHistory1hUSD: float
    v1hChangePercent: float
    vBuy1h: float
    vBuy1hUSD: float
    vBuyHistory1h: float
    vBuyHistory1hUSD: float
    vBuy1hChangePercent: float
    vSell1h: float
    vSell1hUSD: float
    vSellHistory1h: float
    vSellHistory1hUSD: float
    vSell1hChangePercent: float
    v2h: float
    v2hUSD: float
    vHistory2h: float
    vHistory2hUSD: float
    v2hChangePercent: float
    vBuy2h: float
    vBuy2hUSD: float
    vBuyHistory2h: float
    vBuyHistory2hUSD: float
    vBuy2hChangePercent: float
    vSell2h: float
    vSell2hUSD: float
    vSellHistory2h: float
    vSellHistory2hUSD: float
    vSell2hChangePercent: float
    v4h: float
    v4hUSD: float
    vHistory4h: float
    vHistory4hUSD: float
    v4hChangePercent: float
    vBuy4h: float
    vBuy4hUSD: float
    vBuyHistory4h: float
    vBuyHistory4hUSD: float
    vBuy4hChangePercent: float
    vSell4h: float
    vSell4hUSD: float
    vSellHistory4h: float
    vSellHistory4hUSD: float
    vSell4hChangePercent: float
    v8h: float
    v8hUSD: float
    vHistory8h: float
    vHistory8hUSD: float
    v8hChangePercent: float
    vBuy8h: float
    vBuy8hUSD: float
    vBuyHistory8h: float
    vBuyHistory8hUSD: float
    vBuy8hChangePercent: float
    vSell8h: float
    vSell8hUSD: float
    vSellHistory8h: float
    vSellHistory8hUSD: float
    vSell8hChangePercent: float
    v24h: float
    v24hUSD: float
    vHistory24h: float
    vHistory24hUSD: float
    v24hChangePercent: float
    vBuy24h: float
    vBuy24hUSD: float
    vBuyHistory24h: float
    vBuyHistory24hUSD: float
    vBuy24hChangePercent: float
    vSell24h: float
    vSell24hUSD: float
    vSellHistory24h: float
    vSellHistory24hUSD: float
    vSell24hChangePercent: float


class RespTokenMetadata(TypedDict):
    """Token metadata response.
    
    Example:
        {
            "address": "So11111111111111111111111111111111111111112",
            "symbol": "SOL", 
            "name": "Wrapped SOL",
            "decimals": 9,
            "extensions": {
                "coingecko_id": "solana",
                "website": "https://solana.com/",
                "twitter": "https://twitter.com/solana", 
                "discord": "https://discordapp.com/invite/pquxPsq",
                "medium": "https://medium.com/solana-labs"
            },
            "logo_uri": "https://img.fotofolio.xyz/?url=https%3A%2F%2Fraw.githubusercontent.com%2Fsolana-labs%2Ftoken-list%2Fmain%2Fassets%2Fmainnet%2FSo11111111111111111111111111111111111111112%2Flogo.png"
        }
    """
    class Extensions(TypedDict, total=False):
        """Token extension metadata."""
        coingecko_id: Optional[str]
        website: Optional[str]
        twitter: Optional[str]
        discord: Optional[str]
        medium: Optional[str]

    address: str
    symbol: str
    name: str
    decimals: int
    extensions: Extensions
    logo_uri: str


class RespTokenMarketData(TypedDict):
    """Token market data response.
    
    Example:
        {
            "address": "So11111111111111111111111111111111111111112",
            "price": 185.74132384799458,
            "liquidity": 23338480211.61425,
            "total_supply": 607187823.0928401,
            "circulating_supply": 539542621.8877238,
            "fdv": 112779870085.64606,
            "market_cap": 100215360861.8438,
            "is_scaled_ui_token": false,
            "multiplier": null
        }
    """
    address: str
    price: float
    liquidity: float
    total_supply: float
    circulating_supply: float
    fdv: float  # Fully diluted valuation
    market_cap: float
    is_scaled_ui_token: bool
    multiplier: Optional[float]


class RespTokenTradeData(TypedDict):
    """Token trade data response.
    
    Example:
        {
            "address": "So11111111111111111111111111111111111111112",
            "holder": 3498897,
            "market": 189737,
            "last_trade_unix_time": 1755058915,
            "last_trade_human_time": "2025-08-13T04:21:55",
            "price": 199.57308084999997,
            "history_1m_price": 200.0657028658876,
            "price_change_1m_percent": -0.246230117821773,
            "history_5m_price": 199.04185542048768,
            "price_change_5m_percent": 0.2668913171001369,
            "history_30m_price": 198.08683911027157,
            "price_change_30m_percent": 0.750298074523282,
            "history_1h_price": 198.6762767605752,
            "price_change_1h_percent": 0.4513896193582795,
            "history_2h_price": 194.219974488669,
            "price_change_2h_percent": 2.75620794175486,
            "history_4h_price": 191.95599557869642,
            "price_change_4h_percent": 3.968141369244581,
            "history_6h_price": 192.36297986748752,
            "price_change_6h_percent": 3.748174928190051,
            "history_8h_price": 190.83016849547622,
            "price_change_8h_percent": 4.581514769626696,
            "history_12h_price": 181.29476421508093,
            "price_change_12h_percent": 10.082098462167592,
            "history_24h_price": 175.69158133703775,
            "price_change_24h_percent": 13.592853642286466,
            "unique_wallet_1m": 10535,
            "unique_wallet_history_1m": 10512,
            "unique_wallet_1m_change_percent": 0.21879756468797565,
            "unique_wallet_5m": 30484,
            "unique_wallet_history_5m": 31329,
            "unique_wallet_5m_change_percent": -2.697181525104536,
            "unique_wallet_30m": 84841,
            "unique_wallet_history_30m": 91310,
            "unique_wallet_30m_change_percent": -7.084656664111269,
            "unique_wallet_1h": 141012,
            "unique_wallet_history_1h": 139362,
            "unique_wallet_1h_change_percent": 1.1839669350325053,
            "unique_wallet_2h": 229096,
            "unique_wallet_history_2h": 256234,
            "unique_wallet_2h_change_percent": -10.59110032236159,
            "unique_wallet_4h": 398071,
            "unique_wallet_history_4h": 319789,
            "unique_wallet_4h_change_percent": 24.47926601602932,
            "unique_wallet_8h": 616389,
            "unique_wallet_history_8h": 598174,
            "unique_wallet_8h_change_percent": 3.0451005894605916,
            "unique_wallet_24h": 1312446,
            "unique_wallet_history_24h": 1595218,
            "unique_wallet_24h_change_percent": -17.72622926772391,
            "trade_1m": 25063,
            "trade_history_1m": 25516,
            "trade_1m_change_percent": -1.7753566389716258,
            "sell_1m": 14783,
            "sell_history_1m": 14281,
            "sell_1m_change_percent": 3.5151600028009247,
            "buy_1m": 10280,
            "buy_history_1m": 11235,
            "buy_1m_change_percent": -8.500222518914107,
            "volume_1m": 28014.353663877002,
            "volume_1m_usd": 5594914.331353994,
            "volume_history_1m": 30288.275618175,
            "volume_history_1m_usd": 6053381.114696328,
            "volume_1m_change_percent": -7.507597933153688,
            "volume_buy_1m": 13316.670472043998,
            "volume_buy_1m_usd": 2659745.040809564,
            "volume_buy_history_1m": 15438.603833983001,
            "volume_buy_history_1m_usd": 3085880.865821625,
            "volume_buy_1m_change_percent": -13.74433455743107,
            "volume_sell_1m": 14697.683191833004,
            "volume_sell_1m_usd": 2935169.29054443,
            "volume_sell_history_1m": 14849.671784191998,
            "volume_sell_history_1m_usd": 2967500.248874703,
            "volume_sell_1m_change_percent": -1.0235148262387246,
            "trade_5m": 125589,
            "trade_history_5m": 133103,
            "trade_5m_change_percent": -5.64525217312908,
            "sell_5m": 72259,
            "sell_history_5m": 75307,
            "sell_5m_change_percent": -4.047432509594062,
            "buy_5m": 53330,
            "buy_history_5m": 57796,
            "buy_5m_change_percent": -7.727178351443007,
            "volume_5m": 138839.93120513,
            "volume_5m_usd": 27706918.700082216,
            "volume_history_5m": 168486.357245985,
            "volume_history_5m_usd": 33501205.892243676,
            "volume_5m_change_percent": -17.595742780272776,
            "volume_buy_5m": 71016.083050991,
            "volume_buy_5m_usd": 14172671.643556839,
            "volume_buy_history_5m": 86636.89562773002,
            "volume_buy_history_5m_usd": 17227812.75124113,
            "volume_buy_5m_change_percent": -18.030208104247027,
            "volume_sell_5m": 67823.84815413899,
            "volume_sell_5m_usd": 13534247.056525378,
            "volume_sell_history_5m": 81849.46161825501,
            "volume_sell_history_5m_usd": 16273393.141002549,
            "volume_sell_5m_change_percent": -17.13586526632432,
            "trade_30m": 742916,
            "trade_history_30m": 726567,
            "trade_30m_change_percent": 2.2501710096935317,
            "sell_30m": 429567,
            "sell_history_30m": 423206,
            "sell_30m_change_percent": 1.5030505238583574,
            "buy_30m": 313349,
            "buy_history_30m": 303361,
            "buy_30m_change_percent": 3.2924469526405833,
            "volume_30m": 999257.254695175,
            "volume_30m_usd": 198262635.32251042,
            "volume_history_30m": 1007682.2970747652,
            "volume_history_30m_usd": 200156959.86425337,
            "volume_30m_change_percent": -0.8360812136967729,
            "volume_buy_30m": 496626.18523781083,
            "volume_buy_30m_usd": 98550796.11048704,
            "volume_buy_history_30m": 479675.0794320691,
            "volume_buy_history_30m_usd": 95280522.80842383,
            "volume_buy_30m_change_percent": 3.5338725175824632,
            "volume_sell_30m": 502631.0694573641,
            "volume_sell_30m_usd": 99711839.21202336,
            "volume_sell_history_30m": 528007.2176426961,
            "volume_sell_history_30m_usd": 104876437.05582954,
            "volume_sell_30m_change_percent": -4.8060229741980764,
            "trade_1h": 1365500,
            "trade_history_1h": 1460948,
            "trade_1h_change_percent": -6.533292081579906,
            "sell_1h": 790911,
            "sell_history_1h": 833994,
            "sell_1h_change_percent": -5.165864502622321,
            "buy_1h": 574589,
            "buy_history_1h": 626954,
            "buy_1h_change_percent": -8.35228740864561,
            "volume_1h": 1869915.2789910787,
            "volume_1h_usd": 371272087.7773213,
            "volume_history_1h": 2215504.2512326725,
            "volume_history_1h_usd": 436450282.08621264,
            "volume_1h_change_percent": -15.598659855846062,
            "volume_buy_1h": 911052.9765842077,
            "volume_buy_1h_usd": 180903043.40620133,
            "volume_buy_history_1h": 1115539.1923768108,
            "volume_buy_history_1h_usd": 219688244.87947023,
            "volume_buy_1h_change_percent": -18.330706548903663,
            "volume_sell_1h": 958862.302406871,
            "volume_sell_1h_usd": 190369044.37111995,
            "volume_sell_history_1h": 1099965.058855862,
            "volume_sell_history_1h_usd": 216762037.2067424,
            "volume_sell_1h_change_percent": -12.827930788616154,
            "trade_2h": 2721996,
            "trade_history_2h": 2737323,
            "trade_2h_change_percent": -0.5599266144331524,
            "sell_2h": 1565257,
            "sell_history_2h": 1520437,
            "sell_2h_change_percent": 2.9478367074729173,
            "buy_2h": 1156739,
            "buy_history_2h": 1216886,
            "buy_2h_change_percent": -4.942698001291822,
            "volume_2h": 3881149.9454533085,
            "volume_2h_usd": 767124563.4685572,
            "volume_history_2h": 4109861.943241723,
            "volume_history_2h_usd": 795392999.4275689,
            "volume_2h_change_percent": -5.564955732016972,
            "volume_buy_2h": 1946568.1169466476,
            "volume_buy_2h_usd": 384689701.5502614,
            "volume_buy_history_2h": 2184514.4664095147,
            "volume_buy_history_2h_usd": 422774489.6633253,
            "volume_buy_2h_change_percent": -10.892413537272542,
            "volume_sell_2h": 1934581.8285066609,
            "volume_sell_2h_usd": 382434861.91829586,
            "volume_sell_history_2h": 1925347.4768322085,
            "volume_sell_history_2h_usd": 372618509.7642436,
            "volume_sell_2h_change_percent": 0.47962000550912426,
            "trade_4h": 5720496,
            "trade_history_4h": 4738200,
            "trade_4h_change_percent": 20.73141699379511,
            "sell_4h": 3227114,
            "sell_history_4h": 2598002,
            "sell_4h_change_percent": 24.215223852791492,
            "buy_4h": 2493382,
            "buy_history_4h": 2140198,
            "buy_4h_change_percent": 16.502398376225003,
            "volume_4h": 8359034.497538514,
            "volume_4h_usd": 1632746418.2793252,
            "volume_history_4h": 5827559.3867111625,
            "volume_history_4h_usd": 1117139333.4616933,
            "volume_4h_change_percent": 43.439713657830495,
            "volume_buy_4h": 4308151.652644951,
            "volume_buy_4h_usd": 841240490.7863214,
            "volume_buy_history_4h": 2923792.0279110167,
            "volume_buy_history_4h_usd": 560556194.860776,
            "volume_buy_4h_change_percent": 47.34808808282536,
            "volume_sell_4h": 4050882.844893563,
            "volume_sell_4h_usd": 791505927.4930038,
            "volume_sell_history_4h": 2903767.358800146,
            "volume_sell_history_4h_usd": 556583138.6009173,
            "volume_sell_4h_change_percent": 39.50438669327189,
            "trade_8h": 9875698,
            "trade_history_8h": 10453618,
            "trade_8h_change_percent": -5.528420877824309,
            "sell_8h": 5503762,
            "sell_history_8h": 5773818,
            "sell_8h_change_percent": -4.677251690302673,
            "buy_8h": 4371936,
            "buy_history_8h": 4679800,
            "buy_8h_change_percent": -6.578571733834779,
            "volume_8h": 13272186.797145639,
            "volume_8h_usd": 2574392837.701419,
            "volume_history_8h": 14155274.76815367,
            "volume_history_8h_usd": 2581042172.9211245,
            "volume_8h_change_percent": -6.238578801697224,
            "volume_buy_8h": 6738594.148704853,
            "volume_buy_8h_usd": 1307097533.3850877,
            "volume_buy_history_8h": 7280589.108363739,
            "volume_buy_history_8h_usd": 1327749998.8559382,
            "volume_buy_8h_change_percent": -7.444383299096738,
            "volume_sell_8h": 6533592.648440785,
            "volume_sell_8h_usd": 1267295304.3163311,
            "volume_sell_history_8h": 6874685.65978993,
            "volume_sell_history_8h_usd": 1253292174.0651865,
            "volume_sell_8h_change_percent": -4.961579746754095,
            "trade_24h": 30786907,
            "trade_history_24h": 33058246,
            "trade_24h_change_percent": -6.870718428315888,
            "sell_24h": 17145270,
            "sell_history_24h": 18482135,
            "sell_24h_change_percent": -7.233282302071703,
            "buy_24h": 13641637,
            "buy_history_24h": 14576111,
            "buy_24h_change_percent": -6.410996732942004,
            "volume_24h": 43327455.84829509,
            "volume_24h_usd": 7930210206.693316,
            "volume_history_24h": 49475082.60178679,
            "volume_history_24h_usd": 8868558906.245562,
            "volume_24h_change_percent": -12.425702859300893,
            "volume_buy_24h": 21945096.556108054,
            "volume_buy_24h_usd": 4018154448.1608233,
            "volume_buy_history_24h": 24403487.274207145,
            "volume_buy_history_24h_usd": 4374621039.616789,
            "volume_buy_24h_change_percent": -10.073932018303982,
            "volume_sell_24h": 21382359.29218704,
            "volume_sell_24h_usd": 3912055758.532493,
            "volume_sell_history_24h": 25071595.327579647,
            "volume_sell_history_24h_usd": 4493937866.628773,
            "volume_sell_24h_change_percent": -14.714803693940917,
            "is_scaled_ui_token": false,
            "multiplier": null
        }
    """
    address: str
    holder: int
    market: int
    last_trade_unix_time: int
    last_trade_human_time: str
    price: float
    history_1m_price: float
    price_change_1m_percent: float
    history_5m_price: float
    price_change_5m_percent: float
    history_30m_price: float
    price_change_30m_percent: float
    history_1h_price: float
    price_change_1h_percent: float
    history_2h_price: float
    price_change_2h_percent: float
    history_4h_price: float
    price_change_4h_percent: float
    history_6h_price: float
    price_change_6h_percent: float
    history_8h_price: float
    price_change_8h_percent: float
    history_12h_price: float
    price_change_12h_percent: float
    history_24h_price: float
    price_change_24h_percent: float
    unique_wallet_1m: int
    unique_wallet_history_1m: int
    unique_wallet_1m_change_percent: float
    unique_wallet_5m: int
    unique_wallet_history_5m: int
    unique_wallet_5m_change_percent: float
    unique_wallet_30m: int
    unique_wallet_history_30m: int
    unique_wallet_30m_change_percent: float
    unique_wallet_1h: int
    unique_wallet_history_1h: int
    unique_wallet_1h_change_percent: float
    unique_wallet_2h: int
    unique_wallet_history_2h: int
    unique_wallet_2h_change_percent: float
    unique_wallet_4h: int
    unique_wallet_history_4h: int
    unique_wallet_4h_change_percent: float
    unique_wallet_8h: int
    unique_wallet_history_8h: int
    unique_wallet_8h_change_percent: float
    unique_wallet_24h: int
    unique_wallet_history_24h: int
    unique_wallet_24h_change_percent: float
    trade_1m: int
    trade_history_1m: int
    trade_1m_change_percent: float
    sell_1m: int
    sell_history_1m: int
    sell_1m_change_percent: float
    buy_1m: int
    buy_history_1m: int
    buy_1m_change_percent: float
    volume_1m: float
    volume_1m_usd: float
    volume_history_1m: float
    volume_history_1m_usd: float
    volume_1m_change_percent: float
    volume_buy_1m: float
    volume_buy_1m_usd: float
    volume_buy_history_1m: float
    volume_buy_history_1m_usd: float
    volume_buy_1m_change_percent: float
    volume_sell_1m: float
    volume_sell_1m_usd: float
    volume_sell_history_1m: float
    volume_sell_history_1m_usd: float
    volume_sell_1m_change_percent: float
    trade_5m: int
    trade_history_5m: int
    trade_5m_change_percent: float
    sell_5m: int
    sell_history_5m: int
    sell_5m_change_percent: float
    buy_5m: int
    buy_history_5m: int
    buy_5m_change_percent: float
    volume_5m: float
    volume_5m_usd: float
    volume_history_5m: float
    volume_history_5m_usd: float
    volume_5m_change_percent: float
    volume_buy_5m: float
    volume_buy_5m_usd: float
    volume_buy_history_5m: float
    volume_buy_history_5m_usd: float
    volume_buy_5m_change_percent: float
    volume_sell_5m: float
    volume_sell_5m_usd: float
    volume_sell_history_5m: float
    volume_sell_history_5m_usd: float
    volume_sell_5m_change_percent: float
    trade_30m: int
    trade_history_30m: int
    trade_30m_change_percent: float
    sell_30m: int
    sell_history_30m: int
    sell_30m_change_percent: float
    buy_30m: int
    buy_history_30m: int
    buy_30m_change_percent: float
    volume_30m: float
    volume_30m_usd: float
    volume_history_30m: float
    volume_history_30m_usd: float
    volume_30m_change_percent: float
    volume_buy_30m: float
    volume_buy_30m_usd: float
    volume_buy_history_30m: float
    volume_buy_history_30m_usd: float
    volume_buy_30m_change_percent: float
    volume_sell_30m: float
    volume_sell_30m_usd: float
    volume_sell_history_30m: float
    volume_sell_history_30m_usd: float
    volume_sell_30m_change_percent: float
    trade_1h: int
    trade_history_1h: int
    trade_1h_change_percent: float
    sell_1h: int
    sell_history_1h: int
    sell_1h_change_percent: float
    buy_1h: int
    buy_history_1h: int
    buy_1h_change_percent: float
    volume_1h: float
    volume_1h_usd: float
    volume_history_1h: float
    volume_history_1h_usd: float
    volume_1h_change_percent: float
    volume_buy_1h: float
    volume_buy_1h_usd: float
    volume_buy_history_1h: float
    volume_buy_history_1h_usd: float
    volume_buy_1h_change_percent: float
    volume_sell_1h: float
    volume_sell_1h_usd: float
    volume_sell_history_1h: float
    volume_sell_history_1h_usd: float
    volume_sell_1h_change_percent: float
    trade_2h: int
    trade_history_2h: int
    trade_2h_change_percent: float
    sell_2h: int
    sell_history_2h: int
    sell_2h_change_percent: float
    buy_2h: int
    buy_history_2h: int
    buy_2h_change_percent: float
    volume_2h: float
    volume_2h_usd: float
    volume_history_2h: float
    volume_history_2h_usd: float
    volume_2h_change_percent: float
    volume_buy_2h: float
    volume_buy_2h_usd: float
    volume_buy_history_2h: float
    volume_buy_history_2h_usd: float
    volume_buy_2h_change_percent: float
    volume_sell_2h: float
    volume_sell_2h_usd: float
    volume_sell_history_2h: float
    volume_sell_history_2h_usd: float
    volume_sell_2h_change_percent: float
    trade_4h: int
    trade_history_4h: int
    trade_4h_change_percent: float
    sell_4h: int
    sell_history_4h: int
    sell_4h_change_percent: float
    buy_4h: int
    buy_history_4h: int
    buy_4h_change_percent: float
    volume_4h: float
    volume_4h_usd: float
    volume_history_4h: float
    volume_history_4h_usd: float
    volume_4h_change_percent: float
    volume_buy_4h: float
    volume_buy_4h_usd: float
    volume_buy_history_4h: float
    volume_buy_history_4h_usd: float
    volume_buy_4h_change_percent: float
    volume_sell_4h: float
    volume_sell_4h_usd: float
    volume_sell_history_4h: float
    volume_sell_history_4h_usd: float
    volume_sell_4h_change_percent: float
    trade_8h: int
    trade_history_8h: int
    trade_8h_change_percent: float
    sell_8h: int
    sell_history_8h: int
    sell_8h_change_percent: float
    buy_8h: int
    buy_history_8h: int
    buy_8h_change_percent: float
    volume_8h: float
    volume_8h_usd: float
    volume_history_8h: float
    volume_history_8h_usd: float
    volume_8h_change_percent: float
    volume_buy_8h: float
    volume_buy_8h_usd: float
    volume_buy_history_8h: float
    volume_buy_history_8h_usd: float
    volume_buy_8h_change_percent: float
    volume_sell_8h: float
    volume_sell_8h_usd: float
    volume_sell_history_8h: float
    volume_sell_history_8h_usd: float
    volume_sell_8h_change_percent: float
    trade_24h: int
    trade_history_24h: int
    trade_24h_change_percent: float
    sell_24h: int
    sell_history_24h: int
    sell_24h_change_percent: float
    buy_24h: int
    buy_history_24h: int
    buy_24h_change_percent: float
    volume_24h: float
    volume_24h_usd: float
    volume_history_24h: float
    volume_history_24h_usd: float
    volume_24h_change_percent: float
    volume_buy_24h: float
    volume_buy_24h_usd: float
    volume_buy_history_24h: float
    volume_buy_history_24h_usd: float
    volume_buy_24h_change_percent: float
    volume_sell_24h: float
    volume_sell_24h_usd: float
    volume_sell_history_24h: float
    volume_sell_history_24h_usd: float
    volume_sell_24h_change_percent: float
    is_scaled_ui_token: bool
    multiplier: Optional[float]


class RespNewTokenListingItem(TypedDict):
    """Newly listed token information.
    
    Example:
        {
            "address": "6Zk9e3nfXdYLXHYu5NvDiPHGMcjujVBv6gWRr7ckSdhP",
            "symbol": "TOPCAT", 
            "name": "TOPCAT",
            "decimals": 9,
            "source": "raydium",
            "liquidityAddedAt": "2024-09-18T17:59:23",
            "logoURI": null,
            "liquidity": 15507.41635596545
        }
    """
    address: str
    symbol: str
    name: str
    decimals: int
    source: str
    liquidityAddedAt: str
    logoURI: Optional[str]
    liquidity: float


class RespTokenTopTraderItem(TypedDict):
    """Top trader details for a token.
    
    Example:
        {
            "tokenAddress": "So11111111111111111111111111111111111111112",
            "owner": "MfDuWeqSHEqTFVYZ7LoexgAK9dxk7cy4DFJWjWMGVWa",
            "tags": [],
            "type": "24h",
            "volume": 1649180.8809921234,
            "trade": 195729,
            "tradeBuy": 101729,
            "tradeSell": 94000,
            "volumeBuy": 827695.1022708704,
            "volumeSell": 821485.7787212529,
            "isScaledUiToken": false,
            "multiplier": null
        }
    """
    tokenAddress: str
    owner: str
    tags: list[str]
    type: str
    volume: float
    trade: int
    tradeBuy: int
    tradeSell: int
    volumeBuy: float
    volumeSell: float
    isScaledUiToken: bool
    multiplier: Optional[float]


class RespTokenAllMarketList(TypedDict):
    """Token all market list response.
    
    Example:
        {
            "items": [
                {
                    "address": "Jito4APyf642JPZPx3hGc6WWJ8zPKtRbRs4P815Awbb",
                    "base": {
                        "address": "J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn",
                        "decimals": 9,
                        "symbol": "JitoSOL",
                        "icon": "https://img.fotofolio.xyz/?url=..."
                    },
                    "createdAt": "2024-05-28T07:19:22.813Z",
                    "liquidity": 1733225301.1348372,
                    "name": "JitoSOL-SOL",
                    "price": null,
                    "quote": {
                        "address": "So11111111111111111111111111111111111111112",
                        "decimals": 9,
                        "icon": "https://img.fotofolio.xyz/?url=...",
                        "symbol": "SOL"
                    },
                    "source": "Stake Pool",
                    "trade24h": 1021,
                    "trade24hChangePercent": 72.46621621621621,
                    "uniqueWallet24h": 382,
                    "uniqueWallet24hChangePercent": -13.769751693002258,
                    "volume24h": 7610352.270776577
                }
            ],
            "total": 1523
        }
    """
    class TokenInfo(TypedDict):
        """Token information."""
        address: str
        decimals: int
        symbol: str
        icon: str

    class MarketItem(TypedDict):
        """Market item details."""
        address: str
        base: "RespTokenAllMarketList.TokenInfo"
        createdAt: str
        liquidity: float
        name: str
        price: Optional[float]
        quote: "RespTokenAllMarketList.TokenInfo"
        source: str
        trade24h: int
        trade24hChangePercent: float
        uniqueWallet24h: int
        uniqueWallet24hChangePercent: float
        volume24h: float

    items: list[MarketItem]
    total: int


class RespTokenTrendingList(TypedDict):
    """Trending token list response.
    
    Example:
        {
            "updateUnixTime": 1726681733,
            "updateTime": "2024-09-18T17:48:53",
            "tokens": [
                {
                    "address": "HJXh1XULVe2Mdp6mTKd5K7of1uFqBTbmcWzvBv6cpump",
                    "decimals": 6,
                    "liquidity": 34641.80933146691,
                    "logoURI": "https://ipfs.io/ipfs/QmR7QnPaYcfwoG8oymK5JRDsB9GSgHr71mJmL2MuJ7Qk3x",
                    "name": "AVOCATO",
                    "symbol": "ATO", 
                    "volume24hUSD": 1202872.3148187269,
                    "volume24hChangePercent": 33,
                    "rank": 1,
                    "price": 0.00010551649518689046,
                    "price24hChangePercent": 210,
                    "fdv": 17028232129,
                    "marketcap": 28232129
                }
            ],
            "total": 1000
        }
    """
    class TrendingToken(TypedDict):
        """Individual trending token details."""
        address: str
        decimals: int
        liquidity: float
        logoURI: str
        name: str
        symbol: str
        volume24hUSD: float
        volume24hChangePercent: float
        rank: int
        price: float
        price24hChangePercent: float
        fdv: float
        marketcap: float

    updateUnixTime: int
    updateTime: str
    tokens: list[TrendingToken]
    total: int


class RespTokenSecurity(TypedDict):
    """Token security information response.
    
    Example:
        {
            "creatorAddress": "9AhKqLR67hwapvG8SA2JFXaCshXc9nALJjpKaHZrsbkw",
            "creatorOwnerAddress": null,
            "ownerAddress": null,
            "ownerOfOwnerAddress": null,
            "creationTx": "2K5X6HT9QZ8dcApbWL6mzYw6WBDvL5vWndTpGrFkQuMfuStGTP5LxPNQnnn5v5KR2T6UD1zEXnfCdajzUfuCPZgS",
            "creationTime": 1670531612,
            "creationSlot": 165714665,
            "mintTx": "44Jfxh3VFp6N2h3CLMGeHHxeexdtUnHRsvQ2QXF9h9JqHiBvjt2xCbJg7G443hPVvG4y5VP95iaiSRKuLVVcadCe",
            "mintTime": 1683780182,
            "mintSlot": 193273646,
            "creatorBalance": 48343.76164,
            "ownerBalance": null,
            "ownerPercentage": null,
            "creatorPercentage": 5.44198858929173e-10,
            "metaplexUpdateAuthority": "9AhKqLR67hwapvG8SA2JFXaCshXc9nALJjpKaHZrsbkw",
            "metaplexOwnerUpdateAuthority": null,
            "metaplexUpdateAuthorityBalance": 48343.76164,
            "metaplexUpdateAuthorityPercent": 5.44198858929173e-10,
            "mutableMetadata": true,
            "top10HolderBalance": 27020571907755.746,
            "top10HolderPercent": 0.3041667404641445,
            "top10UserBalance": 27020571907755.746,
            "top10UserPercent": 0.3041667404641445,
            "isTrueToken": null,
            "fakeToken": null,
            "totalSupply": 88834735403757.8,
            "preMarketHolder": [],
            "lockInfo": null,
            "freezeable": null,
            "freezeAuthority": null,
            "transferFeeEnable": null,
            "transferFeeData": null,
            "isToken2022": false,
            "nonTransferable": null,
            "jupStrictList": true
        }
    """
    creatorAddress: Optional[str]
    creatorOwnerAddress: Optional[str]
    ownerAddress: Optional[str]
    ownerOfOwnerAddress: Optional[str]
    creationTx: Optional[str]
    creationTime: Optional[int]
    creationSlot: Optional[int]
    mintTx: Optional[str]
    mintTime: Optional[int]
    mintSlot: Optional[int]
    creatorBalance: Optional[float]
    ownerBalance: Optional[float]
    ownerPercentage: Optional[float]
    creatorPercentage: Optional[float]
    metaplexUpdateAuthority: Optional[str]
    metaplexOwnerUpdateAuthority: Optional[str]
    metaplexUpdateAuthorityBalance: Optional[float]
    metaplexUpdateAuthorityPercent: Optional[float]
    mutableMetadata: Optional[bool]
    top10HolderBalance: Optional[float]
    top10HolderPercent: Optional[float]
    top10UserBalance: Optional[float]
    top10UserPercent: Optional[float]
    isTrueToken: Optional[bool]
    fakeToken: Optional[bool]
    totalSupply: Optional[float]
    preMarketHolder: list[Any]
    lockInfo: Optional[Any]
    freezeable: Optional[bool]
    freezeAuthority: Optional[str]
    transferFeeEnable: Optional[bool]
    transferFeeData: Optional[Any]
    isToken2022: bool
    nonTransferable: Optional[bool]
    jupStrictList: bool


class RespTokenCreationInfo(TypedDict):
    """Token creation information response.
    
    Example:
        {
            "txHash": "3cW2HpkUs5Hg2FBMa52iJoSMUf8MNkkzkRcGuBs1JEesQ1pnsvNwCbTmZfeJf8hTi9NSHh1Tqx6Rz5Wrr7ePDEps",
            "slot": 223012712,
            "tokenAddress": "D7rcV8SPxbv94s3kJETkrfMrWqHFs6qrmtbiu6saaany", 
            "decimals": 5,
            "owner": "JEFL3KwPQeughdrQAjLo9o75qh15nYbFJ2ZDrb695qsZ",
            "blockUnixTime": 1697044029,
            "blockHumanTime": "2023-10-11T17:07:09.000Z"
        }
    """
    txHash: str
    slot: int
    tokenAddress: str
    decimals: int
    owner: str
    blockUnixTime: int
    blockHumanTime: str


class RespTokenMintBurnTxItem(TypedDict):
    """Token mint/burn transaction details.
    
    Example:
        {
            "amount": "870",
            "block_human_time": "2024-11-08T07:28:18.000Z", 
            "block_time": 1731050898,
            "common_type": "burn",
            "decimals": 0,
            "mint": "fueL3hBZjLLLJHiFH9cqZoozTG3XQZ53diwFPwbzNim",
            "program_id": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
            "slot": 300145960,
            "tx_hash": "TyqmrBiZaW6bXsm6fV1owkVL2ea3PF2rbHPNZQtQrLYiZVThHEmkcD4QHKw37W43nyUdrFSdNr2xxTPZkPBY3pZ",
            "ui_amount": 870,
            "ui_amount_string": "870"
        }
    """
    amount: str
    block_human_time: str
    block_time: int
    common_type: Literal["mint", "burn"]
    decimals: int
    mint: str
    program_id: str
    slot: int
    tx_hash: str
    ui_amount: float
    ui_amount_string: str


class RespTokenAllTimeTrades(TypedDict):
    """Token all-time trade statistics response.
    
    Example:
        {
            "address": "So11111111111111111111111111111111111111112",
            "total_volume": 158766463.26959822,
            "total_volume_usd": 20188521260.405678,
            "volume_buy_usd": 20188521260.405678,
            "volume_sell_usd": 20188521260.405678,
            "volume_buy": 78227859.16098201,
            "volume_sell": 80538604.1086162,
            "total_trade": 258522892,
            "buy": 87829497,
            "sell": 170693395
        }
    """
    address: str
    total_volume: float  # Total volume in token units
    total_volume_usd: float  # Total volume in USD
    volume_buy_usd: float  # Buy volume in USD
    volume_sell_usd: float  # Sell volume in USD
    volume_buy: float  # Buy volume in token units
    volume_sell: float  # Sell volume in token units
    total_trade: int  # Total number of trades
    buy: int  # Number of buy trades
    sell: int  # Number of sell trades


class RespTokenExitLiquidity(TypedDict):
    """Token exit liquidity information.
    
    Example:
        {
            "token": "0x60a3E35Cc302bFA44Cb288Bc5a4F316Fdb1adb42",
            "exit_liquidity": 6787432.938612048,
            "liquidity": 10355070.125772206,
            "price": {
                "value": 1.1515311597782227,
                "update_unix_time": 1750385475,
                "update_human_time": "2025-06-20T02:11:15",
                "update_in_slot": 31798064
            },
            "currency": "USD", 
            "address": "0x60a3E35Cc302bFA44Cb288Bc5a4F316Fdb1adb42",
            "name": "EURC",
            "symbol": "EURC",
            "decimals": 6,
            "extensions": {
                "twitter": "https://twitter.com/circlepay",
                "website": "https://www.circle.com",
                "telegram": null
            },
            "logo_uri": "https://coin-images.coingecko.com/coins/images/26045/small/euro.png?1696525125"
        }
    """
    class Price(TypedDict):
        value: float
        update_unix_time: int
        update_human_time: str
        update_in_slot: int

    class Extensions(TypedDict):
        twitter: Optional[str]
        website: Optional[str]
        telegram: Optional[str]

    token: str
    exit_liquidity: float
    liquidity: float
    price: Price
    currency: str
    address: str
    name: str
    symbol: str
    decimals: int
    extensions: Extensions
    logo_uri: str


class RespTokenHoldersItem(TypedDict):
    """Token holder information.
    
    Example:
        {
            "amount": "4995300410087424",
            "decimals": 9,
            "mint": "So11111111111111111111111111111111111111112", 
            "owner": "AVzP2GeRmqGphJsMxWoqjpUifPpCret7LqWhD8NWQK49",
            "token_account": "BUvduFTd2sWFagCunBPLupG8fBTJqweLw9DuhruNFSCm",
            "ui_amount": 4995300.410087424,
            "is_scaled_ui_token": false,
            "multiplier": null
        }
    """
    amount: str
    decimals: int
    mint: str
    owner: str
    token_account: str
    ui_amount: float
    is_scaled_ui_token: bool
    multiplier: Optional[float]


class RespTokenHolderBatchItem(TypedDict):
    """Token holder batch response item.
    
    Example:
        {
            "balance": "2039280",
            "decimals": 9,
            "mint": "So11111111111111111111111111111111111111112", 
            "owner": "2fgUSSpZFi8PjyhbrETSeLutJpFsuCfWsk2H6gb3Reye",
            "amount": 0.00203928
        }
    """
    balance: str
    decimals: int
    mint: str
    owner: str
    amount: float
    


class RespMemeList(TypedDict):
    """Response type for meme token list.
    
    Example:
        {
            "items": [
                {
                    "address": "AYKYhju2mTQtR7MQdXwiWyEwCTTYrU3oTT4zkBtkmoon",
                    "logo_uri": "https://imagedelivery.net/...",
                    "name": "CryptoStop",
                    "symbol": "CST",
                    "decimals": 9,
                    "extensions": null,
                    "market_cap": 10029.10632246309,
                    "fdv": 10029.10632246309,
                    "liquidity": 12242.094226513347,
                    "last_trade_unix_time": 1753255897,
                    "volume_1h_usd": 235.11977278340453,
                    "volume_1h_change_percent": 52.37871950362558,
                    "volume_2h_usd": 383.10579518803587,
                    "volume_2h_change_percent": -25.737252324323144,
                    "volume_4h_usd": 931.3254995946224,
                    "volume_4h_change_percent": -49.354266487949076,
                    "volume_8h_usd": 2743.069549449229,
                    "volume_8h_change_percent": -97.26138638848936,
                    "volume_24h_usd": 102534.05700111619,
                    "volume_24h_change_percent": null,
                    "trade_1h_count": 4,
                    "trade_2h_count": 11,
                    "trade_4h_count": 16,
                    "trade_8h_count": 40,
                    "trade_24h_count": 1893,
                    "price": 0.000010058942924819541,
                    "price_change_1h_percent": 8.271165093090064,
                    "price_change_2h_percent": 2.1377057711345255,
                    "price_change_4h_percent": 1.4128562857622766,
                    "price_change_8h_percent": -34.58129190021828,
                    "price_change_24h_percent": -85.0011848107867,
                    "holder": 154,
                    "recent_listing_time": 1753043373,
                    "meme_info": {
                        "source": "moonshot",
                        "platform_id": "MoonCVVNZFSYkqNXP6bxHLPL6QQJiMagDL3qcqUQTrG",
                        "address": "AYKYhju2mTQtR7MQdXwiWyEwCTTYrU3oTT4zkBtkmoon",
                        "created_at": {
                            "tx_hash": "5FRnyAQPYnCgoF6rCdTdQUbL8E5rwdXSJFCQzQmSqjU5za5chA9oQgFSKPZmZ3KjmDW9xHs29GaQFYJx2y1HcKt2",
                            "slot": 354628160,
                            "block_time": 1753043373
                        },
                        "creation_time": 1753043373,
                        "creator": "HtsetQ2pGkUtTm48Z3F378ojyrbDiHWppMzrWckGhLmS",
                        "graduated": true,
                        "graduated_time": 1753214231,
                        "pool": {
                            "address": "5HjW2SwFU1JPRGQGghuGWHhfN26Y1wGRTUYK9fx4s11T",
                            "curve_amount": "199159017507691861",
                            "total_supply": "1000000000000000000",
                            "marketcap_threshold": "345000000000",
                            "coef_b": "25",
                            "bump": "253"
                        },
                        "progress_percent": 100,
                        "graduated_at": {
                            "block_time": 1753214231,
                            "slot": 355060079,
                            "tx_hash": "58MySb9W8vApR4UeETLrU53tdkqVSJzuV9mZ34kxUN36TFRwbYvmY3tARDX3X8mdkUdbLVRFXDDCZYGnraNGwCQ2"
                        }
                    }
                }
            ],
            "has_next": true
        }
    """
    class Extensions(TypedDict, total=False):
        """Token extension information."""
        twitter: str
        website: str
        description: str

    class CreatedAt(TypedDict):
        """Creation transaction details."""
        tx_hash: str
        slot: int
        block_time: int

    class Pool(TypedDict, total=False):
        """Pool configuration."""
        address: str
        curve_amount: str
        total_supply: str
        marketcap_threshold: str
        coef_b: str
        bump: str
        virtual_base: str
        creator: str
        base_decimals: int
        quote_mint: str
        auth_bump: int
        total_quote_fund_raising: str
        supply: str
        platform_fee: str
        quote_protocol_fee: str
        total_base_sell: str
        virtual_quote: str
        base_mint: str
        base_vault: str
        platform_config: str
        quote_decimals: int
        real_quote: str
        quote_vault: str
        real_base: str
        status: int

    class MemeInfo(TypedDict):
        """Meme token specific information."""
        source: str
        platform_id: str
        address: str
        created_at: "RespMemeList.CreatedAt"
        creation_time: int
        creator: str
        graduated: bool
        graduated_time: int
        pool: "RespMemeList.Pool"
        progress_percent: int
        graduated_at: "RespMemeList.CreatedAt"

    class MemeItem(TypedDict):
        """Individual meme token details."""
        address: str
        logo_uri: str
        name: str
        symbol: str
        decimals: int
        extensions: Optional["RespMemeList.Extensions"]
        market_cap: float
        fdv: float
        liquidity: float
        last_trade_unix_time: int
        volume_1h_usd: float
        volume_1h_change_percent: float
        volume_2h_usd: float
        volume_2h_change_percent: float
        volume_4h_usd: float
        volume_4h_change_percent: float
        volume_8h_usd: float
        volume_8h_change_percent: float
        volume_24h_usd: float
        volume_24h_change_percent: Optional[float]
        trade_1h_count: int
        trade_2h_count: int
        trade_4h_count: int
        trade_8h_count: int
        trade_24h_count: int
        price: float
        price_change_1h_percent: float
        price_change_2h_percent: float
        price_change_4h_percent: float
        price_change_8h_percent: float
        price_change_24h_percent: float
        holder: int
        recent_listing_time: int
        meme_info: "RespMemeList.MemeInfo"

    items: list["RespMemeList.MemeItem"]
    has_next: bool


class RespMemeDetail(TypedDict):
    """Response type for meme token detail.
    
    Example:
        {
            "address": "6R3LxpHiE8RjTL7HnvKWtoQCHVA76CR1ebF9MYk61wzS",
            "name": "RekaAI",
            "symbol": "RekaAI", 
            "decimals": 6,
            "extensions": {
                "twitter": "https://x.com/FusionLab_Inc",
                "website": "https://reka.ai",
                "description": "Multimodal AI you can deploy anywhere"
            },
            "logo_uri": "https://ipfs.io/ipfs/QmXuk2dXxM5hYARaxoPyoryJm5UQHdTkEhXrtsFFU7Siay",
            "price": 0.001,
            "liquidity": 0.2919295560985348,
            "circulating_supply": 1000000000,
            "market_cap": 1000000,
            "total_supply": 1000000000,
            "fdv": 1000000
        }
    """
    class Extensions(TypedDict):
        twitter: str
        website: str
        description: str

    class CreatedAt(TypedDict):
        tx_hash: str
        slot: int
        block_time: int

    class GraduatedAt(TypedDict):
        slot: Optional[int]
        tx_hash: Optional[str]
        block_time: Optional[int]

    class Pool(TypedDict):
        address: str
        real_sol_reserves: str
        real_token_reserves: str
        token_total_supply: str
        virtual_token_reserves: str

    class MemeInfo(TypedDict):
        source: str
        platform_id: str
        created_at: "RespMemeDetail.CreatedAt"
        creation_time: int
        creator: str
        updated_at: "RespMemeDetail.CreatedAt"
        graduated_at: "RespMemeDetail.GraduatedAt"
        graduated: bool
        graduated_time: Optional[int]
        pool: "RespMemeDetail.Pool"
        progress_percent: int
        address: str

    address: str
    name: str
    symbol: str
    decimals: int
    extensions: Extensions
    logo_uri: str
    price: float
    liquidity: float
    circulating_supply: int
    market_cap: int
    total_supply: int
    fdv: int
    meme_info: MemeInfo


class RespGainerLoserItem(TypedDict):
    """Response type for gainers/losers endpoints.
    
    Example:
        {
            "network": "solana",
            "address": "FciNKwZAvSzepKH1nFEGeejzbP4k87dJiP9BAzGt2Sm3",
            "pnl": 675542.1369220349,
            "trade_count": 74194,
            "volume": 1372626.717443506
        }
    """
    network: str
    address: str
    pnl: float
    trade_count: int
    volume: float


class RespWalletTrades(TypedDict):
    """Response for wallet trades endpoint.
    
    Example:
        {
            "items": [{
                "quote": {
                    "symbol": "SOL",
                    "decimals": 9,
                    "address": "So11111111111111111111111111111111111111112",
                    "amount": 8791828613200,
                    "type": "split", 
                    "type_swap": "to",
                    "ui_amount": 8791.8286132,
                    "price": 182.32478738013168,
                    "nearest_price": 182.32478738013168,
                    "change_amount": 8791828613200,
                    "ui_change_amount": 8791.8286132,
                    "is_scaled_ui_token": false,
                    "multiplier": null
                },
                "base": {...},
                "base_price": 195.07266605796318,
                "quote_price": 182.32478738013168,
                "tx_hash": "3tiVFmNkAzesSgJ8RJfRMFSMSTGMbvVd8Qm23uroSCPQFSi6rqhr9tqCCRCu4nZD8u3jLVMcuh3qxmEzFnbS61rF",
                "source": "stake_pool",
                "block_unix_time": 1754870741,
                "tx_type": "swap",
                "address": "Hr9pzexrBge3vgmBNRR8u42CNQgBXdHm4UkUN2DH4a7r",
                "owner": "GBJ4MZe8fqpA6UVgjh19BwJPMb79KDfMv78XnFVxgH2Q",
                "block_number": 359226070,
                "volume_usd": 1602968.2825842479,
                "volume": 8243.05705506,
                "ins_index": 2,
                "inner_ins_index": 0,
                "signers": ["GBJ4MZe8fqpA6UVgjh19BwJPMb79KDfMv78XnFVxgH2Q"]
            }],
            "hasNext": true
        }
    """
    class Token(TypedDict):
        """Token details in a wallet trade."""
        symbol: str
        decimals: int
        address: str
        amount: int
        type: str
        type_swap: str
        ui_amount: float
        price: float
        nearest_price: float
        change_amount: int
        ui_change_amount: float
        is_scaled_ui_token: bool
        multiplier: Optional[float]

    class Trade(TypedDict):
        """Individual wallet trade details."""
        quote: "RespWalletTrades.Token"
        base: "RespWalletTrades.Token"
        base_price: float
        quote_price: float
        tx_hash: str
        source: str
        block_unix_time: int
        tx_type: str
        address: str
        owner: str
        block_number: int
        volume_usd: float
        volume: float
        ins_index: int
        inner_ins_index: int
        signers: list[str]
        interacted_program_id: str

    items: list["RespWalletTrades.Trade"]
    hasNext: bool


class RespWalletBalanceChangesItem(TypedDict):
    """Response type for wallet balance changes endpoint.
    
    Example:
        {
            "time": "2025-08-01T08:55:58Z",
            "block_number": 357129280, 
            "block_unix_time": 1754038558,
            "address": "51dEMNojjd2hZKrMeDWBRMPmhDS5QH1eCQWCdtR7CYKp",
            "token_account": "ATgjegWTEidtsDniCfVJp5Py86fi5X8nzRyzndfimr59",
            "tx_hash": "mBxrLzapLZtcdPsKSr6EkUUXgFJDyXJs7bJcwQ58xh7JXhN7nsz9ELNspxsnG6TxVaJdzsbrkvhjgrX8QArrp4h",
            "pre_balance": "257629693",
            "post_balance": "293106471", 
            "amount": "35476777",
            "token_info": {
                "address": "4a79c1TRehFCpHxQ7niHAiBAvHRJRWey3UkWuMDREKL7",
                "decimals": 9,
                "symbol": "",
                "name": "",
                "logo_uri": "",
                "is_scaled_ui_token": true,
                "multiplier": 1.5
            },
            "type": 2,
            "type_text": "SPL",
            "change_type": 1,
            "change_type_text": "INCR"
        }
    """
    class TokenInfo(TypedDict):
        """Token information in balance change response"""
        address: str
        decimals: int
        symbol: str
        name: str
        logo_uri: str
        is_scaled_ui_token: bool
        multiplier: Optional[float]

    time: str
    block_number: int
    block_unix_time: int
    address: str
    token_account: str
    tx_hash: str
    pre_balance: str
    post_balance: str
    amount: str
    token_info: TokenInfo
    type: int
    type_text: Literal["SOL", "SPL"]
    change_type: int
    change_type_text: Literal["INCR", "DECR"]


class RespWalletPortfolioItem(TypedDict):
    """Response type for individual token in wallet portfolio.
    
    Example:
        {
            "address": "So11111111111111111111111111111111111111112",
            "decimals": 9,
            "balance": 130718,
            "uiAmount": 0.000130718,
            "chainId": "solana", 
            "name": "Wrapped SOL",
            "symbol": "SOL",
            "icon": "https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/So11111111111111111111111111111111111111112/logo.png",
            "logoURI": "https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/So11111111111111111111111111111111111111112/logo.png",
            "priceUsd": 186.35315787784225,
            "valueUsd": 0.02435971209147578,
            "isScaledUiToken": false,
            "multiplier": Optional[float]
        }
    """
    address: str
    decimals: int
    balance: int
    uiAmount: float
    chainId: str
    name: str
    symbol: str
    icon: str
    logoURI: str
    priceUsd: float
    valueUsd: float
    isScaledUiToken: bool
    multiplier: Optional[float]


class RespWalletTokenBalance(TypedDict):
    """Response type for wallet token balance.
    
    Example:
        {
            "address": "So11111111111111111111111111111111111111112",
            "decimals": 9,
            "balance": 130718,
            "uiAmount": 0.000130718,
            "chainId": "solana-mainnet", 
            "logoURI": "https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/So11111111111111111111111111111111111111112/logo.png",
            "name": "Wrapped SOL",
            "symbol": "SOL",
            "priceUsd": 186.17611361160655,
            "valueUsd": 0.024336569219081984,
            "isScaledUiToken": false,
            "multiplier": null
        }
    """
    address: str
    decimals: int
    balance: int
    uiAmount: float
    chainId: str
    logoURI: str
    name: str
    symbol: str
    priceUsd: float
    valueUsd: float
    isScaledUiToken: bool
    multiplier: Optional[float]


class RespWalletTx(TypedDict):
    """Response type for wallet transaction details.
    
    Example:
        {
            "txHash": "3MvG4bVz7HF76hWSGeGtcSkVAtDnLA5PmUVC97S22GPpGGvxbv7UqKEh91MVsAHJ35zSw4RkW9NBiHLfZbJm8xFn",
            "blockNumber": 328889251,
            "blockTime": "2025-03-24T15:06:14+00:00", 
            "status": true,
            "from": "Gt4RRcMg2mzEN9SDtSUjEjezC9b1nXjEGDQyEVbrc7Sk",
            "to": "11111111111111111111111111111111",
            "fee": 80000,
            "mainAction": "send",
            "balanceChange": [...],
            "contractLabel": {...},
            "tokenTransfers": [...]
        }
    """
    class BalanceChange(TypedDict):
        """Token balance change details."""
        amount: int
        symbol: str
        name: str
        decimals: int
        address: str
        logoURI: str
        isScaledUiToken: bool
        multiplier: Optional[float]
        
    class ContractLabel(TypedDict):
        """Contract label information."""
        class Metadata(TypedDict):
            """Contract metadata."""
            icon: str
            
        address: str
        name: str
        metadata: "RespWalletTx.ContractLabel.Metadata"
        
    class TokenTransfer(TypedDict):
        """Token transfer details."""
        fromTokenAccount: str
        toTokenAccount: str
        fromUserAccount: str
        toUserAccount: str
        tokenAmount: float
        mint: str
        transferNative: bool
        isScaledUiToken: bool
        multiplier: Optional[float]
        
    txHash: str
    blockNumber: int
    blockTime: str
    status: bool
    from_: str # alias for from
    to: str
    fee: int
    mainAction: str
    balanceChange: list["RespWalletTx.BalanceChange"]
    contractLabel: "RespWalletTx.ContractLabel"
    tokenTransfers: list["RespWalletTx.TokenTransfer"]


class RespWalletNetWorth(TypedDict):
    """Response type for wallet net worth endpoint.
    
    Example:
        {
            "wallet_address": "8X35rQUK2u9hfn8rMPwwr6ZSEUhbmfDPEapp589XyoM1",
            "currency": "usd",
            "total_value": "0.010349446772590722",
            "current_timestamp": "2025-05-19T04:47:19.414327725Z",
            "items": [...],
            "pagination": {
                "limit": 100,
                "offset": 0,
                "total": 1
            }
        }
    """
    class Item(TypedDict):
        """Token details in wallet net worth response.
        
        Example:
            {
                "address": "cCpv5Z3nqKbKohYqgY7rxFebjMjvU7SBhwgYbCipump",
                "decimals": 6,
                "price": 0.00014999198221145974,
                "balance": "69000000",
                "amount": 69,
                "network": "solana", 
                "name": "Smellow",
                "symbol": "SMLO",
                "logo_uri": "https://pump.mypinata.cloud/ipfs/QmcCjKS4MMeji11PqnNhqDSXd6gD4iGj1nC6zjyfaekuQZ",
                "value": "0.010349446772590722"
            }
        """
        address: str
        decimals: int
        price: float
        balance: str
        amount: float
        network: str
        name: str
        symbol: str
        logo_uri: str
        value: str

    class Pagination(TypedDict):
        """Pagination details in wallet net worth response.
        
        Example:
            {
                "limit": 100,
                "offset": 0,
                "total": 1
            }
        """
        limit: int
        offset: int
        total: int

    wallet_address: str
    currency: str
    total_value: str
    current_timestamp: str
    items: list["RespWalletNetWorth.Item"]
    # pagination is included in response, not in data
    # add pagination to data in _request
    pagination: "RespWalletNetWorth.Pagination"


class RespWalletNetWorthHistories(TypedDict):
    """Response type for wallet net worth history.
    
    Example:
        {
            "wallet_address": "HV1KXxWFaSeriyFvXyx48FqG9BoFbfinB8njCJonqP7K",
            "currency": "usd",
            "current_timestamp": "2025-07-31T23:59:59Z", 
            "past_timestamp": "2025-07-01T23:59:59Z",
            "history": [
                {
                    "timestamp": "2025-07-30T23:59:59Z",
                    "net_worth": 13210463.21,
                    "net_worth_change": 1971274.94,
                    "net_worth_change_percent": 17.54
                }
            ]
        }
    """
    class HistoryItem(TypedDict):
        """Individual net worth history data point."""
        timestamp: str
        net_worth: float
        net_worth_change: float
        net_worth_change_percent: float
        
    wallet_address: str
    currency: str
    current_timestamp: str
    past_timestamp: str
    history: list["RespWalletNetWorthHistories.HistoryItem"]


class RespWalletNetWorthDetails(TypedDict):
    """Response type for wallet net worth details.
    
    Example:
        {
            "wallet_address": "HV1KXxWFaSeriyFvXyx48FqG9BoFbfinB8njCJonqP7K",
            "currency": "usd", 
            "net_worth": 11839478.53162622,
            "requested_timestamp": "2025-07-31T04:50:06.303258803Z",
            "resolved_timestamp": "2025-07-31T04:50:06.475623209Z",
            "net_assets": [{
                "symbol": "Salute",
                "token_address": "49aR46Zgvh3w7cLnM3nZRC4DSVV2A25tYV1fVxYbjtb4", 
                "decimal": 4,
                "balance": "50000000000",
                "price": 1.931249899999106,
                "value": 9656249.49999553
            }]
        }
    """
    class NetAsset(TypedDict):
        """Details of an individual asset in the wallet."""
        symbol: str
        token_address: str
        decimal: int
        balance: str
        price: float
        value: float

    wallet_address: str
    currency: str
    net_worth: float
    requested_timestamp: str
    resolved_timestamp: str
    net_assets: list["RespWalletNetWorthDetails.NetAsset"]


class RespWalletTokensPnl(TypedDict):
    """Response type for wallet tokens PnL endpoint.
    
    Example:
        {
            "meta": {
                "address": "4mwReoK1x668B6KuuSAbGm2tUQULSTHGgTpCa2jUMXtD",
                "currency": "usd",
                "holding_check": false,
                "time": "2025-08-27T14:06:48.987054346Z"
            },
            "tokens": {
                "So11111111111111111111111111111111111111112": {
                    "symbol": "SOL",
                    "decimals": 9,
                    "counts": {
                        "total_buy": 236570,
                        "total_sell": 236570,
                        "total_trade": 473140
                    },
                    "quantity": {
                        "total_bought_amount": 12092390.76837637,
                        "total_sold_amount": 0.00047313999999776897,
                        "holding": 0
                    },
                    "cashflow_usd": {
                        "cost_of_quantity_sold": 0.07608073802599198,
                        "total_invested": 1944451989.1810136,
                        "total_sold": 0.07602689546632857,
                        "current_value": 0
                    },
                    "pnl": {
                        "realized_profit_usd": -0.00005384255966340998,
                        "realized_profit_percent": -0.0707702909572399,
                        "unrealized_usd": 523529777.302561,
                        "unrealized_percent": 26.92428407777512,
                        "total_usd": 523529777.30250716,
                        "total_percent": 26.92428407671888,
                        "avg_profit_per_trade_usd": -2.275967352724774e-10
                    },
                    "pricing": {
                        "current_price": 204.09378209627866,
                        "avg_buy_cost": 160.79963229984938,
                        "avg_sell_cost": 160.6858339322126
                    }
                }
            }
        }
    """
    class Meta(TypedDict):
        """Metadata about the PnL request."""
        address: str
        currency: str
        holding_check: bool
        time: str

    class TokenCounts(TypedDict):
        """Trade count statistics."""
        total_buy: int
        total_sell: int
        total_trade: int

    class TokenQuantity(TypedDict):
        """Token quantity statistics."""
        total_bought_amount: float
        total_sold_amount: float
        holding: float

    class TokenCashflow(TypedDict):
        """USD cashflow statistics."""
        cost_of_quantity_sold: float
        total_invested: float
        total_sold: float
        current_value: float

    class TokenPnL(TypedDict):
        """Profit/loss metrics."""
        realized_profit_usd: float
        realized_profit_percent: float
        unrealized_usd: float
        unrealized_percent: float
        total_usd: float
        total_percent: float
        avg_profit_per_trade_usd: float

    class TokenPricing(TypedDict):
        """Token pricing data."""
        current_price: float
        avg_buy_cost: float
        avg_sell_cost: float

    class TokenStats(TypedDict):
        """Per-token statistics."""
        symbol: str
        decimals: int
        counts: "RespWalletTokensPnl.TokenCounts"
        quantity: "RespWalletTokensPnl.TokenQuantity"
        cashflow_usd: "RespWalletTokensPnl.TokenCashflow"
        pnl: "RespWalletTokensPnl.TokenPnL"
        pricing: "RespWalletTokensPnl.TokenPricing"

    meta: Meta
    tokens: dict[str, TokenStats]


class RespWalletsPnlByToken(TypedDict):
    """Response type for wallet PnL by token endpoint.
    
    Example:
        {
            "token_metadata": {
                "symbol": "PUMP",
                "decimals": 9
            },
            "data": {
                "3aLF8VXyUbEPSFyqSoQrsq6TdgKXgLmwJprE2yTfdNA2": {
                    "counts": {
                        "total_buy": 3,
                        "total_sell": 0,
                        "total_trade": 3
                    },
                    "quantity": {
                        "total_bought_amount": 29285.756489887,
                        "total_sold_amount": 0,
                        "holding": 880839335.5814558
                    },
                    "cashflow_usd": {
                        "cost_of_quantity_sold": 0,
                        "total_invested": 2.6329984012898864,
                        "total_sold": 0,
                        "current_value": 7.5417466875590655
                    },
                    "pnl": {
                        "realized_profit_usd": 0,
                        "realized_profit_percent": 0,
                        "unrealized_usd": -2.6327476566329686,
                        "unrealized_percent": -99.99047683975823,
                        "total_usd": -2.6327476566329686,
                        "total_percent": -99.99047683975824,
                        "avg_profit_per_trade_usd": 0
                    },
                    "pricing": {
                        "current_price": 8.562000336395786e-9,
                        "avg_buy_cost": 0.00008990713291627338,
                        "avg_sell_cost": null
                    }
                }
            }
        }
    """
    class TokenMetadata(TypedDict):
        """Token metadata information."""
        symbol: str
        decimals: int
        
    class WalletPnlData(TypedDict):
        """PnL data for a single wallet."""
        class Counts(TypedDict):
            """Trade count statistics."""
            total_buy: int
            total_sell: int
            total_trade: int
            
        class Quantity(TypedDict):
            """Token quantity statistics."""
            total_bought_amount: float
            total_sold_amount: float
            holding: float
            
        class CashflowUsd(TypedDict):
            """USD cashflow statistics."""
            cost_of_quantity_sold: float
            total_invested: float
            total_sold: float
            current_value: float
            
        class Pnl(TypedDict):
            """Profit/loss metrics."""
            realized_profit_usd: float
            realized_profit_percent: float
            unrealized_usd: float
            unrealized_percent: float
            total_usd: float
            total_percent: float
            avg_profit_per_trade_usd: float
            
        class Pricing(TypedDict):
            """Token pricing information."""
            current_price: float
            avg_buy_cost: float
            avg_sell_cost: Optional[float]
            
        counts: Counts
        quantity: Quantity
        cashflow_usd: CashflowUsd
        pnl: Pnl
        pricing: Pricing
        
    token_metadata: TokenMetadata
    data: dict[str, WalletPnlData]


class RespWalletTokensBalanceItem(TypedDict):
    """Response type for wallet token balances.
    
    Example:
        {
            "address": "8i42ZVsjEGVhZ6spj4Z5aB36Msh9Vq4nnBaw5kq4pump",
            "decimals": 9,
            "price": 0.0020303701828560256,
            "balance": "4998929789571623824",
            "amount": 4998929789.571624,
            "network": "solana", 
            "name": "BIGIFTRUE",
            "symbol": "BIGIFTRUE",
            "logo_uri": "https://ipfs.io/ipfs/bafkreihgbhs4sumfhvdcquud7mvggjjbidfuoisytxqnpafrx6ukrh4hlm",
            "value": "10149677.99093697"
        }
    """
    address: str
    decimals: int
    price: float
    balance: str
    amount: float
    network: str
    name: str
    symbol: str
    logo_uri: str
    value: str


class RespWalletTokenFirstTx(TypedDict):
    """Response type for first token transaction in a wallet.
    
    Example:
        {
            "tx_hash": "8g5kPkNNhbxozv7veVjwHqCdJ6FB4B3zMaXBfHigZKwPprNB3A3WcVBCdEm1rfuG1m3syHEVZHeYfCZfM7BgQ6s",
            "block_unix_time": 1717292678,
            "block_number": 269344897,
            "balance_change": "7182720",
            "token_address": "So11111111111111111111111111111111111111111",
            "token_decimals": 9
        }
    """
    tx_hash: str
    block_unix_time: int
    block_number: int
    balance_change: str
    token_address: str
    token_decimals: int


class RespSearchItem(TypedDict):
    """Search result containing token and market results.
    
    Example:
        {
            "type": "token",
            "result": [
                {
                    "name": "TRENDSDOTFUN",
                    "symbol": "",
                    "address": "CdsF47CkMGnXnMuGNPw9TpCbE6hxRvA4XUbxbZcLrfJ8",
                    "network": "solana",
                    "decimals": 6,
                    "verified": false,
                    "fdv": 13697.614698138917,
                    "market_cap": 13697.614698138917,
                    "liquidity": 60054.03786109897,
                    "price": 0.000013697614670743687,
                    "price_change_24h_percent": 333.97707074856015,
                    "sell_24h": 4088,
                    "sell_24h_change_percent": null,
                    "buy_24h": 4374,
                    "buy_24h_change_percent": null,
                    "unique_wallet_24h": 203,
                    "unique_wallet_24h_change_percent": null,
                    "trade_24h": 8462,
                    "trade_24h_change_percent": null,
                    "volume_24h_change_percent": null,
                    "volume_24h_usd": 1867782.2902830783,
                    "last_trade_unix_time": 1749490559,
                    "last_trade_human_time": "2025-06-09T17:35:59",
                    "updated_time": 1749491343,
                    "creation_time": "2025-06-09T17:13:02.490Z",
                    "is_scaled_ui_token": false,
                    "multiplier": null
                }
            ]
        }
    """
    class TokenResult(TypedDict):
        """Token search result information."""
        name: str
        symbol: str
        address: str
        network: str
        decimals: int
        verified: bool
        fdv: float
        market_cap: float
        liquidity: float
        price: float
        price_change_24h_percent: float
        sell_24h: int
        sell_24h_change_percent: Optional[float]
        buy_24h: int
        buy_24h_change_percent: Optional[float]
        unique_wallet_24h: int
        unique_wallet_24h_change_percent: Optional[float]
        trade_24h: int
        trade_24h_change_percent: Optional[float]
        volume_24h_change_percent: Optional[float]
        volume_24h_usd: float
        last_trade_unix_time: int
        last_trade_human_time: str
        updated_time: int
        creation_time: str
        is_scaled_ui_token: bool
        multiplier: Optional[float]

    type: Literal["token", "market"]
    result: list[TokenResult]


# ============================================================================
# Type Aliases
# ============================================================================

RespSupportedNetworks = list[Chain]
RespWalletSupportedNetworks = list[Chain]
RespTokensPrice = dict[str, RespTokenPrice]
RespPairOHLCVs = list[RespPairOHLCVItem]
RespPairOHLCVsV3 = list[RespPairOHLCVItemV3]
RespTokensPriceVolume = dict[str, RespTokenPriceVolume]
RespPairsOverview = dict[str, RespPairOverview]
RespTokensPriceStats = list[RespTokenPriceStats]
RespTokensMetadata = list[RespTokenMetadata]
RespTokensMarketData = dict[str, RespTokenMarketData]
RespTokensTradeData = dict[str, RespTokenTradeData]
RespTokenNewListing = list[RespNewTokenListingItem]
RespTokenTopTraders = list[RespTokenTopTraderItem]
RespTokenMintBurnTxs = list[RespTokenMintBurnTxItem]
RespTokensAllTimeTrades = list[RespTokenAllTimeTrades]
RespTokensExitLiquidity = list[RespTokenExitLiquidity]
RespTokenHolders = list[RespTokenHoldersItem]
RespTokenHolderBatch = list[RespTokenHolderBatchItem]
RespGainerLosers = list[RespGainerLoserItem]
RespWalletBalanceChanges = list[RespWalletBalanceChangesItem]
RespWalletPortfolio = list[RespWalletPortfolioItem]
RespWalletTxs = dict[Chain, list[RespWalletTx]]
RespWalletTokensBalances = list[RespWalletTokensBalanceItem]
RespWalletsTokenFirstTx = dict[str, RespWalletTokenFirstTx]
RespSearchItems = list[RespSearchItem]
RespLatestBlockNumber = int
