class ContractConsolePayloads:
    def __init__(self):
        self.payload_data = {}

    def add_payload(self, payload_artifact, alias=''):
        if alias != '':
            self.payload_data[alias] = {'payload': payload_artifact}
            return self.payload_data
        self.payload_data['uPayload' + str(len(self.payload_data))] = {'payload': payload_artifact}
        return self.payload_data

    def get_payload_from_alias(self, alias, key=None):
        try:
            if key is None:
                return self.payload_data[alias]
            return self.payload_data[alias]['payload']
        except KeyError:
            raise KeyError
        except Exception as err:
            print(type(err), err)
