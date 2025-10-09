from typing import TypedDict


RespGetEthBalance = str

class RespBridgeTx(TypedDict):
    """Example:
    {
        "hash": "0x79eaf9951f474d5fd78bae5e3d6e089b54e61b81d272ce6f98e8ac6b56ec0f93",
        "blockNumber": "42107370",
        "timeStamp": "1757792370",
        "from": "0xfa98b60e02a61b6590f073cad56e68326652d094", 
        "address": "0x1545c4ccf40a5e89ac1482a32485f62d369560d3",
        "amount": "1000000000000000000",
        "tokenName": "",
        "symbol": "",
        "contractAddress": "0x7301cfa0e1756b71869e93d4e4dca5c7d0eb0aa6",
        "divisor": ""
    }
    """
    hash: str
    blockNumber: str
    timeStamp: str
    from_: str
    address: str
    amount: str
    tokenName: str
    symbol: str
    contractAddress: str
    divisor: str

RespGetBridgeTxs = list[RespBridgeTx]

class RespEthBalanceEntry(TypedDict):
    """Example:
    {
        "account": "0xddbd2b932c763ba5b1b7ae3b362eac3e8d40121a",
        "balance": "40891626854930000000000"
    }
    """
    account: str
    balance: str

RespGetEthBalances = list[RespEthBalanceEntry]

class RespNormalTx(TypedDict):
    """Example:
    {
        "blockNumber": "14923678",
        "timeStamp": "1654646411", 
        "hash": "0xc52783ad354aecc04c670047754f062e3d6d04e8f5b24774472651f9c3882c60",
        "nonce": "1",
        "blockHash": "0x7e1638fd2c6bdd05ffd83c1cf06c63e2f67d0f802084bef076d06bdcf86d1bb0",
        "transactionIndex": "61",
        "from": "0x9aa99c23f67c81701c772b106b4f83f6e858dd2e",
        "to": "",
        "value": "0",
        "gas": "6000000",
        "gasPrice": "83924748773",
        "isError": "0",
        "txreceipt_status": "1",
        "input": "0x6101606040...",
        "contractAddress": "0xc5102fe9359fd9a28f877a67e36b0f050d81a3cc",
        "cumulativeGasUsed": "10450178",
        "gasUsed": "4457269",
        "confirmations": "122485",
        "methodId": "0x61016060",
        "functionName": ""
    }
    """
    blockNumber: str
    timeStamp: str
    hash: str
    nonce: str
    blockHash: str
    transactionIndex: str
    from_: str
    to: str
    value: str
    gas: str
    gasPrice: str
    isError: str
    txreceipt_status: str
    input: str
    contractAddress: str
    cumulativeGasUsed: str
    gasUsed: str
    confirmations: str
    methodId: str
    functionName: str

RespGetNormalTxs = list[RespNormalTx]

class RespInternalTxByAddress(TypedDict):
    """Example:
    {
        "blockNumber": "2535368",
        "timeStamp": "1477837690",
        "hash": "0x8a1a9989bda84f80143181a68bc137ecefa64d0d4ebde45dd94fc0cf49e70cb6",
        "from": "0x20d42f2e99a421147acf198d775395cac2e8b03d",
        "to": "",
        "value": "0",
        "contractAddress": "0x2c1ba59d6f58433fb1eaee7d20b26ed83bda51a3",
        "input": "",
        "type": "create",
        "gas": "254791", 
        "gasUsed": "46750",
        "traceId": "0",
        "isError": "0",
        "errCode": ""
    }
    """
    blockNumber: str
    timeStamp: str
    hash: str
    from_: str
    to: str
    value: str
    contractAddress: str
    input: str
    type: str
    gas: str
    gasUsed: str
    traceId: str
    isError: str
    errCode: str

RespGetInternalTxsByAddress = list[RespInternalTxByAddress]

class RespInternalTxByHash(TypedDict):
    """Example:
    {
        "blockNumber": "1743059",
        "timeStamp": "1466489498", 
        "from": "0x2cac6e4b11d6b58f6d3c1c9d5fe8faa89f60e5a2",
        "to": "0x66a1c3eaf0f1ffc28d209c0763ed0ca614f3b002",
        "value": "7106740000000000",
        "contractAddress": "",
        "input": "",
        "type": "call",
        "gas": "2300",
        "gasUsed": "0",
        "isError": "0",
        "errCode": ""
    }
    """
    blockNumber: str
    timeStamp: str
    from_: str
    to: str
    value: str
    contractAddress: str
    input: str
    type: str
    gas: str
    gasUsed: str
    isError: str
    errCode: str

RespGetInternalTxsByHash = list[RespInternalTxByHash]

class RespInternalTxByBlockRange(TypedDict):
    """Example:
    {
        "blockNumber": "50107",
        "timeStamp": "1438984016",
        "hash": "0x3f97c969ddf71f515ce5373b1f8e76e9fd7016611d8ce455881009414301789e",
        "from": "0x109c4f2ccc82c4d77bde15f306707320294aea3f", 
        "to": "0x881b0a4e9c55d08e31d8d3c022144d75a454211c",
        "value": "1000000000000000000",
        "contractAddress": "",
        "input": "",
        "type": "call",
        "gas": "2300",
        "gasUsed": "0",
        "traceId": "0",
        "isError": "1",
        "errCode": ""
    }
    """
    blockNumber: str
    timeStamp: str
    hash: str
    from_: str
    to: str
    value: str
    contractAddress: str
    input: str
    type: str
    gas: str
    gasUsed: str
    traceId: str
    isError: str
    errCode: str

RespGetInternalTxsByBlockRange = list[RespInternalTxByBlockRange]

