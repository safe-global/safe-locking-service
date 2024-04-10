from hexbytes import HexBytes
from web3.datastructures import AttributeDict
from web3.types import LogReceipt

invalid_key_event_mock: LogReceipt = AttributeDict(
    {
        "address": "0x286A5d99174B45A182C28227760494bb730F7996",
        "blockHash": HexBytes(
            "0x6e1f11c92f838e977a6d4faa739079c59e9a5568ba1a690dd433d625cf824855"
        ),
        "blockNumber": 1523,
        "data": HexBytes(
            "0x0000000000000000000000000000000000000000000000000000000000000064"
        ),
        "logIndex": 2,
        "removed": False,
        "topics": [
            HexBytes(
                "0xe87ef84d870121e49051dda6f8d297713cb00a0c072f0d771f78ea368815009f"
            ),
            HexBytes(
                "0x00000000000000000000000022d491bde2303f2f43325b2108d26f1eaba1e32a"
            ),
        ],
        "transactionHash": HexBytes(
            "0x396bccc79fca90671f6719d9572b9fda55b1985041e048faa6ba7da2b11d318b"
        ),
        "transactionIndex": 0,
    }
)

valid_lock_event_mock: LogReceipt = AttributeDict(
    {
        "address": "0x286A5d99174B45A182C28227760494bb730F7996",
        "blockHash": HexBytes(
            "0x6e1f11c92f838e977a6d4faa739079c59e9a5568ba1a690dd433d625cf824855"
        ),
        "blockNumber": 1523,
        "data": HexBytes(
            "0x0000000000000000000000000000000000000000000000000000000000000064"
        ),
        "logIndex": 2,
        "removed": False,
        "topics": [
            HexBytes(
                "0xe87ef84d870121e49051dda6f8d297713cb00a0c072c0d771f78ea368815009f"
            ),
            HexBytes(
                "0x00000000000000000000000022d491bde2303f2f43325b2108d26f1eaba1e32a"
            ),
        ],
        "transactionHash": HexBytes(
            "0x396bccc79fca90671f6719d9572b9fda55b1985041e048faa6ba7da2b11d318b"
        ),
        "transactionIndex": 0,
    }
)

invalid_lock_event_mock: LogReceipt = AttributeDict(
    {
        "address": "0x286A5d99174B45A182C28227760494bb730F7996",
        "blockHash": HexBytes(
            "0x6e1f11c92f838e977a6d4faa739079c59e9a5568ba1a690dd433d625cf824855"
        ),
        "blockNumber": 1523,
        "data": HexBytes("0x"),
        "logIndex": 2,
        "removed": False,
        "topics": [
            HexBytes(
                "0xe87ef84d870121e49051dda6f8d297713cb00a0c072c0d771f78ea368815009f"
            ),
            HexBytes("0x"),
        ],
        "transactionHash": HexBytes(
            "0x396bccc79fca90671f6719d9572b9fda55b1985041e048faa6ba7da2b11d318b"
        ),
        "transactionIndex": 0,
    }
)

valid_unlock_event_mock: LogReceipt = AttributeDict(
    {
        "address": "0x286A5d99174B45A182C28227760494bb730F7996",
        "blockHash": HexBytes(
            "0x4320d20c35235e62e8c40382bc5965561d49a194b868ab1460322a5445047c11"
        ),
        "blockNumber": 1533,
        "data": HexBytes(
            "0x000000000000000000000000000000000000000000000000000000000000000a"
        ),
        "logIndex": 0,
        "removed": False,
        "topics": [
            HexBytes(
                "0x1bd2aac5b8fbf8aacc4b880dbd7230d62fc208b7c317a6f219a23703a80262c8"
            ),
            HexBytes(
                "0x00000000000000000000000022d491bde2303f2f43325b2108d26f1eaba1e32b"
            ),
            HexBytes(
                "0x0000000000000000000000000000000000000000000000000000000000000009"
            ),
        ],
        "transactionHash": HexBytes(
            "0x6a5ee672171a64e7811a35900115bea47dc4db835d89f0a10be1309102e2c466"
        ),
        "transactionIndex": 0,
    }
)

invalid_unlock_event_mock: LogReceipt = AttributeDict(
    {
        "address": "0x286A5d99174B45A182C28227760494bb730F7996",
        "blockHash": HexBytes(
            "0x4320d20c35235e62e8c40382bc5965561d49a194b868ab1460322a5445047c11"
        ),
        "blockNumber": 1533,
        "data": HexBytes("0x"),
        "logIndex": 0,
        "removed": False,
        "topics": [
            HexBytes(
                "0x1bd2aac5b8fbf8aacc4b880dbd7230d62fc208b7c317a6f219a23703a80262c8"
            ),
            HexBytes("0x"),
            HexBytes("0x"),
        ],
        "transactionHash": HexBytes(
            "0x6a5ee672171a64e7811a35900115bea47dc4db835d89f0a10be1309102e2c466"
        ),
        "transactionIndex": 0,
    }
)

valid_withdrawn_event_mock: LogReceipt = AttributeDict(
    {
        "address": "0x286A5d99174B45A182C28227760494bb730F7996",
        "blockHash": HexBytes(
            "0xae7b647d58d989545a93a7748470fd957c4897417b3da3a9d7aaaf44ed61a286"
        ),
        "blockNumber": 1535,
        "data": HexBytes(
            "0x000000000000000000000000000000000000000000000000000000000000000a"
        ),
        "logIndex": 2,
        "removed": False,
        "topics": [
            HexBytes(
                "0xd37890a72e2e5df42bee9bd278d8b896297dffeb08b2b2503f726cfb2e3b9826"
            ),
            HexBytes(
                "0x00000000000000000000000022d491bde2303f2f43325b2108d26f1eaba1e32b"
            ),
            HexBytes(
                "0x0000000000000000000000000000000000000000000000000000000000000002"
            ),
        ],
        "transactionHash": HexBytes(
            "0x4ff4c69ee6267e96191f5cc12096dfca19de772461ca0eaa69dec544ca2a9b47"
        ),
        "transactionIndex": 0,
    }
)

invalid_withdrawn_event_mock: LogReceipt = AttributeDict(
    {
        "address": "0x286A5d99174B45A182C28227760494bb730F7996",
        "blockHash": HexBytes(
            "0xae7b647d58d989545a93a7748470fd957c4897417b3da3a9d7aaaf44ed61a286"
        ),
        "blockNumber": 1535,
        "data": HexBytes("0x"),
        "logIndex": 2,
        "removed": False,
        "topics": [
            HexBytes(
                "0xd37890a72e2e5df42bee9bd278d8b896297dffeb08b2b2503f726cfb2e3b9826"
            ),
            HexBytes("0x"),
            HexBytes("0x"),
        ],
        "transactionHash": HexBytes(
            "0x4ff4c69ee6267e96191f5cc12096dfca19de772461ca0eaa69dec544ca2a9b47"
        ),
        "transactionIndex": 0,
    }
)
