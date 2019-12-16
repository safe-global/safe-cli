# gnosis-cli 0.1.0

Current gnosis-cli was implemented using **python 3.x** and it will focus on the development of a terminal
console to operate with **Safe-Contract** from versions ***0.0.1*** to ***1.1.1*** using tested procedures. 
As side effect of the developing the Safe console a **low-level contract console** will be available 
atleast in the current version of the prototype (the abi will be automatically parsed and the 
function calls generated).

![alt text](https://i.imgur.com/xwVkCol.png)

**[ Console Features ]**

+ Prompt **safe-cli** for directly interact with a Safe contract, using tested procedures in safe-cli.
+ Prompt **contract-cli** for interacting directly with smart contracts using low level calls in contract-cli.
+ Prompt **syntax highlight** for console-cli, contract-cli and safe-cli.
+ Prompt **auto completer** for console-cli, contract-cli and safe-cli commands.
+ Prompt launch options

### [  Run gnosis-cli ]:

+ Run **pip install -r** ***requirements.txt***

+ Previous to launching the console, since this is currently a prototype, Run  **ganache-cli -d** or setup a **network**
and **api_key** to connet to another blockchain. Currently Ganache/Rinkeby are supported, otherwise you will 
be prompted with a **ConnectionError** exception.

+ To launch console use **python** ***gnosis_cli.py***

[![asciicast](https://asciinema.org/a/SI2GwRR8S8QCTU1dLYcKhhs7R.svg)](https://asciinema.org/a/SI2GwRR8S8QCTU1dLYcKhhs7R)

  #### [ Launch Options ]:
    ```
    usage: gnosis_cli.py [-h] [--quiet] [--debug] [--network NETWORK]
                     [--private_key PRIVATE_KEY_COLLECTION]
                     [--api_key API_KEY] [--safe SAFE_ADDRESS]
                     [--contract CONTRACT_COLLECTION] [--abi ABI_COLLECTION]
                     [--erc20 ERC20_COLLECTION] [--erc721 ERC721_COLLECTION]
                     [--test] [--version]

    optional arguments:
      -h, --help            show this help message and exit
      --quiet               This init option will store the value for the quiet
                            param, and subsequently will disable/hide the Banners
                            in the Console. (By default, it will be set to False).
      --debug               This init option will store the value for the debug
                            param, and subsequently will enable the Debug Output
                            Mode in the Console. (By default, it will be set to
                            False).
      --network NETWORK     This init option, will store the value of the network
                            you like to operate with during the execution of the
                            Console. This value can be changed in the Console via
                            setNetwork command, also it can be viewed through
                            viewNetworks command. (By default, it will be set to
                            ganache).
      --private_key PRIVATE_KEY_COLLECTION
                            This init option will store a list o private keys to
                            be initialize during the Loading Processin the Safe
                            Console and they will be converted to LocalAccounts if
                            valid.
      --api_key API_KEY
      --safe SAFE_ADDRESS   This init option, will store the value of the safe
                            address you like to operate with during the execution
                            of the Console. This value will launch directly the
                            safe avoiding the gnosis-cli.
      --contract CONTRACT_COLLECTION
      --abi ABI_COLLECTION  This init option, will store the values of the abi
                            paths you like to operate with during the execution of
                            the Console.
      --erc20 ERC20_COLLECTION
                            This init option, will store the values of the erc20
                            token addresses you like to operate with during the
                            execution of the Console.
      --erc721 ERC721_COLLECTION
                            This init option, will store the values of the erc721
                            token addresses you like to operate with during the
                            execution of the Console.
      --test                This init option will launch the loading 10 random
                            local accounts and the 10 default local accounts
                            provided by the ganacheExample( Ganache Account 0
                            Alias ): isOwner
                            --address=gAccount0.addressblockchain.
      --version             show program's version number and exit
    ```

### [ Avaliable gnosis-cli Commands ]:

+ Command **viewNetwork**:

  This Command will show the current network and the current ***provider*** with the ***url node*** and **status**

    ```
    [ ./gnosis-cli ][  ]: viewNetwork                                                                                                                                                                                                                                              
    10:34:13 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    10:34:13 AM - [ INFO ]: |    Network     |    Network Status    |                                              Node Url                                              |
    10:34:13 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    10:34:13 AM - [ INFO ]: |    GANACHE     |      CONNECTED       |                                       http://localhost:8545                                        |
    10:34:13 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    ```

+ Command **viewContracts**:
  
  This Command will show the current contracts that have been loaded within the gnosis-cli.

    ```
    [ ./gnosis-cli ][  ]: viewContracts                                                                                                                                                                                                                                            
    10:38:25 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    10:38:25 AM - [ INFO ]: |             Alias              |      ContractName      |                      Address                       |     ABI      |   Bytecode   |
    10:38:25 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    10:38:25 AM - [ INFO ]: |        GnosisSafeV1.1.0        |    GnosisSafeV1.1.0    |     0x5b1869D9A4C187F2EAa108f3062412ecf0526b24     |     True     |     True     |
    10:38:25 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    ```

+ Command **viewTokens**:

  This Command will show the current stored tokens that the console currently holds.

    ```
    [ ./safe-cli ][ Safe (0x6C6862EDEB82E767990C0b14d99753927f1afB4B) ]: viewTokens                                                                                                                                                                                                
    10:40:59 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    10:40:59 AM - [ INFO ]: |    Symbol     |                  Address                   |                         Instance                         |        Type        | 
    10:40:59 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    10:40:59 AM - [ INFO ]: |     CHUZA     | 0xE64ffc4f665b92149B21B3E0de99C9E3bbCc0953 | <web3.utils.datatypes.Contract object at 0x7f340792e890> | TypeOfTokens.ERC20 | 
    10:40:59 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    ```

+ Command **viewOwners**:

  This Command will show the current loaded owners within the safe-cli.

    ```
    [ ./safe-cli ][ Safe (0x6C6862EDEB82E767990C0b14d99753927f1afB4B) ]: viewOwners                                                                                                                                                                                                
    10:41:48 AM - [ INFO ]:  -:[ Loaded Owner Data ]:--------------------------------------------------------------------------------------------------------------------
    10:41:48 AM - [ INFO ]: |  (#) Owner 0 | Address: 0x9fF08f7FfF6ab9E3817e33612EbfBCD18d0E165c | Sender: [X] | Balance: 6857186045000000000                            |
    10:41:48 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    ```

+ Command **viewAccounts**:

  This Command will show the current stored accounts that the console currently holds.

    ```
    10:35:13 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    10:35:13 AM - [ INFO ]: |    Account     |                   Address                    |                                Private Key                                 | 
    10:35:13 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    10:35:13 AM - [ INFO ]: |      NULL      |  0x0000000000000000000000000000000000000000  |                                     0x                                     |
    10:35:13 AM - [ INFO ]: |   gAccount0    |  0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1  |     0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d     |
    10:35:13 AM - [ INFO ]: |   gAccount1    |  0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0  |     0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1     |
    10:35:13 AM - [ INFO ]: |   gAccount2    |  0x22d491Bde2303f2f43325b2108D26f1eAbA1e32b  |     0x6370fd033278c143179d81c5526140625662b8daa446c22ee2d73db3707e620c     |
    10:35:13 AM - [ INFO ]: |   gAccount3    |  0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d  |     0x646f1ce2fdad0e6deeeb5c7e8e5543bdde65e86029e2fd9fc169899c440a7913     |
    10:35:13 AM - [ INFO ]: |   gAccount4    |  0xd03ea8624C8C5987235048901fB614fDcA89b117  |     0xadd53f9a7e588d003326d1cbf9e4a43c061aadd9bc938c843a79e7b4fd2ad743     |
    10:35:13 AM - [ INFO ]: |   gAccount5    |  0x95cED938F7991cd0dFcb48F0a06a40FA1aF46EBC  |     0x395df67f0c2d2d9fe1ad08d1bc8b6627011959b79c53d7dd6a3536a33ab8a4fd     |
    10:35:13 AM - [ INFO ]: |   gAccount6    |  0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9  |     0xe485d098507f54e7733a205420dfddbe58db035fa577fc294ebd14db90767a52     |
    10:35:13 AM - [ INFO ]: |   gAccount7    |  0x28a8746e75304c0780E011BEd21C72cD78cd535E  |     0xa453611d9419d0e56f499079478fd72c37b251a94bfde4d19872c44cf65386e3     |
    10:35:13 AM - [ INFO ]: |   gAccount8    |  0xACa94ef8bD5ffEE41947b4585a84BdA5a3d3DA6E  |     0x829e924fdf021ba3dbbc4225edfece9aca04b929d6e75613329ca6f1d31c0bb4     |
    10:35:13 AM - [ INFO ]: |   gAccount9    |  0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e  |     0xb0057716d5917badaf911b193b12b910811c1497b5bada8d7711f758981c3773     |
    10:35:13 AM - [ INFO ]: |   rAccount10   |  0x0a2E699EEB887797425d8E5f6B0f5954044d4F9C  |     0x7f80b8da877e524e2976567b76023fc0641dadf7fefaf8b9d5fa319ee2fcc6c4     |
    10:35:13 AM - [ INFO ]: |   rAccount11   |  0xe187A420C99B6fEAC59fF01cFF9623345EA0b654  |     0x9166fd29e46ac0040e11f616074f87ec8bfd0597aac6a7f1ee073f38aeb3eb17     |
    10:35:13 AM - [ INFO ]: |   rAccount12   |  0x66b4F430E478E61A5c415eDCD0AC50260517fA0A  |     0x7a724ce1fa30434e8bfcf7098af2f9985e755b77782befaf9b518f61223562e2     |
    10:35:13 AM - [ INFO ]: |   rAccount13   |  0x5445FE15C4ccb0cba1c7C02ff149b53a2B57F038  |     0x92754b1a3e2d1abfe13eec3416ce18dbef654fc383a8619a72ba33952cdd8e93     |
    10:35:13 AM - [ INFO ]: |   rAccount14   |  0xB7A02284ED3e0fA63ef30E5F6BF87e0593C9F2ea  |     0x160d8c79acec307d397676697ccde2223f031d2766e65a1412b17eb9594665e1     |
    10:35:13 AM - [ INFO ]: |   rAccount15   |  0x8036a33e68e565e1f3bE309d09f696CFBC519c34  |     0x74b620024d83d2cbd144ef69413e11ae2ea6692105fdb16825dde45a7e227b50     |
    10:35:13 AM - [ INFO ]: |   rAccount16   |  0x01BED4EDCA074b723711DB465aB531274AaD176d  |     0x27931ace797bd2cbc19ef2344910c74ce22ffdf7689cd384df3de2168484886d     |
    10:35:13 AM - [ INFO ]: |   rAccount17   |  0x5ee922012CfAfDe99e52eb80DB99f17b157f297F  |     0xbea8f805581e6223e098527119686d816d8c92ecf11533346c74f96110b568d2     |
    10:35:13 AM - [ INFO ]: |   rAccount18   |  0x6cA9634fF9899003b952dA9C86301707FD2eb6Cf  |     0x9abf2e520a567ac6d62be94c4fefb1acaf76a9cd11ffbcc40968cf9e3337c3c4     |
    10:35:13 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    ```

+ Command **loadSafe --address="safe-address"**:

    ```
    [ ./gnosis-cli ][  ]: loadSafe --address=0x6C6862EDEB82E767990C0b14d99753927f1afB4B  
    10:44:32 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    10:44:32 AM - [ INFO ]: |                                                        :[ Entering Safe Console ]:                                                         |
    10:44:32 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    10:44:33 AM - [ INFO ]:  ===========================================================:[ Safe Information ]:===========================================================
    10:44:33 AM - [ INFO ]:  -:[ Safe Owner Data ]:----------------------------------------------------------------------------------------------------------------------
    10:44:33 AM - [ INFO ]: |  (#) Owner 0 | Address: 0x9fF08f7FfF6ab9E3817e33612EbfBCD18d0E165c | Sender: [ ] | Balance: 6857186045000000000                            |
    10:44:33 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    10:44:33 AM - [ INFO ]:  -:[ Safe Ether Balance ]:-------------------------------------------------------------------------------------------------------------------
    10:44:33 AM - [ INFO ]: |  (#) Total Owners Funds: 6.857186045 Ether                                                                                                 |
    10:44:33 AM - [ INFO ]: |  (#) Total Safe Funds: 1.867489185000000001 Ether                                                                                          |
    10:44:33 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    10:44:33 AM - [ INFO ]:  -:[ Safe Token Balance ]:-------------------------------------------------------------------------------------------------------------------
    10:44:34 AM - [ INFO ]: |  (#) Total Safe CHUZA (0xE64ffc4f665b92149B21B3E0de99C9E3bbCc0953) Funds: 4999999999999999999 Token                                        |
    10:44:34 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    10:44:34 AM - [ INFO ]:  -:[ Safe Threshold ]:-----------------------------------------------------------------------------------------------------------------------
    10:44:34 AM - [ INFO ]: |  (#) Threshold: 1                                                                                                                          |
    10:44:34 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    10:44:34 AM - [ INFO ]:  -:[ Safe General Information ]:-------------------------------------------------------------------------------------------------------------
    10:44:34 AM - [ INFO ]: |  (#) MasterCopy Name: Gnosis Safe                                                                                                          |
    10:44:34 AM - [ INFO ]: |  (#) MasterCopy: 0xb6029EA3B2c51D09a50B53CA8012FeEB05bDa35A                                                                                |
    10:44:35 AM - [ INFO ]: |  (#) MasterCopy Version: 1.0.0                                                                                                             |
    10:44:35 AM - [ INFO ]: |  (#) ProxyCopy: 0x6C6862EDEB82E767990C0b14d99753927f1afB4B                                                                                 |
    10:44:35 AM - [ INFO ]: |  (#) Fallback Handler: 0x0000000000000000000000000000000000000000                                                                          |
    10:44:35 AM - [ INFO ]: |  (#) Nonce: 31                                                                                                                             |
    10:44:35 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    ```

+ Command **loadContract  --alias="contract-alias"**:

    This command will load a contract instance, if --abi/--contract has been passed on launch or via newContract.
    
    ```
    [ ./gnosis-cli ][  ]: loadContract --alias=GnosisSafeV1.1.0                                                                                                                                                                                                                    
    10:46:29 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    10:46:29 AM - [ INFO ]: |                                                      :[ Entering Contract Console ]:                                                       |
    10:46:29 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------

    ```

+ Command **newContract --address=<contract-address> --abi_path=<abi-path>**: **[TODO]**

    ``` 
    [ ./gnosis-cli ][  ]: newContract   
  
    ```

+ Command **newToken**:

    This command will create a new token object to be used as custom sender in the gnosis-cli.

    ```
    [ ./gnosis-cli ][  ]: newToken                                                                                                                                                                                                                                                 
              Type :  ERC20                                                                                                                                                                                                                                                    
           Address :  0xE64ffc4f665b92149B21B3E0de99C9E3bbCc0953                                                                                                                                                                                                               
    10:51:01 AM - [ INFO ]: newToken: {'address': '0xE64ffc4f665b92149B21B3E0de99C9E3bbCc0953', 'instance': <web3.utils.datatypes.Contract object at 0x7fcbd63d74d0>, 'type': <TypeOfTokens.ERC20: 'ERC20'>, 'name': CHUZA}
    ```

+ Command **newPayload**:

    This command will create a new payload object to be used as custom sender in the gnosis-cli.
    ```
    [ ./gnosis-cli ][  ]: newPayload                                                               
             'alias' :  0      
              'from' :  0x      
               'gas' :  0      
          'gasPrice' :  0
    newPayload:  {'from' : '0x', 'gas' : 0, 'gasPrice' : 0}
    ```

+ Command **setNetwork --network="network-name" --api_key="infura-api-key"**:

  This command will set the current network to operate with in the gnosis-cli.

    ```
    [ ./gnosis-cli ][  ]: setNetwork --network=rinkeby --api_key=b3fa360a82cd459e8f1b459b3cf9127c                                                                                                                                                                                  
    10:54:47 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    10:54:47 AM - [ INFO ]: |    Network     |    Network Status    |                                              Node Url                                              |
    10:54:47 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    10:54:47 AM - [ INFO ]: |    RINKEBY     |      CONNECTED       |                   https://rinkeby.infura.io/v3/b3fa360a82cd459e8f1b459b3cf9127c                    |
    10:54:47 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    [ ./gnosis-cli ][  ]: setNetwork --network=ganache                                                                                                                                                                                                                             
    10:55:08 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    10:55:08 AM - [ INFO ]: |    Network     |    Network Status    |                                              Node Url                                              |
    10:55:08 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    10:55:08 AM - [ INFO ]: |    GANACHE     |      CONNECTED       |                                       http://localhost:8545                                        |
    10:55:08 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    ```

+ Command **exit | quit | close**:

  This Command will exit the gnosis-cli. If --now it's not provided the console will prompt a confirmation dialog.

    ```
    [ ./gnosis-cli ][  ]: exit | quit | close
    [ ./gnosis-cli ][  ]: exit | quit | close --now
    ```

### [ Avaliable safe-cli Commands ]:

+ Command **info**:
    
    This Command will show the current information for the loaded safe within safe-cli.

    ```
    10:50:27 AM - [ INFO ]:  ===========================================================:[ Safe Information ]:===========================================================
    10:50:27 AM - [ INFO ]:  -:[ Safe Owner Data ]:----------------------------------------------------------------------------------------------------------------------
    10:50:28 AM - [ INFO ]: |  (#) Owner 0 | Address: 0x9fF08f7FfF6ab9E3817e33612EbfBCD18d0E165c | Sender: [ ] | Balance: 6857186045000000000                            |
    10:50:28 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    10:50:28 AM - [ INFO ]:  -:[ Safe Ether Balance ]:-------------------------------------------------------------------------------------------------------------------
    10:50:28 AM - [ INFO ]: |  (#) Total Owners Funds: 6.857186045 Ether                                                                                                 |
    10:50:28 AM - [ INFO ]: |  (#) Total Safe Funds: 1.867489185000000001 Ether                                                                                          |
    10:50:28 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    10:50:28 AM - [ INFO ]:  -:[ Safe Token Balance ]:-------------------------------------------------------------------------------------------------------------------
    10:50:29 AM - [ INFO ]: |  (#) Total Safe CHUZA (0xE64ffc4f665b92149B21B3E0de99C9E3bbCc0953) Funds: 4999999999999999999 Token                                        |
    10:50:29 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    10:50:29 AM - [ INFO ]:  -:[ Safe Threshold ]:-----------------------------------------------------------------------------------------------------------------------
    10:50:29 AM - [ INFO ]: |  (#) Threshold: 1                                                                                                                          |
    10:50:29 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    10:50:29 AM - [ INFO ]:  -:[ Safe General Information ]:-------------------------------------------------------------------------------------------------------------
    10:50:29 AM - [ INFO ]: |  (#) MasterCopy Name: Gnosis Safe                                                                                                          |
    10:50:29 AM - [ INFO ]: |  (#) MasterCopy: 0xb6029EA3B2c51D09a50B53CA8012FeEB05bDa35A                                                                                |
    10:50:29 AM - [ INFO ]: |  (#) MasterCopy Version: 1.0.0                                                                                                             |
    10:50:29 AM - [ INFO ]: |  (#) ProxyCopy: 0x6C6862EDEB82E767990C0b14d99753927f1afB4B                                                                                 |
    10:50:29 AM - [ INFO ]: |  (#) Fallback Handler: 0x0000000000000000000000000000000000000000                                                                          |
    10:50:30 AM - [ INFO ]: |  (#) Nonce: 31                                                                                                                             |
    10:50:30 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    ```

  Command **viewGas**
  
  This command will show the current gas configuration withing the safe-cli.
  
    ```
    [ ./safe-cli ][ Safe (0x6C6862EDEB82E767990C0b14d99753927f1afB4B) ]: viewGas                                                                                                                                                                                                   
    11:13:53 AM - [ INFO ]:  -:[ Current Gas Configuration ]:------------------------------------------------------------------------------------------------------------
    11:13:53 AM - [ INFO ]: |  (#) BaseGas value 100000                                                                                                                  |
    11:13:53 AM - [ INFO ]: |  (#) SafeTxGas value 300000                                                                                                                |
    11:13:53 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    ```
  
  Command **viewGas**
  
  This command will show the current gas configuration withing the safe-cli.
  
    ```
    [ ./safe-cli ][ Safe (0x6C6862EDEB82E767990C0b14d99753927f1afB4B) ]: viewGas                                                                                                                                                                                                   
    11:13:53 AM - [ INFO ]:  -:[ Current Gas Configuration ]:------------------------------------------------------------------------------------------------------------
    11:13:53 AM - [ INFO ]: |  (#) BaseGas value 100000                                                                                                                  |
    11:13:53 AM - [ INFO ]: |  (#) SafeTxGas value 300000                                                                                                                |
    11:13:53 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    ```
  
  Command setAutoFillTokenDecimals ON / OFF
  
  This command will enable the calculation of the proper amount of decimals to fill in a token transaction. Otherwise
  you'll need to put the proper number of 0.
  
    ```
    [ ./safe-cli ][ Safe (0x6C6862EDEB82E767990C0b14d99753927f1afB4B) ]: setAutoFillTokenDecimals ON / OFF                                                                                                                                                                                                   
    11:19:44 AM - [ INFO ]:  -:[ setAutoFillTokenDecimals ]:-------------------------------------------------------------------------------------------------------------
    11:19:44 AM - [ INFO ]: |  (#) setAutoFillTokenDecimals is (no longer) in effect                                                                                                 |
    11:19:44 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    ```
  Command setAutoExecute ON / OFF
  
  This command will enable the auto execution of the transactions without needing to use --execute in the safe-cli. 
  
    ```
    [ ./safe-cli ][ Safe (0x6C6862EDEB82E767990C0b14d99753927f1afB4B) ]: setAutoExecute ON / OFF 
    11:21:55 AM - [ INFO ]:  -:[ setAutoExecute ]:-----------------------------------------------------------------------------------------------------------------------
    11:21:55 AM - [ INFO ]: |  (#) setAutoExecute is in effect                                                                                                           |
    11:21:55 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    ```
  
  Command setBaseGas 10000
    ```
    [ ./safe-cli ][ Safe (0x6C6862EDEB82E767990C0b14d99753927f1afB4B) ]: setAutoExecute ON / OFF 
    11:21:55 AM - [ INFO ]:  -:[ setAutoExecute ]:-----------------------------------------------------------------------------------------------------------------------
    11:21:55 AM - [ INFO ]: |  (#) setAutoExecute is in effect                                                                                                           |
    11:21:55 AM - [ INFO ]:  --------------------------------------------------------------------------------------------------------------------------------------------
    ```
  
  Command setSafeTxGas 10000
  
  
  Command **VERSION**:

  ```
  [ ./safe-cli ][ Safe (0x(0*40)) ]>: VERSION
  11/30/2019 05:01:41 PM - [INFO]:  | Version: 1.1.0 | 
  
  ```

  Command **NAME**:

  ```
  [ ./safe-cli ][ Safe (0x(0*40)) ]>: NAME
  11/30/2019 05:01:57 PM - [INFO]:  | Name: Gnosis Safe | 
  
  ```

  Command **code**:

  ```
  [ ./safe-cli ][ Safe (0x(0*40)) ]>: code
  11/30/2019 05:00:50 PM - [INFO]:  | Code: b'`\x80`@Rs\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff`\x00T\x16\x7f\xa6\x19Hn\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00`\x005\x14\x15`PW\x80`\x00R` `\x00\xf3[6`\x00\x807`\x00\x806`\x00\x84Z\xf4=`\x00\x80>`\x00\x81\x14\x15`pW=`\x00\xfd[=`\x00\xf3\xfe\xa2ebzzr1X \xb6\x0eAj\xb5\xb1wj .}8\xfd6\xa1@\xb6\x12\x13\xfe\xf71="\xff\xbeUy\no\xd7\x07dsolcC\x00\x05\x0b\x002' | 
  
  ```

  Command **nonce**:

  ```
  [ ./safe-cli ][ Safe (0x(0*40)) ]>: nonce
  11/30/2019 05:02:43 PM - [INFO]:  | Nonce: 0 | 
  
  ```

  Command **exit | quit | close**:

  This command will return you to the gnosis-cli prompt.

  ```
  [ ./safe-cli ][ Safe (0x(0*40)) ]>: exit | close | quit
  
  ```

  Command **isOwner <owner-address>**:

+ ```
  [ ./safe-cli ][ Safe (0x(0*40)) ]>: isOwner 0x(0*40)                           
  11/30/2019 05:04:28 PM - [INFO]:  | Owner with Address: xd03ea8624C8C5987235048901fB614fDcA89b117 | isOwner: True  | 
  
  [ ./safe-cli ][ Safe (0x(0*40)) ]>: isOwner 0x(0*40)                           
  11/30/2019 05:04:28 PM - [INFO]:  | Owner with Address: xd03ea8624C8C5987235048901fB614fDcA89b117 | isOwner: False  | 
  
  ```

+ Command **areOwners <owner-address-0> to <owner-address-n>**

  ```
  [ ./safe-cli ][ Safe (0x(0*40)) ]>: areOwners 0x(0*40) 0x(0*40) 0x(0*40) 0x(0*40) 0x(0*40)
  11/30/2019 05:05:21 PM - [INFO]:  | Owner with Address: xd03ea8624C8C5987235048901fB614fDcA89b117 | isOwner: True  | 
  11/30/2019 05:05:21 PM - [INFO]:  | Owner with Address: x95cED938F7991cd0dFcb48F0a06a40FA1aF46EBC | isOwner: True  | 
  11/30/2019 05:05:21 PM - [INFO]:  | Owner with Address: x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9 | isOwner: True  | 
  11/30/2019 05:05:21 PM - [INFO]:  | Owner with Address: x28a8746e75304c0780E011BEd21C72cD78cd535E | isOwner: True  | 
  11/30/2019 05:05:21 PM - [INFO]:  | Owner with Address: xACa94ef8bD5ffEE41947b4585a84BdA5a3d3DA6E | isOwner: True  | 
  
  ```

+ Command **getOwners**:

  ```
  [ ./safe-cli ][ Safe (0x(0*40)) ]>:  getOwners
  11/30/2019 05:06:16 PM - [INFO]:  | Owner Address: 0xd03ea8624C8C5987235048901fB614fDcA89b117 | 
  11/30/2019 05:06:16 PM - [INFO]:  | Owner Address: 0x95cED938F7991cd0dFcb48F0a06a40FA1aF46EBC | 
  11/30/2019 05:06:16 PM - [INFO]:  | Owner Address: 0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9 | 
  11/30/2019 05:06:16 PM - [INFO]:  | Owner Address: 0x28a8746e75304c0780E011BEd21C72cD78cd535E | 
  11/30/2019 05:06:16 PM - [INFO]:  | Owner Address: 0xACa94ef8bD5ffEE41947b4585a84BdA5a3d3DA6E | 
  
  ```

+ Command **getThreshold**:

  ```
  [ ./safe-cli ][ Safe (0x(0*40)) ]>:  getThreshold
  11/30/2019 05:14:23 PM - [INFO]:  | Threshold: 5 | 
  
  ```

+ Command **changeThreshold <new-threshold-uint>**:

  ```
  [ ./safe-cli ][ Safe (0x(0*40)) ]>: changeThreshold 10
  
  ```

+ Command **addOwner <new-owner-address>**:

  ```
  [ ./safe-cli ][ Safe (0x(0*40)) ]>: addOwner 0x(0*40)
  
  ```

+ Command **addOwnerWithThreshold <new-owner-address> <new-threshold-uint>**:

  ```
  [ ./safe-cli ][ Safe (0x(0*40)) ]>:  addOwnerWithThreshold 0x(0*40) 3
  
  ```

+ Command **changeOwner | swapOwner  <old-owner-address>  <new-owner-address>**:

  ```
  [ ./safe-cli ][ Safe (0x(0*40)) ]>:  changeOwner | swapOwner 0x(0*40) 0x(0*40) 
  
  ```

+ Command **removeOwner  <old-owner-address>**:

  ```
  [ ./safe-cli ][ Safe (0x(0*40)) ]>:  changeOwner | swapOwner 0x(0*40) 0x(0*40) 
  
  ```

+ Command **sendEther  <to-address> <amount-of-ether-uint>**:

  ```
  [./safe-cli ][ Safe (0x(0*40)) ]>:  sendEther 0x(0*40) --ether= --miliEther= --wei= -- 
  
  ```

+ Command **sendToken <to-address> <token-alias> <amount-of-tokens-uint>**:

  ```
  [./safe-cli ][ Safe (0x(0*40)) ]>:  sendToken 0x(0*40) name.Token --ether= --miliEther= --wei=
  
  ```

### [ Avaliable contract-cli Commands ]:

### [ Functional ]

**Modifier** ***--query*** will use a **call()** procedure & ***--execute*** will use a **transact()** procedure

+ Command **contract_method --params --query** for pre-loaded safe contract
+ Command **contract_method --params --execute** for pre-loaded safe contract

## Current Command Roadmap:

### General

+  **[ Pending ]:** Console Input Validator
+  **[ Pending ]:** Fully integrate console argument parsing with ArgParse

+ **[ On Hold ]:** Command newContract --address=0x --abi=(./path/to/abi )
+ **[ Pending ]:** Command setAutoFill On/Off

### Safe CLI

+ **[ In Progress ]**: Implement sendEther procedure with proper sum of the --ether= --miliether= --wei= 
+ **[ In Progress ]:** Implement sendToken procedure
+ **[ In Progress ]:** Automatically select the best fitted owner to be the default sender for the operations with the safe.
+ **[ In Progress ]:** Decoupling from getter and moving operate_with function to a controller class
+ **[ In Progress ]:** Remove prototype operations and add option to pass arguments that are been provided by the user input.
+ **[ Pending ]:** Implement setDefaultGas, setDefaultGasPrice, setDefaultSafeTxGas, setDefaultGasPrice

### Contract CLI

+ **[ On Hold ]:** Improve automatically retrieve function name, function params & autogenerate call and transact using the abi file.
+ **[ On Hold ]:** Functional --query for call, --execute for transact, Pending --queue for future implementation of Batch behaviour (Transactions Needs Review).
+ **[ Future ]:** Command runMacro & newMacro in case the contract needs to be inicialized prior to operations.