class RespERC20TokenTransfer(TypedDict):
    """Example:
    {
        "blockNumber": "4730207",
        "timeStamp": "1513240363", 
        "hash": "0xe8c208398bd5ae8e4c237658580db56a2a94dfa0ca382c99b776fa6e7d31d5b4",
        "nonce": "406",
        "blockHash": "0x022c5e6a3d2487a8ccf8946a2ffb74938bf8e5c8a3f6d91b41c56378a96b5c37",
        "from": "0x642ae78fafbb8032da552d619ad43f1d81e4dd7c",
        "contractAddress": "0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2",
        "to": "0x4e83362442b8d1bec281594cea3050c8eb01311c",
        "value": "5901522149285533025181",
        "tokenName": "Maker",
        "tokenSymbol": "MKR", 
        "tokenDecimal": "18",
        "transactionIndex": "81",
        "gas": "940000",
        "gasPrice": "32010000000",
        "gasUsed": "77759",
        "cumulativeGasUsed": "2523379",
        "input": "deprecated",
        "confirmations": "7968350"
    }
    """
    blockNumber: str
    timeStamp: str
    hash: str
    nonce: str
    blockHash: str
    from_: str
    contractAddress: str
    to: str
    value: str
    tokenName: str
    tokenSymbol: str
    tokenDecimal: str
    transactionIndex: str
    gas: str
    gasPrice: str
    gasUsed: str
    cumulativeGasUsed: str
    input: str
    confirmations: str

RespGetERC20TokenTransfers = list[RespERC20TokenTransfer]

class RespERC721TokenTransfer(TypedDict):
    """Example:
    {
        "blockNumber": "4708120",
        "timeStamp": "1512907118",
        "hash": "0x031e6968a8de362e4328d60dcc7f72f0d6fc84284c452f63176632177146de66", 
        "nonce": "0",
        "blockHash": "0x4be19c278bfaead5cb0bc9476fa632e2447f6e6259e0303af210302d22779a24",
        "from": "0xb1690c08e213a35ed9bab7b318de14420fb57d8c",
        "contractAddress": "0x06012c8cf97bead5deae237070f9587f8e7a266d",
        "to": "0x6975be450864c02b4613023c2152ee0743572325",
        "tokenID": "202106",
        "tokenName": "CryptoKitties",
        "tokenSymbol": "CK",
        "tokenDecimal": "0",
        "transactionIndex": "81",
        "gas": "158820",
        "gasPrice": "40000000000",
        "gasUsed": "60508",
        "cumulativeGasUsed": "4880352",
        "input": "deprecated",
        "confirmations": "7990490"
    }
    """
    blockNumber: str
    timeStamp: str
    hash: str
    nonce: str
    blockHash: str
    from_: str
    contractAddress: str
    to: str
    tokenID: str
    tokenName: str
    tokenSymbol: str
    tokenDecimal: str
    transactionIndex: str
    gas: str
    gasPrice: str
    gasUsed: str
    cumulativeGasUsed: str
    input: str
    confirmations: str

RespGetERC721TokenTransfers = list[RespERC721TokenTransfer]

class RespERC1155TokenTransfer(TypedDict):
    """Example:
    {
        "blockNumber": "13472395",
        "timeStamp": "1634973285",
        "hash": "0x643b15f3ffaad5d38e33e5872b4ebaa7a643eda8b50ffd5331f682934ee65d4d",
        "nonce": "41", 
        "blockHash": "0xa5da536dfbe8125eb146114e2ee0d0bdef2b20483aacbf30fed6b60f092059e6",
        "transactionIndex": "100",
        "gas": "140000",
        "gasPrice": "52898577246",
        "gasUsed": "105030",
        "cumulativeGasUsed": "11739203",
        "input": "deprecated",
        "contractAddress": "0x76be3b62873462d2142405439777e971754e8e77",
        "from": "0x1e63326a84d2fa207bdfa856da9278a93deba418",
        "to": "0x83f564d180b58ad9a02a449105568189ee7de8cb",
        "tokenID": "10371",
        "tokenValue": "1",
        "tokenName": "parallel",
        "tokenSymbol": "LL",
        "confirmations": "1447769"
    }
    """
    blockNumber: str
    timeStamp: str
    hash: str
    nonce: str
    blockHash: str
    transactionIndex: str
    gas: str
    gasPrice: str
    gasUsed: str
    cumulativeGasUsed: str
    input: str
    contractAddress: str
    from_: str
    to: str
    tokenID: str
    tokenValue: str
    tokenName: str
    tokenSymbol: str
    confirmations: str

RespGetERC1155TokenTransfers = list[RespERC1155TokenTransfer]

class RespAddressFundedBy(TypedDict):
    """Example:
    {
        "block": 8665142,
        "timeStamp": "1704119631", 
        "fundingAddress": "0xcb566e3b6934fa77258d68ea18e931fa75e1aaaa",
        "fundingTxn": "0x495cdddefc559eb5928589c0bd8070e8182ff0aed082bde3cd6fbd78431ca278",
        "value": "500000000000000"
    }
    """
    block: int
    timeStamp: str
    fundingAddress: str 
    fundingTxn: str
    value: str
    
class RespBlockValidated(TypedDict):
    """Example:
    {
        "blockNumber": "3462296",
        "timeStamp": "1491118514", 
        "blockReward": "5194770940000000000"
    }
    """
    blockNumber: str
    timeStamp: str
    blockReward: str

RespBlocksValidatedByAddress = list[RespBlockValidated]

class RespBeaconChainWithdrawal(TypedDict):
    """Example:
    {
        "withdrawalIndex": "13",
        "validatorIndex": "117823", 
        "address": "0xb9d7934878b5fb9610b3fe8a5e441e8fad7e293f",
        "amount": "3402931175",
        "blockNumber": "17034877",
        "timestamp": "1681338599"
    }
    """
    withdrawalIndex: str
    validatorIndex: str
    address: str
    amount: str
    blockNumber: str
    timestamp: str

RespBeaconChainWithdrawals = list[RespBeaconChainWithdrawal]

RespEthBalanceByBlockNumber = str

RespContractABI = str

