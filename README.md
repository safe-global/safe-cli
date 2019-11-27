# gnosis-cli
Python 3 gnosis-cli focuses on the development of a console to operate with the safe-contracts

### [ Run gnosis-cli ]:
+ Run **python setup.py**
+ To Launch the current version for the console, previous to execution, run **ganache-cli -d**
+ Launch console using **python gnosis_cli.py**

## Current Command Roadmap:
### General

+  **[ Partial Implementation ]:** CLI Syntax Highlight
+  **[ Partial Implementation ]:** CLI with Multi Session Implementation for the loaded Contracts and Configuration Menus
+  **[ Partial Implementation ]:** CLI AutoCompleter
+  **[ In Progress ]:** CLI Input Validator
+  **[ Pending ]:** Move from concept Parsing to ArgParse implementation 
+  **[ Pending ]:** ArgParse implementation on cli launch --silence|--debug|--network=|--abi=|--build=|--address=

### Gnosis CLI

+ **[ Partial Implementation ]:** Command newContract, loadContract --address=0x --abi=(./path/to/abi | abi_asset )
+ **[ Partial Implementation ]:** Command setNerwork --id=| --name=
+ **[ Implemented ]:** Command viewNetwork

### Contract CLI

+ **[ Implemented ]:** Automatically retrieve function name, function params & autogenerate call and transact using the abi file
+ **[ Partial Implementation ]:** Functional --query for call, --execute for transact, Pending --queue for future implementation of Batch behaviour (Transactions Needs Review)
+ **[ Pending ]:** Command setDefaultGasLimit, setDefaultGas, setDefaultGasLimit, etc etc to be able to autofill the params
+ **[ Pending ]:** Command setAutoFill On/Off
+ **[ Pending ]:** Command setDefaultOwner 0x(0*40) & setDefaultOwnerList 0x(0*40) 0x(0*40) 0x(0*40) to be able to autofill the params
+ **[ Pending ]:** Command view txReceipts, txHistory, batchQueue, defaultOwners
+ **[ Pending ]:** Command runSetup & newSetup in case the contract needs to be inicialized prior to operations
+ **[ Pending ]:** Command newPayload (uPayload0/Alias) & setDefaultPayload to generate a custom Transaction Data to be autofilled

## Operations with cli:

#### [ Functional ]:
+ viewNetwork
+ viewPayloads
+ viewAccounts
+ viewContracts
+ loadContract --alias=Gnosis-Safe-v1.1.0 or loadContract --alias=uContract1

### [ Partial Functioning ]
+ setNetwork --name=ganache ***(Pending Proper Validation)***
+ setDefaultOwner
+ setDefaultOwnerList
+ newContract --abi=/path/to/abi --address=0x(0*40) ***(Pending Proper Validation & Execution)***
+ newPayload
+ newTxPayload

### [ Pending ]
+ setDefaultGas
+ setDefaultGasPrice
+ setDefaultSafeTxGas
+ setDefaultGasPrice

### Gnosis Safe Contract

### [ Functional ]

+ getThreshold --query
+ getOwners --query
+ isOwner --address=0x(0*40) --query
+ NAME --query
+ VERSION --query
+ nonce --query

### [ In Progress ]

+ swapOwner --execute
+ changeThreshold --execute 