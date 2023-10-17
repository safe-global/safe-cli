data_decoded_mock = {
    "method": "multiSend",
    "parameters": [
        {
            "name": "transactions",
            "type": "bytes",
            "value": "0x00c68877b75c3f9b950a798f9c9df4cde121c432ed000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000247de7edef00000000000000000000000034cfac646f301356faa8b21e94227e3583fe3f5f00c68877b75c3f9b950a798f9c9df4cde121c432ed00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000024f08a0323000000000000000000000000d5d82b6addc9027b22dca772aa68d5d74cdbdf44",
            "decodedValue": [
                {
                    "operation": "CALL",
                    "to": "0xc68877B75c3f9b950a798f9C9dF4cDE121C432eD",
                    "value": 0,
                    "data": "0x7de7edef00000000000000000000000034cfac646f301356faa8b21e94227e3583fe3f5f",
                    "decodedData": {
                        "method": "changeMasterCopy",
                        "parameters": [
                            {
                                "name": "_masterCopy",
                                "type": "address",
                                "value": "0x34CfAC646f301356fAa8B21e94227e3583Fe3F5F",
                            }
                        ],
                    },
                },
                {
                    "operation": "CALL",
                    "to": "0xc68877B75c3f9b950a798f9C9dF4cDE121C432eD",
                    "value": 0,
                    "data": "0xf08a0323000000000000000000000000d5d82b6addc9027b22dca772aa68d5d74cdbdf44",
                    "decodedData": {
                        "method": "setFallbackHandler",
                        "parameters": [
                            {
                                "name": "handler",
                                "type": "address",
                                "value": "0xd5D82B6aDDc9027B22dCA772Aa68D5d74cdBdF44",
                            }
                        ],
                    },
                },
            ],
        }
    ],
}
