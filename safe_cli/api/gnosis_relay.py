from .base_api import BaseAPI


class RelayService(BaseAPI):
    URL_BY_NETWORK = {
        1: 'https://safe-relay.gnosis.io',
        # 3:
        4: 'https://safe-relay.rinkeby.gnosis.io',
        # 5:
        # 42
    }
