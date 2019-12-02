# gnosis-cli

gnosis-cli was implemented using **python3** and it will focus on development a console to operate with **safe-console** from versions ***0.0.1*** to ***1.1.0*** with tested procedures. Additionally as side effect of the developing the safe-console a **low-level contract console** will be available atleast in the current version of the prototype, the abi will be automatically parsed and the function calls generated. This can be accessed via method params --query or --execute calls.

**[ Console Features ]**

+ Prompt safe-cli for directly interact with a safe, using tested procedures with gnosis-py
+ Prompt contract-cli for interacting directly with smart contracts using low level procedures.
+ Prompt syntax highlight for console, contract and safe syntax
+ Prompt auto completer for console, contract and safe commands
+ Prompt launch options

### [  Run gnosis-cli ]:

+ Run **pip install -r** ***requirements.txt***

+ Previous to launching the console, since this is currently a prototype, Run  **ganache-cli -d**, otherwise you will be prompted with a **ConnectionError** exception.

+ To launch console use **python** ***gnosis_cli.py***

  #### [ Launch Options ]:

  + Launch option ***--debug*** will enable debug mode.

  + Launch option ***--network <network-name>***

  + Launch option ***--private_key <private-key-0> to <private-key-n>***

  + Launch option ***--help*** or ***-h***

    ```
    usage: gnosis_cli.py [-h] [--silence] [--debug] [--network NETWORK]
                         [--private_key PRIVATE_KEY_COLLECTION] [--version]
    
    optional arguments:
      -h, --help            show this help message and exit
      --silence             This init option will store the value for the silence
                            param, and subsequently will disable/hide the Loading
                            Process in the Console. (By default, it will be set to
                            False).
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
                            be initialize during the Loading Processin the Console
                            and they will be converted to LocalAccounts. Those
                            values can be viewed through viewAccounts command.
                            Additionally while using the General Contract or Safe
                            ContractConsoles, those values can be accessed during
                            contract interaction via alias. Example( Ganache
                            Account 0 Alias ): isOwner --address=gAccount0.address
      --version             show program's version number and exit
    ```

### [ Avaliable gnosis-cli Commands ]:

+ Command **viewNetwork**:

  This Command will show the current network and the current ***provider*** with the ***url node***.

  ```
  [ GNOSIS-CLI v0.0.1a ]>: viewNetwork
  11/30/2019 03:56:56 PM - [INFO]:  | Network Status: True | 
  11/30/2019 03:56:56 PM - [INFO]:  | Connected to Ganache Through http://localhost:8545 | 
  ```

+ Command **viewContracts**:

  ```
  [ GNOSIS-CLI v0.0.1a ]>: viewContracts
  GnosisSafeV1.1.0 0x5109F62E4e0CA152f5543E59E42dc0360C3aeD25 <web3.utils.datatypes.Contract object at 0x7f077e997f50>
  uContract1 0x5109F62E4e0CA152f5543E59E42dc0360C3aeD25 <web3.utils.datatypes.Contract object at 0x7f077e997f50>
  
  ```

+ Command **viewTokens**:

  This Command will show the current stored tokens that the console currently holds. **[ Todo ]**

  ```
  [ GNOSIS-CLI v0.0.1a ]>: viewTokens
  ```

+ Command **viewOwners**:

  This Command will show the current stored default owner & default owner list that the console currently holds. **[ Todo ]**

  ```
  [ GNOSIS-CLI v0.0.1a ]>: viewOwners
  ```