class RespContractSourceCode(TypedDict):
    """Example:
    {
        "SourceCode": "contract Token {...}",
        "ABI": "[{...}]",
        "ContractName": "DAO",
        "CompilerVersion": "v0.3.1-2016-04-12-3ad5e82",
        "OptimizationUsed": "1", 
        "Runs": "200",
        "ConstructorArguments": "000000...",
        "EVMVersion": "Default",
        "Library": "",
        "LicenseType": "",
        "Proxy": "0",
        "Implementation": "",
        "SwarmSource": "",
        "SimilarMatch": ""
    }
    """
    SourceCode: str
    ABI: str
    ContractName: str
    CompilerVersion: str
    OptimizationUsed: str
    Runs: str
    ConstructorArguments: str
    EVMVersion: str
    Library: str
    LicenseType: str
    Proxy: str
    Implementation: str
    SwarmSource: str
    SimilarMatch: str

RespContractSourceCodes = list[RespContractSourceCode]

class RespContractCreationAndCreation(TypedDict):
    """Example:
    {
        "contractAddress": "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45",
        "contractCreator": "0x6c9fc64a53c1b71fb3f9af64d1ae3a4931a5f4e9", 
        "txHash": "0x7299cca7203f60a831756e043f4c2ccb0ee6cb7cf8aed8420f0ae99a16883a2b",
        "blockNumber": "13804681",
        "timestamp": "1639503446",
        "contractFactory": "",
        "creationBytecode": "0x610..."
    }
    """
    contractAddress: str
    contractCreator: str
    txHash: str
    blockNumber: str
    timestamp: str
    contractFactory: str
    creationBytecode: str

RespContractCreationAndCreations = list[RespContractCreationAndCreation]

RespVerifySourceCode = str

RespVerifyVyperSourceCode = str

RespVerifyStylusSourceCode = str

RespCheckSourceCodeVerificationStatus = str

class RespContractExecutionStatus(TypedDict):
    """Example:
    {
        "isError": "1",
        "errDescription": "Bad jump destination"
    }
    """
    isError: str
    errDescription: str

class RespCheckTxReceiptStatus(TypedDict):
    """Example:
    {
        "status": "1"
    }
    """
    status: str
    
class RespBlockReward(TypedDict):
    """Example:
    {
        "blockNumber": "2165403",
        "timeStamp": "1472533979",
        "blockMiner": "0x13a06d3dfe21e0db5c016c03ea7d2509f7f8d1e3",
        "blockReward": "5314181600000000000",
        "uncles": list[UncleReward],
        "uncleInclusionReward": "312500000000000000"
    }
    """
    class UncleReward(TypedDict):
        """Example:
        {
            "miner": "0xbcdfc35b86bedf72f0cda046a3c16829a2ef41d1",
            "unclePosition": "0", 
            "blockreward": "3750000000000000000"
        }
        """
        miner: str
        unclePosition: str
        blockreward: str

    blockNumber: str
    timeStamp: str 
    blockMiner: str
    blockReward: str
    uncles: list[UncleReward]
    uncleInclusionReward: str

class RespBlockTxsCountByBlockNo(TypedDict):
    """Example:
    {
        "block": 2165403,
        "txsCount": 4,
        "internalTxsCount": 0,
        "erc20TxsCount": 0,
        "erc721TxsCount": 0,
        "erc1155TxsCount": 0
    }
    """
    block: int
    txsCount: int
    internalTxsCount: int
    erc20TxsCount: int
    erc721TxsCount: int
    erc1155TxsCount: int

class RespEstimateBlockCountdownTimeByBlockNo(TypedDict):
    """Get Estimated Block Countdown Time by BlockNo
    Example:
    {
        "CurrentBlock": "12715477",
        "CountdownBlock": "16701588", 
        "RemainingBlock": "3986111",
        "EstimateTimeInSec": "52616680.2"
    }
    """
    CurrentBlock: str
    CountdownBlock: str
    RemainingBlock: str
    EstimateTimeInSec: str

RespBlockNumber = int

class RespDailyAvgBlockSize(TypedDict):
    """Example:
    {
        "UTCDate": "2019-02-01",
        "unixTimeStamp": "1548979200", 
        "blockSize_bytes": 20373
    }
    """
    UTCDate: str
    unixTimeStamp: str
    blockSize_bytes: int

RespDailyAvgBlockSizes = list[RespDailyAvgBlockSize]

class RespDailyBlockCountReward(TypedDict):
    """Example:
    {
        "UTCDate": "2019-02-01",
        "unixTimeStamp": "1548979200",
        "blockCount": 4848,
        "blockRewards_Eth": "14929.464690870590355682"
    }
    """
    UTCDate: str
    unixTimeStamp: str
    blockCount: int
    blockRewards_Eth: str

RespDailyBlockCountRewards = list[RespDailyBlockCountReward]

class RespDailyBlockReward(TypedDict):
    """Example:
    {
        "UTCDate": "2019-02-01",
        "unixTimeStamp": "1548979200",
        "blockRewards_Eth": "15300.65625"
    }
    """
    UTCDate: str
    unixTimeStamp: str 
    blockRewards_Eth: str

RespDailyBlockRewards = list[RespDailyBlockReward]

class RespDailyAvgTimeBlockMined(TypedDict):
    """Example:
    {
        "UTCDate": "2019-02-01",
        "unixTimeStamp": "1548979200",
        "blockTime_sec": "17.67"
    }
    """
    UTCDate: str
    unixTimeStamp: str
    blockTime_sec: str

RespDailyAvgTimeBlockMineds = list[RespDailyAvgTimeBlockMined]

class RespDailyUncleBlockCountAndReward(TypedDict):
    """Example:
    {
        "UTCDate": "2019-02-01", 
        "unixTimeStamp": "1548979200",
        "uncleBlockCount": 287,
        "uncleBlockRewards_Eth": "729.75"
    }
    """
    UTCDate: str
    unixTimeStamp: str
    uncleBlockCount: int
    uncleBlockRewards_Eth: str

RespDailyUncleBlockCountAndRewards = list[RespDailyUncleBlockCountAndReward]

