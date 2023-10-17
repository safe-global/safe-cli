class GetMultisigTxRequestMock:
    ok = True

    def __init__(self, executed: bool):
        self.executed = executed

    def json(self):
        return {
            "safe": "0x389416768c1811168ba89940fD7dFD0C190c53a1",
            "to": "0x5aC255889882aCd3da2aA939679E3f3d4cea221e",
            "value": "1000000000000000",
            "data": None,
            "operation": 0,
            "gasToken": "0x0000000000000000000000000000000000000000",
            "safeTxGas": 0,
            "baseGas": 0,
            "gasPrice": "0",
            "refundReceiver": "0x0000000000000000000000000000000000000000",
            "nonce": 6,
            "executionDate": "2023-02-28T20:18:24Z",
            "submissionDate": "2023-02-28T20:18:24Z",
            "modified": "2023-02-28T20:18:24Z",
            "blockNumber": 8573938,
            "transactionHash": "0x7d229cdd1a197acdd23787cedcb7ec4d746ce0e730dff75e209359894af7fb52"
            if self.executed
            else None,
            "safeTxHash": "0xeb5fa8e85dd530397172da07792c5d05dff9ffe5816fc0a260d672e924825b01",
            "proposer": None,
            "executor": "0x5aC255889882aCd3da2aA939679E3f3d4cea221e",
            "isExecuted": True,
            "isSuccessful": True,
            "ethGasPrice": "37052821773",
            "maxFeePerGas": "100000000000",
            "maxPriorityFeePerGas": "1500000000",
            "gasUsed": 59925,
            "fee": "2220390344747025",
            "origin": "{}",
            "dataDecoded": None,
            "confirmationsRequired": 1,
            "confirmations": [
                {
                    "owner": "0x5aC255889882aCd3da2aA939679E3f3d4cea221e",
                    "submissionDate": "2023-02-28T20:18:24Z",
                    "transactionHash": None,
                    "signature": "0x0000000000000000000000005ac255889882acd3da2aa939679e3f3d4cea221e000000000000000000000000000000000000000000000000000000000000000001",
                    "signatureType": "APPROVED_HASH",
                }
            ],
            "trusted": True,
            "signatures": "0x0000000000000000000000005ac255889882acd3da2aa939679e3f3d4cea221e000000000000000000000000000000000000000000000000000000000000000001",
        }
