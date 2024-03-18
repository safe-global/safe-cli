"""
Get the correct addresses for the contracts by testing the deployment addresses using the RPC
Currently using Safe v1.4.1 when available, and 1.3.0 as fallback as they are compatible
https://github.com/gnosis/safe-deployments/tree/main/src/assets/v1.4.1
https://github.com/gnosis/safe-deployments/tree/main/src/assets/v1.3.0
"""

from typing import Sequence

from eth_typing import ChecksumAddress

from gnosis.eth import EthereumClient


def _get_valid_contract(
    ethereum_client: EthereumClient, addresses: Sequence[ChecksumAddress]
) -> ChecksumAddress:
    """
    :param ethereum_client:
    :param addresses:
    :return: First valid contract from the list of addresses provided found in blockchain
    """

    for address in addresses:
        if ethereum_client.is_contract(address):
            return address
    raise ValueError(f"Network {ethereum_client.get_network().name} is not supported")


def get_safe_contract_address(ethereum_client: EthereumClient) -> ChecksumAddress:
    return _get_valid_contract(
        ethereum_client,
        [
            "0x41675C099F32341bf84BFc5382aF534df5C7461a",  # v1.4.1
            "0xd9Db270c1B5E3Bd161E8c8503c55cEABeE709552",  # v1.3.0
            "0x69f4D1788e39c87893C980c06EdF4b7f686e2938",  # v1.3.0
        ],
    )


def get_safe_l2_contract_address(ethereum_client: EthereumClient) -> ChecksumAddress:
    return _get_valid_contract(
        ethereum_client,
        [
            "0x29fcB43b46531BcA003ddC8FCB67FFE91900C762",  # v1.4.1
            "0x3E5c63644E683549055b9Be8653de26E0B4CD36E",  # v1.3.0
            "0xfb1bffC9d739B8D520DaF37dF666da4C687191EA",  # v1.3.0
            "0x1727c2c531cf966f902E5927b98490fDFb3b2b70",  # v1.3.0 zkSync
        ],
    )


def get_default_fallback_handler_address(
    ethereum_client: EthereumClient,
) -> ChecksumAddress:
    return _get_valid_contract(
        ethereum_client,
        [
            "0xfd0732Dc9E303f09fCEf3a7388Ad10A83459Ec99",  # v1.4.1
            "0xf48f2B2d2a534e402487b3ee7C18c33Aec0Fe5e4",  # v1.3.0
            "0x017062a1dE2FE6b99BE3d9d37841FeD19F573804",  # v1.3.0
            "0x2f870a80647BbC554F3a0EBD093f11B4d2a7492A",  # v1.3.0 zkSync
        ],
    )


def get_proxy_factory_address(ethereum_client: EthereumClient) -> ChecksumAddress:
    return _get_valid_contract(
        ethereum_client,
        [
            "0x4e1DCf7AD4e460CfD30791CCC4F9c8a4f820ec67",  # v1.4.1
            "0xa6B71E26C5e0845f74c812102Ca7114b6a896AB2",  # v1.3.0
            "0xC22834581EbC8527d974F8a1c97E1bEA4EF910BC",  # v1.3.0
            "0xDAec33641865E4651fB43181C6DB6f7232Ee91c2",  # v1.3.0 zkSync
        ],
    )


def get_last_multisend_address(ethereum_client: EthereumClient) -> ChecksumAddress:
    return _get_valid_contract(
        ethereum_client,
        [
            "0x38869bf66a61cF6bDB996A6aE40D5853Fd43B526",  # v1.4.1
            "0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761",  # v1.3.0
            "0x998739BFdAAdde7C933B942a68053933098f9EDa",  # v1.3.0
            "0x0dFcccB95225ffB03c6FBB2559B530C2B7C8A912",  # v1.3.0 zkSync
        ],
    )


def get_last_multisend_call_only_address(
    ethereum_client: EthereumClient,
) -> ChecksumAddress:
    return _get_valid_contract(
        ethereum_client,
        [
            "0x40A2aCCbd92BCA938b02010E17A5b8929b49130D",  # v1.4.1
            "0x40A2aCCbd92BCA938b02010E17A5b8929b49130D",  # v1.3.0
            "0xA1dabEF33b3B82c7814B6D82A79e50F4AC44102B",  # v1.3.0
            "0xf220D3b4DFb23C4ade8C88E526C1353AbAcbC38F",  # v1.3.0 zkSync
        ],
    )


def get_last_sign_message_lib_address(
    ethereum_client: EthereumClient,
) -> ChecksumAddress:
    return _get_valid_contract(
        ethereum_client,
        [
            "0xd53cd0aB83D845Ac265BE939c57F53AD838012c9",  # v1.4.1
            "0xA65387F16B013cf2Af4605Ad8aA5ec25a2cbA3a2",  # v1.3.0
            "0x98FFBBF51bb33A056B08ddf711f289936AafF717",  # v1.3.0
            "0x357147caf9C0cCa67DfA0CF5369318d8193c8407",  # v1.3.0 zkSync
        ],
    )