class RespEventLogByAddress(TypedDict):
    """Example:
    {
        "address": "0xbd3531da5cf5857e7cfaa92426877b022e612cf8",
        "topics": [
            "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
            "0x0000000000000000000000000000000000000000000000000000000000000000",
            "0x000000000000000000000000c45a4b3b698f21f88687548e7f5a80df8b99d93d", 
            "0x00000000000000000000000000000000000000000000000000000000000000b5"
        ],
        "data": "0x",
        "blockNumber": "0xc48174",
        "timeStamp": "0x60f9ce56", 
        "gasPrice": "0x2e90edd000",
        "gasUsed": "0x247205",
        "logIndex": "0x",
        "transactionHash": "0x4ffd22d986913d33927a392fe4319bcd2b62f3afe1c15a2c59f77fc2cc4c20a9",
        "transactionIndex": "0x"
    }
    """
    address: str
    topics: list[str]
    data: str
    blockNumber: str
    timeStamp: str
    gasPrice: str
    gasUsed: str
    logIndex: str
    transactionHash: str
    transactionIndex: str

RespEventLogsByAddress = list[RespEventLogByAddress]

class RespEventLogByTopics(TypedDict):
    """Example:
    {
        "address": "0xbd3531da5cf5857e7cfaa92426877b022e612cf8",
        "topics": [
            "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
            "0x0000000000000000000000000000000000000000000000000000000000000000",
            "0x000000000000000000000000c45a4b3b698f21f88687548e7f5a80df8b99d93d",
            "0x00000000000000000000000000000000000000000000000000000000000000b5"
        ],
        "data": "0x",
        "blockNumber": "0xc48174",
        "timeStamp": "0x60f9ce56",
        "gasPrice": "0x2e90edd000",
        "gasUsed": "0x247205",
        "logIndex": "0x",
        "transactionHash": "0x4ffd22d986913d33927a392fe4319bcd2b62f3afe1c15a2c59f77fc2cc4c20a9",
        "transactionIndex": "0x"
    }
    """
    address: str
    topics: list[str]
    data: str
    blockNumber: str
    timeStamp: str
    gasPrice: str
    gasUsed: str
    logIndex: str
    transactionHash: str
    transactionIndex: str

RespEventLogsByTopics = list[RespEventLogByTopics]

class RespEventLogByAddressFilteredByTopics(TypedDict):
    """Example:
    {
        "address": "0x59728544b08ab483533076417fbbb2fd0b17ce3a",
        "topics": [
            "0x27c4f0403323142b599832f26acd21c74a9e5b809f2215726e244a4ac588cd7d",
            "0x00000000000000000000000023581767a106ae21c074b2276d25e5c3e136a68b",
            "0x000000000000000000000000000000000000000000000000000000000000236d",
            "0x000000000000000000000000c8a5592031f93debea5d9e67a396944ee01bb2ca"
        ],
        "data": "0x000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000000000000000000000000000000f207539952d0000",
        "blockNumber": "0xe60262",
        "timeStamp": "0x62c26caf", 
        "gasPrice": "0x5e2d742c9",
        "gasUsed": "0xfb7f8",
        "logIndex": "0x4b",
        "transactionHash": "0x26fe1a0a403fd44ef11ee72f3b4ceff590b6ea533684cb279cb4242be463304c",
        "transactionIndex": "0x39"
    }
    """
    address: str
    topics: list[str]
    data: str
    blockNumber: str
    timeStamp: str
    gasPrice: str
    gasUsed: str
    logIndex: str
    transactionHash: str
    transactionIndex: str

RespEventLogsByAddressFilteredByTopics = list[RespEventLogByAddressFilteredByTopics]

class RespJsonRpc[Result](TypedDict):
    jsonrpc: str
    id: int
    result: Result

RespEthBlockNumberHex = RespJsonRpc[str]

class RespEthBlockInfo(TypedDict):
    """Example:
    {
        "baseFeePerGas": "0x5cfe76044",
        "difficulty": "0x1b4ac252b8a531",
        "extraData": "0xd883010a06846765746888676f312e31362e36856c696e7578",
        "gasLimit": "0x1caa87b", 
        "gasUsed": "0x5f036a",
        "hash": "0x396288e0ad6690159d56b5502a172d54baea649698b4d7af2393cf5d98bf1bb3",
        "logsBloom": "0x5020418e211832c600000411c00098852850124700800500580d406984009104010420410c00420080414b044000012202448082084560844400d00002202b1209122000812091288804302910a246e25380282000e00002c00050009038cc205a018180028225218760100040820ac12302840050180448420420b000080000410448288400e0a2c2402050004024a240200415016c105844214060005009820302001420402003200452808508401014690208808409000033264a1b0d200c1200020280000cc0220090a8000801c00b0100a1040a8110420111870000250a22dc210a1a2002409c54140800c9804304b408053112804062088bd700900120",
        "miner": "0x5a0b54d5dc17e0aadc383d2db43b0a0d3e029c4c",
        "mixHash": "0xc547c797fb85c788ecfd4f5d24651bddf15805acbaad2c74b96b0b2a2317e66c",
        "nonce": "0x04a99df972bd8412",
        "number": "0xc63251",
        "parentHash": "0xbb2d43395f93dab5c424421be22d874f8c677e3f466dc993c218fa2cd90ef120",
        "receiptsRoot": "0x3de3b59d208e0fd441b6a2b3b1c814a2929f5a2d3016716465d320b4d48cc1e5",
        "sha3Uncles": "0xee2e81479a983dd3d583ab89ec7098f809f74485e3849afb58c2ea8e64dd0930",
        "size": "0x6cb6",
        "stateRoot": "0x60fdb78b92f0e621049e0aed52957971e226a11337f633856d8b953a56399510",
        "timestamp": "0x6110bab2",
        "totalDifficulty": "0x612789b0aba90e580f8",
        "transactions": list[str],
        "transactionsRoot": "0xaceb14fcf363e67d6cdcec0d7808091b764b4428f5fd7e25fb18d222898ef779",
        "uncles": list[str]
    }
    """
    baseFeePerGas: str
    difficulty: str
    extraData: str
    gasLimit: str
    gasUsed: str
    hash: str
    logsBloom: str
    miner: str
    mixHash: str
    nonce: str
    number: str
    parentHash: str
    receiptsRoot: str
    sha3Uncles: str
    size: str
    stateRoot: str
    timestamp: str
    totalDifficulty: str
    transactions: list[str]
    transactionsRoot: str
    uncles: list[str]

