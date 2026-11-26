from unittest import TestCase

import safe_eth_native
from eth_hash.auto import keccak
from safe_eth.eth.utils import fast_keccak
from web3 import Web3


class TestKeccakBackend(TestCase):
    def test_eth_hash_uses_native_keccak(self):
        """
        web3, eth-utils and eth-account hash with the native keccak256 of safe-eth-py.
        Any `ETH_HASH_BACKEND` value makes them use an eth-hash backend instead
        """
        self.assertEqual(Web3.keccak(b""), fast_keccak(b""))
        self.assertIs(keccak.hasher, safe_eth_native.keccak256)
