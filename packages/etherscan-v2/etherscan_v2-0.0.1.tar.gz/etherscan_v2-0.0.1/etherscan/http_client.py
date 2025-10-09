import asyncio, httpx, logging
from typing import Any, Literal, Optional
from urllib.parse import urlencode
from etherscan.ratelimiter import RATE_LIMIT_BLOCK, MultiRateLimiter, RateLimitBehavior
from etherscan.http_resp import *


BASE_URL = "https://api.etherscan.io/v2/api"
API_ASHX = "https://api-metadata.etherscan.io/v1/api.ashx"

ETHEREUM_MAINNET = 1
SEPOLIA_TESTNET = 11155111
HOLESKY_TESTNET = 17000
HOODI_TESTNET = 560048
ABSTRACT_MAINNET = 2741
ABSTRACT_SEPOLIA_TESTNET = 11124
APECHAIN_CURTIS_TESTNET = 33111
APECHAIN_MAINNET = 33139
ARBITRUM_NOVA_MAINNET = 42170
ARBITRUM_ONE_MAINNET = 42161
ARBITRUM_SEPOLIA_TESTNET = 421614
AVALANCHE_C_CHAIN = 43114
AVALANCHE_FUJI_TESTNET = 43113
BASE_MAINNET = 8453
BASE_SEPOLIA_TESTNET = 84532
BERACHAIN_MAINNET = 80094
BERACHAIN_BEPOLIA_TESTNET = 80069
BITTORRENT_CHAIN_MAINNET = 199
BITTORRENT_CHAIN_TESTNET = 1029
BLAST_MAINNET = 81457
BLAST_SEPOLIA_TESTNET = 168587773
BNB_SMART_CHAIN_MAINNET = 56
BNB_SMART_CHAIN_TESTNET = 97
CELO_ALFAJORES_TESTNET = 44787
CELO_MAINNET = 42220
CRONOS_MAINNET = 25
FRAXTAL_MAINNET = 252
FRAXTAL_TESTNET = 2522
GNOSIS = 100
HYPEREVM_MAINNET = 999
LINEA_MAINNET = 59144
LINEA_SEPOLIA_TESTNET = 59141
MANTLE_MAINNET = 5000
MANTLE_SEPOLIA_TESTNET = 5003
MEMECORE_TESTNET = 43521
MOONBASE_ALPHA_TESTNET = 1287
MONAD_TESTNET = 10143
MOONBEAM_MAINNET = 1284
MOONRIVER_MAINNET = 1285
OP_MAINNET = 10
OP_SEPOLIA_TESTNET = 11155420
POLYGON_MAINNET = 137
POLYGON_AMOY_TESTNET = 80002
KATANA_MAINNET = 747474
KATANA_BOKUTO_TESTNET = 737373
SEI_MAINNET = 1329
SEI_TESTNET = 1328
SCROLL_MAINNET = 534352
SCROLL_SEPOLIA_TESTNET = 534351
SONIC_TESTNET = 14601
SONIC_MAINNET = 146
SOPHON_MAINNET = 50104
SOPHON_SEPOLIA_TESTNET = 531050104
SWELLCHAIN_MAINNET = 1923
SWELLCHAIN_TESTNET = 1924
TAIKO_MAINNET = 167000
TAIKO_HOODI_TESTNET = 167012
UNICHAIN_MAINNET = 130
UNICHAIN_SEPOLIA_TESTNET = 1301
WORLD_MAINNET = 480
WORLD_SEPOLIA_TESTNET = 4801
XDC_APOTHEM_TESTNET = 51
XDC_MAINNET = 50
ZKSYNC_MAINNET = 324
ZKSYNC_SEPOLIA_TESTNET = 300
OPBNB_MAINNET = 204
OPBNB_TESTNET = 5611

# API tiers
FREE_TIER = "free"
STANDARD_TIER = "standard" 
ADVANCED_TIER = "advanced"
PROFESSIONAL_TIER = "professional"
PRO_PLUS_TIER = "pro_plus"

# API rate limits by tier
FREE_TIER_RATE_LIMIT = 5  # calls/second
STANDARD_TIER_RATE_LIMIT = 10  # calls/second
ADVANCED_TIER_RATE_LIMIT = 20  # calls/second
PROFESSIONAL_TIER_RATE_LIMIT = 30  # calls/second
PRO_PLUS_TIER_RATE_LIMIT = 30  # calls/second

# API daily call limits by tier
FREE_TIER_DAILY_LIMIT = 100_000  # calls/day
STANDARD_TIER_DAILY_LIMIT = 200_000  # calls/day
ADVANCED_TIER_DAILY_LIMIT = 500_000  # calls/day
PROFESSIONAL_TIER_DAILY_LIMIT = 1_000_000  # calls/day
PRO_PLUS_TIER_DAILY_LIMIT = 1_500_000  # calls/day