RespEthBlock = RespJsonRpc[RespEthBlockInfo]

class RespEthUncleBlockInfo(TypedDict):
    """Example:
    {
        "baseFeePerGas": "0x65a42b13c",
        "difficulty": "0x1b1457a8247bbb", 
        "extraData": "0x486976656f6e2063612d68656176792059476f6e",
        "gasLimit": "0x1ca359a",
        "gasUsed": "0xb48fe1",
        "hash": "0x1da88e3581315d009f1cb600bf06f509cd27a68cb3d6437bda8698d04089f14a",
        "logsBloom": "0xf1a360ca505cdda510d810c1c81a03b51a8a508ed601811084833072945290235c8721e012182e40d57df552cf00f1f01bc498018da19e008681832b43762a30c26e11709948a9b96883a42ad02568e3fcc3000004ee12813e4296498261619992c40e22e60bd95107c5bd8462fcca570a0095d52a4c24720b00f13a2c3d62aca81e852017470c109643b15041fd69742406083d67654fc841a18b405ab380e06a8c14c0138b6602ea8f48b2cd90ac88c3478212011136802900264718a085047810221225080dfb2c214010091a6f233883bb0084fa1c197330a10bb0006686e678b80e50e4328000041c218d1458880181281765d28d51066058f3f80a7822",
        "miner": "0x1ad91ee08f21be3de0ba2ba6918e714da6b45836",
        "mixHash": "0xa8e1dbbf073614c7ed05f44b9e92fbdb3e1d52575ed8167fa57f934210bbb0a2",
        "nonce": "0x28cc3e5b7bee9866",
        "number": "0xc63274",
        "parentHash": "0x496dae3e722efdd9ee1eb69499bdc7ed0dca54e13cd1157a42811c442f01941f", 
        "receiptsRoot": "0x9c9a7a99b4af7607691a7f2a50d474290385c0a6f39c391131ea0c67307213f4",
        "sha3Uncles": "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",
        "size": "0x224",
        "stateRoot": "0xde9a11f0ee321390c1a7843cab7b9ffd3779d438bc8f77de4361dfe2807d7dee",
        "timestamp": "0x6110bd1a",
        "transactionsRoot": "0xa04a79e531db3ec373cb63e9ebfbc9c95525de6347958918a273675d4f221575",
        "uncles": []
    }
    """
    baseFeePerGas: str
    difficulty: str
    extraData: str
    gasLimit: str
    gasUsed: str
    hash: str
    logsBloom: str
    miner: str
    mixHash: str
    nonce: str
    number: str
    parentHash: str
    receiptsRoot: str
    sha3Uncles: str
    size: str
    stateRoot: str
    timestamp: str
    transactionsRoot: str
    uncles: list[str]

RespEthUncleBlock = RespJsonRpc[RespEthUncleBlockInfo]

RespEthBlockTxCount = RespJsonRpc[str]

class RespEthTxInfo(TypedDict):
    """Example:
    {
        "blockHash": "0xf850331061196b8f2b67e1f43aaa9e69504c059d3d3fb9547b04f9ed4d141ab7",
        "blockNumber": "0xcf2420",
        "from": "0x00192fb10df37c9fb26829eb2cc623cd1bf599e8", 
        "gas": "0x5208",
        "gasPrice": "0x19f017ef49",
        "maxFeePerGas": "0x1f6ea08600",
        "maxPriorityFeePerGas": "0x3b9aca00",
        "hash": "0xbc78ab8a9e9a0bca7d0321a27b2c03addeae08ba81ea98b03cd3dd237eabed44",
        "input": "0x",
        "nonce": "0x33b79d",
        "to": "0xc67f4e626ee4d3f272c2fb31bad60761ab55ed9f",
        "transactionIndex": "0x5b",
        "value": "0x19755d4ce12c00",
        "type": "0x2",
        "accessList": [],
        "chainId": "0x1",
        "v": "0x0",
        "r": "0xa681faea68ff81d191169010888bbbe90ec3eb903e31b0572cd34f13dae281b9",
        "s": "0x3f59b0fa5ce6cf38aff2cfeb68e7a503ceda2a72b4442c7e2844d63544383e3"
    }
    """
    blockHash: str
    blockNumber: str
    from_: str
    gas: str
    gasPrice: str
    maxFeePerGas: str
    maxPriorityFeePerGas: str
    hash: str
    input: str
    nonce: str
    to: str
    transactionIndex: str
    value: str
    type: str
    accessList: list
    chainId: str
    v: str
    r: str
    s: str

RespEthTx = RespJsonRpc[RespEthTxInfo]

RespEthTxCount = RespJsonRpc[str]

RespEthSendRawTx = RespJsonRpc[str]

class RespEthTxReceiptLog(TypedDict):
    """Example:
    {
        "address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "topics": [
            "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
            "0x000000000000000000000000292f04a44506c2fd49bac032e1ca148c35a478c8",
            "0x000000000000000000000000ab6960a6511ff18ed8b8c012cb91c7f637947fc0"
        ],
        "data": "0x00000000000000000000000000000000000000000000000000000000013f81a6",
        "blockNumber": "0xcf2427",
        "transactionHash": "0xadb8aec59e80db99811ac4a0235efa3e45da32928bcff557998552250fa672eb",
        "transactionIndex": "0x122", 
        "blockHash": "0x07c17710dbb7514e92341c9f83b4aab700c5dba7c4fb98caadd7926a32e47799",
        "logIndex": "0xdb",
        "removed": false
    }
    """
    address: str
    topics: list[str]
    data: str
    blockNumber: str
    transactionHash: str
    transactionIndex: str
    blockHash: str
    logIndex: str
    removed: bool

