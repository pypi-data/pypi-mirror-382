from arize.config import SDKConfiguration


class ExperimentsClient:
    def __init__(self, sdk_config: SDKConfiguration):
        self._sdk_config = sdk_config
        from arize._generated import api_client as gen

        self._api = gen.ExperimentsApi(self._sdk_config.get_generated_client())
        self.list = self._api.experiments_list
