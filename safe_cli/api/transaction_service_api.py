import time
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin

import requests
from eth_account.signers.local import LocalAccount
from hexbytes import HexBytes
from web3 import Web3

from gnosis.eth.ethereum_client import EthereumNetwork
from gnosis.safe import SafeTx

from .base_api import BaseAPI, BaseAPIException


class TransactionServiceApi(BaseAPI):
    URL_BY_NETWORK = {
        EthereumNetwork.MAINNET: "https://safe-transaction-mainnet.safe.global",
        EthereumNetwork.ARBITRUM_ONE: "https://safe-transaction-arbitrum.safe.global",
        EthereumNetwork.AURORA_MAINNET: "https://safe-transaction-aurora.safe.global",
        EthereumNetwork.AVALANCHE_C_CHAIN: "https://safe-transaction-avalanche.safe.global",
        EthereumNetwork.BINANCE_SMART_CHAIN_MAINNET: "https://safe-transaction-bsc.safe.global",
        EthereumNetwork.ENERGY_WEB_CHAIN: "https://safe-transaction-ewc.safe.global",
        EthereumNetwork.GOERLI: "https://safe-transaction-goerli.safe.global",
        EthereumNetwork.POLYGON: "https://safe-transaction-polygon.safe.global",
        EthereumNetwork.OPTIMISM: "https://safe-transaction-optimism.safe.global",
        EthereumNetwork.ENERGY_WEB_VOLTA_TESTNET: "https://safe-transaction-volta.safe.global",
        EthereumNetwork.GNOSIS: "https://safe-transaction-gnosis-chain.safe.global",
    }

    @classmethod
    def create_delegate_message_hash(cls, delegate_address: str) -> str:
        totp = int(time.time()) // 3600
        hash_to_sign = Web3.keccak(text=delegate_address + str(totp))
        return hash_to_sign

    def data_decoded_to_text(self, data_decoded: Dict[str, Any]) -> Optional[str]:
        """
        Decoded data decoded to text
        :param data_decoded:
        :return:
        """
        if not data_decoded:
            return None

        method = data_decoded["method"]
        parameters = data_decoded.get("parameters", [])
        text = ""
        for (
            parameter
        ) in parameters:  # Multisend or executeTransaction from another Safe
            if "decodedValue" in parameter:
                text += (
                    method
                    + ":\n - "
                    + "\n - ".join(
                        [
                            self.data_decoded_to_text(
                                decoded_value.get("decodedData", {})
                            )
                            for decoded_value in parameter.get("decodedValue", {})
                        ]
                    )
                    + "\n"
                )
        if text:
            return text.strip()
        else:
            return (
                method
                + ": "
                + ",".join([str(parameter["value"]) for parameter in parameters])
            )

    def get_balances(self, safe_address: str) -> List[Dict[str, Any]]:
        response = self._get_request(f"/api/v1/safes/{safe_address}/balances/")
        if not response.ok:
            raise BaseAPIException(f"Cannot get balances: {response.content}")
        else:
            return response.json()

    def get_safe_transaction(
        self, safe_tx_hash: bytes
    ) -> Tuple[SafeTx, Optional[HexBytes]]:
        """
        :param safe_tx_hash:
        :return: SafeTx and `tx-hash` if transaction was executed
        """
        safe_tx_hash = HexBytes(safe_tx_hash).hex()
        response = self._get_request(f"/api/v1/multisig-transactions/{safe_tx_hash}/")
        if not response.ok:
            raise BaseAPIException(
                f"Cannot get transaction with safe-tx-hash={safe_tx_hash}: {response.content}"
            )
        else:
            result = response.json()
            # TODO return tx-hash if executed
            signatures = self.parse_signatures(result)
            return (
                SafeTx(
                    self.ethereum_client,
                    result["safe"],
                    result["to"],
                    int(result["value"]),
                    HexBytes(result["data"]) if result["data"] else b"",
                    int(result["operation"]),
                    int(result["safeTxGas"]),
                    int(result["baseGas"]),
                    int(result["gasPrice"]),
                    result["gasToken"],
                    result["refundReceiver"],
                    signatures=signatures if signatures else b"",
                    safe_nonce=int(result["nonce"]),
                ),
                HexBytes(result["transactionHash"])
                if result["transactionHash"]
                else None,
            )

    def parse_signatures(self, raw_tx: Dict[str, Any]) -> Optional[HexBytes]:
        if raw_tx["signatures"]:
            # Tx was executed and signatures field is populated
            return raw_tx["signatures"]
        elif raw_tx["confirmations"]:
            # Parse offchain transactions
            return b"".join(
                [
                    HexBytes(confirmation["signature"])
                    for confirmation in sorted(
                        raw_tx["confirmations"], key=lambda x: int(x["owner"], 16)
                    )
                    if confirmation["signatureType"] == "EOA"
                ]
            )

    def get_transactions(self, safe_address: str) -> List[Dict[str, Any]]:
        response = self._get_request(
            f"/api/v1/safes/{safe_address}/multisig-transactions/"
        )
        if not response.ok:
            raise BaseAPIException(f"Cannot get transactions: {response.content}")
        else:
            return response.json().get("results", [])

    def get_delegates(self, safe_address: str) -> List[Dict[str, Any]]:
        response = self._get_request(f"/api/v1/safes/{safe_address}/delegates/")
        if not response.ok:
            raise BaseAPIException(f"Cannot get delegates: {response.content}")
        else:
            return response.json().get("results", [])

    def post_signatures(self, safe_tx_hash: bytes, signatures: bytes) -> None:
        safe_tx_hash = HexBytes(safe_tx_hash).hex()
        response = self._post_request(
            f"/api/v1/multisig-transactions/{safe_tx_hash}/confirmations/",
            payload={"signature": HexBytes(signatures).hex()},
        )
        if not response.ok:
            raise BaseAPIException(
                f"Cannot post signatures for tx with safe-tx-hash={safe_tx_hash}: {response.content}"
            )

    def add_delegate(
        self,
        safe_address: str,
        delegate_address: str,
        label: str,
        signer_account: LocalAccount,
    ):
        hash_to_sign = self.create_delegate_message_hash(delegate_address)
        signature = signer_account.signHash(hash_to_sign)
        add_payload = {
            "safe": safe_address,
            "delegate": delegate_address,
            "signature": signature.signature.hex(),
            "label": label,
        }
        response = self._post_request(
            f"/api/v1/safes/{safe_address}/delegates/", add_payload
        )
        if not response.ok:
            raise BaseAPIException(f"Cannot add delegate: {response.content}")

    def remove_delegate(
        self, safe_address: str, delegate_address: str, signer_account: LocalAccount
    ):
        hash_to_sign = self.create_delegate_message_hash(delegate_address)
        signature = signer_account.signHash(hash_to_sign)
        remove_payload = {"signature": signature.signature.hex()}
        response = self._delete_request(
            f"/api/v1/safes/{safe_address}/delegates/{delegate_address}/",
            remove_payload,
        )
        if not response.ok:
            raise BaseAPIException(f"Cannot remove delegate: {response.content}")

    def post_transaction(self, safe_address: str, safe_tx: SafeTx):
        url = urljoin(
            self.base_url, f"/api/v1/safes/{safe_address}/multisig-transactions/"
        )
        random_account = "0x1b95E981F808192Dc5cdCF92ef589f9CBe6891C4"
        sender = safe_tx.sorted_signers[0] if safe_tx.sorted_signers else random_account
        data = {
            "to": safe_tx.to,
            "value": safe_tx.value,
            "data": safe_tx.data.hex() if safe_tx.data else None,
            "operation": safe_tx.operation,
            "gasToken": safe_tx.gas_token,
            "safeTxGas": safe_tx.safe_tx_gas,
            "baseGas": safe_tx.base_gas,
            "gasPrice": safe_tx.gas_price,
            "refundReceiver": safe_tx.refund_receiver,
            "nonce": safe_tx.safe_nonce,
            "contractTransactionHash": safe_tx.safe_tx_hash.hex(),
            "sender": sender,
            "signature": safe_tx.signatures.hex() if safe_tx.signatures else None,
            "origin": "Safe-CLI",
        }
        response = requests.post(url, json=data)
        if not response.ok:
            raise BaseAPIException(f"Error posting transaction: {response.content}")