class RespEthTxReceiptInfo(TypedDict):
    """Example:
    {
        "blockHash": "0x07c17710dbb7514e92341c9f83b4aab700c5dba7c4fb98caadd7926a32e47799",
        "blockNumber": "0xcf2427",
        "contractAddress": None,
        "cumulativeGasUsed": "0xeb67d5",
        "effectiveGasPrice": "0x1a96b24c26",
        "from": "0x292f04a44506c2fd49bac032e1ca148c35a478c8",
        "gasUsed": "0xb41d",
        "logs": [...],
        "logsBloom": "0x...",
        "status": "0x1",
        "to": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "transactionHash": "0xadb8aec59e80db99811ac4a0235efa3e45da32928bcff557998552250fa672eb",
        "transactionIndex": "0x122",
        "type": "0x2"
    }
    """
    blockHash: str
    blockNumber: str
    contractAddress: str | None
    cumulativeGasUsed: str
    effectiveGasPrice: str
    from_: str
    gasUsed: str
    logs: list[RespEthTxReceiptLog]
    logsBloom: str
    status: str
    to: str
    transactionHash: str
    transactionIndex: str
    type: str

RespEthTxReceipt = RespJsonRpc[RespEthTxReceiptInfo]

RespEthCall = RespJsonRpc[str]

RespEthGetCode = RespJsonRpc[str]

RespEthGetStorageAt = RespJsonRpc[str]

RespEthGetGasPrice = RespJsonRpc[str]

RespEthEstimateGas = RespJsonRpc[str]

RespERC20TotalSupply = str

RespERC20AccountBalance = str

RespERC20HistoricalTotalSupply = str

RespERC20HistoricalAccountBalance = str

class RespERC20HolderInfo(TypedDict):
    """
    {
        "TokenHolderAddress": "0x0000000000000000000000000000000000000000",
        "TokenHolderQuantity": "34956"
    }
    """
    TokenHolderAddress: str
    TokenHolderQuantity: str

RespERC20Holders = list[RespERC20HolderInfo]

RespERC20HolderCount = str

class RespTopTokenHolder(TypedDict):
    """
    {
        "TokenHolderAddress": "0x4da27a545c0c5b758a6ba100e3a049001de870f5",
        "TokenHolderQuantity": "2696124.3026660371030000",
        "TokenHolderAddressType": "C"
    }
    """
    TokenHolderAddress: str
    TokenHolderQuantity: str
    TokenHolderAddressType: str

RespTopTokenHolders = list[RespTopTokenHolder]

class RespTokenInfo(TypedDict):
    """
    {
        "contractAddress": "0x0e3a2a1f2146d86a604adc220b4967a898d7fe07",
        "tokenName": "Gods Unchained Cards", 
        "symbol": "CARD",
        "divisor": "0",
        "tokenType": "ERC721",
        "totalSupply": "6962498",
        "blueCheckmark": "true",
        "description": "A TCG on the Etheum blockchain that uses NFT's to bring real ownership to in-game assets.",
        "website": "https://godsunchained.com/",
        "email": "",
        "blog": "https://medium.com/@fuelgames",
        "reddit": "https://www.reddit.com/r/GodsUnchained/",
        "slack": "",
        "facebook": "https://www.facebook.com/godsunchained/",
        "twitter": "https://twitter.com/godsunchained",
        "bitcointalk": "",
        "github": "",
        "telegram": "",
        "wechat": "",
        "linkedin": "",
        "discord": "https://discordapp.com/invite/DKGr2pW",
        "whitepaper": "",
        "tokenPriceUSD": "0.000000000000000000"
    }
    """
    contractAddress: str
    tokenName: str
    symbol: str
    divisor: str
    tokenType: str
    totalSupply: str
    blueCheckmark: str
    description: str
    website: str
    email: str
    blog: str
    reddit: str
    slack: str
    facebook: str
    twitter: str
    bitcointalk: str
    github: str
    telegram: str
    wechat: str
    linkedin: str
    discord: str
    whitepaper: str
    tokenPriceUSD: str

class RespERC20Holding(TypedDict):
    """Example response:
    {
         "TokenAddress":"0xffffffff2ba8f66d4e51811c5190992176930278",
         "TokenName":"Furucombo", 
         "TokenSymbol":"COMBO",
         "TokenQuantity":"1861606940000000000",
         "TokenDivisor":"18"
    }
    """
    TokenAddress: str
    TokenName: str 
    TokenSymbol: str
    TokenQuantity: str
    TokenDivisor: str

RespERC20Holdings = list[RespERC20Holding]

class RespNFTHolding(TypedDict):
    """Example response:
    {
        "TokenAddress": "0x49cf6f5d44e70224e2e23fdcdd2c053f30ada28b",
        "TokenName": "CloneX",
        "TokenSymbol": "CloneX", 
        "TokenQuantity": "52"
    }
    """
    TokenAddress: str
    TokenName: str
    TokenSymbol: str
    TokenQuantity: str

RespNFTHoldings = list[RespNFTHolding]

class RespNFTTokenInventory(TypedDict):
    """Example response:
    {
        "TokenAddress": "0xed5af388653567af2f388e6224dc7c4b3241c544",
        "TokenId": "5401"
    }
    """
    TokenAddress: str
    TokenId: str

RespNFTTokenInventories = list[RespNFTTokenInventory]

RespConfirmationTimeEstimation = str

class RespGasOracle(TypedDict):
    """Example response:
    {
        "LastBlock": "13053741",
        "SafeGasPrice": "20",
        "ProposeGasPrice": "22", 
        "FastGasPrice": "24",
        "suggestBaseFee": "19.230609716",
        "gasUsedRatio": "0.370119078777807,0.8954731,0.550911766666667,0.212457033333333,0.552463633333333"
    }
    """
    LastBlock: str
    SafeGasPrice: str
    ProposeGasPrice: str
    FastGasPrice: str
    suggestBaseFee: str
    gasUsedRatio: str

class RespDailyAvgGasLimit(TypedDict):
    """Example response:
    {
        "UTCDate": "2019-02-01",
        "unixTimeStamp": "1548979200", 
        "gasLimit": "8001360"
    }
    """
    UTCDate: str
    unixTimeStamp: str
    gasLimit: str