+ Command **viewAccounts**:

  This Command will show the current stored accounts that the console currently holds.

  ```
  11/30/2019 04:05:44 PM - [INFO]:  |      NULL       | TypeOfAccount.LOCAL_ACCOUNT |             0             |     0x0000000000000000000000000000000000000000     | b'' 
  11/30/2019 04:05:44 PM - [INFO]:  |    gAccount0    | TypeOfAccount.LOCAL_ACCOUNT |   99372862240000000000    |     0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1     | b'O>\xdf\x98:\xc66\xa6Z\x84,\xe7\xc7\x8d\x9a\xa7\x06\xd3\xb1\x13\xbc\xe9\xc4o0\xd7\xd2\x17\x15\xb2;\x1d' 
  11/30/2019 04:05:44 PM - [INFO]:  |    gAccount1    | TypeOfAccount.LOCAL_ACCOUNT |   100000000000000000000   |     0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0     | b'l\xbe\xd1\\y<\xe5vP\xb9\x87|\xf6\xfa\x15o\xbe\xf5\x13\xc4\xe6\x13O\x02*\x85\xb1\xff\xddY\xb2\xa1' 
  11/30/2019 04:05:44 PM - [INFO]:  |    gAccount2    | TypeOfAccount.LOCAL_ACCOUNT |   100000000000000000000   |     0x22d491Bde2303f2f43325b2108D26f1eAbA1e32b     | b'cp\xfd\x032x\xc1C\x17\x9d\x81\xc5Ra@bVb\xb8\xda\xa4F\xc2.\xe2\xd7=\xb3p~b\x0c' 
  11/30/2019 04:05:44 PM - [INFO]:  |    gAccount3    | TypeOfAccount.LOCAL_ACCOUNT |   100000000000000000000   |     0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d     | b'do\x1c\xe2\xfd\xad\x0em\xee\xeb\\~\x8eUC\xbd\xdee\xe8`)\xe2\xfd\x9f\xc1i\x89\x9cD\ny\x13' 
  11/30/2019 04:05:44 PM - [INFO]:  |    gAccount4    | TypeOfAccount.LOCAL_ACCOUNT |   99973541040000000000    |     0xd03ea8624C8C5987235048901fB614fDcA89b117     | b'\xad\xd5?\x9a~X\x8d\x003&\xd1\xcb\xf9\xe4\xa4<\x06\x1a\xad\xd9\xbc\x93\x8c\x84:y\xe7\xb4\xfd*\xd7C' 
  11/30/2019 04:05:44 PM - [INFO]:  |    gAccount5    | TypeOfAccount.LOCAL_ACCOUNT |   100000000000000000000   |     0x95cED938F7991cd0dFcb48F0a06a40FA1aF46EBC     | b"9]\xf6\x7f\x0c--\x9f\xe1\xad\x08\xd1\xbc\x8bf'\x01\x19Y\xb7\x9cS\xd7\xddj56\xa3:\xb8\xa4\xfd" 
  11/30/2019 04:05:44 PM - [INFO]:  |    gAccount6    | TypeOfAccount.LOCAL_ACCOUNT |   100000000000000000000   |     0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9     | b'\xe4\x85\xd0\x98P\x7fT\xe7s: T \xdf\xdd\xbeX\xdb\x03_\xa5w\xfc)N\xbd\x14\xdb\x90vzR' 
  11/30/2019 04:05:44 PM - [INFO]:  |    gAccount7    | TypeOfAccount.LOCAL_ACCOUNT |   100000000000000000000   |     0x28a8746e75304c0780E011BEd21C72cD78cd535E     | b'\xa4Sa\x1d\x94\x19\xd0\xe5oI\x90yG\x8f\xd7,7\xb2Q\xa9K\xfd\xe4\xd1\x98r\xc4L\xf6S\x86\xe3' 
  11/30/2019 04:05:44 PM - [INFO]:  |    gAccount8    | TypeOfAccount.LOCAL_ACCOUNT |   100000000000000000000   |     0xACa94ef8bD5ffEE41947b4585a84BdA5a3d3DA6E     | b'\x82\x9e\x92O\xdf\x02\x1b\xa3\xdb\xbcB%\xed\xfe\xce\x9a\xca\x04\xb9)\xd6\xe7V\x132\x9c\xa6\xf1\xd3\x1c\x0b\xb4' 
  11/30/2019 04:05:44 PM - [INFO]:  |    gAccount9    | TypeOfAccount.LOCAL_ACCOUNT |   100000000000000000000   |     0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e     | b'\xb0\x05w\x16\xd5\x91{\xad\xaf\x91\x1b\x19;\x12\xb9\x10\x81\x1c\x14\x97\xb5\xba\xda\x8dw\x11\xf7X\x98\x1c7s' 
  11/30/2019 04:05:44 PM - [INFO]:  |   rAccount10    | TypeOfAccount.LOCAL_ACCOUNT |             0             |     0x9E7bBd61950Fe554c31ac39bC41E79c6483E7856     | b'Kc\xbe~\xefc\x00\xcf \xfeb(U1\x06qs*\xbd\xfe\x8f\x9a6\x12,\xf6.5\xed\xfdD\xea' 
  11/30/2019 04:05:44 PM - [INFO]:  |   rAccount11    | TypeOfAccount.LOCAL_ACCOUNT |             0             |     0x6f9B076b62a1aA4bBC38Cf0a7B7f2cf9A2e839Dd     | b'\xd7\xb0\xda\xea\xcc\x99\xbc\xf9M\xeb]R\xff\x89\xfa\xf7(x\x07\xa68\xbe7\xb0\xc7\xc7/\xad\xc1\xf4\x15\x91' 
  11/30/2019 04:05:44 PM - [INFO]:  |   rAccount12    | TypeOfAccount.LOCAL_ACCOUNT |             0             |     0x472f0150f314bC25Ee0A73cfAD0361b074D0e406     | b'\xdf\x8dF\xbfK\xd9\x97\x0f\xf5\xe9&\x9b\x16\x90\x8fB\xf30\x98\xdd\x19\xb9n\xeab\x8cV\xba\x83_x\x94' 
  11/30/2019 04:05:44 PM - [INFO]:  |   rAccount13    | TypeOfAccount.LOCAL_ACCOUNT |             0             |     0x668AEF25343D44e6cfDcea9f7AE5D79a3Ed32B98     | b"T\xd6[\r'\x00kh\x96!\xc8\x98se\xe6Y\xac\xae\xb2\x08\xd6\xfex\xa4Q\xeb\xa1\x9c\x06b@\xc7" 
  11/30/2019 04:05:44 PM - [INFO]:  |   rAccount14    | TypeOfAccount.LOCAL_ACCOUNT |             0             |     0x8b6003fB122586C3596207E87cB856841Cf45094     | b'sI_\x1c\x9cb<*\xe8v\xa0Y0\xf0Z\x99\xcd\x96\xaa&cJP\xbe\x8a5\xfe\xc5+\x06C\xdf' 
  11/30/2019 04:05:44 PM - [INFO]:  |   rAccount15    | TypeOfAccount.LOCAL_ACCOUNT |             0             |     0x24448fA378c556737C64FA37161daD4B08562FfA     | b'd\x8bF\x915h?E\x00\xb3\xa8\t\xfb\xc7\x9ba\xbd}\x8eT[\xe3\x17\x91\x95B\x96\xc5\x94\x0c\xce\xcd' 
  11/30/2019 04:05:44 PM - [INFO]:  |   rAccount16    | TypeOfAccount.LOCAL_ACCOUNT |             0             |     0xaCe40fad359271F474A47572d7FaF073A39730d6     | b'\xeb\xbb\x83\xbf\x96\xb1q\xb2H\x9a\xb0\xec\xcf\xa9M\xda\xf7\x93\xd4c\xfa\xb6{\xa1\xf9\xb3\xa0\xa4\xfe^c9' 
  11/30/2019 04:05:44 PM - [INFO]:  |   rAccount17    | TypeOfAccount.LOCAL_ACCOUNT |             0             |     0xC983175F8A803ba0Bc098d0Ae8646eae04d64d52     | b'J\x8b2\xbb5\x9b\xb4\xac\xe6\xf0\xe6\xd6\x96\x85-\x18[\xfaM>$:F\xeb\x1e\x93\xc4\xde\x03CO\xf6' 
  11/30/2019 04:05:44 PM - [INFO]:  |   rAccount18    | TypeOfAccount.LOCAL_ACCOUNT |             0             |     0xB88cC272371Ba4Dd5779eedc78612646a15CBf59     | b'\x95C\xbeQ\xb9\xd2\xe1&\xa7XyNY\xaf\xbac\x16@\x8e\xb4\xb1\xc5\x8a\xbe5\xf1\x17\xab{\xdc!-' 
  [ GNOSIS-CLI v0.0.1a ]>: viewAccounts
  
  ```

+ Command **loadSafe --address=<safe-address>**:

  ```
  [ GNOSIS-CLI v0.0.1a ]>: loadSafe --address=0x5fD287667AC7D13161648e82dA6e8B8A3C9Bc432            11/30/2019 04:12:02 PM - [INFO]:  | Name: Gnosis Safe | 
  11/30/2019 04:12:02 PM - [INFO]:  | Version: 1.1.0 | 
  11/30/2019 04:12:02 PM - [INFO]:  | Master Copy Address: 0xA57B8a5584442B467b4689F1144D269d096A3daF | 
  11/30/2019 04:12:02 PM - [INFO]:  | Proxy Address: 0x5fD287667AC7D13161648e82dA6e8B8A3C9Bc432 | 
  11/30/2019 04:12:02 PM - [INFO]:  | Nonce: 0 | 
  11/30/2019 04:12:02 PM - [INFO]:  | Owner Address: 0xd03ea8624C8C5987235048901fB614fDcA89b117 | 
  11/30/2019 04:12:02 PM - [INFO]:  | Owner Address: 0x95cED938F7991cd0dFcb48F0a06a40FA1aF46EBC | 
  11/30/2019 04:12:02 PM - [INFO]:  | Owner Address: 0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9 | 
  11/30/2019 04:12:02 PM - [INFO]:  | Owner Address: 0x28a8746e75304c0780E011BEd21C72cD78cd535E | 
  11/30/2019 04:12:02 PM - [INFO]:  | Owner Address: 0xACa94ef8bD5ffEE41947b4585a84BdA5a3d3DA6E | 
  11/30/2019 04:12:02 PM - [INFO]:  | Threshold: 5 | 
  [ ./ ][ Safe (0x5fD287667AC7D13161648e82dA6e8B8A3C9Bc432) ]>: 
  ```

+ Command **loadContract  --address=<contract-address>** or **--alias=<contract-alias>**:

  ```
  [ GNOSIS-CLI v0.0.1a ]>: loadContract --alias=ALIAS
  ```

  +  **loadContract --alias=uContract** or **loadContract --alias=GnosisSafeV1.1.0** to enter a pre-loaded contract from the current version of the prototype.

+ Command **newContract  --address=<contract-address> --abi_path=<abi-path>**:

  ``` 
  [ GNOSIS-CLI v0.0.1a ]>: newContract   
  
  ```

+ Command **newToken  --address=<contract-address> --abi_path=<abi-path>**:

  ```
  [ GNOSIS-CLI v0.0.1a ]>: newToken   
  
  ```

+ Command **newPayload**:

  ```
  [ GNOSIS-CLI v0.0.1a ]>: newPayload                                                               
             'alias' :        
              'from' :        
               'gas' :        
          'gasPrice' :
  newPayload:  {'from' : '', 'gas' : 0, 'gasPrice' : 0}
  
  ```

+ Command **setDefaultOwner <owner-address>**:

  ```
  [ GNOSIS-CLI v0.0.1a ]>: setDefaultOwner
  
  ```

+ Command **setDefaultOwnerList <owner-address-0> to <owner-address-n>** :

  ```
  [ GNOSIS-CLI v0.0.1a ]>: setDefaultOwnerList
  
  ```

+ Command **setNetwork  <network-name> --api_key=<infura-api-key>**:

  This command will set the current network to operate with

  ```
  [ GNOSIS-CLI v0.0.1a ]>: setNetwork
  
  ```

+ Command **exit | quit | close**:

  This Command will exit the gnosis-cli console.

  ```
  [ GNOSIS-CLI v0.0.1a ]>: exit | close | quit
  
  ```

### [ Avaliable safe-cli Commands ]:

+ Command **info**:

  ```
  [ ./safe-cli ][ Safe (0x(0*40)) ]>: info
  11/30/2019 05:00:10 PM - [INFO]:  | Name: Gnosis Safe | 
  11/30/2019 05:00:10 PM - [INFO]:  | Version: 1.1.0 | 
  11/30/2019 05:00:10 PM - [INFO]:  | Master Copy Address: 0xA57B8a5584442B467b4689F1144D269d096A3daF | 
  11/30/2019 05:00:10 PM - [INFO]:  | Proxy Address: 0x5fD287667AC7D13161648e82dA6e8B8A3C9Bc432 | 
  11/30/2019 05:00:10 PM - [INFO]:  | Nonce: 0 | 
  11/30/2019 05:00:10 PM - [INFO]:  | Owner Address: 0xd03ea8624C8C5987235048901fB614fDcA89b117 | 
  11/30/2019 05:00:10 PM - [INFO]:  | Owner Address: 0x95cED938F7991cd0dFcb48F0a06a40FA1aF46EBC | 
  11/30/2019 05:00:10 PM - [INFO]:  | Owner Address: 0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9 | 
  11/30/2019 05:00:10 PM - [INFO]:  | Owner Address: 0x28a8746e75304c0780E011BEd21C72cD78cd535E | 
  11/30/2019 05:00:10 PM - [INFO]:  | Owner Address: 0xACa94ef8bD5ffEE41947b4585a84BdA5a3d3DA6E | 
  11/30/2019 05:00:10 PM - [INFO]:  | Threshold: 5 | 
  
  ```

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
