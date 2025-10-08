from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url        import Safe_Str__Url

class Schema__Fast_API__Client__Server__Details(Type_Safe):
    api_key        : Safe_Str__Id
    api_key_header : Safe_Str__Id
    base_url       : Safe_Str__Url
    configured     : bool