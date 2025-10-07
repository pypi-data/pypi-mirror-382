"""Type stubs for http_client module."""

from typing import Any, Literal, Optional

from birdeye.ratelimiter import RateLimitBehavior, RateLimiter, MultiRateLimiter
from birdeye.http_resp import *  # Import all response types
from birdeye.consts import Chain
from birdeye.http_client import PUBLIC_API_BASE_URL


class HTTPClient:
    """Birdeye API client with automatic rate limiting."""
    
    api_key: str
    base_url: str
    limiter_150_rps: RateLimiter
    limiter_100_rps: RateLimiter
    limiter_wallet: MultiRateLimiter
    limiter_2_rps: RateLimiter
    endpoint_limiters: dict[str, Any]
    
    def __init__(
        self,
        *,
        api_key: str,
        chains: Optional[list[Chain]] = None,
        base_url: str = PUBLIC_API_BASE_URL,
        on_rate_limit_exceeded: RateLimitBehavior = ...
    ) -> None: ...
    
    # Network endpoints
    async def get_supported_networks(
        self,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespSupportedNetworks: ...
    
    async def get_wallet_supported_networks(
        self,
        *,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletSupportedNetworks: ...
    
    # Price endpoints
    async def get_token_price(
        self,
        address: str,
        *,
        check_liquidity: Optional[int] = 100,
        include_liquidity: Optional[bool] = True,
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenPrice: ...
    
    async def get_tokens_price(
        self,
        list_address: list[str],
        *,
        check_liquidity: Optional[int] = 100,
        include_liquidity: Optional[bool] = True,
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokensPrice: ...
    
    # Transaction endpoints
    async def get_token_txs(
        self,
        address: str,
        *,
        offset: Optional[int] = 0,
        limit: Optional[int] = 50,
        tx_type: Literal["swap", "add", "remove", "all"] = "swap",
        sort_type: Literal["desc", "asc"] = "desc",
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenTxs: ...
    
    async def get_pair_txs(
        self,
        address: str,
        *,
        offset: Optional[int] = 0,
        limit: Optional[int] = 50,
        tx_type: Literal["swap", "add", "remove", "all"] = "swap",
        sort_type: Literal["desc", "asc"] = "desc",
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespPairTxs: ...
    
    async def get_token_txs_by_time(
        self,
        address: str,
        *,
        before_time: Optional[int] = None,
        after_time: Optional[int] = None,
        tx_type: Literal["swap", "add", "remove", "all"] = "swap",
        sort_type: Literal["desc", "asc"] = "desc",
        limit: Optional[int] = 50,
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenTxsByTime: ...
    
    async def get_pair_txs_by_time(
        self,
        address: str,
        *,
        before_time: Optional[int] = None,
        after_time: Optional[int] = None,
        tx_type: Literal["swap", "add", "remove", "all"] = "swap",
        sort_type: Literal["desc", "asc"] = "desc",
        limit: Optional[int] = 50,
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespPairTxsByTime: ...
    
    async def get_all_txs(
        self,
        *,
        before_time: Optional[int] = None,
        after_time: Optional[int] = None,
        tx_type: Literal["swap", "add", "remove", "all"] = "swap",
        sort_type: Literal["desc", "asc"] = "desc",
        limit: Optional[int] = 50,
        pairAddress: Optional[str] = None,
        tokenAddress: Optional[str] = None,
        walletAddress: Optional[str] = None,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespAllTxsV3: ...
    
    async def get_token_txs_v3(
        self,
        address: str,
        *,
        tx_type: Literal["swap", "add_liquidity", "remove_liquidity", "burn", "mint"] = "swap",
        before_time: Optional[int] = None,
        after_time: Optional[int] = None,
        sort_type: Literal["desc", "asc"] = "desc",
        limit: Optional[int] = 50,
        offset: Optional[int] = 0,
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenTxsV3: ...
    
    async def get_recent_txs(
        self,
        *,
        tx_type: Literal["swap", "add_liquidity", "remove_liquidity", "burn", "mint"] = "swap",
        sort_type: Literal["desc", "asc"] = "desc",
        sort_by: Literal["blockUnixTime", "volume"] = "blockUnixTime",
        limit: Optional[int] = 50,
        offset: Optional[int] = 0,
        pairAddress: Optional[str] = None,
        tokenAddress: Optional[str] = None,
        walletAddress: Optional[str] = None,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespRecentTxsV3: ...
    
    # OHLCV endpoints
    async def get_token_ohlcv(
        self,
        address: str,
        *,
        time_from: int,
        time_to: int,
        type: Literal["1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "8H", "12H", "1D", "3D", "1W", "1M"],
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenOHLCVs: ...
    
    async def get_pair_ohlcv(
        self,
        address: str,
        *,
        time_from: int,
        time_to: int,
        type: Literal["1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "8H", "12H", "1D", "3D", "1W", "1M"],
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespPairOHLCVs: ...
    
    async def get_ohlcv_by_base_quote(
        self,
        *,
        base_address: str,
        quote_address: str,
        time_from: int,
        time_to: int,
        type: Literal["1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "8H", "12H", "1D", "3D", "1W", "1M"],
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespOHLCVBaseQuote: ...
    
    async def get_token_ohlcv_v3(
        self,
        address: str,
        *,
        time_from: int,
        time_to: int,
        type: Literal["1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "8H", "12H", "1D", "3D", "1W", "1M"],
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenOHLCVsV3: ...
    
    async def get_pair_ohlcv_v3(
        self,
        address: str,
        *,
        time_from: int,
        time_to: int,
        type: Literal["1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "8H", "12H", "1D", "3D", "1W", "1M"],
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespPairOHLCVsV3: ...
    
    # Historical price endpoints
    async def get_token_price_histories(
        self,
        address: str,
        *,
        address_type: Literal["token", "pair"] = "token",
        type: Literal["1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "8H", "12H", "1D", "3D", "1W", "1M"],
        time_from: int,
        time_to: int,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenPriceHistories: ...
    
    async def get_token_price_history_by_time(
        self,
        address: str,
        *,
        unixtime: int,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenPriceHistoryByTime: ...
    
    # Price volume endpoints
    async def get_token_price_volume(
        self,
        address: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenPriceVolume: ...
    
    async def get_tokens_price_volume(
        self,
        list_address: list[str],
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokensPriceVolume: ...
    
    # Pair overview endpoints
    async def get_pair_overview(
        self,
        address: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespPairOverview: ...
    
    async def get_pairs_overview(
        self,
        list_address: list[str],
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespPairsOverview: ...
    
    # Token stats endpoints
    async def get_token_price_stats(
        self,
        address: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenPriceStats: ...
    
    async def get_tokens_price_stats(
        self,
        list_address: list[str],
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokensPriceStats: ...
    
    # Token list endpoints
    async def get_token_list_v1(
        self,
        *,
        sort_by: Optional[Literal["v24hUSD", "v24hChangePercent", "liquidity", "lastTradeUnixTime", "holder", "marketCap"]] = "v24hUSD",
        sort_type: Optional[Literal["asc", "desc"]] = "desc",
        offset: Optional[int] = 0,
        limit: Optional[int] = 50,
        min_liquidity: Optional[float] = None,
        max_liquidity: Optional[float] = None,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenListV1: ...
    
    async def get_token_list_v3(
        self,
        *,
        sort_by: Optional[str] = "v24hUSD",
        sort_type: Optional[Literal["asc", "desc"]] = "desc",
        offset: Optional[int] = 0,
        limit: Optional[int] = 50,
        verify_token: Optional[bool] = None,
        min_liquidity: Optional[float] = None,
        max_liquidity: Optional[float] = None,
        min_mc: Optional[float] = None,
        max_mc: Optional[float] = None,
        min_24h_volume: Optional[float] = None,
        max_24h_volume: Optional[float] = None,
        min_24h_change: Optional[float] = None,
        max_24h_change: Optional[float] = None,
        min_holder: Optional[int] = None,
        max_holder: Optional[int] = None,
        min_created_time: Optional[int] = None,
        max_created_time: Optional[int] = None,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenListV3: ...
    
    async def get_token_list_v3_scroll(
        self,
        *,
        sort_by: Optional[str] = "v24hUSD",
        sort_type: Optional[Literal["asc", "desc"]] = "desc",
        verify_token: Optional[bool] = None,
        min_liquidity: Optional[float] = None,
        max_liquidity: Optional[float] = None,
        min_mc: Optional[float] = None,
        max_mc: Optional[float] = None,
        min_24h_volume: Optional[float] = None,
        max_24h_volume: Optional[float] = None,
        min_24h_change: Optional[float] = None,
        max_24h_change: Optional[float] = None,
        min_holder: Optional[int] = None,
        max_holder: Optional[int] = None,
        min_created_time: Optional[int] = None,
        max_created_time: Optional[int] = None,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenListV3Scroll: ...
    
    # Token metadata endpoints
    async def get_token_overview(
        self,
        address: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenOverview: ...
    
    async def get_token_metadata(
        self,
        address: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenMetadata: ...
    
    async def get_tokens_metadata(
        self,
        list_address: list[str],
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokensMetadata: ...
    
    async def get_token_market_data(
        self,
        address: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenMarketData: ...
    
    async def get_tokens_market_data(
        self,
        list_address: list[str],
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokensMarketData: ...
    
    async def get_token_trade_data(
        self,
        address: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenTradeData: ...
    
    async def get_tokens_trade_data(
        self,
        list_address: list[str],
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokensTradeData: ...
    
    # Token discovery endpoints
    async def get_new_listing(
        self,
        *,
        sort_by: Optional[Literal["v24hUSD", "v24hChangePercent", "liquidity", "lastTradeUnixTime", "holder", "marketCap"]] = "v24hUSD",
        sort_type: Optional[Literal["asc", "desc"]] = "desc",
        offset: Optional[int] = 0,
        limit: Optional[int] = 50,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenNewListing: ...
    
    async def get_token_top_traders(
        self,
        address: str,
        *,
        sort_by: Optional[Literal["pnl", "profitUSD", "lossUSD", "totalUSD", "winRate", "duration"]] = "totalUSD",
        sort_type: Optional[Literal["asc", "desc"]] = "desc",
        offset: Optional[int] = 0,
        limit: Optional[int] = 50,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenTopTraders: ...
    
    async def get_token_all_market_list(
        self,
        address: str,
        *,
        sort_by: Optional[Literal["liquidity", "volume_24h", "price_change_24h_percent"]] = "volume_24h",
        sort_type: Optional[Literal["asc", "desc"]] = "desc",
        offset: Optional[int] = 0,
        limit: Optional[int] = 10,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenAllMarketList: ...
    
    async def get_token_trending_list(
        self,
        *,
        sort_by: Optional[Literal["volume", "volume_change_percent", "trade", "trade_change_percent", "unique_wallet_24h", "unique_wallet_24h_change_percent"]] = "unique_wallet_24h",
        sort_type: Optional[Literal["asc", "desc"]] = "desc",
        offset: Optional[int] = 0,
        limit: Optional[int] = 10,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenTrendingList: ...
    
    async def get_token_security(
        self,
        address: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenSecurity: ...
    
    async def get_token_creation_info(
        self,
        address: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenCreationInfo: ...
    
    async def get_token_mint_burn_txs(
        self,
        address: str,
        *,
        offset: Optional[int] = 0,
        limit: Optional[int] = 50,
        sort_type: Optional[Literal["asc", "desc"]] = "desc",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenMintBurnTxs: ...
    
    async def get_token_all_time_trades(
        self,
        address: str,
        *,
        time_from: Optional[int] = None,
        time_to: Optional[int] = None,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenAllTimeTrades: ...
    
    async def get_tokens_all_time_trades(
        self,
        list_address: list[str],
        *,
        time_from: Optional[int] = None,
        time_to: Optional[int] = None,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokensAllTimeTrades: ...
    
    async def get_token_exit_liquidity(
        self,
        address: str,
        *,
        time_from: Optional[int] = None,
        time_to: Optional[int] = None,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenExitLiquidity: ...
    
    async def get_tokens_exit_liquidity(
        self,
        list_address: list[str],
        *,
        time_from: Optional[int] = None,
        time_to: Optional[int] = None,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokensExitLiquidity: ...
    
    # Token holder endpoints
    async def get_token_holders(
        self,
        address: str,
        *,
        offset: Optional[int] = 0,
        limit: Optional[int] = 10,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenHolders: ...
    
    async def get_token_holder_batch(
        self,
        addresses: list[str],
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenHolderBatch: ...
    
    # Meme endpoints
    async def get_meme_list(
        self,
        *,
        sort_by: Optional[str] = "last_trade_unix_time",
        sort_type: Optional[Literal["asc", "desc"]] = "desc",
        time_to: Optional[int] = None,
        time_from: Optional[int] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = 50,
        min_last_trade_unix_time: Optional[int] = None,
        max_last_trade_unix_time: Optional[int] = None,
        min_open_timestamp: Optional[int] = None,
        max_open_timestamp: Optional[int] = None,
        min_reply_count: Optional[int] = None,
        max_reply_count: Optional[int] = None,
        min_holder: Optional[int] = None,
        max_holder: Optional[int] = None,
        min_unique_wallet_24h: Optional[int] = None,
        max_unique_wallet_24h: Optional[int] = None,
        min_decimals: Optional[int] = None,
        max_decimals: Optional[int] = None,
        min_circulating_supply: Optional[float] = None,
        max_circulating_supply: Optional[float] = None,
        min_liquidity: Optional[float] = None,
        max_liquidity: Optional[float] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_mc: Optional[float] = None,
        max_mc: Optional[float] = None,
        min_real_mc: Optional[float] = None,
        max_real_mc: Optional[float] = None,
        min_v24h_usd: Optional[float] = None,
        max_v24h_usd: Optional[float] = None,
        min_v24h_change_percent: Optional[float] = None,
        max_v24h_change_percent: Optional[float] = None,
        min_progress_percent: Optional[float] = None,
        max_progress_percent: Optional[float] = None,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespMemeList: ...
    
    async def get_meme_detail(
        self,
        address: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespMemeDetail: ...
    
    # Trader endpoints
    async def get_gainers_losers(
        self,
        *,
        type: Literal["gainers", "losers"] = "gainers",
        time_type: Literal["24h", "7d", "30d"] = "24h",
        sort_by: Optional[Literal["total_profit_usd", "total_profit_percentage", "total_invest_usd", "total_invest_count"]] = "total_profit_usd",
        sort_type: Optional[Literal["asc", "desc"]] = "desc",
        offset: Optional[int] = 0,
        limit: Optional[int] = 50,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespGainerLosers: ...
    
    async def get_wallet_trades(
        self,
        wallet: str,
        *,
        token_address: Optional[str] = None,
        before_time: Optional[int] = None,
        after_time: Optional[int] = None,
        limit: Optional[int] = 50,
        offset: Optional[int] = 0,
        tx_type: Optional[Literal["buy", "sell"]] = None,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletTrades: ...
    
    async def get_wallet_balance_changes(
        self,
        wallet: str,
        *,
        token_address: Optional[str] = None,
        before_time: Optional[int] = None,
        after_time: Optional[int] = None,
        limit: Optional[int] = 50,
        offset: Optional[int] = 0,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletBalanceChanges: ...
    
    # Wallet endpoints
    async def get_wallet_portfolio(
        self,
        wallet: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletPortfolio: ...
    
    async def get_wallet_token_balance(
        self,
        wallet: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletTokenBalance: ...
    
    async def get_wallet_txs(
        self,
        wallet: str,
        *,
        limit: Optional[int] = 50,
        before: Optional[str] = None,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletTxs: ...
    
    async def get_wallet_net_worth(
        self,
        wallet: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletNetWorth: ...
    
    async def get_wallet_net_worth_histories(
        self,
        wallet: str,
        *,
        time_from: int,
        time_to: int,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletNetWorthHistories: ...
    
    async def get_wallet_net_worth_details(
        self,
        wallet: str,
        *,
        time_from: Optional[int] = None,
        time_to: Optional[int] = None,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletNetWorthDetails: ...
    
    async def get_wallet_tokens_pnl(
        self,
        wallet: str,
        *,
        sort_by: Optional[Literal["total_profit_usd", "profit_usd", "realized_profit_usd", "unrealized_profit_usd"]] = "total_profit_usd",
        sort_type: Optional[Literal["asc", "desc"]] = "desc",
        offset: Optional[int] = 0,
        limit: Optional[int] = 50,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletTokensPnl: ...
    
    async def get_wallets_pnl_by_token(
        self,
        token_address: str,
        *,
        wallets: list[str],
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletsPnlByToken: ...
    
    async def get_wallet_tokens_balance(
        self,
        wallet: str,
        *,
        sort_by: Optional[Literal["value_usd", "balance_usd"]] = "value_usd",
        sort_type: Optional[Literal["asc", "desc"]] = "desc",
        offset: Optional[int] = 0,
        limit: Optional[int] = 50,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletTokensBalances: ...
    
    async def get_wallet_token_first_tx(
        self,
        wallet: str,
        token_address: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletsTokenFirstTx: ...
    
    # Search endpoint
    async def search(
        self,
        keyword: str,
        *,
        offset: Optional[int] = 0,
        limit: Optional[int] = 10,
        verify_token: Optional[bool] = None,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespSearchItems: ...
    
    # Utility endpoints
    async def get_latest_block_number(
        self,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespLatestBlockNumber: ...