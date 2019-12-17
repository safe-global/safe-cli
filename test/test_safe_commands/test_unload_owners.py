def test_un_load_legit_safe_owner():
    # Load Safe
    console_safe = ConsoleSafeCommands(safe_address, logger, data_artifacts, network_agent)

    # Load Owner
    owner_private_key_safe = '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    console_safe.load_owner(owner_private_key_safe)

    # Assert the new loaded owner, and the variables that are affected by it
    assert len(console_safe.local_owner_account_list) == 1
    assert console_safe.sender_address == '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'
    assert console_safe.sender_private_key == '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    assert console_safe.sender_address == console_safe.local_owner_account_list[0].address
    assert console_safe.sender_private_key == HexBytes(console_safe.local_owner_account_list[0].privateKey).hex()

    # Unload Owner
    console_safe.command_unload_owner(owner_private_key_safe)

    # Assert current loaded owner, length of local_accounts should be 0 and the values for private_key/address for the
    # sender should be None
    assert len(console_safe.local_owner_account_list) == 0
    assert console_safe.sender_private_key is None
    assert console_safe.sender_address is None


def test_unload_unlegit_safe_owner():
    return