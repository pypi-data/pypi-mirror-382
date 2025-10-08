"""Type stubs for http_client module."""

from typing import Any, Literal, Optional

from birdeye.ratelimiter import RATE_LIMIT_BLOCK, RateLimitBehavior, RateLimiter, MultiRateLimiter
from birdeye.http_resp import *  # Import all response types
from birdeye.consts import Chain
from birdeye.http_client import PUBLIC_API_BASE_URL


class HTTPClient:
    """
    Birdeye API client with automatic rate limiting and type safety.
    
    This client provides a comprehensive interface to the Birdeye API with built-in
    rate limiting, error handling, and type safety. All API endpoints are automatically
    rate-limited according to Birdeye's official limits.
    
    Features:
    - Automatic rate limiting for all endpoints
    - Type-safe responses with TypedDict definitions
    - Support for multiple blockchain networks
    - Comprehensive error handling and retry logic
    - Async/await support for high-performance applications
    
    Rate Limiting:
    - 300 RPS: Price and market data endpoints
    - 150 RPS: Token list and security endpoints  
    - 100 RPS: Historical data and transaction endpoints
    - 30 RPS / 150 RPM: Wallet endpoints (multi-tier limiting)
    - 2 RPS: Scroll endpoints (very strict)
    
    Attributes:
        api_key (str): Your Birdeye API key
        base_url (str): Base URL for the Birdeye API
        chains (Optional[list[Chain]]): List of supported blockchain networks
        limiter_300_rps (RateLimiter): Rate limiter for 300 RPS endpoints
        limiter_150_rps (RateLimiter): Rate limiter for 150 RPS endpoints
        limiter_100_rps (RateLimiter): Rate limiter for 100 RPS endpoints
        limiter_wallet (MultiRateLimiter): Multi-tier rate limiter for wallet endpoints
        limiter_2_rps (RateLimiter): Rate limiter for 2 RPS endpoints
        endpoint_limiters (dict[str, Any]): Mapping of endpoints to rate limiters
    
    Example:
        ```python
        from birdeye import HTTPClient
        
        # Initialize client
        client = HTTPClient(api_key="your-api-key")
        
        # Get token price
        price = await client.get_token_price("So11111111111111111111111111111111111111112")
        print(f"SOL Price: ${price['value']}")
        
        # Get wallet portfolio
        portfolio = await client.get_wallet_portfolio("wallet-address")
        print(f"Portfolio value: ${portfolio['total_value']}")
        ```
    """
    
    api_key: str
    base_url: str
    chains: Optional[list[Chain]]
    limiter_300_rps: RateLimiter
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
        on_rate_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK
    ) -> None:
        """
        Initialize the Birdeye API client with automatic rate limiting.
        
        Args:
            api_key (str): Your Birdeye API key. Get one from https://birdeye.so/
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            base_url (str): Base URL for the Birdeye API. 
                Default: "https://public-api.birdeye.so"
            on_rate_limit_exceeded (RateLimitBehavior): Behavior when rate limit is exceeded.
                Options: RATE_LIMIT_BLOCK (wait), RATE_LIMIT_RAISE (raise exception).
                Default: RATE_LIMIT_BLOCK
        
        Raises:
            ValueError: If api_key is empty or invalid
            TypeError: If chains contains invalid network types
        
        Example:
            ```python
            # Basic initialization
            client = HTTPClient(api_key="your-api-key")
            
            # With specific chains
            client = HTTPClient(
                api_key="your-api-key",
                chains=["solana", "ethereum"]
            )
            
            # With custom rate limit behavior
            client = HTTPClient(
                api_key="your-api-key",
                on_rate_limit_exceeded=RATE_LIMIT_RAISE
            )
            ```
        """
        ...
    
    # Network endpoints
    async def get_supported_networks(
        self,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespSupportedNetworks:
        """
        Get the list of supported blockchain networks.
        
        This method retrieves all blockchain networks that are currently
        supported by the Birdeye API.

        Args:
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespSupportedNetworks: List of supported blockchain networks
        
        Raises:
            BirdeyeAPIException: If API request fails
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            networks = await client.get_supported_networks()
            print(f"Supported networks: {networks}")
            # Output: ['solana', 'ethereum', 'arbitrum', ...]
            ```
        """
        ...
    
    async def get_wallet_supported_networks(
        self,
        *,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletSupportedNetworks:
        """
        Get the list of blockchain networks supported for wallet operations.
        
        This method retrieves blockchain networks that support wallet-related
        operations such as portfolio queries, transaction history, and balance checks.

        Args:
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespWalletSupportedNetworks: List of networks supporting wallet operations
        
        Raises:
            BirdeyeAPIException: If API request fails
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            wallet_networks = await client.get_wallet_supported_networks()
            print(f"Wallet networks: {wallet_networks}")
            # Output: ['solana', 'ethereum', 'arbitrum', ...]
            ```
        """
        ...
    
    # Price endpoints
    async def get_token_price(
        self,
        address: str,
        *,
        check_liquidity: int = 100,
        include_liquidity: bool = True,
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenPrice:
        """
        Get the current price of a token with optional liquidity filtering.
        
        This method retrieves the current market price for a token, including
        24-hour price change and liquidity information. The response includes
        both raw and scaled token amounts based on the specified mode.

        Args:
            address (str): Token contract address to query
            check_liquidity (Optional[int]): Minimum liquidity threshold in USD.
                Tokens below this threshold may not be included. Default: 100
            include_liquidity (Optional[bool]): Whether to include liquidity information
                in the response. Default: True
            ui_amount_mode (Literal["raw", "scaled", "both"]): Token amount display mode.
                - "raw": Raw amounts (e.g., 1000000000 for 1 token with 9 decimals)
                - "scaled": Human-readable amounts (e.g., 1.0)
                - "both": Include both raw and scaled amounts. Default: "raw"
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenPrice: Price response containing:
                - value (float): Current token price in USD
                - priceChange24h (float): 24-hour price change percentage
                - liquidity (float): Current liquidity in USD
                - updateUnixTime (int): Last update timestamp
                - updateHumanTime (str): Human-readable update time
                - priceInNative (float): Price in native token (e.g., SOL)
                - isScaledUiToken (bool): Whether token uses scaled UI amounts
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            # Get SOL price
            sol_price = await client.get_token_price("So11111111111111111111111111111111111111112")
            print(f"SOL Price: ${sol_price['value']:.2f}")
            print(f"24h Change: {sol_price['priceChange24h']:.2f}%")
            
            # Get price with liquidity filtering
            price = await client.get_token_price(
                "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
                check_liquidity=1000,  # Only include if liquidity > $1000
                include_liquidity=True
            )
            print(f"USDC Liquidity: ${price['liquidity']:,.2f}")
            ```
        """
        ...
    
    async def get_tokens_price(
        self,
        list_address: list[str],
        *,
        check_liquidity: int = 100,
        include_liquidity: bool = True,
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokensPrice:
        """
        Get the current price of multiple tokens in a single request.
        
        This method efficiently retrieves prices for multiple tokens in one API call,
        which is more efficient than making individual requests for each token.
        All tokens are filtered by the same liquidity threshold.

        Args:
            list_address (list[str]): List of token contract addresses to query
            check_liquidity (Optional[int]): Minimum liquidity threshold in USD.
                Tokens below this threshold may not be included. Default: 100
            include_liquidity (Optional[bool]): Whether to include liquidity information
                in the response. Default: True
            ui_amount_mode (Literal["raw", "scaled", "both"]): Token amount display mode.
                - "raw": Raw amounts (e.g., 1000000000 for 1 token with 9 decimals)
                - "scaled": Human-readable amounts (e.g., 1.0)
                - "both": Include both raw and scaled amounts. Default: "raw"
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokensPrice: Dictionary mapping token addresses to RespTokenPrice objects.
                Each RespTokenPrice contains:
                - value (float): Current token price in USD
                - priceChange24h (float): 24-hour price change percentage
                - liquidity (float): Current liquidity in USD
                - updateUnixTime (int): Last update timestamp
                - updateHumanTime (str): Human-readable update time
                - priceInNative (float): Price in native token (e.g., SOL)
                - isScaledUiToken (bool): Whether token uses scaled UI amounts
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If any address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            # Get prices for multiple tokens
            addresses = [
                "So11111111111111111111111111111111111111112",  # SOL
                "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
                "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"   # USDT
            ]
            
            prices = await client.get_tokens_price(addresses)
            
            for address, price_data in prices.items():
                print(f"{address}: ${price_data['value']:.2f}")
            
            # Get prices with liquidity filtering
            prices = await client.get_tokens_price(
                addresses,
                check_liquidity=1000,  # Only include tokens with > $1000 liquidity
                include_liquidity=True
            )
            ```
        """
        ...
    
    # Transaction endpoints
    async def get_token_txs(
        self,
        address: str,
        *,
        offset: int = 0,
        limit: int = 50,
        tx_type: Literal["swap", "add", "remove", "all"] = "swap",
        sort_type: Literal["desc", "asc"] = "desc",
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenTxs:
        """
        Get transaction history for a specific token.
        
        This method retrieves transaction history for a token, including
        swaps, adds, and removes. Results can be filtered by transaction type
        and sorted by timestamp.

        Args:
            address (str): Token contract address to query
            offset (Optional[int]): Number of transactions to skip for pagination. Default: 0
            limit (Optional[int]): Maximum number of transactions to return (1-1000). Default: 50
            tx_type (Literal["swap", "add", "remove", "all"]): Type of transactions to retrieve.
                - "swap": Only swap transactions
                - "add": Only liquidity add transactions
                - "remove": Only liquidity remove transactions
                - "all": All transaction types. Default: "swap"
            sort_type (Literal["desc", "asc"]): Sort order by timestamp.
                - "desc": Newest first
                - "asc": Oldest first. Default: "desc"
            ui_amount_mode (Literal["raw", "scaled", "both"]): Token amount display mode.
                - "raw": Raw amounts (e.g., 1000000000 for 1 token with 9 decimals)
                - "scaled": Human-readable amounts (e.g., 1.0)
                - "both": Include both raw and scaled amounts. Default: "raw"
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenTxs: Transaction response containing:
                - items (list[RespTokenTxsItem]): List of transaction records
                - hasNext (bool): Whether more transactions are available
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            # Get recent swap transactions for SOL
            txs = await client.get_token_txs(
                "So11111111111111111111111111111111111111112",
                limit=20,
                tx_type="swap"
            )
            
            for tx in txs['items']:
                print(f"Tx: {tx['txHash']}, Amount: {tx['quote']['uiAmount']}")
            
            # Get all transaction types
            all_txs = await client.get_token_txs(
                "token-address",
                tx_type="all",
                sort_type="desc",
                limit=100
            )
            ```
        """
        ...
    
    async def get_pair_txs(
        self,
        address: str,
        *,
        offset: int = 0,
        limit: int = 50,
        tx_type: Literal["swap", "add", "remove", "all"] = "swap",
        sort_type: Literal["desc", "asc"] = "desc",
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespPairTxs:
        """
        Get transaction history for a specific trading pair.
        
        This method retrieves transaction history for a trading pair, including
        swaps, liquidity adds, and removes. Results can be filtered by transaction type
        and sorted by timestamp.

        Args:
            address (str): Trading pair address to query
            offset (Optional[int]): Number of transactions to skip for pagination. Default: 0
            limit (Optional[int]): Maximum number of transactions to return (1-1000). Default: 50
            tx_type (Literal["swap", "add", "remove", "all"]): Type of transactions to retrieve.
                - "swap": Only swap transactions
                - "add": Only liquidity add transactions
                - "remove": Only liquidity remove transactions
                - "all": All transaction types. Default: "swap"
            sort_type (Literal["desc", "asc"]): Sort order by timestamp.
                - "desc": Newest first
                - "asc": Oldest first. Default: "desc"
            ui_amount_mode (Literal["raw", "scaled", "both"]): Token amount display mode.
                - "raw": Raw amounts (e.g., 1000000000 for 1 token with 9 decimals)
                - "scaled": Human-readable amounts (e.g., 1.0)
                - "both": Include both raw and scaled amounts. Default: "raw"
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespPairTxs: Transaction response containing:
                - items (list[RespPairTxsItem]): List of transaction records
                - hasNext (bool): Whether more transactions are available
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            # Get recent transactions for a trading pair
            pair_txs = await client.get_pair_txs(
                "pair-address",
                limit=20,
                tx_type="swap"
            )
            
            for tx in pair_txs['items']:
                print(f"Tx: {tx['txHash']}, Type: {tx['txType']}")
            
            # Get liquidity operations
            liquidity_txs = await client.get_pair_txs(
                "pair-address",
                tx_type="all",
                sort_type="desc"
            )
            ```
        """
        ...
    
    async def get_token_txs_by_time(
        self,
        address: str,
        *,
        after_time: Optional[int] = None,
        before_time: Optional[int] = None,
        offset: int = 0,
        limit: int = 100,
        tx_type: Literal["swap", "add", "remove", "all"] = "swap",
        sort_type: Literal["desc", "asc"] = "desc",
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenTxsByTime:
        """
        Get token transactions within a specific time range.
        
        This method retrieves transaction history for a token within a specified
        time window, allowing for precise time-based filtering of transactions.

        Args:
            address (str): Token contract address to query
            before_time (Optional[int]): Get transactions before this Unix timestamp.
                If None, no upper time limit. Default: None
            after_time (Optional[int]): Get transactions after this Unix timestamp.
                If None, no lower time limit. Default: None
            tx_type (Literal["swap", "add", "remove", "all"]): Type of transactions to retrieve.
                - "swap": Only swap transactions
                - "add": Only liquidity add transactions
                - "remove": Only liquidity remove transactions
                - "all": All transaction types. Default: "swap"
            sort_type (Literal["desc", "asc"]): Sort order by timestamp.
                - "desc": Newest first
                - "asc": Oldest first. Default: "desc"
            limit (Optional[int]): Maximum number of transactions to return (1-1000). Default: 50
            ui_amount_mode (Literal["raw", "scaled", "both"]): Token amount display mode.
                - "raw": Raw amounts (e.g., 1000000000 for 1 token with 9 decimals)
                - "scaled": Human-readable amounts (e.g., 1.0)
                - "both": Include both raw and scaled amounts. Default: "raw"
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenTxsByTime: Transaction response containing:
                - items (list[RespTokenTxsItem]): List of transaction records
                - hasNext (bool): Whether more transactions are available
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid or time range is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            import time
            
            # Get transactions from the last hour
            current_time = int(time.time())
            one_hour_ago = current_time - 3600
            
            txs = await client.get_token_txs_by_time(
                "So11111111111111111111111111111111111111112",  # SOL
                after_time=one_hour_ago,
                before_time=current_time,
                tx_type="swap",
                limit=100
            )
            
            for tx in txs['items']:
                print(f"Tx: {tx['txHash']}, Time: {tx['blockUnixTime']}")
            
            # Get all transaction types in a specific time window
            all_txs = await client.get_token_txs_by_time(
                "token-address",
                after_time=1640995200,  # Jan 1, 2022
                before_time=1672531200,  # Jan 1, 2023
                tx_type="all"
            )
            ```
        """
        ...
    
    async def get_pair_txs_by_time(
        self,
        address: str,
        *,
        after_time: Optional[int] = None,
        before_time: Optional[int] = None,
        offset: int = 0,
        limit: int = 100,
        tx_type: Literal["swap", "add", "remove", "all"] = "swap",
        sort_type: Literal["desc", "asc"] = "desc",
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespPairTxsByTime:
        """
        Get trading pair transactions within a specific time range.
        
        This method retrieves transaction history for a trading pair within a specified
        time window, allowing for precise time-based filtering of pair transactions.

        Args:
            address (str): Trading pair address to query
            before_time (Optional[int]): Get transactions before this Unix timestamp.
                If None, no upper time limit. Default: None
            after_time (Optional[int]): Get transactions after this Unix timestamp.
                If None, no lower time limit. Default: None
            tx_type (Literal["swap", "add", "remove", "all"]): Type of transactions to retrieve.
                - "swap": Only swap transactions
                - "add": Only liquidity add transactions
                - "remove": Only liquidity remove transactions
                - "all": All transaction types. Default: "swap"
            sort_type (Literal["desc", "asc"]): Sort order by timestamp.
                - "desc": Newest first
                - "asc": Oldest first. Default: "desc"
            limit (Optional[int]): Maximum number of transactions to return (1-1000). Default: 50
            ui_amount_mode (Literal["raw", "scaled", "both"]): Token amount display mode.
                - "raw": Raw amounts (e.g., 1000000000 for 1 token with 9 decimals)
                - "scaled": Human-readable amounts (e.g., 1.0)
                - "both": Include both raw and scaled amounts. Default: "raw"
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespPairTxsByTime: Transaction response containing:
                - items (list[RespPairTxsItem]): List of transaction records
                - hasNext (bool): Whether more transactions are available
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid or time range is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            import time
            
            # Get pair transactions from the last 24 hours
            current_time = int(time.time())
            one_day_ago = current_time - 86400
            
            pair_txs = await client.get_pair_txs_by_time(
                "pair-address",
                after_time=one_day_ago,
                before_time=current_time,
                tx_type="swap",
                limit=100
            )
            
            for tx in pair_txs['items']:
                print(f"Tx: {tx['txHash']}, Type: {tx['txType']}")
            
            # Get liquidity operations in a specific time window
            liquidity_txs = await client.get_pair_txs_by_time(
                "pair-address",
                after_time=1640995200,  # Jan 1, 2022
                before_time=1672531200,  # Jan 1, 2023
                tx_type="all"
            )
            ```
        """
        ...
    
    async def get_all_txs(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        sort_by: Literal['block_unix_time', 'block_number'] = "block_unix_time",
        sort_type: Literal["desc", "asc"] = "desc",
        tx_type: Literal["swap", "add", "remove", "all"] = "swap",
        source: Optional[Literal['raydium', 'raydium_clamm', 'raydium_cp', 'orca', 'lifinity', 'fluxbeam', 'saber', 'phoenix', 'bonkswap', 'pump_dot_fun']] = None,
        owner: Optional[str] = None,
        pool_id: Optional[str] = None,
        before_time: Optional[int] = None,
        after_time: Optional[int] = None,
        before_block_number: Optional[int] = None,
        after_block_number: Optional[int] = None,
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespAllTxsV3:
        """
        Get all transactions across the platform with advanced filtering.
        
        This method retrieves transactions from across all supported networks
        with comprehensive filtering options for pairs, tokens, wallets, and time ranges.

        Args:
            before_time (Optional[int]): Get transactions before this Unix timestamp.
                If None, no upper time limit. Default: None
            after_time (Optional[int]): Get transactions after this Unix timestamp.
                If None, no lower time limit. Default: None
            tx_type (Literal["swap", "add", "remove", "all"]): Type of transactions to retrieve.
                - "swap": Only swap transactions
                - "add": Only liquidity add transactions
                - "remove": Only liquidity remove transactions
                - "all": All transaction types. Default: "swap"
            sort_type (Literal["desc", "asc"]): Sort order by timestamp.
                - "desc": Newest first
                - "asc": Oldest first. Default: "desc"
            limit (Optional[int]): Maximum number of transactions to return (1-1000). Default: 50
            pairAddress (Optional[str]): Filter by specific trading pair address.
                If None, includes all pairs. Default: None
            tokenAddress (Optional[str]): Filter by specific token address.
                If None, includes all tokens. Default: None
            walletAddress (Optional[str]): Filter by specific wallet address.
                If None, includes all wallets. Default: None
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespAllTxsV3: Transaction response containing:
                - items (list[RespAllTxsV3Item]): List of transaction records
                - hasNext (bool): Whether more transactions are available
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If any address is invalid or time range is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            import time
            
            # Get all recent swap transactions
            current_time = int(time.time())
            one_hour_ago = current_time - 3600
            
            all_txs = await client.get_all_txs(
                after_time=one_hour_ago,
                before_time=current_time,
                tx_type="swap",
                limit=100
            )
            
            for tx in all_txs['items']:
                print(f"Tx: {tx['txHash']}, Pair: {tx.get('pairAddress', 'N/A')}")
            
            # Get transactions for a specific wallet
            wallet_txs = await client.get_all_txs(
                walletAddress="wallet-address",
                tx_type="all",
                limit=50
            )
            
            # Get transactions for a specific token
            token_txs = await client.get_all_txs(
                tokenAddress="token-address",
                tx_type="swap",
                chains=["solana", "ethereum"]
            )
            ```
        """
        ...
    
    async def get_token_txs_v3(
        self,
        address: str,
        *,
        offset: int = 0,
        limit: int = 100,
        sort_by: Literal['block_unix_time', 'block_number'] = "block_unix_time",
        sort_type: Literal["desc", "asc"] = "desc",
        tx_type: Literal["swap", "add", "remove", "all"] = "swap",
        source: Optional[Literal['raydium', 'raydium_clamm', 'raydium_cp', 'orca', 'lifinity', 'fluxbeam', 'saber', 'phoenix', 'bonkswap', 'pump_dot_fun']] = None,
        owner: Optional[str] = None,
        pool_id: Optional[str] = None,
        before_time: Optional[int] = None,
        after_time: Optional[int] = None,
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenTxsV3:
        """
        Get token transactions using the V3 API with enhanced filtering.
        
        This method retrieves transaction history for a token using the V3 API,
        which provides enhanced filtering options and improved data structure.

        Args:
            address (str): Token contract address to query
            tx_type (Literal["swap", "add_liquidity", "remove_liquidity", "burn", "mint"]): Type of transactions to retrieve.
                - "swap": Only swap transactions
                - "add_liquidity": Only liquidity add transactions
                - "remove_liquidity": Only liquidity remove transactions
                - "burn": Only burn transactions
                - "mint": Only mint transactions. Default: "swap"
            before_time (Optional[int]): Get transactions before this Unix timestamp.
                If None, no upper time limit. Default: None
            after_time (Optional[int]): Get transactions after this Unix timestamp.
                If None, no lower time limit. Default: None
            sort_type (Literal["desc", "asc"]): Sort order by timestamp.
                - "desc": Newest first
                - "asc": Oldest first. Default: "desc"
            limit (Optional[int]): Maximum number of transactions to return (1-1000). Default: 50
            offset (Optional[int]): Number of transactions to skip for pagination. Default: 0
            ui_amount_mode (Literal["raw", "scaled", "both"]): Token amount display mode.
                - "raw": Raw amounts (e.g., 1000000000 for 1 token with 9 decimals)
                - "scaled": Human-readable amounts (e.g., 1.0)
                - "both": Include both raw and scaled amounts. Default: "raw"
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenTxsV3: Transaction response containing:
                - items (list[RespTokenTxsV3Item]): List of transaction records
                - hasNext (bool): Whether more transactions are available
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid or time range is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            import time
            
            # Get recent swap transactions for SOL
            current_time = int(time.time())
            one_hour_ago = current_time - 3600
            
            txs = await client.get_token_txs_v3(
                "So11111111111111111111111111111111111111112",  # SOL
                tx_type="swap",
                after_time=one_hour_ago,
                limit=100
            )
            
            for tx in txs['items']:
                print(f"Tx: {tx['txHash']}, Volume: {tx.get('volume', 'N/A')}")
            
            # Get liquidity operations
            liquidity_txs = await client.get_token_txs_v3(
                "token-address",
                tx_type="add_liquidity",
                sort_type="desc",
                limit=50
            )
            ```
        """
        ...
    
    async def get_recent_txs(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        tx_type: Literal["swap", "add", "remove", "all"] = "swap",
        owner: Optional[str] = None,
        before_time: Optional[int] = None,
        after_time: Optional[int] = None,
        before_block_number: Optional[int] = None,
        after_block_number: Optional[int] = None,
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespRecentTxsV3:
        """
        Get recent transactions across the platform with advanced filtering.
        
        This method retrieves the most recent transactions across all supported networks
        with comprehensive filtering options and sorting capabilities.

        Args:
            tx_type (Literal["swap", "add_liquidity", "remove_liquidity", "burn", "mint"]): Type of transactions to retrieve.
                - "swap": Only swap transactions
                - "add_liquidity": Only liquidity add transactions
                - "remove_liquidity": Only liquidity remove transactions
                - "burn": Only burn transactions
                - "mint": Only mint transactions. Default: "swap"
            sort_type (Literal["desc", "asc"]): Sort order.
                - "desc": Newest/highest first
                - "asc": Oldest/lowest first. Default: "desc"
            sort_by (Literal["blockUnixTime", "volume"]): Field to sort by.
                - "blockUnixTime": Sort by transaction timestamp
                - "volume": Sort by transaction volume. Default: "blockUnixTime"
            limit (Optional[int]): Maximum number of transactions to return (1-1000). Default: 50
            offset (Optional[int]): Number of transactions to skip for pagination. Default: 0
            pairAddress (Optional[str]): Filter by specific trading pair address.
                If None, includes all pairs. Default: None
            tokenAddress (Optional[str]): Filter by specific token address.
                If None, includes all tokens. Default: None
            walletAddress (Optional[str]): Filter by specific wallet address.
                If None, includes all wallets. Default: None
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespRecentTxsV3: Transaction response containing:
                - items (list[RespRecentTxsV3Item]): List of recent transaction records
                - hasNext (bool): Whether more transactions are available
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If any address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            # Get recent high-volume swap transactions
            recent_txs = await client.get_recent_txs(
                tx_type="swap",
                sort_by="volume",
                sort_type="desc",
                limit=100
            )
            
            for tx in recent_txs['items']:
                print(f"Tx: {tx['txHash']}, Volume: ${tx.get('volume', 'N/A')}")
            
            # Get recent transactions for a specific token
            token_txs = await client.get_recent_txs(
                tokenAddress="So11111111111111111111111111111111111111112",  # SOL
                tx_type="swap",
                limit=50
            )
            
            # Get recent transactions for a specific wallet
            wallet_txs = await client.get_recent_txs(
                walletAddress="wallet-address",
                tx_type="all",
                sort_by="blockUnixTime"
            )
            ```
        """
        ...
    
    # OHLCV endpoints
    async def get_token_ohlcv(
        self,
        address: str,
        type: Literal["1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "8H", "12H", "1D", "3D", "1W", "1M"],
        time_from: int,
        time_to: int,
        *,
        currency: Literal['usd', 'native'] = 'usd',
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenOHLCVs:
        """
        Get OHLCV (Open, High, Low, Close, Volume) data for a token.
        
        This method retrieves historical OHLCV data for a token over a specified
        time range with configurable time intervals.

        Args:
            address (str): Token contract address to query
            time_from (int): Start time in Unix timestamp (seconds)
            time_to (int): End time in Unix timestamp (seconds)
            type (Literal): Time interval for OHLCV data.
                Options: "1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "8H", "12H", "1D", "3D", "1W", "1M"
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenOHLCVs: OHLCV response containing:
                - items (list[RespTokenOHLCVItem]): List of OHLCV data points
                - Each item contains: open, high, low, close, volume, timestamp
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid or time range is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            import time
            
            # Get 1-hour OHLCV data for the last 24 hours
            end_time = int(time.time())
            start_time = end_time - 86400  # 24 hours ago
            
            ohlcv = await client.get_token_ohlcv(
                "So11111111111111111111111111111111111111112",  # SOL
                time_from=start_time,
                time_to=end_time,
                type="1H"
            )
            
            for candle in ohlcv['items']:
                print(f"Time: {candle['unixTime']}, Close: ${candle['c']}")
            
            # Get daily data for a month
            monthly_ohlcv = await client.get_token_ohlcv(
                "token-address",
                time_from=start_time,
                time_to=end_time,
                type="1D"
            )
            ```
        """
        ...
    
    async def get_pair_ohlcv(
        self,
        address: str,
        type: Literal["1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "8H", "12H", "1D", "3D", "1W", "1M"],
        time_from: int,
        time_to: int,
        *,
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespPairOHLCVs:
        """
        Get OHLCV (Open, High, Low, Close, Volume) data for a trading pair.
        
        This method retrieves historical OHLCV data for a trading pair over a specified
        time range with configurable time intervals.

        Args:
            address (str): Trading pair address to query
            time_from (int): Start time in Unix timestamp (seconds)
            time_to (int): End time in Unix timestamp (seconds)
            type (Literal): Time interval for OHLCV data.
                Options: "1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "8H", "12H", "1D", "3D", "1W", "1M"
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespPairOHLCVs: OHLCV response containing:
                - items (list[RespPairOHLCVItem]): List of OHLCV data points
                - Each item contains: open, high, low, close, volume, timestamp
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid or time range is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            import time
            
            # Get 1-hour OHLCV data for a trading pair over the last 24 hours
            end_time = int(time.time())
            start_time = end_time - 86400  # 24 hours ago
            
            pair_ohlcv = await client.get_pair_ohlcv(
                "pair-address",
                time_from=start_time,
                time_to=end_time,
                type="1H"
            )
            
            for candle in pair_ohlcv['items']:
                print(f"Time: {candle['unixTime']}, Close: ${candle['c']}")
            
            # Get daily data for a month
            monthly_ohlcv = await client.get_pair_ohlcv(
                "pair-address",
                time_from=start_time,
                time_to=end_time,
                type="1D"
            )
            ```
        """
        ...
    
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
    ) -> RespOHLCVBaseQuote:
        """
        Get OHLCV data for a trading pair by base and quote token addresses.
        
        This method retrieves OHLCV data for a trading pair by specifying the base
        and quote token addresses, which is useful when you don't have the pair address.

        Args:
            base_address (str): Base token contract address
            quote_address (str): Quote token contract address
            time_from (int): Start time in Unix timestamp (seconds)
            time_to (int): End time in Unix timestamp (seconds)
            type (Literal): Time interval for OHLCV data.
                Options: "1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "8H", "12H", "1D", "3D", "1W", "1M"
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespOHLCVBaseQuote: OHLCV response containing:
                - items (list[RespOHLCVItem]): List of OHLCV data points
                - Each item contains: open, high, low, close, volume, timestamp
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If addresses are invalid or time range is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            import time
            
            # Get OHLCV data for SOL/USDC pair
            end_time = int(time.time())
            start_time = end_time - 86400  # 24 hours ago
            
            ohlcv = await client.get_ohlcv_by_base_quote(
                base_address="So11111111111111111111111111111111111111112",  # SOL
                quote_address="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
                time_from=start_time,
                time_to=end_time,
                type="1H"
            )
            
            for candle in ohlcv['items']:
                print(f"Time: {candle['unixTime']}, Close: ${candle['c']}")
            
            # Get daily data for ETH/USDT pair
            eth_usdt_ohlcv = await client.get_ohlcv_by_base_quote(
                base_address="eth-address",
                quote_address="usdt-address",
                time_from=start_time,
                time_to=end_time,
                type="1D"
            )
            ```
        """
        ...
    
    async def get_token_ohlcv_v3(
        self,
        address: str,
        type: Literal["1s", "15s", "1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "8H", "12H", "1D", "3D", "1W", "1M"],
        time_from: int,
        time_to: int,
        *,
        currency: Literal["usd", "native"] = "usd",
        mode: Literal["range", "count"] = "range",
        count_limit: int = 5000,
        padding: bool = False,
        outlier: bool = True,
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenOHLCVsV3:
        """
        Get OHLCV data for a token using the V3 API.
        
        This method retrieves historical OHLCV data for a token using the V3 API,
        which provides enhanced data structure and improved performance.

        Args:
            address (str): Token contract address to query
            time_from (int): Start time in Unix timestamp (seconds)
            time_to (int): End time in Unix timestamp (seconds)
            type (Literal): Time interval for OHLCV data.
                Options: "1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "8H", "12H", "1D", "3D", "1W", "1M"
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenOHLCVsV3: OHLCV response containing:
                - items (list[RespTokenOHLCVItemV3]): List of OHLCV data points
                - Each item contains: open, high, low, close, volume, timestamp
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid or time range is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_pair_ohlcv_v3(
        self,
        address: str,
        type: Literal["1s", "15s", "1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "8H", "12H", "1D", "3D", "1W", "1M"],
        time_from: int,
        time_to: int,
        *,
        currency: Literal["usd", "native"] = "usd",
        mode: Literal["range", "count"] = "range",
        count_limit: int = 5000,
        padding: bool = False,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespPairOHLCVsV3:
        """
        Get OHLCV data for a trading pair using the V3 API.
        
        This method retrieves historical OHLCV data for a trading pair using the V3 API,
        which provides enhanced data structure and improved performance.

        Args:
            address (str): Trading pair address to query
            time_from (int): Start time in Unix timestamp (seconds)
            time_to (int): End time in Unix timestamp (seconds)
            type (Literal): Time interval for OHLCV data.
                Options: "1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "8H", "12H", "1D", "3D", "1W", "1M"
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespPairOHLCVsV3: OHLCV response containing:
                - items (list[RespPairOHLCVItemV3]): List of OHLCV data points
                - Each item contains: open, high, low, close, volume, timestamp
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid or time range is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    # Historical price endpoints
    async def get_token_price_histories(
        self,
        address: str,
        address_type: Literal["token", "pair"],
        type: Literal["1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "8H", "12H", "1D", "3D", "1W", "1M"],
        time_from: int,
        time_to: int,
        *,
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenPriceHistories:
        """
        Get historical price data for a token or trading pair.
        
        This method retrieves historical price data over a specified time range
        with configurable time intervals for tokens or trading pairs.

        Args:
            address (str): Token or pair contract address to query
            address_type (Literal["token", "pair"]): Type of address being queried.
                - "token": Query token price history
                - "pair": Query trading pair price history. Default: "token"
            type (Literal): Time interval for price data.
                Options: "1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "8H", "12H", "1D", "3D", "1W", "1M"
            time_from (int): Start time in Unix timestamp (seconds)
            time_to (int): End time in Unix timestamp (seconds)
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenPriceHistories: Price history response containing:
                - items (list[RespPriceHistoryItem]): List of price data points
                - Each item contains: price, timestamp, and other metrics
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid or time range is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            import time
            
            # Get daily price history for SOL over the last month
            end_time = int(time.time())
            start_time = end_time - 2592000  # 30 days ago
            
            price_history = await client.get_token_price_histories(
                "So11111111111111111111111111111111111111112",  # SOL
                address_type="token",
                type="1D",
                time_from=start_time,
                time_to=end_time
            )
            
            for price_point in price_history['items']:
                print(f"Date: {price_point['unixTime']}, Price: ${price_point['value']}")
            
            # Get hourly data for a trading pair
            pair_history = await client.get_token_price_histories(
                "pair-address",
                address_type="pair",
                type="1H",
                time_from=start_time,
                time_to=end_time
            )
            ```
        """
        ...
    
    async def get_token_price_history_by_time(
        self,
        address: str,
        *,
        unixtime: int,
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenPriceHistoryByTime:
        """
        Get token price at a specific time point.
        
        This method retrieves the token price at a specific Unix timestamp,
        useful for historical price analysis and backtesting.

        Note:
            This endpoint is only available for Solana chain.

        Args:
            address (str): Token contract address to query
            unixtime (int): Unix timestamp in seconds for the price query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenPriceHistoryByTime: Price history response containing:
                - value (float): Token price at the specified time
                - unixtime (int): The queried timestamp
                - priceChange24h (float): 24-hour price change at that time
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid or timestamp is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            # Get SOL price on January 1, 2024
            sol_price = await client.get_token_price_history_by_time(
                "So11111111111111111111111111111111111111112",  # SOL
                unixtime=1704067200  # Jan 1, 2024 00:00:00 UTC
            )
            print(f"SOL price on Jan 1, 2024: ${sol_price['value']}")
            ```
        """
        ...
    
    # Price volume endpoints
    async def get_token_price_volume(
        self,
        address: str,
        *,
        type: Literal["1h", "2h", "4h", "8h", "24h"] = "24h",
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenPriceVolume:
        """
        Get token price and trading volume data.
        
        This method retrieves current price and trading volume information
        for a specific token across supported networks.

        Args:
            address (str): Token contract address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenPriceVolume: Price and volume response containing:
                - price (float): Current token price
                - volume24h (float): 24-hour trading volume
                - priceChange24h (float): 24-hour price change percentage
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            # Get SOL price and volume
            sol_data = await client.get_token_price_volume(
                "So11111111111111111111111111111111111111112"  # SOL
            )
            print(f"SOL Price: ${sol_data['price']}")
            print(f"24h Volume: ${sol_data['volume24h']}")
            ```
        """
        ...
    
    async def get_tokens_price_volume(
        self,
        list_address: list[str],
        *,
        type: Literal["1h", "2h", "4h", "8h", "24h"] = "24h",
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokensPriceVolume:
        """
        Get price and trading volume data for multiple tokens.
        
        This method retrieves current price and trading volume information
        for multiple tokens in a single request, improving efficiency.

        Args:
            list_address (list[str]): List of token contract addresses to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokensPriceVolume: Price and volume response containing:
                - items (list[RespTokenPriceVolumeItem]): List of token price/volume data
                - Each item contains: price, volume24h, priceChange24h
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If any address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            # Get price and volume for multiple tokens
            tokens_data = await client.get_tokens_price_volume([
                "So11111111111111111111111111111111111111112",  # SOL
                "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
                "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"   # Bonk
            ])
            
            for token_data in tokens_data['items']:
                print(f"Token: {token_data['address']}, Price: ${token_data['price']}")
            ```
        """
        ...
    
    # Pair overview endpoints
    async def get_pair_overview(
        self,
        address: str,
        *,
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespPairOverview:
        """
        Get comprehensive overview data for a trading pair.
        
        This method retrieves detailed information about a trading pair including
        liquidity, volume, price changes, and market statistics.

        Note:
            Just for Solana.

        Args:
            address (str): Trading pair address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespPairOverview: Pair overview response containing:
                - baseToken (dict): Base token information
                - quoteToken (dict): Quote token information
                - price (float): Current pair price
                - liquidity (float): Total liquidity
                - volume24h (float): 24-hour trading volume
                - priceChange24h (float): 24-hour price change percentage
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            # Get SOL/USDC pair overview
            pair_overview = await client.get_pair_overview(
                "pair-address"
            )
            print(f"Price: ${pair_overview['price']}")
            print(f"Liquidity: ${pair_overview['liquidity']}")
            print(f"24h Volume: ${pair_overview['volume24h']}")
            ```
        """
        ...
    
    async def get_pairs_overview(
        self,
        list_address: list[str],
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespPairsOverview:
        """
        Get comprehensive overview data for multiple trading pairs.
        
        This method retrieves detailed information about multiple trading pairs
        in a single request, improving efficiency for batch operations.

        Note:
            Just for Solana.

        Args:
            list_address (list[str]): List of trading pair addresses to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespPairsOverview: Pairs overview response containing:
                - items (list[RespPairOverviewItem]): List of pair overview data
                - Each item contains: baseToken, quoteToken, price, liquidity, volume24h
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If any address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            # Get overview for multiple pairs
            pairs_overview = await client.get_pairs_overview([
                "pair-address-1",
                "pair-address-2",
                "pair-address-3"
            ])
            
            for pair in pairs_overview['items']:
                print(f"Pair: {pair['baseToken']['symbol']}/{pair['quoteToken']['symbol']}")
                print(f"Price: ${pair['price']}")
            ```
        """
        ...
    
    # Token stats endpoints
    async def get_token_price_stats(
        self,
        address: str,
        list_timeframe: list[Literal["1m", "5m", "30m", "1h", "2h", "4h", "8h", "24h", "2d", "3d", "7d"]],
        *,
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenPriceStats:
        """
        Get comprehensive price statistics for a token.
        
        This method retrieves detailed price statistics including historical
        performance, volatility metrics, and market indicators.

        Args:
            address (str): Token contract address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenPriceStats: Price statistics response containing:
                - currentPrice (float): Current token price
                - priceChange24h (float): 24-hour price change percentage
                - priceChange7d (float): 7-day price change percentage
                - priceChange30d (float): 30-day price change percentage
                - volume24h (float): 24-hour trading volume
                - marketCap (float): Current market capitalization
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            # Get SOL price statistics
            sol_stats = await client.get_token_price_stats(
                "So11111111111111111111111111111111111111112"  # SOL
            )
            print(f"Current Price: ${sol_stats['currentPrice']}")
            print(f"24h Change: {sol_stats['priceChange24h']}%")
            print(f"Market Cap: ${sol_stats['marketCap']}")
            ```
        """
        ...
    
    async def get_tokens_price_stats(
        self,
        list_address: list[str],
        list_timeframe: list[Literal["1m", "5m", "30m", "1h", "2h", "4h", "8h", "24h", "2d", "3d", "7d"]],
        *,
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokensPriceStats:
        """
        Get comprehensive price statistics for multiple tokens.
        
        This method retrieves detailed price statistics for multiple tokens
        in a single request, improving efficiency for batch operations.

        Args:
            list_address (list[str]): List of token contract addresses to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokensPriceStats: Price statistics response containing:
                - items (list[RespTokenPriceStatsItem]): List of token price statistics
                - Each item contains: currentPrice, priceChange24h, volume24h, marketCap
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If any address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            # Get price statistics for multiple tokens
            tokens_stats = await client.get_tokens_price_stats([
                "So11111111111111111111111111111111111111112",  # SOL
                "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
                "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"   # Bonk
            ])
            
            for token_stats in tokens_stats['items']:
                print(f"Token: {token_stats['address']}")
                print(f"Price: ${token_stats['currentPrice']}")
                print(f"24h Change: {token_stats['priceChange24h']}%")
            ```
        """
        ...
    
    # Token list endpoints
    async def get_token_list_v1(
        self,
        *,
        sort_by: Literal["liquidity", "market_cap", "fdv", "recent_listing_time", "last_trade_unix_time", "volume_1h_usd", "volume_2h_usd", "volume_4h_usd", "volume_8h_usd", "volume_24h_usd", "volume_1h_change_percent", "volume_2h_change_percent", "volume_4h_change_percent", "volume_8h_change_percent", "volume_24h_change_percent", "price_change_1h_percent", "price_change_2h_percent", "price_change_4h_percent", "price_change_8h_percent", "price_change_24h_percent", "trade_1h_count", "trade_2h_count", "trade_4h_count", "trade_8h_count", "trade_24h_count"] = "liquidity",
        sort_type: Literal["desc", "asc"] = "desc",
        offset: int = 0,
        limit: int = 50,
        min_liquidity: float = 100,
        max_liquidity: Optional[float] = None,
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenListV1:
        """
        Get token list using V1 API with basic filtering.
        
        This method retrieves a list of tokens with basic information
        using the V1 API endpoint.

        Args:
            offset (Optional[int]): Number of tokens to skip for pagination. Default: 0
            limit (Optional[int]): Maximum number of tokens to return. Default: 20
            sort_by (Optional[Literal["market_cap", "volume", "price"]]): Sort criteria.
                - "market_cap": Sort by market capitalization
                - "volume": Sort by trading volume
                - "price": Sort by token price. Default: "market_cap"
            sort_type (Optional[Literal["desc", "asc"]]): Sort order.
                - "desc": Highest first
                - "asc": Lowest first. Default: "desc"
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenListV1: Token list response containing:
                - items (list[RespTokenListItemV1]): List of token information
                - hasNext (bool): Whether more tokens are available
        
        Raises:
            BirdeyeAPIException: If API request fails
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_token_list_v3(
        self,
        *,
        sort_by: str = "v24hUSD",
        sort_type: Literal["asc", "desc"] = "desc",
        offset: int = 0,
        limit: int = 50,
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
    ) -> RespTokenListV3:
        """
        Get token list using V3 API with advanced filtering.
        
        This method retrieves a list of tokens with advanced filtering options
        using the V3 API endpoint, providing more comprehensive data.

        Args:
            sort_by (Optional[str]): Sort criteria field. Default: "v24hUSD"
            sort_type (Optional[Literal["desc", "asc"]]): Sort order.
                - "desc": Highest first
                - "asc": Lowest first. Default: "desc"
            offset (Optional[int]): Number of tokens to skip for pagination. Default: 0
            limit (Optional[int]): Maximum number of tokens to return. Default: 20
            min_liquidity (Optional[float]): Minimum liquidity filter. Default: None
            max_liquidity (Optional[float]): Maximum liquidity filter. Default: None
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenListV3: Token list response containing:
                - items (list[RespTokenListItemV3]): List of token information
                - hasNext (bool): Whether more tokens are available
        
        Raises:
            BirdeyeAPIException: If API request fails
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_token_list_v3_scroll(
        self,
        *,
        sort_by: str = "v24hUSD",
        sort_type: Literal["asc", "desc"] = "desc",
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
    ) -> RespTokenListV3Scroll:
        """
        Get token list using V3 API with Scroll network support.
        
        This method retrieves a list of tokens with advanced filtering options
        specifically optimized for the Scroll network.

        Args:
            sort_by (Optional[str]): Sort criteria field. Default: "v24hUSD"
            sort_type (Optional[Literal["desc", "asc"]]): Sort order.
                - "desc": Highest first
                - "asc": Lowest first. Default: "desc"
            offset (Optional[int]): Number of tokens to skip for pagination. Default: 0
            limit (Optional[int]): Maximum number of tokens to return. Default: 20
            min_liquidity (Optional[float]): Minimum liquidity filter. Default: None
            max_liquidity (Optional[float]): Maximum liquidity filter. Default: None
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenListV3Scroll: Token list response containing:
                - items (list[RespTokenListItemV3Scroll]): List of token information
                - hasNext (bool): Whether more tokens are available
        
        Raises:
            BirdeyeAPIException: If API request fails
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    # Token metadata endpoints
    async def get_token_overview(
        self,
        address: str,
        frames: Optional[list[Literal["1m", "5m", "30m", "1h", "2h", "4h", "8h", "24h"]]] = None,
        *,
        ui_amount_mode: Literal["raw", "scaled", "both"] = "scaled",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenOverview:
        """
        Get comprehensive overview information for a token.
        
        This method retrieves detailed overview information about a token including
        basic metadata, market data, and key statistics.

        Args:
            address (str): Token contract address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenOverview: Token overview response containing:
                - address (str): Token contract address
                - symbol (str): Token symbol
                - name (str): Token name
                - decimals (int): Token decimals
                - price (float): Current token price
                - marketCap (float): Market capitalization
                - volume24h (float): 24-hour trading volume
                - priceChange24h (float): 24-hour price change percentage
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            # Get SOL token overview
            sol_overview = await client.get_token_overview(
                "So11111111111111111111111111111111111111112"  # SOL
            )
            print(f"Symbol: {sol_overview['symbol']}")
            print(f"Name: {sol_overview['name']}")
            print(f"Price: ${sol_overview['price']}")
            print(f"Market Cap: ${sol_overview['marketCap']}")
            ```
        """
        ...
    
    async def get_token_metadata(
        self,
        address: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenMetadata:
        """
        Get detailed metadata for a token.
        
        This method retrieves comprehensive metadata information about a token
        including description, social links, and additional details.

        Args:
            address (str): Token contract address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenMetadata: Token metadata response containing:
                - address (str): Token contract address
                - symbol (str): Token symbol
                - name (str): Token name
                - description (str): Token description
                - website (str): Official website URL
                - twitter (str): Twitter handle
                - telegram (str): Telegram channel
                - discord (str): Discord server
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_tokens_metadata(
        self,
        list_address: list[str],
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokensMetadata:
        """
        Get detailed metadata for multiple tokens.
        
        This method retrieves comprehensive metadata information for multiple tokens
        in a single request, improving efficiency for batch operations.

        Args:
            list_address (list[str]): List of token contract addresses to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokensMetadata: Tokens metadata response containing:
                - items (list[RespTokenMetadataItem]): List of token metadata
                - Each item contains: address, symbol, name, description, social links
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If any address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_token_market_data(
        self,
        address: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenMarketData:
        """
        Get comprehensive market data for a token.
        
        This method retrieves detailed market data including price, volume,
        liquidity, and other key market indicators for a token.

        Args:
            address (str): Token contract address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenMarketData: Token market data response containing:
                - price (float): Current token price
                - volume24h (float): 24-hour trading volume
                - liquidity (float): Total liquidity
                - marketCap (float): Market capitalization
                - priceChange24h (float): 24-hour price change percentage
                - priceChange7d (float): 7-day price change percentage
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_tokens_market_data(
        self,
        list_address: list[str],
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokensMarketData:
        """
        Get comprehensive market data for multiple tokens.
        
        This method retrieves detailed market data for multiple tokens
        in a single request, improving efficiency for batch operations.

        Args:
            list_address (list[str]): List of token contract addresses to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokensMarketData: Tokens market data response containing:
                - items (list[RespTokenMarketDataItem]): List of token market data
                - Each item contains: price, volume24h, liquidity, marketCap, priceChange24h
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If any address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_token_trade_data(
        self,
        address: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenTradeData:
        """
        Get trading data for a token.
        
        This method retrieves trading data including recent trades,
        trade volume, and trading statistics for a token.

        Args:
            address (str): Token contract address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenTradeData: Token trade data response containing:
                - recentTrades (list): List of recent trades
                - volume24h (float): 24-hour trading volume
                - tradeCount (int): Number of trades in 24h
                - avgTradeSize (float): Average trade size
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_tokens_trade_data(
        self,
        list_address: list[str],
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokensTradeData:
        """
        Get trading data for multiple tokens.
        
        This method retrieves trading data for multiple tokens
        in a single request, improving efficiency for batch operations.

        Args:
            list_address (list[str]): List of token contract addresses to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokensTradeData: Tokens trade data response containing:
                - items (list[RespTokenTradeDataItem]): List of token trade data
                - Each item contains: recentTrades, volume24h, tradeCount, avgTradeSize
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If any address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    # Token discovery endpoints
    async def get_new_listing(
        self,
        *,
        time_to: Optional[int] = None,
        limit: int = 20,
        meme_platform_enabled: bool = False,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenNewListing:
        """
        Get newly listed tokens.
        
        This method retrieves a list of newly listed tokens across
        supported networks, useful for discovering new opportunities.

        Args:
            offset (Optional[int]): Number of tokens to skip for pagination. Default: 0
            limit (Optional[int]): Maximum number of tokens to return. Default: 20
            sort_by (Optional[Literal["created_time", "market_cap", "volume"]]): Sort criteria.
                - "created_time": Sort by listing time
                - "market_cap": Sort by market capitalization
                - "volume": Sort by trading volume. Default: "created_time"
            sort_type (Optional[Literal["desc", "asc"]]): Sort order.
                - "desc": Newest/highest first
                - "asc": Oldest/lowest first. Default: "desc"
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenNewListing: New listing response containing:
                - items (list[RespTokenNewListingItem]): List of newly listed tokens
                - hasNext (bool): Whether more tokens are available
        
        Raises:
            BirdeyeAPIException: If API request fails
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_token_top_traders(
        self,
        address: str,
        *,
        time_frame: Literal["30m", "1h", "2h", "4h", "6h", "8h", "12h", "24h"] = "24h",
        sort_type: Literal["desc", "asc"] = "desc",
        sort_by: Literal["volume", "trade"] = "volume",
        offset: int = 0,
        limit: int = 10,
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenTopTraders:
        """
        Get top traders for a token.
        
        This method retrieves information about the top traders
        for a specific token, including their trading activity and statistics.

        Args:
            address (str): Token contract address to query
            limit (Optional[int]): Maximum number of traders to return. Default: 20
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenTopTraders: Top traders response containing:
                - items (list[RespTokenTopTradersItem]): List of top traders
                - Each item contains: wallet address, trade count, volume, profit/loss
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_token_all_market_list(
        self,
        address: str,
        time_frame: Literal["30m", "1h", "2h", "4h", "6h", "8h", "12h", "24h"] = "24h",
        sort_type: Literal["desc", "asc"] = "desc",
        sort_by: Literal["liquidity", "volume24h"] = "liquidity",
        *,
        offset: int = 0,
        limit: int = 20,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenAllMarketList:
        """
        Get all market information for a token.
        
        This method retrieves comprehensive market information including
        all trading pairs, exchanges, and market data for a token.

        Args:
            address (str): Token contract address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenAllMarketList: All market list response containing:
                - items (list[RespTokenAllMarketListItem]): List of market information
                - Each item contains: exchange, pair, price, volume, liquidity
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_token_trending_list(
        self,
        *,
        sort_by: Literal["volume", "volume_change_percent", "trade", "trade_change_percent", "unique_wallet_24h", "unique_wallet_24h_change_percent"] = "unique_wallet_24h",
        sort_type: Literal["asc", "desc"] = "desc",
        offset: int = 0,
        limit: int = 10,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenTrendingList:
        """
        Get trending tokens list.
        
        This method retrieves a list of trending tokens based on various
        metrics like volume, trades, and unique wallet activity.

        Args:
            sort_by (Optional[Literal["volume", "volume_change_percent", "trade", "trade_change_percent", "unique_wallet_24h", "unique_wallet_24h_change_percent"]]): Sort criteria.
                - "volume": Sort by trading volume
                - "volume_change_percent": Sort by volume change percentage
                - "trade": Sort by trade count
                - "trade_change_percent": Sort by trade change percentage
                - "unique_wallet_24h": Sort by unique wallet count
                - "unique_wallet_24h_change_percent": Sort by wallet change percentage. Default: "unique_wallet_24h"
            sort_type (Optional[Literal["asc", "desc"]]): Sort order.
                - "desc": Highest first
                - "asc": Lowest first. Default: "desc"
            offset (Optional[int]): Number of tokens to skip for pagination. Default: 0
            limit (Optional[int]): Maximum number of tokens to return. Default: 20
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenTrendingList: Trending list response containing:
                - items (list[RespTokenTrendingListItem]): List of trending tokens
                - hasNext (bool): Whether more tokens are available
        
        Raises:
            BirdeyeAPIException: If API request fails
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_token_security(
        self,
        address: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenSecurity:
        """
        Get security information for a token.
        
        This method retrieves security-related information about a token
        including risk assessment, security scores, and safety indicators.

        Args:
            address (str): Token contract address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenSecurity: Security response containing:
                - riskScore (float): Overall risk score (0-100)
                - securityScore (float): Security score (0-100)
                - isHoneypot (bool): Whether token is a honeypot
                - isRugpull (bool): Whether token is a rugpull
                - isVerified (bool): Whether token is verified
                - warnings (list[str]): List of security warnings
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_token_creation_info(
        self,
        address: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenCreationInfo:
        """
        Get token creation information.
        
        This method retrieves information about when and how a token
        was created, including creation details and initial parameters.

        Note:
            This endpoint is only available for Solana chain.

        Args:
            address (str): Token contract address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenCreationInfo: Creation info response containing:
                - createdAt (int): Creation timestamp
                - creator (str): Creator wallet address
                - initialSupply (float): Initial token supply
                - decimals (int): Token decimals
                - symbol (str): Token symbol
                - name (str): Token name
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_token_mint_burn_txs(
        self,
        address: str,
        *,
        offset: int = 0,
        limit: int = 50,
        sort_type: Literal["asc", "desc"] = "desc",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenMintBurnTxs:
        """
        Get mint and burn transactions for a token.
        
        This method retrieves all mint and burn transactions for a token,
        useful for tracking token supply changes.

        Note:
            This endpoint is only available for Solana chain.

        Args:
            address (str): Token contract address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenMintBurnTxs: Mint/burn transactions response containing:
                - items (list[RespTokenMintBurnTxsItem]): List of mint/burn transactions
                - Each item contains: txHash, type, amount, timestamp, from, to
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_token_all_time_trades(
        self,
        address: str,
        *,
        time_frame: Literal["1m", "5m", "30m", "1h", "2h", "4h", "8h", "24h", "3d", "7d", "14d", "30d", "90d", "180d", "1y", "alltime"] = "24h",
        ui_amount_mode: Literal["raw", "scaled", "both"] = "raw",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenAllTimeTrades:
        """
        Get all-time trading data for a token.
        
        This method retrieves comprehensive trading data for a token
        including all-time statistics and trading history.

        Args:
            address (str): Token contract address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenAllTimeTrades: All-time trades response containing:
                - totalTrades (int): Total number of trades
                - totalVolume (float): Total trading volume
                - avgTradeSize (float): Average trade size
                - firstTrade (int): First trade timestamp
                - lastTrade (int): Last trade timestamp
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_tokens_all_time_trades(
        self,
        list_address: list[str],
        *,
        time_from: Optional[int] = None,
        time_to: Optional[int] = None,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokensAllTimeTrades:
        """
        Get all-time trading data for multiple tokens.
        
        This method retrieves comprehensive trading data for multiple tokens
        in a single request, improving efficiency for batch operations.

        Args:
            list_address (list[str]): List of token contract addresses to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokensAllTimeTrades: All-time trades response containing:
                - items (list[RespTokenAllTimeTradesItem]): List of token all-time trades
                - Each item contains: totalTrades, totalVolume, avgTradeSize
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If any address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_token_exit_liquidity(
        self,
        address: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenExitLiquidity:
        """
        Get exit liquidity information for a token.
        
        This method retrieves information about exit liquidity for a token,
        including liquidity removal events and related data.

        Args:
            address (str): Token contract address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenExitLiquidity: Exit liquidity response containing:
                - totalExitLiquidity (float): Total exit liquidity amount
                - exitEvents (list): List of exit liquidity events
                - avgExitSize (float): Average exit liquidity size
                - lastExitTime (int): Last exit liquidity timestamp
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_tokens_exit_liquidity(
        self,
        list_address: list[str],
        *,
        time_from: Optional[int] = None,
        time_to: Optional[int] = None,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokensExitLiquidity:
        """
        Get exit liquidity information for multiple tokens.
        
        This method retrieves exit liquidity information for multiple tokens
        in a single request, improving efficiency for batch operations.

        Args:
            list_address (list[str]): List of token contract addresses to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokensExitLiquidity: Exit liquidity response containing:
                - items (list[RespTokenExitLiquidityItem]): List of token exit liquidity
                - Each item contains: totalExitLiquidity, exitEvents, avgExitSize
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If any address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    # Token holder endpoints
    async def get_token_holders(
        self,
        address: str,
        *,
        offset: int = 0,
        limit: int = 100,
        ui_amount_mode: Literal["raw", "scaled", "both"] = "scaled",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenHolders:
        """
        Get token holders information.
        
        This method retrieves information about token holders including
        holder addresses, balances, and percentage of total supply.

        Args:
            address (str): Token contract address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenHolders: Token holders response containing:
                - totalHolders (int): Total number of holders
                - holders (list[RespTokenHolderItem]): List of holder information
                - Each item contains: address, balance, percentage
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_token_holder_batch(
        self,
        token_address: str,
        wallets: list[str],
        *,
        ui_amount_mode: Literal["raw", "scaled", "both"] = "scaled",
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespTokenHolderBatch:
        """
        Get token holder information for multiple tokens.
        
        This method retrieves holder information for multiple tokens
        in a single request, improving efficiency for batch operations.

        Note:
            This endpoint is only available for Solana chain.

        Args:
            addresses (list[str]): List of token contract addresses to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespTokenHolderBatch: Token holder batch response containing:
                - items (list[RespTokenHolderBatchItem]): List of token holder data
                - Each item contains: address, totalHolders, topHolders
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If any address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    # Meme endpoints
    async def get_meme_list(
        self,
        *,
        sort_by: str = "last_trade_unix_time",
        sort_type: Literal["asc", "desc"] = "desc",
        time_to: Optional[int] = None,
        time_from: Optional[int] = None,
        offset: int = 0,
        limit: int = 50,
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
    ) -> RespMemeList:
        """
        Get list of meme tokens.
        
        This method retrieves a list of meme tokens with their basic
        information and market data.

        Note:
            This endpoint is only available for Solana chain.

        Args:
            offset (Optional[int]): Number of tokens to skip for pagination. Default: 0
            limit (Optional[int]): Maximum number of tokens to return. Default: 20
            sort_by (Optional[Literal["market_cap", "volume", "price"]]): Sort criteria.
                - "market_cap": Sort by market capitalization
                - "volume": Sort by trading volume
                - "price": Sort by token price. Default: "market_cap"
            sort_type (Optional[Literal["desc", "asc"]]): Sort order.
                - "desc": Highest first
                - "asc": Lowest first. Default: "desc"
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespMemeList: Meme list response containing:
                - items (list[RespMemeListItem]): List of meme tokens
                - hasNext (bool): Whether more tokens are available
        
        Raises:
            BirdeyeAPIException: If API request fails
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_meme_detail(
        self,
        address: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespMemeDetail:
        """
        Get detailed information for a meme token.
        
        This method retrieves comprehensive information about a specific
        meme token including metadata, market data, and social metrics.

        Note:
            This endpoint is only available for Solana chain.

        Args:
            address (str): Meme token contract address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespMemeDetail: Meme detail response containing:
                - address (str): Token contract address
                - symbol (str): Token symbol
                - name (str): Token name
                - description (str): Token description
                - marketCap (float): Market capitalization
                - volume24h (float): 24-hour trading volume
                - priceChange24h (float): 24-hour price change percentage
                - socialMetrics (dict): Social media metrics
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    # Trader endpoints
    async def get_gainers_losers(
        self,
        *,
        type: Literal["yesterday", "today", "1W"] = "1W",
        sort_by: Literal["PnL"] = "PnL",
        sort_type: Literal["desc", "asc"] = "desc",
        offset: int = 0,
        limit: int = 10,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespGainerLosers:
        """
        Get top gainers and losers tokens.
        
        This method retrieves a list of tokens with the highest gains
        and losses over a specified time period.

        Note:
            This endpoint is only available for Solana chain.

        Args:
            time_range (Optional[Literal["1h", "4h", "24h", "7d", "30d"]]): Time range for analysis.
                - "1h": 1 hour
                - "4h": 4 hours
                - "24h": 24 hours
                - "7d": 7 days
                - "30d": 30 days. Default: "24h"
            limit (Optional[int]): Maximum number of tokens to return. Default: 20
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespGainerLosers: Gainers/losers response containing:
                - gainers (list[RespGainerLoserItem]): List of top gaining tokens
                - losers (list[RespGainerLoserItem]): List of top losing tokens
                - Each item contains: address, symbol, price, changePercent
        
        Raises:
            BirdeyeAPIException: If API request fails
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_wallet_trades(
        self,
        wallet: str,
        *,
        token_address: Optional[str] = None,
        before_time: Optional[int] = None,
        after_time: Optional[int] = None,
        limit: int = 50,
        offset: int = 0,
        tx_type: Optional[Literal["buy", "sell"]] = None,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletTrades:
        """
        Get trading history for a wallet.
        
        This method retrieves the trading history for a specific wallet
        including all trades, volumes, and profit/loss information.

        Note:
            This endpoint is only available for Solana chain.

        Args:
            wallet (str): Wallet address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespWalletTrades: Wallet trades response containing:
                - totalTrades (int): Total number of trades
                - totalVolume (float): Total trading volume
                - totalProfit (float): Total profit/loss
                - trades (list[RespWalletTradeItem]): List of individual trades
                - Each trade contains: token, amount, price, timestamp, type
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If wallet address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_wallet_balance_changes(
        self,
        wallet: str,
        *,
        token_address: Optional[str] = None,
        before_time: Optional[int] = None,
        after_time: Optional[int] = None,
        limit: int = 50,
        offset: int = 0,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletBalanceChanges:
        """
        Get balance changes for a wallet.
        
        This method retrieves balance changes for a specific wallet
        including token balance updates and transaction history.

        Note:
            This endpoint is only available for Solana chain.

        Args:
            wallet (str): Wallet address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespWalletBalanceChanges: Wallet balance changes response containing:
                - totalChanges (int): Total number of balance changes
                - changes (list[RespWalletBalanceChangeItem]): List of balance changes
                - Each change contains: token, oldBalance, newBalance, timestamp
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If wallet address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    # Wallet endpoints
    async def get_wallet_portfolio(
        self,
        wallet: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletPortfolio:
        """
        Get the complete portfolio overview for a wallet.
        
        This method retrieves comprehensive portfolio information including
        total value, token holdings, and performance metrics for a wallet
        across multiple blockchain networks.

        Note:
            This endpoint is only available for Solana chain.

        Args:
            wallet (str): Wallet address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespWalletPortfolio: Portfolio response containing:
                - total_value (float): Total portfolio value in USD
                - tokens (list[RespWalletPortfolioItem]): List of token holdings
                - performance (dict): Performance metrics and statistics
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If wallet address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            # Get wallet portfolio
            portfolio = await client.get_wallet_portfolio("wallet-address")
            print(f"Total Value: ${portfolio['total_value']:,.2f}")
            
            # Get portfolio for specific chains
            portfolio = await client.get_wallet_portfolio(
                "wallet-address",
                chains=["solana", "ethereum"]
            )
            
            for token in portfolio['tokens']:
                print(f"{token['symbol']}: ${token['value']:,.2f}")
            ```
        """
        ...
    
    async def get_wallet_token_balance(
        self,
        wallet: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletTokenBalance:
        """
        Get token balance for a wallet.
        
        This method retrieves the current token balance for a specific
        wallet address across supported networks.

        Note:
            This endpoint is only available for Solana chain.

        Args:
            wallet (str): Wallet address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespWalletTokenBalance: Wallet token balance response containing:
                - totalBalance (float): Total wallet balance in USD
                - tokens (list[RespWalletTokenBalanceItem]): List of token balances
                - Each item contains: token, balance, value, price
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If wallet address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_wallet_txs(
        self,
        wallet: str,
        *,
        limit: int = 50,
        before: Optional[str] = None,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletTxs:
        """
        Get transaction history for a wallet.
        
        This method retrieves the transaction history for a specific
        wallet address including all transactions and their details.

        Note:
            This endpoint is only available for Solana chain.

        Args:
            wallet (str): Wallet address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespWalletTxs: Wallet transactions response containing:
                - totalTxs (int): Total number of transactions
                - txs (list[RespWalletTxItem]): List of transactions
                - Each item contains: txHash, timestamp, type, amount, token
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If wallet address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_wallet_net_worth(
        self,
        wallet: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletNetWorth:
        """
        Get net worth for a wallet.
        
        This method retrieves the current net worth for a specific
        wallet address including total value and asset breakdown.

        Note:
            This endpoint is only available for Solana chain.

        Args:
            wallet (str): Wallet address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespWalletNetWorth: Wallet net worth response containing:
                - totalValue (float): Total wallet value in USD
                - assets (list[RespWalletAssetItem]): List of assets
                - Each item contains: token, balance, value, percentage
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If wallet address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_wallet_net_worth_histories(
        self,
        wallet: str,
        *,
        time_from: int,
        time_to: int,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletNetWorthHistories:
        """
        Get net worth history for a wallet.
        
        This method retrieves the historical net worth data for a specific
        wallet address over time, useful for tracking portfolio performance.

        Note:
            This endpoint is only available for Solana chain.

        Args:
            wallet (str): Wallet address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespWalletNetWorthHistories: Wallet net worth history response containing:
                - histories (list[RespWalletNetWorthHistoryItem]): List of historical data
                - Each item contains: timestamp, totalValue, changePercent
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If wallet address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_wallet_net_worth_details(
        self,
        wallet: str,
        *,
        time_from: Optional[int] = None,
        time_to: Optional[int] = None,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletNetWorthDetails:
        """
        Get detailed net worth information for a wallet.
        
        This method retrieves comprehensive net worth details for a specific
        wallet address including asset breakdown and performance metrics.

        Note:
            This endpoint is only available for Solana chain.

        Args:
            wallet (str): Wallet address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespWalletNetWorthDetails: Wallet net worth details response containing:
                - totalValue (float): Total wallet value in USD
                - assets (list[RespWalletAssetDetailItem]): List of detailed asset information
                - Each item contains: token, balance, value, percentage, change24h
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If wallet address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_wallet_tokens_pnl(
        self,
        wallet: str,
        token_addresses: list[str],
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletTokensPnl:
        """
        Get profit and loss for wallet tokens.
        
        This method retrieves profit and loss information for all tokens
        in a specific wallet address.

        Note:
            This endpoint is only available for Solana chain.

        Args:
            wallet (str): Wallet address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespWalletTokensPnl: Wallet tokens PnL response containing:
                - totalPnl (float): Total profit/loss in USD
                - tokens (list[RespWalletTokenPnlItem]): List of token PnL data
                - Each item contains: token, pnl, pnlPercent, cost, currentValue
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If wallet address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_wallets_pnl_by_token(
        self,
        token_address: str,
        *,
        wallets: list[str],
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletsPnlByToken:
        """
        Get profit and loss for wallets by token.
        
        This method retrieves profit and loss information for all wallets
        that hold a specific token.

        Note:
            This endpoint is only available for Solana chain.

        Args:
            token_address (str): Token contract address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespWalletsPnlByToken: Wallets PnL by token response containing:
                - totalPnl (float): Total profit/loss in USD
                - wallets (list[RespWalletPnlByTokenItem]): List of wallet PnL data
                - Each item contains: wallet, pnl, pnlPercent, balance, cost
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If token address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_wallet_tokens_balance(
        self,
        wallet: str,
        *,
        sort_by: Literal["value_usd", "balance_usd"] = "value_usd",
        sort_type: Literal["asc", "desc"] = "desc",
        offset: int = 0,
        limit: int = 50,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletTokensBalances:
        """
        Get token balances for a wallet.
        
        This method retrieves the current token balances for a specific
        wallet address across all supported networks.

        Args:
            wallet (str): Wallet address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespWalletTokensBalances: Wallet tokens balances response containing:
                - totalValue (float): Total wallet value in USD
                - tokens (list[RespWalletTokenBalanceItem]): List of token balances
                - Each item contains: token, balance, value, price, change24h
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If wallet address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    async def get_wallet_token_first_tx(
        self,
        wallet: str,
        token_address: str,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespWalletsTokenFirstTx:
        """
        Get first transaction for a wallet and token.
        
        This method retrieves the first transaction between a specific
        wallet and token, useful for tracking initial interactions.

        Note:
            This endpoint is only available for Solana chain.

        Args:
            wallet (str): Wallet address to query
            token_address (str): Token contract address to query
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespWalletsTokenFirstTx: First transaction response containing:
                - txHash (str): Transaction hash
                - timestamp (int): Transaction timestamp
                - type (str): Transaction type (buy/sell)
                - amount (float): Transaction amount
                - price (float): Transaction price
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If wallet or token address is invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        """
        ...
    
    # Search endpoint
    async def search(
        self,
        keyword: str,
        *,
        offset: int = 0,
        limit: int = 10,
        verify_token: Optional[bool] = None,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespSearchItems:
        """
        Search for tokens, markets, and other entities across blockchain networks.
        
        This method provides comprehensive search functionality across multiple
        blockchain networks, allowing users to find tokens, markets, and other
        entities by name, symbol, or address.

        Args:
            keyword (str): Search keyword (token name, symbol, or address)
            offset (Optional[int]): Number of results to skip for pagination. Default: 0
            limit (Optional[int]): Maximum number of results to return (1-100). Default: 10
            verify_token (Optional[bool]): Whether to verify token authenticity.
                If None, uses default verification. Default: None
            chains (Optional[list[Chain]]): List of blockchain networks to search.
                If None, searches all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespSearchItems: Search results containing:
                - items (list[RespSearchItem]): List of search results
                - total (int): Total number of results available
                - has_more (bool): Whether more results are available
        
        Raises:
            BirdeyeAPIException: If API request fails
            ValueError: If keyword is empty or invalid
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            # Search for tokens
            results = await client.search("SOL")
            print(f"Found {len(results['items'])} results")
            
            for item in results['items']:
                print(f"{item['symbol']}: {item['name']}")
            
            # Search with pagination
            results = await client.search(
                "USDC",
                offset=0,
                limit=20,
                chains=["solana", "ethereum"]
            )
            
            # Search with token verification
            results = await client.search(
                "Bitcoin",
                verify_token=True,
                limit=5
            )
            ```
        """
        ...
    
    # Utility endpoints
    async def get_latest_block_number(
        self,
        *,
        chains: Optional[list[Chain]] = None,
        on_rate_limit_exceeded: Optional[RateLimitBehavior] = None
    ) -> RespLatestBlockNumber:
        """
        Get the latest block number for supported blockchain networks.
        
        This method retrieves the current block number for the specified
        blockchain networks, which is useful for tracking blockchain state
        and ensuring data freshness.

        Args:
            chains (Optional[list[Chain]]): List of blockchain networks to query.
                If None, queries all supported networks. Default: None
            on_rate_limit_exceeded (Optional[RateLimitBehavior]): Override rate limit behavior
                for this request. If None, uses client default. Default: None
        
        Returns:
            RespLatestBlockNumber: Latest block number as an integer
        
        Raises:
            BirdeyeAPIException: If API request fails
            RateLimitError: If rate limit is exceeded (when on_rate_limit_exceeded=RAISE)
        
        Example:
            ```python
            # Get latest block number for all networks
            block_number = await client.get_latest_block_number()
            print(f"Latest block: {block_number}")
            
            # Get latest block for specific networks
            block_number = await client.get_latest_block_number(
                chains=["solana", "ethereum"]
            )
            print(f"Latest block: {block_number}")
            ```
        """
        ...