class HTTPClient:
    """
    HTTPClient is a client for the Ethscan V2 API.
    """
    
    def __init__(self, api_key: str, *,
                 default_chain_id: int = ETHEREUM_MAINNET,
                 api_tier: str = PRO_PLUS_TIER,
                 on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK):
        self.api_key = api_key
        self.default_chain_id = default_chain_id
        rate_limit = []
        if api_tier == STANDARD_TIER:
            rate_limit = [(STANDARD_TIER_RATE_LIMIT, 1), (STANDARD_TIER_DAILY_LIMIT, 86400)]
        elif api_tier == ADVANCED_TIER:
            rate_limit = [(ADVANCED_TIER_RATE_LIMIT, 1), (ADVANCED_TIER_DAILY_LIMIT, 86400)]
        elif api_tier == PROFESSIONAL_TIER:
            rate_limit = [(PROFESSIONAL_TIER_RATE_LIMIT, 1), (PROFESSIONAL_TIER_DAILY_LIMIT, 86400)]
        elif api_tier == PRO_PLUS_TIER:
            rate_limit = [(PRO_PLUS_TIER_RATE_LIMIT, 1), (PRO_PLUS_TIER_DAILY_LIMIT, 86400)]
        else:
            rate_limit = [(FREE_TIER_RATE_LIMIT, 1), (FREE_TIER_DAILY_LIMIT, 86400)]
        self.on_limit_exceeded = on_limit_exceeded
        self.rate_limiter = MultiRateLimiter(rate_limit, on_limit_exceeded)
        
    
    async def _request(self, module: str, action: str, kwargs: dict[str, Any], *, method: Literal["GET", "POST"] = "GET", no_found_return: Any = [], base_url: str = BASE_URL) -> Any:
        kwargs.pop("self", None)
    
        on_limit_exceeded = kwargs.pop("on_limit_exceeded", None)
        if on_limit_exceeded is None:
            on_limit_exceeded = self.on_limit_exceeded
    
        # Acquire rate limit token before making request
        if not self.rate_limiter.acquire(on_limit_exceeded=on_limit_exceeded):
            return None
        
        chain_id = kwargs.get("chainid", None)
        if chain_id is None:
            kwargs["chainid"] = self.default_chain_id
            
        # Remove None values from kwargs
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # Build query parameters
        if method == "GET":
            params = {
                "module": module,
                "action": action,
                "apikey": self.api_key,
                **kwargs
            }
            kwargs = None
        elif method == "POST":
            params = {
                "chainid": kwargs.pop("chainid", None),
                "module": module,
                "action": action,
                "apikey": self.api_key,
            }

        uri = f"{base_url}?{urlencode(params)}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(method, uri, json=kwargs)
            except Exception as e:
                retry_times = 3
                err = e
                for i in range(retry_times):
                    try:
                        logging.error(f"etherscan: request {module} {action} failed: {err}, retrying {i+1} of {retry_times}...")
                        response = await client.request(method, uri)
                        break
                    except Exception as e:
                        logging.error(f"etherscan: request {module} {action} retrying {i+1} of {retry_times} failed: {e}")
                        if i == retry_times - 1:
                            raise e
                        await asyncio.sleep(1)
    
            try:
                body = response.json()
            except Exception as e:
                logging.error(f"etherscan: parse {module} {action} response failed: {e}")
                body = {}
    
            status = ""
            message = ""
            result = None
            if isinstance(body, dict):
                status = body.get("status", "")
                message = body.get("message", "")
                json_rpc = body.get("jsonrpc", None)
                if json_rpc is not None:
                    result = body
                else:   
                    result = body.get("result", None)
    
            status_code = response.status_code
            if status_code != 200:
                raise Exception(f"etherscan: {module} {action} failed: {status_code} {status} {message} {result}")
            
            if status == "0":
                if message.startswith("No ") and message.endswith(" found"):
                    return no_found_return
                raise Exception(f"etherscan: {module} {action} failed: {status_code} {status} {message} {result}")
            
            return result
                
    async def get_eth_balance(self,
                          address: str,
                          tag: Literal["latest", "earliest", "pending"] = "latest",
                          chainid: Optional[int] = None,
                          on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespGetEthBalance:
        return await self._request("account", "balance", locals(), no_found_return="0")
    
    async def get_bridge_transactions(self,
                              address: str,
                              page: int = 1,
                              offset: int = 100,
                              chainid: Optional[int] = None,
                              on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespGetBridgeTxs:
        """
        Get bridge transactions for an address
        
        Note:
            Applicable to Gnosis (100), BTTC (199), and Polygon (137) only.
        """
        return await self._request("account", "txnbridge", locals())

    async def get_eth_balances(self,
                          addresses: list[str],
                          tag: Literal["latest", "earliest", "pending"] = "latest", 
                          chainid: Optional[int] = None,
                          on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespGetEthBalances:
        """
        Get ether balances for multiple addresses in a single call
        
        Args:
            addresses: List of addresses to get balances for (max 20 addresses per call)
            tag: Block parameter - "latest", "earliest" or "pending"
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
        """
        # Join addresses with comma
        address = ",".join(addresses)
        del locals()["addresses"]
        return await self._request("account", "balancemulti", locals())

    async def get_normal_transactions(self,
                               address: str,
                               startblock: int = 0,
                               endblock: int = 999_999_999_999,
                               page: int = 1,
                               offset: int = 100,
                               sort: Literal["asc", "desc"] = "asc",
                               chainid: Optional[int] = None,
                               on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespGetNormalTxs:
        """
        Get list of 'Normal' transactions by address
        
        Args:
            address: Address to get transactions for
            startblock: Start block number
            endblock: End block number  
            page: Page number for pagination
            offset: Number of transactions per page (max 10000)
            sort: Sort transactions by block number - "asc" or "desc"
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Note:
            This endpoint returns max 1000 records for free tier and 5000 for paid tier.
            Use startblock and endblock parameters to paginate through larger ranges.
        """
        return await self._request("account", "txlist", locals())

    async def get_internal_transactions_by_address(self,
                                 address: str,
                                 startblock: int = 0,
                                 endblock: int = 999_999_999_999,
                                 page: int = 1,
                                 offset: int = 100,
                                 sort: Literal["asc", "desc"] = "asc",
                                 chainid: Optional[int] = None,
                                 on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespGetInternalTxsByAddress:
        """
        Get list of 'Internal' transactions by address
        
        Args:
            address: Address to get transactions for
            startblock: Start block number
            endblock: End block number
            page: Page number for pagination  
            offset: Number of transactions per page (max 10000)
            sort: Sort transactions by block number - "asc" or "desc"
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Note:
            This endpoint returns max 10000 records.
            Use startblock and endblock parameters to paginate through larger ranges.
        """
        return await self._request("account", "txlistinternal", locals())
    
    async def get_internal_transactions_by_hash(self,
                                 txhash: str,
                                 chainid: Optional[int] = None,
                                 on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespGetInternalTxsByHash:
        """
        Get list of internal transactions by transaction hash
        
        Args:
            txhash: Tx hash to get internal transactions for
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Note:
            This endpoint returns max 10000 records.
        """
        return await self._request("account", "txlistinternal", locals())
    
    async def get_internal_transactions_by_block_range(self,
                                 startblock: int,
                                 endblock: int,
                                 page: int = 1,
                                 offset: int = 100,
                                 sort: Literal["asc", "desc"] = "asc", 
                                 chainid: Optional[int] = None,
                                 on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespGetInternalTxsByBlockRange:
        """
        Get list of internal transactions within a block range
        
        Args:
            startblock: Start block number
            endblock: End block number
            page: Page number for pagination
            offset: Number of transactions per page (max 10000)
            sort: Sort transactions by block number - "asc" or "desc"
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Note:
            This endpoint returns max 10000 records.
            Use page and offset parameters to paginate through results.
        """
        return await self._request("account", "txlistinternal", locals())

    async def get_erc20_token_transfers(self,
                                 address: Optional[str] = None,
                                 contractaddress: Optional[str] = None,
                                 page: int = 1,
                                 offset: int = 100,
                                 startblock: int = 0,
                                 endblock: int = 999_999_999_999,
                                 sort: Literal["asc", "desc"] = "asc",
                                 chainid: Optional[int] = None,
                                 on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespGetERC20TokenTransfers:
        """
        Get list of ERC-20 token transfers by address and/or contract address
        
        Args:
            address: Address to get token transfers for (optional)
            contractaddress: Token contract address to filter by (optional) 
            page: Page number for pagination
            offset: Number of transfers per page (max 10000)
            startblock: Start block number
            endblock: End block number
            sort: Sort transfers by block number - "asc" or "desc"
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Note:
            This endpoint returns max 10000 records.
            Use page and offset parameters to paginate through results.
            At least one of address or contractaddress must be provided.
        """
        if address is None and contractaddress is None:
            raise ValueError("Either address or contractaddress must be provided")
        
        if address is None:
            del locals()["address"]
        if contractaddress is None:
            del locals()["contractaddress"]
            
        return await self._request("account", "tokentx", locals())
    
    async def get_erc721_token_transfers(self,
                                 address: Optional[str] = None,
                                 contractaddress: Optional[str] = None,
                                 page: int = 1,
                                 offset: int = 100,
                                 startblock: int = 0,
                                 endblock: int = 999_999_999_999,
                                 sort: Literal["asc", "desc"] = "asc",
                                 chainid: Optional[int] = None,
                                 on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespGetERC721TokenTransfers:
        """
        Get list of ERC-721 (NFT) token transfers by address and/or contract address
        
        Args:
            address: Address to get token transfers for (optional)
            contractaddress: Token contract address to filter by (optional)
            page: Page number for pagination 
            offset: Number of transfers per page (max 10000)
            startblock: Start block number
            endblock: End block number
            sort: Sort transfers by block number - "asc" or "desc"
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Note:
            This endpoint returns max 10000 records.
            Use page and offset parameters to paginate through results.
            At least one of address or contractaddress must be provided.
        """
        if address is None and contractaddress is None:
            raise ValueError("Either address or contractaddress must be provided")
        
        if address is None:
            del locals()["address"]
        if contractaddress is None:
            del locals()["contractaddress"]
            
        return await self._request("account", "tokennfttx", locals())
    
    async def get_erc1155_token_transfers(self,
                                 address: Optional[str] = None,
                                 contractaddress: Optional[str] = None,
                                 page: int = 1,
                                 offset: int = 100,
                                 startblock: int = 0,
                                 endblock: int = 999_999_999_999,
                                 sort: Literal["asc", "desc"] = "asc",
                                 chainid: Optional[int] = None,
                                 on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespGetERC1155TokenTransfers:
        """
        Get list of ERC-1155 (Multi Token Standard) token transfers by address and/or contract address
        
        Args:
            address: Address to get token transfers for (optional)
            contractaddress: Token contract address to filter by (optional)
            page: Page number for pagination 
            offset: Number of transfers per page (max 10000)
            startblock: Start block number
            endblock: End block number
            sort: Sort transfers by block number - "asc" or "desc"
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Note:
            This endpoint returns max 10000 records.
            Use page and offset parameters to paginate through results.
            At least one of address or contractaddress must be provided.
        """
        if address is None and contractaddress is None:
            raise ValueError("Either address or contractaddress must be provided")
        
        if address is None:
            del locals()["address"]
        if contractaddress is None:
            del locals()["contractaddress"]
            
        return await self._request("account", "token1155tx", locals())

    async def get_address_funded_by(self,
                                  address: str,
                                  chainid: Optional[int] = None,
                                  on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespAddressFundedBy:
        """
        Get the address that funded the specified address and its relative age.
        
        Args:
            address: The address to check funding source for
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Dictionary containing funding address details including:
            - block: Block number when funding occurred
            - timeStamp: Unix timestamp of funding
            - fundingAddress: Address that provided the funding
            - fundingTxn: Tx hash of the funding
            - value: Amount funded in wei
        """
        return await self._request("account", "fundedby", locals(), no_found_return={})
    
    async def get_blocks_validated_by_address(self,
                                            address: str,
                                            blocktype: str = "blocks",
                                            page: int = 1,
                                            offset: int = 10,
                                            chainid: Optional[int] = None,
                                            on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespBlocksValidatedByAddress:
        """
        Get list of blocks validated by an address.
        
        Args:
            address: Address to get validated blocks for
            blocktype: Block type - "blocks" for canonical blocks or "uncles" for uncle blocks only
            page: Page number for pagination
            offset: Number of blocks per page
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of validated blocks containing:
            - blockNumber: Block number
            - timeStamp: Unix timestamp when block was mined
            - blockReward: Block reward in wei
        """
        return await self._request("account", "getminedblocks", locals())

    async def get_beacon_chain_withdrawals(self,
                                         address: str,
                                         startblock: int = 0,
                                         endblock: int = 999_999_999_999,
                                         page: int = 1,
                                         offset: int = 100,
                                         sort: str = "asc",
                                         chainid: Optional[int] = None,
                                         on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespBeaconChainWithdrawals:
        """
        Get list of beacon chain withdrawals made to an address.
        
        Args:
            address: Address to get withdrawals for
            startblock: Starting block number to search from
            endblock: Ending block number to search to
            page: Page number for pagination
            offset: Number of withdrawals per page
            sort: Sort by ascending ("asc") or descending ("desc")
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of beacon chain withdrawals containing:
            - withdrawalIndex: Index of the withdrawal
            - validatorIndex: Index of the validator
            - address: Withdrawal address
            - amount: Amount withdrawn in Gwei
            - blockNumber: Block number of withdrawal
            - timestamp: Unix timestamp of withdrawal
        """
        return await self._request("account", "txsBeaconWithdrawal", locals())
    
    async def get_eth_balance_by_block_number(self,
                                               address: str,
                                               blockno: int,
                                               chainid: Optional[int] = None,
                                               on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespEthBalanceByBlockNumber:
        """
        Get historical Eth balance for a single address at a specific block number.
        
        Note: This endpoint is throttled to 2 calls/second regardless of API Pro tier.
        
        Args:
            address: Address to get balance for
            blockno: Block number to get balance at
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Balance in wei as a string
        """
        return await self._request("account", "balancehistory", locals(), no_found_return="0")


    async def get_contract_abi(self,
                             address: str,
                             chainid: Optional[int] = None,
                             on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespContractABI:
        """
        Get the Contract Application Binary Interface (ABI) of a verified smart contract.
        
        Args:
            address: The contract address that has a verified source code
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Contract ABI as a string
        """
        return await self._request("contract", "getabi", locals(), no_found_return="")

    async def get_contract_source_code(self,
                                     address: str, 
                                     chainid: Optional[int] = None,
                                     on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespContractSourceCodes:
        """
        Get the Solidity source code of a verified smart contract.
        
        Args:
            address: The contract address that has a verified source code
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List containing contract source code details including:
            - SourceCode: The contract source code
            - ABI: Contract ABI
            - ContractName: Name of the contract
            - CompilerVersion: Version of compiler used
            - OptimizationUsed: Whether optimization was used (1/0)
            - Runs: Number of optimization runs
            - ConstructorArguments: Constructor arguments
            - EVMVersion: EVM version
            - Library: Library used
            - LicenseType: License type
            - Proxy: Whether contract is proxy (0/1)
            - Implementation: Implementation address if proxy
            - SwarmSource: Swarm source
            - SimilarMatch: Similar contract match
        """
        return await self._request("contract", "getsourcecode", locals())
    
    async def get_contract_creator_and_creation(self,
                                  contractaddresses: list[str],
                                  chainid: Optional[int] = None,
                                  on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespContractCreationAndCreations:
        """
        Get the creator address and creation transaction hash for contracts.
        
        Args:
            addresses: Contract address or list of addresses (up to 5)
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List containing contract creation details including:
            - contractAddress: The contract address
            - contractCreator: Address that deployed the contract  
            - txHash: Tx hash of contract creation
        """
        # Validate max 5 addresses
        if len(contractaddresses) > 5:
            raise ValueError("Maximum 5 contract addresses allowed")
            
        # Join addresses with comma
        contractaddresses = ",".join(contractaddresses)
        
        return await self._request("contract", "getcontractcreation", locals())
    
    async def verify_source_code(self,
                               sourceCode: str,
                               contractaddress: str,
                               contractname: str,
                               compilerversion: str,
                               codeformat: str = "solidity-single-file",
                               constructorArguements: Optional[str] = None,
                               compilermode: Optional[str] = None,
                               zksolcVersion: Optional[str] = None,
                               chainid: Optional[int] = None,
                               on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespVerifySourceCode:
        """
        Submit contract source code for verification.
        
        Args:
            sourceCode: The Solidity source code
            contractaddress: The deployed contract address
            contractname: Contract name (e.g. "contracts/Verified.sol:Verified")
            compilerversion: Compiler version (e.g. "v0.8.24+commit.e11b9ed9")
            codeformat: Source code format ("solidity-single-file" or "solidity-standard-json-input")
            constructorArguements: Optional constructor arguments
            compilermode: Compiler mode (e.g. "solc/zksync" for ZK Stack)
            zksolcVersion: zkSolc version for ZK Stack (e.g. "v1.3.14")
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Response containing verification submission details
            
        Raises:
            ValueError: If invalid parameters are provided
        """
        return await self._request("contract", "verifysourcecode", locals(), 
                                 method="POST", no_found_return="")
        
    async def verify_vyper_source_code(self,
                                     sourceCode: str,
                                     contractaddress: str, 
                                     contractname: str,
                                     compilerversion: str,
                                     constructorArguments: Optional[str] = None,
                                     optimizationUsed: int = 0,
                                     chainid: Optional[int] = None,
                                     on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespVerifySourceCode:
        """
        Submit Vyper contract source code for verification.
        
        Args:
            sourceCode: The Vyper source code in JSON format
            contractaddress: The deployed contract address
            contractname: Contract name (e.g. "contracts/Verified.vy:Verified") 
            compilerversion: Vyper compiler version (e.g. "vyper:0.4.0")
            constructorArguments: Optional constructor arguments
            optimizationUsed: Whether optimization was used (0=no, 1=yes)
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Response containing verification submission details
            
        Raises:
            ValueError: If invalid parameters are provided
        """
        locals()['codeformat'] = 'vyper-json'
        
        return await self._request("contract", "verifysourcecode", locals(),
                                 method="POST", no_found_return="")
        
    async def verify_stylus_source_code(self,
                                      sourceCode: str,
                                      contractaddress: str,
                                      contractname: str,
                                      compilerversion: str,
                                      licenseType: int,
                                      chainid: Optional[int] = None,
                                      on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespVerifyStylusSourceCode:
        """
        Submit Stylus contract source code for verification.
        
        Args:
            sourceCode: The Github link to the source code (e.g. "https://github.com/OffchainLabs/stylus-hello-world")
            contractaddress: The deployed contract address
            contractname: Contract name (e.g. "stylus_hello_world")
            compilerversion: Stylus compiler version (e.g. "stylus:0.5.3")
            licenseType: Open source license type (e.g. 3 for MIT)
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Response containing verification submission details
            
        Raises:
            ValueError: If invalid parameters are provided
        """
        locals()['codeformat'] = 'stylus'
        
        return await self._request("contract", "verifysourcecode", locals(),
                                 method="POST", no_found_return="")
        
    async def check_source_code_verification_status(self,
                                                  guid: str,
                                                  chainid: Optional[int] = None,
                                                  on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespCheckSourceCodeVerificationStatus:
        """
        Check the verification status of a submitted source code verification request.
        
        Args:
            guid: The unique GUID received from the verification request
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Response containing verification status
            
        Raises:
            ValueError: If invalid parameters are provided
        """
        return await self._request("contract", "checkverifystatus", locals(), no_found_return="")
    
    async def get_contract_execution_status(self,
                                          txhash: str,
                                          chainid: Optional[int] = None,
                                          on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespContractExecutionStatus:
        """
        Get the status code of a contract execution.
        
        Args:
            txhash: The transaction hash to check the execution status
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Response containing contract execution status
            
        Raises:
            ValueError: If invalid parameters are provided
        """
        return await self._request("transaction", "getstatus", locals(), no_found_return={})
    
    async def get_transaction_receipt_status(self,
                                           txhash: str,
                                           chainid: Optional[int] = None,
                                           on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespCheckTxReceiptStatus:
        """
        Get the status code of a transaction execution.
        
        Args:
            txhash: The transaction hash to check the execution status
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Response containing transaction receipt status
            
        Note:
            Only applicable for post Byzantium Fork transactions.
            
        Raises:
            ValueError: If invalid parameters are provided
        """
        return await self._request("transaction", "gettxreceiptstatus", locals(), no_found_return={})
    
    async def get_block_and_uncle_rewards(self,
                                         blockno: int,
                                         chainid: Optional[int] = None,
                                         on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespBlockReward:
        """
        Get the block reward and 'Uncle' block rewards for a given block number.
        
        Args:
            blockno: The block number to check block rewards for
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Response containing block and uncle rewards information
            
        Raises:
            ValueError: If invalid parameters are provided
        """
        return await self._request("block", "getblockreward", locals(), no_found_return={})
    
    async def get_block_transactions_count(self,
                                         blockno: int,
                                         chainid: Optional[int] = None,
                                         on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespBlockTxsCountByBlockNo:
        """
        Get the number of transactions in a specified block.
        
        Args:
            blockno: The block number to get transaction count for
            chainid: Chain ID. If None, uses Etheum mainnet. Only supported on Etheum mainnet (chainid=1)
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Response containing transaction count details including:
            - block: Block number
            - txsCount: Number of normal transactions
            - internalTxsCount: Number of internal transactions
            - erc20TxsCount: Number of ERC20 token transfers
            - erc721TxsCount: Number of ERC721 token transfers
            - erc1155TxsCount: Number of ERC1155 token transfers
            
        Raises:
            ValueError: If invalid parameters are provided or if chainid is not 1
        """
        # Validate chainid is Etheum mainnet
        if chainid is not None and chainid != 1:
            raise ValueError("This endpoint is only supported on Etheum mainnet (chainid=1)")
            
        return await self._request("block", "getblocktxnscount", locals(), no_found_return={})
    
    async def get_block_countdown_time(self,
                                     blockno: int,
                                     chainid: Optional[int] = None,
                                     on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespEstimateBlockCountdownTimeByBlockNo:
        """
        Get estimated time remaining until a future block is mined.
        
        Args:
            blockno: The future block number to estimate countdown for
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Response containing countdown details including:
            - CurrentBlock: Current block number
            - CountdownBlock: Target block number
            - RemainingBlock: Number of blocks remaining
            - EstimateTimeInSec: Estimated time in seconds until target block
            
        Raises:
            ValueError: If invalid parameters are provided
        """
        return await self._request("block", "getblockcountdown", locals(), no_found_return={})
    
    async def get_block_number_by_timestamp(self,
                                          timestamp: int,
                                          closest: Literal["before", "after"],
                                          chainid: Optional[int] = None,
                                          on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespBlockNumber:
        """
        Get the block number that was mined at a certain timestamp.
        
        Args:
            timestamp: Unix timestamp in seconds
            closest: Return closest block "before" or "after" the timestamp
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Block number that was mined closest to the provided timestamp
            
        Raises:
            ValueError: If invalid parameters are provided
        """
        return await self._request("block", "getblocknobytime", locals(), no_found_return=-1)
    
    async def get_daily_avg_block_sizes(self,
                                      startdate: str,
                                      enddate: str,
                                      sort: Literal["asc", "desc"] = "asc",
                                      chainid: Optional[int] = None,
                                      on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespDailyAvgBlockSizes:
        """
        Get daily average block size within a date range.
        
        Args:
            startdate: Starting date in yyyy-MM-dd format (e.g. "2019-02-01")
            enddate: Ending date in yyyy-MM-dd format (e.g. "2019-02-28")
            sort: Sort order - "asc" for ascending, "desc" for descending
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of daily average block sizes containing:
            - UTCDate: Date in yyyy-MM-dd format
            - unixTimeStamp: Unix timestamp
            - blockSize_bytes: Average block size in bytes
            
        Raises:
            ValueError: If invalid parameters are provided
        """
        return await self._request("stats", "dailyavgblocksize", locals())
    
    async def get_daily_block_count_rewards(self,
                                    startdate: str,
                                    enddate: str,
                                    sort: Literal["asc", "desc"] = "asc",
                                    chainid: Optional[int] = None,
                                    on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespDailyBlockRewards:
        """
        Get daily block count and rewards within a date range.
        
        Args:
            startdate: Starting date in yyyy-MM-dd format (e.g. "2019-02-01")
            enddate: Ending date in yyyy-MM-dd format (e.g. "2019-02-28") 
            sort: Sort order - "asc" for ascending, "desc" for descending
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of daily block rewards containing:
            - UTCDate: Date in yyyy-MM-dd format
            - unixTimeStamp: Unix timestamp
            - blockCount: Number of blocks mined
            - blockRewards_Eth: Total block rewards in ETH
            
        Raises:
            ValueError: If invalid parameters are provided
        """
        return await self._request("stats", "dailyblkcount", locals())
    
    async def get_daily_block_rewards(self,
                                          startdate: str,
                                          enddate: str,
                                          sort: Literal["asc", "desc"] = "asc",
                                          chainid: Optional[int] = None,
                                          on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespDailyBlockCountRewards:
        """
        Get daily block rewards distributed to miners within a date range.
        
        Args:
            startdate: Starting date in yyyy-MM-dd format (e.g. "2019-02-01")
            enddate: Ending date in yyyy-MM-dd format (e.g. "2019-02-28")
            sort: Sort order - "asc" for ascending, "desc" for descending
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of daily block rewards containing:
            - UTCDate: Date in yyyy-MM-dd format
            - unixTimeStamp: Unix timestamp
            - blockRewards_Eth: Total block rewards in ETH
            
        Raises:
            ValueError: If invalid parameters are provided
        """
        return await self._request("stats", "dailyblockrewards", locals())
    
    async def get_daily_avg_block_time(self,
                                     startdate: str,
                                     enddate: str,
                                     sort: Literal["asc", "desc"] = "asc",
                                     chainid: Optional[int] = None,
                                     on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespDailyAvgTimeBlockMineds:
        """
        Get daily average time for a block to be included in the blockchain.
        
        Args:
            startdate: Starting date in yyyy-MM-dd format (e.g. "2019-02-01")
            enddate: Ending date in yyyy-MM-dd format (e.g. "2019-02-28")
            sort: Sort order - "asc" for ascending, "desc" for descending
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of daily average block times containing:
            - UTCDate: Date in yyyy-MM-dd format
            - unixTimeStamp: Unix timestamp
            - blockTime_sec: Average time in seconds for block to be mined
            
        Raises:
            ValueError: If invalid parameters are provided
        """
        return await self._request("stats", "dailyavgblocktime", locals())
    
    async def get_daily_uncle_block_count_and_rewards(self,
                                                     startdate: str,
                                                     enddate: str,
                                                     sort: Literal["asc", "desc"] = "asc",
                                                     chainid: Optional[int] = None,
                                                     on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespDailyUncleBlockCountAndRewards:
        """
        Get daily uncle block count and rewards.
        
        Args:
            startdate: Starting date in yyyy-MM-dd format (e.g. "2019-02-01")
            enddate: Ending date in yyyy-MM-dd format (e.g. "2019-02-28")
            sort: Sort order - "asc" for ascending, "desc" for descending
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of daily uncle block stats containing:
            - UTCDate: Date in yyyy-MM-dd format
            - unixTimeStamp: Unix timestamp
            - uncleBlockCount: Number of uncle blocks mined
            - uncleBlockRewards_Eth: Total uncle block rewards in ETH
            
        Raises:
            ValueError: If invalid parameters are provided
        """
        return await self._request("stats", "dailyuncleblkcount", locals())
    
    async def get_event_logs_by_address(self,
                                       address: str,
                                       from_block: Optional[int] = None,
                                       to_block: Optional[int] = None,
                                       page: Optional[int] = None,
                                       offset: Optional[int] = None,
                                       chainid: Optional[int] = None,
                                       on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespEventLogsByAddress:
        """
        Get event logs from an address, with optional filtering by block range.
        
        Args:
            address: The address to check for logs
            from_block: Starting block number to search for logs
            to_block: Ending block number to search for logs
            page: Page number for pagination
            offset: Number of records per page (max 1000)
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of event logs containing:
            - address: Contract address
            - topics: List of event topics
            - data: Event data
            - blockNumber: Block number (hex)
            - timeStamp: Block timestamp (hex)
            - gasPrice: Gas price (hex)
            - gasUsed: Gas used (hex)
            - logIndex: Log index in block (hex)
            - transactionHash: Tx hash
            - transactionIndex: Tx index in block (hex)
            
        Raises:
            ValueError: If invalid parameters are provided
        """
        return await self._request("logs", "getLogs", locals())
    
    async def get_event_logs_by_topics(self,
                                      from_block: int = 0,
                                      to_block: int = 999_999_999_999,
                                      page: int = 1,
                                      offset: int = 1000,
                                      topic0: Optional[str] = None,
                                      topic1: Optional[str] = None,
                                      topic2: Optional[str] = None,
                                      topic3: Optional[str] = None,
                                      topic0_1_opr: Optional[str] = None,
                                      topic0_2_opr: Optional[str] = None,
                                      topic0_3_opr: Optional[str] = None,
                                      topic1_2_opr: Optional[str] = None,
                                      topic1_3_opr: Optional[str] = None,
                                      topic2_3_opr: Optional[str] = None,
                                      chainid: Optional[int] = None,
                                      on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespEventLogsByTopics:
        """
        Get event logs filtered by topics in a block range.
        
        Args:
            from_block: Starting block number to search for logs
            to_block: Ending block number to search for logs
            topic0: First topic to filter by
            topic1: Second topic to filter by
            topic2: Third topic to filter by
            topic3: Fourth topic to filter by
            topic0_1_opr: Operator ('and'|'or') between topic0 & topic1
            topic0_2_opr: Operator ('and'|'or') between topic0 & topic2
            topic0_3_opr: Operator ('and'|'or') between topic0 & topic3
            topic1_2_opr: Operator ('and'|'or') between topic1 & topic2
            topic1_3_opr: Operator ('and'|'or') between topic1 & topic3
            topic2_3_opr: Operator ('and'|'or') between topic2 & topic3
            page: Page number for pagination
            offset: Number of records per page (max 1000)
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of event logs containing:
            - address: Contract address
            - topics: List of event topics
            - data: Event data
            - blockNumber: Block number (hex)
            - timeStamp: Block timestamp (hex)
            - gasPrice: Gas price (hex)
            - gasUsed: Gas used (hex)
            - logIndex: Log index in block (hex)
            - transactionHash: Tx hash
            - transactionIndex: Tx index in block (hex)
            
        Raises:
            ValueError: If invalid parameters are provided
        """
        return await self._request("logs", "getLogs", locals())
    
    async def get_event_logs_by_address_filtered_by_topics(self,
                                 from_block: int,
                                 to_block: int,
                                 address: str,
                                 page: int = 1,
                                 offset: int = 1000,
                                 topic0: Optional[str] = None,
                                 topic1: Optional[str] = None,
                                 topic2: Optional[str] = None,
                                 topic3: Optional[str] = None,
                                 topic0_1_opr: Optional[str] = None,
                                 topic0_2_opr: Optional[str] = None,
                                 topic0_3_opr: Optional[str] = None,
                                 topic1_2_opr: Optional[str] = None,
                                 topic1_3_opr: Optional[str] = None,
                                 topic2_3_opr: Optional[str] = None,
                                 chainid: Optional[int] = None,
                                 on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespEventLogsByTopics:
        """
        Get event logs from a specific address filtered by topics and block range.
        
        Args:
            from_block: Starting block number to search for logs
            to_block: Ending block number to search for logs
            address: Contract address to get logs from
            topic0: First topic to filter by
            topic1: Second topic to filter by  
            topic2: Third topic to filter by
            topic3: Fourth topic to filter by
            topic0_1_opr: Operator ('and'|'or') between topic0 & topic1
            topic0_2_opr: Operator ('and'|'or') between topic0 & topic2
            topic0_3_opr: Operator ('and'|'or') between topic0 & topic3
            topic1_2_opr: Operator ('and'|'or') between topic1 & topic2
            topic1_3_opr: Operator ('and'|'or') between topic1 & topic3
            topic2_3_opr: Operator ('and'|'or') between topic2 & topic3
            page: Page number for pagination (max 1000 records per query)
            offset: Number of records per page (max 1000)
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of event logs containing:
            - address: Contract address
            - topics: List of event topics
            - data: Event data
            - blockNumber: Block number (hex)
            - timeStamp: Block timestamp (hex)
            - gasPrice: Gas price (hex)
            - gasUsed: Gas used (hex)
            - logIndex: Log index in block (hex)
            - transactionHash: Tx hash
            - transactionIndex: Tx index in block (hex)
            
        Raises:
            ValueError: If invalid parameters are provided
        """
        return await self._request("logs", "getLogs", locals())
    
    async def rpc_eth_block_number(self,
                                 chainid: Optional[int] = None,
                                 on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespEthBlockNumberHex:
        """
        Get the number of the most recent block.
        
        Args:
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Hex string of the most recent block number
        """
        return await self._request("proxy", "eth_blockNumber", locals(), no_found_return={})
    
    async def rpc_eth_block_by_number(self,
                                    tag: str,
                                    boolean: bool = True,
                                    chainid: Optional[int] = None,
                                    on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespEthBlock:
        """
        Get information about a block by block number.
        
        Args:
            tag: Block number in hex (e.g. "0xC36B3C")
            boolean: If True, returns full transaction objects. If False, returns only transaction hashes
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Dictionary containing block information:
            - number: Block number
            - hash: Block hash
            - parentHash: Parent block hash
            - nonce: Block nonce
            - sha3Uncles: Uncle blocks hash
            - logsBloom: Bloom filter for block logs
            - transactionsRoot: Txs trie root
            - stateRoot: State trie root
            - receiptsRoot: Receipts trie root
            - miner: Miner address
            - difficulty: Block difficulty
            - totalDifficulty: Total chain difficulty
            - extraData: Extra block data
            - size: Block size in bytes
            - gasLimit: Block gas limit
            - gasUsed: Total gas used
            - timestamp: Block timestamp
            - transactions: List of transactions (full objects if boolean=True, hashes if False)
            - uncles: List of uncle block hashes
        """
        return await self._request("proxy", "eth_getBlockByNumber", locals(), no_found_return={})
    
    async def rpc_eth_uncle_by_block_number_and_index(self,
                                                     tag: str,
                                                     index: str,
                                                     chainid: Optional[int] = None,
                                                     on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespEthBlock:
        """
        Get information about an uncle block by block number and index.
        
        Args:
            tag: Block number in hex (e.g. "0xC36B3C")
            index: Position of the uncle's index in the block, in hex (e.g. "0x0")
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Dictionary containing uncle block information:
            - number: Block number
            - hash: Block hash
            - parentHash: Parent block hash
            - nonce: Block nonce
            - sha3Uncles: Uncle blocks hash
            - logsBloom: Bloom filter for block logs
            - transactionsRoot: Txs trie root
            - stateRoot: State trie root
            - receiptsRoot: Receipts trie root
            - miner: Miner address
            - difficulty: Block difficulty
            - totalDifficulty: Total chain difficulty
            - extraData: Extra block data
            - size: Block size in bytes
            - gasLimit: Block gas limit
            - gasUsed: Total gas used
            - timestamp: Block timestamp
            - transactions: List of transaction hashes
            - uncles: List of uncle block hashes
        """
        return await self._request("proxy", "eth_getUncleByBlockNumberAndIndex", locals(), no_found_return={})
    
    async def rpc_eth_block_transaction_count_by_number(self,
                                                   tag: str,
                                                   chainid: Optional[int] = None,
                                                   on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> int:
        """
        Get the number of transactions in a block by block number.
        
        Args:
            tag: Block number in hex (e.g. "0x10FB78")
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Number of transactions in the block
        """
        return await self._request("proxy", "eth_getBlockTxCountByNumber", locals(), no_found_return=0)
    
    async def rpc_eth_transaction_by_hash(self,
                                    txhash: str,
                                    chainid: Optional[int] = None,
                                    on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespEthTx:
        """
        Get information about a transaction by its hash.
        
        Args:
            txhash: Tx hash (e.g. "0xbc78ab8a9e9a0bca7d0321a27b2c03addeae08ba81ea98b03cd3dd237eabed44")
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Dictionary containing transaction information:
            - hash: Tx hash
            - nonce: Number of transactions made by sender prior to this one
            - blockHash: Hash of block containing this transaction
            - blockNumber: Block number containing this transaction
            - transactionIndex: Integer of the transaction's index position in the block
            - from: Address of the sender
            - to: Address of the receiver
            - value: Value transferred in Wei
            - gasPrice: Gas price provided by the sender in Wei
            - gas: Gas provided by the sender
            - input: Data sent along with the transaction
        """
        return await self._request("proxy", "eth_getTxByHash", locals(), no_found_return={})
    
    async def rpc_eth_transaction_by_block_number_and_index(self,
                                                       tag: str,
                                                       index: str,
                                                       chainid: Optional[int] = None,
                                                       on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespEthTx:
        """
        Get information about a transaction by block number and transaction index position.
        
        Args:
            tag: Block number in hex (e.g. "0x10FB78")
            index: Tx index position in hex (e.g. "0x0")
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Dictionary containing transaction information:
            - hash: Tx hash
            - nonce: Number of transactions made by sender prior to this one
            - blockHash: Hash of block containing this transaction
            - blockNumber: Block number containing this transaction
            - transactionIndex: Integer of the transaction's index position in the block
            - from: Address of the sender
            - to: Address of the receiver
            - value: Value transferred in Wei
            - gasPrice: Gas price provided by the sender in Wei
            - gas: Gas provided by the sender
            - input: Data sent along with the transaction
        """
        return await self._request("proxy", "eth_getTxByBlockNumberAndIndex", locals(), no_found_return={})
    
    async def rpc_eth_transaction_count(self,
                                      address: str,
                                      tag: Literal["latest", "earliest", "pending"] = "latest",
                                      chainid: Optional[int] = None,
                                      on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespEthTxCount:
        """
        Get the number of transactions performed by an address.
        
        Args:
            address: Address to get transaction count for
            tag: Block parameter - "latest", "earliest" or "pending"
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Hex string of the number of transactions performed by this address
        """
        return await self._request("proxy", "eth_getTxCount", locals(), no_found_return={})
    
    async def rpc_eth_send_raw_transaction(self,
                                         hex: str,
                                         chainid: Optional[int] = None,
                                         on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespEthSendRawTx:
        """
        Submit a pre-signed transaction for broadcast to the Etheum network.
        
        Args:
            hex: Signed raw transaction data to broadcast
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Tx hash of the broadcasted transaction
            
        Note:
            For long hex strings, the request will automatically be sent as POST
        """
        return await self._request("proxy", "eth_sendRawTx", locals(), no_found_return={}, method="POST")
    
    async def rpc_eth_transaction_receipt(self,
                                        txhash: str,
                                        chainid: Optional[int] = None,
                                        on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespEthTxReceipt:
        """
        Returns the receipt of a transaction by transaction hash.
        
        Args:
            txhash: Hash of the transaction
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Tx receipt object containing:
            - transactionHash: Hash of the transaction
            - transactionIndex: Integer of the transactions index position in the block
            - blockHash: Hash of the block where this transaction was in
            - blockNumber: Block number where this transaction was in
            - from: Address of the sender
            - to: Address of the receiver
            - cumulativeGasUsed: The total amount of gas used when this transaction was executed in the block
            - gasUsed: The amount of gas used by this specific transaction alone
            - contractAddress: The contract address created, if the transaction was a contract creation
            - logs: Array of log objects generated by this transaction
            - logsBloom: Bloom filter for light clients to quickly retrieve related logs
            - status: Either 1 (success) or 0 (failure)
        """
        return await self._request("proxy", "eth_getTxReceipt", locals(), no_found_return={})
    
    async def rpc_eth_call(self,
                          to: str,
                          data: str,
                          tag: Literal["latest", "earliest", "pending"] = "latest",
                          chainid: Optional[int] = None,
                          on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespEthCall:
        """
        Executes a new message call immediately without creating a transaction on the block chain.
        
        Args:
            to: Address to interact with
            data: Hash of the method signature and encoded parameters
            tag: Block parameter - "latest", "earliest" or "pending"
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            The return value of the executed contract call
            
        Note:
            The gas parameter is capped at 2x the current block gas limit
        """
        return await self._request("proxy", "eth_call", locals(), no_found_return={})
    
    async def rpc_eth_get_code(self,
                              address: str,
                              tag: Literal["latest", "earliest", "pending"] = "latest",
                              chainid: Optional[int] = None,
                              on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespEthGetCode:
        """
        Returns code at a given address.
        
        Args:
            address: Address to get code from
            tag: Block parameter - "latest", "earliest" or "pending"
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            The code from the given address
        """
        return await self._request("proxy", "eth_getCode", locals(), no_found_return={})
    
    async def rpc_eth_get_storage_at(self,
                                    address: str,
                                    position: str,
                                    tag: Literal["latest", "earliest", "pending"] = "latest",
                                    chainid: Optional[int] = None,
                                    on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespEthGetStorageAt:
        """
        Returns the value from a storage position at a given address.
        
        Args:
            address: Address to get storage from
            position: Position in storage (hex string)
            tag: Block parameter - "latest", "earliest" or "pending"
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            The value at the given storage position
            
        Note:
            This endpoint is experimental and may have potential issues
        """
        return await self._request("proxy", "eth_getStorageAt", locals(), no_found_return={})
    
    async def rpc_eth_get_gas_price(self,
                                   chainid: Optional[int] = None,
                                   on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespEthGetGasPrice:
        """
        Returns the current price per gas in wei.
        
        Args:
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            The current gas price in wei (hex string)
        """
        return await self._request("proxy", "eth_gasPrice", locals(), no_found_return={})
    
    async def rpc_eth_estimate_gas(self,
                                  to: str,
                                  data: str,
                                  value: Optional[str] = None,
                                  gas: Optional[str] = None,
                                  gas_price: Optional[str] = None,
                                  chainid: Optional[int] = None,
                                  on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespEthEstimateGas:
        """
        Makes a call or transaction, which won't be added to the blockchain and returns the used gas.
        
        Args:
            to: Address to interact with
            data: Hash of the method signature and encoded parameters
            value: Value sent in transaction (hex string)
            gas: Amount of gas provided for transaction (hex string)
            gas_price: Gas price in wei (hex string)
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            The estimated gas usage
            
        Note:
            The gas parameter is capped at 2x the current block gas limit.
            Post EIP-1559, the gasPrice must be higher than the block's baseFeePerGas.
        """
        params = {k: v for k, v in locals().items() if v is not None and k not in ['self', 'on_limit_exceeded']}
        if 'gas_price' in params:
            params['gasPrice'] = params.pop('gas_price')
        return await self._request("proxy", "eth_estimateGas", params, no_found_return={})
    
    async def get_erc20_total_supply(self,
                                    contractaddress: str,
                                    chainid: Optional[int] = None,
                                    on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespERC20TotalSupply:
        """
        Returns the current amount of an ERC-20 token in circulation.
        
        Args:
            contractaddress: The contract address of the ERC-20 token
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            The total supply of the ERC-20 token (hex string)
        """
        return await self._request("stats", "tokensupply", locals(), no_found_return="0")
    
    async def get_erc20_account_balance(self,
                                       contractaddress: str,
                                       address: str,
                                       chainid: Optional[int] = None,
                                       on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespERC20AccountBalance:
        """
        Returns the current balance of an ERC-20 token of an address.
        
        Args:
            contractaddress: The contract address of the ERC-20 token
            address: The address to check for token balance
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            The token balance of the address (hex string)
        """
        return await self._request("account", "tokenbalance", locals(), no_found_return="0")
    
    async def get_erc20_historical_total_supply(self,
                                               contractaddress: str,
                                               blockno: int,
                                               chainid: Optional[int] = None,
                                               on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespERC20HistoricalTotalSupply:
        """
        Returns the amount of an ERC-20 token in circulation at a certain block height.
        
        Args:
            contractaddress: The contract address of the ERC-20 token
            blockno: The block number to check total supply for
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            The historical total supply of the ERC-20 token at the given block (hex string)
            
        Note:
            This endpoint is throttled to 2 calls/second regardless of API Pro tier.
        """
        return await self._request("stats", "tokensupplyhistory", locals(), no_found_return="0")
    
    async def get_erc20_historical_account_balance(self,
                                                  contractaddress: str,
                                                  address: str,
                                                  blockno: int,
                                                  chainid: Optional[int] = None,
                                                  on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespERC20HistoricalAccountBalance:
        """
        Returns the balance of an ERC-20 token of an address at a certain block height.
        
        Args:
            contractaddress: The contract address of the ERC-20 token
            address: The address to check for token balance
            blockno: The block number to check balance for
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            The historical token balance of the address at the given block (hex string)
            
        Note:
            This endpoint is throttled to 2 calls/second regardless of API Pro tier.
        """
        return await self._request("account", "tokenbalancehistory", locals(), no_found_return="0")
    
    async def get_erc20_holders(self,
                               contractaddress: str,
                               page: int = 1,
                               offset: int = 100,
                               chainid: Optional[int] = None,
                               on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespERC20Holders:
        """
        Returns the current ERC20 token holders and number of tokens held.
        
        Args:
            contractaddress: The contract address of the ERC-20 token
            page: The page number for paginated results
            offset: Number of records to return per page
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of token holders with their addresses and token quantities
        """
        return await self._request("token", "tokenholderlist", locals())
    
    async def get_erc20_holder_count(self,
                                    contractaddress: str,
                                    chainid: Optional[int] = None,
                                    on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespERC20HolderCount:
        """
        Returns the total number of holders for an ERC-20 token.
        
        Args:
            contractaddress: The contract address of the ERC-20 token
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            The total number of token holders (hex string)
        """
        return await self._request("token", "tokenholdercount", locals(), no_found_return="0")
    
    async def get_top_token_holders(self,
                                   contractaddress: str,
                                   offset: int = 100,
                                   chainid: Optional[int] = None,
                                   on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespTopTokenHolders:
        """
        Returns the top token holders of an ERC-20 token.
        
        Args:
            contractaddress: The contract address of the ERC-20 token
            offset: Number of top holders to return (max 1000)
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of top token holders with their addresses, quantities and address types
            
        Note:
            This endpoint is throttled to 2 calls/second regardless of API Pro tier.
            This beta endpoint is only available on Etheum mainnet.
        """
        if offset > 1000:
            raise ValueError("offset cannot exceed 1000")
        return await self._request("token", "topholders", locals())
    
    async def get_token_info(self,
                            contractaddress: str,
                            chainid: Optional[int] = None,
                            on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespTokenInfo:
        """
        Returns project information and social media links of an ERC20/ERC721/ERC1155 token.
        
        Args:
            contractaddress: The contract address of the ERC-20/ERC-721/ERC-1155 token
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Token information including name, symbol, supply, social media links etc.
            
        Note:
            This endpoint is throttled to 2 calls/second regardless of API Pro tier.
        """
        res = await self._request("token", "tokeninfo", locals())
        if isinstance(res, list):
            return res[0]
        return res
    
    async def get_account_erc20_holdings(self,
                                      address: str,
                                      page: int = 1,
                                      offset: int = 100,
                                      chainid: Optional[int] = None,
                                      on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespERC20Holdings:
        """
        Returns the ERC-20 tokens and amount held by an address.
        
        Args:
            address: The address to check for token balances
            page: Page number for pagination
            offset: Number of records per page
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of ERC-20 token balances held by the address
            
        Note:
            This endpoint is throttled to 2 calls/second regardless of API Pro tier.
        """
        return await self._request("account", "addresstokenbalance", locals())
    
    async def get_account_nft_holdings(self,
                                     address: str,
                                     page: int = 1,
                                     offset: int = 100,
                                     chainid: Optional[int] = None,
                                     on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespNFTHoldings:
        """
        Returns the ERC-721 tokens and amount held by an address.
        
        Args:
            address: The address to check for token balances
            page: Page number for pagination
            offset: Number of records per page
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of ERC-721 token balances held by the address
            
        Note:
            This endpoint is throttled to 2 calls/second regardless of API Pro tier.
        """
        return await self._request("account", "addresstokennftbalance", locals())
    
    async def get_account_nft_inventories(self,
                                                   address: str,
                                                   contractaddress: str,
                                                   page: int = 1,
                                                   offset: int = 100,
                                                   chainid: Optional[int] = None,
                                                   on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespNFTTokenInventories:
        """
        Returns the ERC-721 token inventory of an address, filtered by contract address.
        
        Args:
            address: The address to check for token inventory
            contractaddress: The ERC-721 token contract address to check for inventory
            page: Page number for pagination
            offset: Number of records per page (max 1000)
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of ERC-721 token inventory for the address filtered by contract
            
        Note:
            This endpoint is throttled to 2 calls/second regardless of API Pro tier.
        """
        return await self._request("account", "addresstokennftinventory", locals())
    
    async def get_confirmation_time_estimate(self,
                                           gasprice: int,
                                           chainid: Optional[int] = None,
                                           on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespConfirmationTimeEstimation:
        """
        Returns the estimated time, in seconds, for a transaction to be confirmed on the blockchain.
        
        Args:
            gasprice: The price paid per unit of gas, in wei
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Estimated confirmation time in seconds
        """
        return await self._request("gastracker", "gasestimate", locals())
    
    async def get_gas_oracle(self,
                            chainid: Optional[int] = None,
                            on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespGasOracle:
        """
        Returns the current Safe, Proposed and Fast gas prices.
        
        Post EIP-1559 changes:
        - Safe/Proposed/Fast gas price recommendations are modeled as Priority Fees
        - suggestBaseFee field shows the baseFee of the next pending block
        - gasUsedRatio field estimates how busy the network is
        
        Args:
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Current gas prices and network statistics
        """
        return await self._request("gastracker", "gasoracle", locals())
    
    async def get_daily_average_gas_limit(self,
                                         startdate: str,
                                         enddate: str,
                                         sort: str = "asc",
                                         chainid: Optional[int] = None,
                                         on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespDailyAvgGasLimits:
        """
        Returns the historical daily average gas limit of the Etheum network.
        
        Args:
            startdate: The starting date in yyyy-MM-dd format, eg. 2019-01-31
            enddate: The ending date in yyyy-MM-dd format, eg. 2019-02-28
            sort: The sorting preference, use 'asc' for ascending and 'desc' for descending
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Historical daily average gas limit data for the specified date range
        """
        return await self._request("stats", "dailyavggaslimit", locals())
    
    async def get_daily_total_gas_useds(self,
                                      startdate: str,
                                      enddate: str, 
                                      sort: str = "asc",
                                      chainid: Optional[int] = None,
                                      on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespDailyTotalGasUseds:
        """
        Returns the total amount of gas used daily for transactions on the Etheum network.
        
        Args:
            startdate: The starting date in yyyy-MM-dd format, eg. 2019-01-31
            enddate: The ending date in yyyy-MM-dd format, eg. 2019-02-28
            sort: The sorting preference, use 'asc' for ascending and 'desc' for descending
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Historical daily total gas used data for the specified date range
        """
        return await self._request("stats", "dailygasused", locals())

    async def get_daily_average_gas_prices(self,
                                         startdate: str,
                                         enddate: str,
                                         sort: str = "asc", 
                                         chainid: Optional[int] = None,
                                         on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespDailyAvgGasPrices:
        """
        Returns the daily average gas price used on the Etheum network.
        
        Args:
            startdate: The starting date in yyyy-MM-dd format, eg. 2019-01-31
            enddate: The ending date in yyyy-MM-dd format, eg. 2019-02-28
            sort: The sorting preference, use 'asc' for ascending and 'desc' for descending
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            Historical daily average gas price data for the specified date range
        """
        return await self._request("stats", "dailyavggasprice", locals())

    async def get_total_eth_supply(self,
                                   chainid: Optional[int] = None,
                                   on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespTotalEthSupply:
        """
        Returns the current amount of Eth in circulation excluding ETH2 Staking rewards and EIP1559 burnt fees.
        
        Args:
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            The total supply of Eth in Wei
        """
        return await self._request("stats", "ethsupply", locals())
    
    async def get_total_eth2_supply(self,
                                      chainid: Optional[int] = None, 
                                      on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespTotalEth2Supply:
        """
        Returns the current amount of Eth in circulation, ETH2 Staking rewards, EIP1559 burnt fees, 
        and total withdrawn ETH from the beacon chain.
        
        Args:
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            The total supply of Eth including ETH2 staking rewards and EIP1559 burnt fees
        """
        return await self._request("stats", "ethsupply2", locals())
    
    async def get_eth_price(self,
                           chainid: Optional[int] = None,
                           on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespEthPrice:
        """
        Returns the latest price of the native/gas token (e.g. ETH for Etheum, BNB for BSC, POL for Polygon).
        
        Args:
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            The latest price information including ETH/BTC and ETH/USD rates with timestamps
        """
        return await self._request("stats", "ethprice", locals())
    
    async def get_ethereum_nodes_size(self,
                                    startdate: str,
                                    enddate: str,
                                    clienttype: str,
                                    syncmode: str,
                                    sort: str,
                                    chainid: Optional[int] = None,
                                    on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespEtheumNodesSize:
        """
        Returns the size of the Etheum blockchain, in bytes, over a date range.
        
        Args:
            startdate: The starting date in yyyy-MM-dd format, eg. 2019-02-01
            enddate: The ending date in yyyy-MM-dd format, eg. 2019-02-28
            clienttype: The Etheum node client to use, either geth or parity
            syncmode: The type of node to run, either default or archive
            sort: The sorting preference, use asc to sort by ascending and desc to sort by descending
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of daily Etheum blockchain size data for the specified date range
        """
        return await self._request("stats", "chainsize", locals())
    
    async def get_node_count(self,
                            chainid: Optional[int] = None,
                            on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespNodeCount:
        """
        Returns the total number of discoverable Etheum nodes.
        
        Args:
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            The total count of discoverable Etheum nodes with date
        """
        return await self._request("stats", "nodecount", locals())
    
    async def get_daily_tx_fees(self,
                                       startdate: str,
                                       enddate: str,
                                       sort: str,
                                       chainid: Optional[int] = None,
                                       on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespDailyTxFees:
        """
        Returns the amount of transaction fees paid to miners per day.
        
        Args:
            startdate: The starting date in yyyy-MM-dd format, eg. 2019-02-01
            enddate: The ending date in yyyy-MM-dd format, eg. 2019-02-28
            sort: The sorting preference, use asc to sort by ascending and desc to sort by descending
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of daily transaction fees paid to miners for the specified date range
        """
        return await self._request("stats", "dailytxnfee", locals())
    
    async def get_daily_new_addresses(self,
                                    startdate: str,
                                    enddate: str,
                                    sort: str,
                                    chainid: Optional[int] = None,
                                    on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespDailyNewAddresses:
        """
        Returns the number of new Etheum addresses created per day.
        
        Args:
            startdate: The starting date in yyyy-MM-dd format, eg. 2019-02-01
            enddate: The ending date in yyyy-MM-dd format, eg. 2019-02-28
            sort: The sorting preference, use asc to sort by ascending and desc to sort by descending
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of daily new Etheum addresses created for the specified date range
        """
        return await self._request("stats", "dailynewaddress", locals())
    
    async def get_daily_network_utilizations(self,
                                          startdate: str,
                                          enddate: str,
                                          sort: str,
                                          chainid: Optional[int] = None,
                                          on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespDailyNetworkUtilizations:
        """
        Returns the daily average gas used over gas limit, in percentage.
        
        Args:
            startdate: The starting date in yyyy-MM-dd format, eg. 2019-02-01
            enddate: The ending date in yyyy-MM-dd format, eg. 2019-02-28
            sort: The sorting preference, use asc to sort by ascending and desc to sort by descending
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of daily network utilization percentages for the specified date range
        """
        return await self._request("stats", "dailynetutilization", locals())
    
    async def get_daily_avg_hashrates(self,
                                       startdate: str,
                                       enddate: str,
                                       sort: str,
                                       chainid: Optional[int] = None,
                                       on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespDailyAvgHashrates:
        """
        Returns the historical measure of processing power of the Etheum network.
        
        Args:
            startdate: The starting date in yyyy-MM-dd format, eg. 2019-02-01
            enddate: The ending date in yyyy-MM-dd format, eg. 2019-02-28
            sort: The sorting preference, use asc to sort by ascending and desc to sort by descending
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of daily average network hash rates for the specified date range
        """
        return await self._request("stats", "dailyavghashrate", locals())
    
    async def get_daily_tx_counts(self,
                                startdate: str,
                                enddate: str,
                                sort: str,
                                chainid: Optional[int] = None,
                                on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespDailyTxCounts:
        """
        Returns the number of transactions performed on the Etheum blockchain per day.
        
        Args:
            startdate: The starting date in yyyy-MM-dd format, eg. 2019-02-01
            enddate: The ending date in yyyy-MM-dd format, eg. 2019-02-28
            sort: The sorting preference, use asc to sort by ascending and desc to sort by descending
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of daily transaction counts for the specified date range
        """
        return await self._request("stats", "dailytx", locals())
    
    async def get_daily_avg_difficulties(self,
                                       startdate: str,
                                       enddate: str,
                                       sort: str,
                                       chainid: Optional[int] = None,
                                       on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespDailyAvgDifficulties:
        """
        Returns the historical mining difficulty of the Etheum network.
        
        Args:
            startdate: The starting date in yyyy-MM-dd format, eg. 2019-02-01
            enddate: The ending date in yyyy-MM-dd format, eg. 2019-02-28
            sort: The sorting preference, use asc to sort by ascending and desc to sort by descending
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of daily average network difficulties for the specified date range
        """
        return await self._request("stats", "dailyavgnetdifficulty", locals())
    
    async def get_eth_historical_prices(self,
                                 startdate: str,
                                 enddate: str,
                                 sort: str,
                                 chainid: Optional[int] = None,
                                 on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespEthHistoricalPrices:
        """
        Returns the historical price of 1 ETH.
        
        Args:
            startdate: The starting date in yyyy-MM-dd format, eg. 2019-02-01
            enddate: The ending date in yyyy-MM-dd format, eg. 2019-02-28
            sort: The sorting preference, use asc to sort by ascending and desc to sort by descending
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of daily ETH prices for the specified date range
        """
        return await self._request("stats", "ethdailyprice", locals())
    
    async def get_plasma_deposits(self,
                                address: str,
                                blocktype: str = "blocks",
                                page: Optional[int] = None,
                                offset: Optional[int] = None,
                                chainid: Optional[int] = 137,
                                on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespPlasmaDeposits:
        """
        Returns a list of Plasma Deposits received by an address.
        Only applicable to Polygon (chainid=137).
        
        Args:
            address: The address to check for deposits
            blocktype: The pre-defined block type, 'blocks' for canonical blocks
            page: The page number for pagination
            offset: Number of transactions per page
            chainid: Chain ID. Defaults to Polygon (137)
            on_limit_exceeded: Behavior when rate limit is exceeded
            
        Returns:
            List of plasma deposits for the specified address
        """
        return await self._request("account", "txnbridge", locals())
    
    async def get_deposit_txs(self,
                             address: str,
                             page: int = 1,
                             offset: int = 1000,
                             sort: Literal["asc", "desc"] = "desc",
                             chainid: Optional[int] = None,
                             on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespDepositTxs:
        """
        Returns a list of deposits in ETH or ERC20 tokens from Etheum to L2.
        Only applicable to Arbitrum Stack (42161, 42170, 33139, 660279) and 
        Optimism Stack (10, 8453, 130, 252, 480, 5000, 81457).

        Args:
            address: The address to check for deposits
            page: The page number for pagination
            offset: Number of transactions per page
            sort: The sorting preference, use asc to sort by ascending and desc to sort by descending
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded

        Returns:
            List of deposit transactions for the specified address
        """
        return await self._request("account", "getdeposittxs", locals())
    
    async def get_withdrawal_txs(self,
                                address: str,
                                page: int = 1,
                                offset: int = 1000,
                                sort: Literal["asc", "desc"] = "desc",
                                chainid: Optional[int] = None,
                                on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespWithdrawalTxs:
        """
        Returns a list of withdrawals in ETH or ERC20 tokens from L2 to Etheum.
        Only applicable to Arbitrum Stack (42161, 42170, 33139, 660279) and 
        Optimism Stack (10, 8453, 130, 252, 480, 5000, 81457).

        Args:
            address: The address to check for withdrawals
            page: The page number for pagination
            offset: Number of transactions per page
            sort: The sorting preference, use asc to sort by ascending and desc to sort by descending
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded

        Returns:
            List of withdrawal transactions for the specified address
        """
        return await self._request("account", "getwithdrawaltxs", locals())
    
    async def get_address_tag(self,
                             address: str | list[str],
                             chainid: Optional[int] = None,
                             on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespAddressTags:
        """
        Returns a single address name tag and metadata.
        Note: This endpoint is throttled to 2 calls/second regardless of API Pro tier.

        Args:
            address: The address to check for its metadata, max 100 addresses
            chainid: Chain ID. If None, uses Ethereum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded

        Returns:
            Address name tag and metadata information
        """
        if isinstance(address, list):
            address = ",".join(address)
        return await self._request("nametag", "getaddresstag", locals())
    
    async def get_label_masterlist(self,
                                  chainid: Optional[int] = None, 
                                  on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespLabelMasterlist:
        """
        Returns the masterlist of available label groupings.

        Args:
            chainid: Chain ID. If None, uses Ethereum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded

        Returns:
            Masterlist of available label groupings
        """
        return await self._request("nametag", "getlabelmasterlist", locals(), base_url=API_ASHX)
    
    async def export_specific_label_csv(self,
                                label: str,
                                chainid: Optional[int] = None,
                                on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> str:
        """
        Returns addresses filtered by a specific label in CSV format.

        Args:
            label: The label to filter addresses by (e.g. 'nft', 'dex', etc.)
            chainid: Chain ID. If None, uses Ethereum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded

        Returns:
            CSV formatted string containing addresses with the specified label

        Args:
            chainid: Chain ID. If None, uses Ethereum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded

        Returns:
            CSV formatted string containing OFAC sanctioned addresses
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_ASHX}?module=nametag&action=exportaddresstags&label=ofac-sanctioned&format=csv&apikey={self.api_key}")
            response.raise_for_status()
            return response.text
        
    async def export_ofac_sanctioned_realted_labels_csv(self,
                                      chainid: Optional[int] = None,
                                      on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> str:
        """
        Returns addresses sanctioned by the U.S. Department of the Treasury's Office of Foreign 
        Assets Control's Specially Designated Nationals list in CSV format.

        Args:
            chainid: Chain ID. If None, uses Ethereum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded

        Returns:
            CSV formatted string containing OFAC sanctioned addresses
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_ASHX}?module=nametag&action=exportaddresstags&label=ofac-sanctioned&format=csv&apikey={self.api_key}")
            response.raise_for_status()
            return response.text
        
    async def export_all_address_tags_csv(self,
                                      chainid: Optional[int] = None, 
                                      on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> str:
        """
        Exports a complete CSV list of ALL address name tags and/or labels.

        Args:
            chainid: Chain ID. If None, uses Ethereum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded

        Returns:
            CSV formatted string containing all addresses with their tags and labels
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_ASHX}?module=nametag&action=exportaddresstags&format=csv&apikey={self.api_key}")
            response.raise_for_status()
            return response.text
        
    async def get_latest_csv_batch_number(self,
                                      chainid: Optional[int] = None,
                                      on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespLatestCSVBatchNumbers:
        """
        Gets the latest running number for CSV Export.

        Args:
            chainid: Chain ID. If None, uses Ethereum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded

        Returns:
            List of latest CSV batch numbers containing nametag, batch number and last updated timestamp
        """
        return await self._request("nametag", "getcurrentbatch", locals())
    
    async def check_credit_usage(self,
                              chainid: Optional[int] = None,
                              on_limit_exceeded: RateLimitBehavior = RATE_LIMIT_BLOCK) -> RespCreditUsage:
        """
        Returns information about API credit usage and limits.

        Args:
            chainid: Chain ID. If None, uses Etheum mainnet
            on_limit_exceeded: Behavior when rate limit is exceeded

        Returns:
            Credit usage information including credits used, available, limit,
            interval type and time remaining in current interval
        """
        return await self._request("getapilimit", "getapilimit", locals())
    

    async def get_supported_chains(self):
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.etherscan.io/v2/chainlist")
            response.raise_for_status()
            return response.json()
    
    