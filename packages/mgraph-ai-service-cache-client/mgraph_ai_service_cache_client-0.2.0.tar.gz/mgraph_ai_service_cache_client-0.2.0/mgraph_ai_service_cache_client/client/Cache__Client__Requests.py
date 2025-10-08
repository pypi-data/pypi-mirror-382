import requests
from osbot_utils.helpers.duration.decorators.capture_duration                       import capture_duration
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.utils.Env                                                          import get_env
from osbot_utils.utils.Http                                                         import url_join_safe
from mgraph_ai_service_cache_client.client.Cache__Client__Config                    import Cache__Client__Config
from mgraph_ai_service_cache_client.schemas.client.Cache__Client__Requests__Result  import Cache__Client__Requests__Result
from mgraph_ai_service_cache_client.schemas.consts.consts__Cache_Client             import ENV_VAR__AUTH__TARGET_SERVER__CACHE_SERVICE__KEY_NAME, ENV_VAR__AUTH__TARGET_SERVER__CACHE_SERVICE__KEY_VALUE


class Cache__Client__Requests(Type_Safe):
    config: Cache__Client__Config

    def auth__key_name(self):
        return get_env(ENV_VAR__AUTH__TARGET_SERVER__CACHE_SERVICE__KEY_NAME)

    def auth__key_value(self):
        return get_env(ENV_VAR__AUTH__TARGET_SERVER__CACHE_SERVICE__KEY_VALUE)

    def auth_headers(self):
        key_name  =  self.auth__key_name()
        key_value = self.auth__key_value()
        if key_name and key_value:
            return { key_name: key_value }
        return {}

    def headers(self):
        return { **self.auth_headers() }                                    # location to add more requests headers (if needed)

    def get(self, path):
        target_server = self.config.target_server
        url           = url_join_safe(target_server, path)
        headers       = self.auth_headers()
        with capture_duration() as duration:
            response      = requests.get(url, headers=headers)


        content_type  = response.headers.get('content-type')
        result_kwargs = dict(content_type  = content_type        ,
                             duration      = duration.seconds    ,
                             path          = path                ,
                             status_code   = response.status_code,
                             target_server = target_server       )

        if   'json' in content_type:  result_kwargs['json'   ] = response.json()
        elif 'text' in content_type:  result_kwargs['text'   ] = response.text
        else:                         result_kwargs['content'] = response.content

        return Cache__Client__Requests__Result(**result_kwargs)