RespDailyAvgGasLimits = list[RespDailyAvgGasLimit]

class RespDailyTotalGasUsed(TypedDict):
    """Example response:
    {
        "UTCDate": "2019-02-01",
        "unixTimeStamp": "1548979200",
        "gasUsed": "32761450415"
    }
    """
    UTCDate: str
    unixTimeStamp: str 
    gasUsed: str

RespDailyTotalGasUseds = list[RespDailyTotalGasUsed]

class RespDailyAvgGasPrice(TypedDict):
    """Example response:
    {
        "UTCDate": "2019-02-01",
        "unixTimeStamp": "1548979200",
        "maxGasPrice_Wei": "60814303896257",
        "minGasPrice_Wei": "432495",
        "avgGasPrice_Wei": "13234562600"
    }
    """
    UTCDate: str
    unixTimeStamp: str
    maxGasPrice_Wei: str
    minGasPrice_Wei: str
    avgGasPrice_Wei: str

RespDailyAvgGasPrices = list[RespDailyAvgGasPrice]

RespTotalEthSupply = str

RespTotalEth2Supply = str

class RespEthPrice(TypedDict):
    """Example response:
    {
        "ethbtc": "0.06116",
        "ethbtc_timestamp": "1624961308",
        "ethusd": "2149.18", 
        "ethusd_timestamp": "1624961308"
    }
    """
    ethbtc: str
    ethbtc_timestamp: str
    ethusd: str
    ethusd_timestamp: str

class RespEtheumNodeSize(TypedDict):
    """Example response:
    {
        "blockNumber": "7156164",
        "chainTimeStamp": "2019-02-01", 
        "chainSize": "184726421279",
        "clientType": "Geth",
        "syncMode": "Default"
    }
    """
    blockNumber: str
    chainTimeStamp: str
    chainSize: str
    clientType: str
    syncMode: str

RespEtheumNodesSize = list[RespEtheumNodeSize]

class RespNodeCount(TypedDict):
    """Example response:
    {
        "UTCDate": "2021-06-29",
        "TotalNodeCount": "6413"
    }
    """
    UTCDate: str
    TotalNodeCount: str
    
class RespDailyTxFee(TypedDict):
    """Example response:
    {
        "UTCDate": "2019-02-01",
        "unixTimeStamp": "1548979200",
        "transactionFee_Eth": "358.558440870590355682"
    }
    """
    UTCDate: str
    unixTimeStamp: str
    transactionFee_Eth: str

RespDailyTxFees = list[RespDailyTxFee]

class RespDailyNewAddress(TypedDict):
    """Example response:
    {
        "UTCDate": "2019-02-01",
        "unixTimeStamp": "1548979200",
        "newAddressCount": 54081
    }
    """
    UTCDate: str
    unixTimeStamp: str 
    newAddressCount: int

RespDailyNewAddresses = list[RespDailyNewAddress]

class RespDailyNetworkUtilization(TypedDict):
    """Example response:
    {
        "UTCDate": "2019-02-01",
        "unixTimeStamp": "1548979200", 
        "networkUtilization": "0.8464"
    }
    """
    UTCDate: str
    unixTimeStamp: str
    networkUtilization: str

RespDailyNetworkUtilizations = list[RespDailyNetworkUtilization]

class RespDailyAvgHashrate(TypedDict):
    """Example response:
    {
        "UTCDate": "2019-02-01",
        "unixTimeStamp": "1548979200",
        "networkHashRate": "143116.0140"
    }
    """
    UTCDate: str
    unixTimeStamp: str
    networkHashRate: str

RespDailyAvgHashrates = list[RespDailyAvgHashrate]

class RespDailyTxCount(TypedDict):
    """Example response:
    {
        "UTCDate": "2019-02-01",
        "unixTimeStamp": "1548979200",
        "transactionCount": 498856
    }
    """
    UTCDate: str
    unixTimeStamp: str
    transactionCount: int

RespDailyTxCounts = list[RespDailyTxCount]

class RespDailyAvgDifficulty(TypedDict):
    """Example response:
    {
        "UTCDate": "2019-02-01",
        "unixTimeStamp": "1548979200",
        "networkDifficulty": "2,408.028"
    }
    """
    UTCDate: str
    unixTimeStamp: str
    networkDifficulty: str

RespDailyAvgDifficulties = list[RespDailyAvgDifficulty]

class RespEthHistoricalPrice(TypedDict):
    """Example response:
    {
        "UTCDate": "2019-02-01", 
        "unixTimeStamp": "1548979200",
        "value": "107.03"
    }
    """
    UTCDate: str
    unixTimeStamp: str
    value: str

RespEthHistoricalPrices = list[RespEthHistoricalPrice]

class RespPlasmaDeposit(TypedDict):
    """Example response:
    {
        "blockNumber": "19569186",
        "timeStamp": "1632738360", 
        "blockReward": "388632493476995398"
    }
    """
    blockNumber: str
    timeStamp: str
    blockReward: str

RespPlasmaDeposits = list[RespPlasmaDeposit]

