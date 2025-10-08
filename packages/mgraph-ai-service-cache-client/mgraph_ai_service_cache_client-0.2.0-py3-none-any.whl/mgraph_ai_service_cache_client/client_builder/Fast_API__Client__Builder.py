from osbot_fast_api.client.Fast_API__Client__Generator                                               import Fast_API__Client__Generator
from osbot_utils.type_safe.Type_Safe                                                                 import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                       import type_safe
from osbot_utils.utils.Env                                                                           import get_env
from mgraph_ai_service_cache.fast_api.Service__Fast_API                                              import Service__Fast_API
from mgraph_ai_service_cache_client                                                                  import client_contract
from mgraph_ai_service_cache_client.client_contract.Service__Fast_API__Client                        import Service__Fast_API__Client
from mgraph_ai_service_cache_client.schemas.client_builder.Schema__Fast_API__Client__Server__Details import Schema__Fast_API__Client__Server__Details
from mgraph_ai_service_cache_client.schemas.consts.consts__Cache_Client                              import ENV_VAR__AUTH__TARGET_SERVER__CACHE_SERVICE__KEY_VALUE, ENV_VAR__AUTH__TARGET_SERVER__CACHE_SERVICE__KEY_NAME, ENV_VAR__URL__TARGET_SERVER__CACHE_SERVICE


class Fast_API__Client__Builder(Type_Safe):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cache_service__fast_api = Service__Fast_API().setup()
        self.generator               = Fast_API__Client__Generator(fast_api=self.cache_service__fast_api)

    def create_client_files(self):
        with self.generator as _:
            output_dir  = self.target_folder()
            saved_files = _.save_client_files(output_dir=output_dir)
            return sorted(saved_files)

    def target_folder(self):
        return client_contract.path

    @type_safe
    def configure_client(self, service_client: Service__Fast_API__Client):
        with self.server_details() as _:
            if _.configured:
                service_client.config.api_key        = _.api_key
                service_client.config.api_key_header = _.api_key_header
                service_client.config.base_url       = _.base_url
            return _

    def server_details(self) -> Schema__Fast_API__Client__Server__Details:
        api_key        = get_env(ENV_VAR__AUTH__TARGET_SERVER__CACHE_SERVICE__KEY_VALUE)
        api_key_header = get_env(ENV_VAR__AUTH__TARGET_SERVER__CACHE_SERVICE__KEY_NAME )
        base_url       = get_env(ENV_VAR__URL__TARGET_SERVER__CACHE_SERVICE            )
        configured     = all([api_key, api_key_header, base_url])

        kwargs = dict(api_key        = api_key          ,
                      api_key_header = api_key_header   ,
                      base_url       = base_url         ,
                      configured     = configured       )
        return Schema__Fast_API__Client__Server__Details(**kwargs)


