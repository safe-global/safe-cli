
from gnosis.eth.ethereum_client import EthereumClient

ethereum_client = EthereumClient()
provider = ethereum_client.w3_provider

print('-------' * 10)
print('[ Summary ]: From Ganache Account To Random Account Transfer')
print(' (+) Balance in Safe Proxy Account: ', provider.eth.getBalance(str(contract_artifacts['Proxy']['address'])))
print(' (+) Balance in Random Account: ', provider.eth.getBalance(str(random_account_address)))
print(' (+) Balance in Ganache Account: ', provider.eth.getBalance(str(account2)))
print('Done.\n')

# Tx Data
tx_data0 = dict(
    nonce=provider.eth.getTransactionCount(str(account2)),
    gasPrice=provider.eth.gasPrice,
    gas=100000,
    to=str(random_account_address),
    value=provider.toWei(1.2, 'ether')
)
signed_txn = provider.eth.account.signTransaction(tx_data0, private_key_account2)
tmp_txn_hash = provider.eth.sendRawTransaction(signed_txn.rawTransaction)

# Wait for the transaction to be mined, and get the transaction receipt
receipt_txn_hash = provider.eth.waitForTransactionReceipt(tmp_txn_hash)
tx_history.add_tx_to_history(ganache_provider['name'], account2, receipt_txn_hash, tx_data0)

print('-------' * 10)
print('[ Summary ]: From Ganache Account To Random Account Transfer')
print(' + Balance in Safe Proxy Account: ', provider.eth.getBalance(str(contract_artifacts['Proxy']['address'])))
print(' + Balance in Random Account: ', provider.eth.getBalance(str(random_account_address)))
print(' + Balance in Ganache Account: ', provider.eth.getBalance(str(account2)))
print('Done.\n')

# Tx Data
tx_data1 = dict(
    nonce=provider.eth.getTransactionCount(str(random_account_address)),
    gasPrice=provider.eth.gasPrice,
    gas=100000,
    to=str(contract_artifacts['Proxy']['address']),
    value=provider.toWei(1.1, 'ether')
)

random_acc_signed_txn = provider.eth.account.signTransaction(tx_data1, random_private_key)
random_acc_tmp_txn_hash = provider.eth.sendRawTransaction(random_acc_signed_txn.rawTransaction)

# Wait for the transaction to be mined, and get the transaction receipt
random_acc_receipt_txn_hash = provider.eth.waitForTransactionReceipt(random_acc_tmp_txn_hash)

tx_history.add_tx_to_history(ganache_provider['name'], random_account_address, random_acc_receipt_txn_hash, tx_data1)
print('-------' * 10)
print('[ Summary ]: From Random Account To Proxy Safe Account Transfer')
print(' + Balance in Safe Proxy Account: ', provider.eth.getBalance(str(contract_artifacts['Proxy']['address'])))
print(' + Balance in Random Account: ', provider.eth.getBalance(str(random_account_address)))
print(' + Balance in Ganache Account: ', provider.eth.getBalance(str(account2)))
print('Done.\n')
print('-------' * 10)
print('[ Summary ]: Transaction History')
print(tx_history.history)
print('Done.\n')

# note: Send Money to a Newly created account in the network, and lastly beetween safes?
# note: Make Tx from the Safe
# reference: https://gnosis-safe.readthedocs.io/en/version_0_0_2/services/relay.html
# reference: https://ethereum.stackexchange.com/questions/760/how-is-the-address-of-an-ethereum-contract-computed/761#761
# note: The proxy contract implements only two functions: The constructor setting the address of the master copy
multi_sig_to = Account.create()
multi_sig_address = multi_sig_to.address
multi_sig_private_key = multi_sig_to.privateKey
print('[ Generate Account() ]')
print(' (+) 2ºRandom Address: ', multi_sig_address)
print(' (+)) 2ºRandom Private Key: ', multi_sig_private_key)
print('Done.\n')