class RespDepositTx(TypedDict):
    """Example response:
    {
        "blockNumber": "132992375",
        "timeStamp": "1741583527",
        "blockHash": "0xef2ff158c8b12be842429f4a8cde58bfa6a389c5274b46f8a1dd2ee7f958ca4d",
        "hash": "0x64ccd0cfa9f333578b36227492f3bc7f5f3ec4bfa82cdc46f82884db680d8e5b", 
        "nonce": "520502",
        "from": "0x36bde71c97b33cc4729cf772ae268934f7ab70b2",
        "to": "0x4200000000000000000000000000000000000007",
        "value": "598200000000000",
        "gas": "490798",
        "gasPrice": "0",
        "input": "0xd764ad0b...",
        "cumulativeGasUsed": "169497",
        "gasUsed": "117234",
        "isError": "0",
        "errDescription": "",
        "txreceipt_status": "1",
        "queueIndex": "999999",
        "L1transactionhash": "0x303bd05c47e62e1243a33210e535ebc70a7567e53a9972fbdef52ee5bcda5acb",
        "L1TxOrigin": "0x36bde71c97b33cc4729cf772ae268934f7ab70b2",
        "tokenAddress": "ETH",
        "tokenSentFrom": "",
        "tokenSentTo": "0x80f3950a4d371c43360f292a4170624abd9eed03",
        "tokenValue": "598200000000000"
    }
    """
    blockNumber: str
    timeStamp: str
    blockHash: str
    hash: str
    nonce: str
    from_: str  # from is a Python keyword, so we use from_
    to: str
    value: str
    gas: str
    gasPrice: str
    input: str
    cumulativeGasUsed: str
    gasUsed: str
    isError: str
    errDescription: str
    txreceipt_status: str
    queueIndex: str
    L1transactionhash: str
    L1TxOrigin: str
    tokenAddress: str
    tokenSentFrom: str
    tokenSentTo: str
    tokenValue: str

RespDepositTxs = list[RespDepositTx]

class RespWithdrawalTx(TypedDict):
    """
    Response model for a withdrawal transaction.
    Example:
    {
        "blockNumber": "132987309",
        "timeStamp": "1741573395", 
        "blockHash": "0xee9bfd69e6866e940c40df94189128534fa5f4af2deec13a793bf49fd5d72f95",
        "hash": "0x481037348afbf205068c2e90d28f7afbb5a1542383e47abf05cbf09a8f960d8d",
        "nonce": "3768",
        "from": "0x7202932b3be70edf0657d5bada261d610e0d7db9",
        "to": "0x5ff137d4b0fdcd49dca30c7cf57e578a026d2789",
        "value": "0",
        "gas": "361196",
        "gasPrice": "162984",
        "input": "0x1fad948c...",
        "cumulativeGasUsed": "8397325",
        "gasUsed": "216038",
        "isError": "0",
        "errDescription": "",
        "txreceipt_status": "1",
        "message": "0x000000...",
        "messageNonce": "1766847064778384329583297500742918515827483896875618958121606201292644580",
        "status": "Waiting",
        "L1transactionhash": "",
        "tokenAddress": "0xdd05d9ee23eda1fcabaffddbf7996be735ac7682",
        "withdrawalType": "ERC20",
        "tokenValue": "1000000000000000000",
        "L1transactionhashProve": ""
    }
    """
    blockNumber: str
    timeStamp: str
    blockHash: str
    hash: str
    nonce: str
    from_: str  # from is a Python keyword, so we use from_
    to: str
    value: str
    gas: str
    gasPrice: str
    input: str
    cumulativeGasUsed: str
    gasUsed: str
    isError: str
    errDescription: str
    txreceipt_status: str
    message: str
    messageNonce: str
    status: str
    L1transactionhash: str
    tokenAddress: str
    withdrawalType: str
    tokenValue: str
    L1transactionhashProve: str

RespWithdrawalTxs = list[RespWithdrawalTx]

class RespCreditUsage(TypedDict):
    """
    Rate limit info response format:
    {
        "creditsUsed": 207,
        "creditsAvailable": 499793, 
        "creditLimit": 500000,
        "limitInterval": "daily",
        "intervalExpiryTimespan": "07:20:05"
    }
    """
    creditsUsed: int
    creditsAvailable: int
    creditLimit: int
    limitInterval: str
    intervalExpiryTimespan: str

class RespSupportedChain(TypedDict):
    """
    Chain info response format:
    {
        "chainname": "Etheum Mainnet",
        "chainid": "1",
        "blockexplorer": "https://etherscan.io",
        "apiurl": "https://api.etherscan.io/v2/api?chainid=1",
        "status": 1
    }
    """
    chainname: str
    chainid: str
    blockexplorer: str
    apiurl: str
    status: int

class RespSupportedChains(TypedDict):
    """
    Supported chains response format:
    {
        "totalcount": 1,
        "result": [
            {
                "chainname": "Etheum Mainnet",
                "chainid": "1",
                "blockexplorer": "https://etherscan.io",
                "apiurl": "https://api.etherscan.io/v2/api?chainid=1",
                "status": 1
    """
    totalcount: int
    result: list[RespSupportedChain]


class RespAddressTag(TypedDict):
    """
    Address label info response format:
    {
        "address": str,
        "nametag": str,
        "internal_nametag": str,
        "url": str,
        "shortdescription": str,
        "notes_1": str,
        "notes_2": str,
        "labels": list[str], eg. DEX, Token Contract, NFT, Uniswap, etc. for ENS: Gitcoin Grantee; for Phishing: Phish / Hack
        "labels_slug": list[str], eg. dex, token-contract, nft, uniswap, etc. for ENS: gitcoin-grantee; for Phishing: phish-hack
        "reputation": int,
        "other_attributes": list[str],
        "lastupdatedtimestamp": int
    }
    """
    address: str
    nametag: str
    internal_nametag: str
    url: str
    shortdescription: str
    notes_1: str
    notes_2: str
    labels: list[str]
    labels_slug: list[str]
    reputation: int
    other_attributes: list[str]
    lastupdatedtimestamp: int

RespAddressTags = list[RespAddressTag]

class RespLabelMaster(TypedDict):
    """
    Label info response format:
    {
        "labelname": str,
        "labelslug": str, 
        "shortdescription": str,
        "notes": str,
        "lastupdatedtimestamp": int
    }
    """
    labelname: str
    labelslug: str
    shortdescription: str
    notes: str
    lastupdatedtimestamp: int

RespLabelMasterlist = list[RespLabelMaster]

class RespLatestCSVBatchNumber(TypedDict):
    """
    Nametag batch info response format:
    {
        "nametag": str,
        "batch": str,
        "lastUpdatedTimestamp": int
    }
    """
    nametag: str
    batch: str
    lastUpdatedTimestamp: int

RespLatestCSVBatchNumbers = list[RespLatestCSVBatchNumber]





