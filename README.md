# gnosis-cli
Python 3 gnosis-cli focuses on the development of a console to operate with the safe-contracts

### [ Run gnosis-cli ]:
+ Run **python setup.py**
+ To Launch the current version for the console, previous to execution, run **ganache-cli -d**
+ Launch console using **python gnosis_cli.py**
+ Once you are in the console, for now you can use loadContract --alias=uContract or --alias=GnosisSafeV1.1.0 to enter a contract session.

## Current Command Roadmap:
### General

+  **[ Partial Implementation ]:** Prompt CLI Syntax Highlight
+  **[ Partial Implementation ]:** Prompt CLI with Multi Session Implementation for the loaded Contracts and Configuration Menus
+  **[ Partial Implementation ]:** Prompt CLI AutoCompleter
+  **[ Pending ]:** Prompt CLI Input Validator
+  **[ Pending ]:** Move from concept Parsing to ArgParse implementation 
+  **[ Pending ]:** ArgParse implementation on cli launch --silence|--debug|--network=|--abi=|--build=|--address=

### Gnosis CLI

+ **[ Partial Implementation ]:** Command newContract --address=0x --abi=(./path/to/abi )
+ **[ Partial Implementation ]:** Command loadContract --address=0x --abi=(./path/to/abi )
+ **[ Partial Implementation ]:** Command setNerwork --id=| --name=
+ **[ Implemented ]:** Command viewNetwork

### Contract CLI

+ **[ Implemented ]:** Automatically retrieve function name, function params & autogenerate call and transact using the abi file
+ **[ Partial Implementation ]:** Functional --query for call, --execute for transact, Pending --queue for future implementation of Batch behaviour (Transactions Needs Review)
+ **[ Pending ]:** Command setDefaultGasLimit, setDefaultGas, setDefaultGasLimit, etc etc to be able to autofill the params
+ **[ Pending ]:** Command setDefaultOwner 0x(0*40) & setDefaultOwnerList 0x(0*40) 0x(0*40) 0x(0*40) to be able to autofill the params
+ **[ Partial Implementation ]:** Command newPayload (uPayload0/Alias) & setDefaultPayload to generate a custom Transaction Data to be autofilled
+ **[ Future ]:** Command runSetup & newSetup in case the contract needs to be inicialized prior to operations
+ **[ Future ]:** Command setAutoFill On/Off

## Operations with cli:

#### [ Functional ]:
+ viewNetwork, viewPayloads, viewAccounts, viewContracts
+ (Preloaded Contract without name) loadContract --alias=uContract1
+ (Preloaded Contract with name) loadContract --alias=GnosisSafeV1.1.0
+ (Developing) loadSafe --address=0x0... will search in the abi assets to find the one that fits the address 


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
