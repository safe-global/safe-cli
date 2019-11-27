import configparser
config = configparser.ConfigParser()

config.read('./gnosis_safe_contract_v1_1_0.ini')
for key in config['GnosisSafeSetup']:
    print(config['GnosisSafeSetup'][key])



