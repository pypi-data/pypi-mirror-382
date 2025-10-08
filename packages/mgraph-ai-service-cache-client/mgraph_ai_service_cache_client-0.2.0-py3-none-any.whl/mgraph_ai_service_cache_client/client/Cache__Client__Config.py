from osbot_utils.type_safe.Type_Safe                                     import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url import Safe_Str__Url

URL__TARGET_SERVER__DEV = "https://cache.dev.mgraph.ai"

class Cache__Client__Config(Type_Safe):
    target_server : Safe_Str__Url = URL__TARGET_SERVER__DEV