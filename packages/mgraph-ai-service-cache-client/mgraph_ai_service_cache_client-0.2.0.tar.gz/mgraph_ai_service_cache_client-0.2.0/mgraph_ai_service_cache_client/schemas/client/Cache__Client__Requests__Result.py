from typing                                                                              import Dict
from osbot_utils.type_safe.Type_Safe                                                     import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                                    import Safe_Float
from osbot_utils.type_safe.primitives.core.Safe_UInt                                     import Safe_UInt
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text             import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path        import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__Content_Type import Safe_Str__Http__Content_Type
from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__Text         import Safe_Str__Http__Text
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now         import Timestamp_Now
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                 import Safe_Str__Url


class Cache__Client__Requests__Result(Type_Safe):
    content_type  : Safe_Str__Http__Content_Type
    content       : bytes                           = None
    duration      : Safe_Float
    error         : Safe_Str__Text
    json          : Dict                            = None
    path          : Safe_Str__File__Path
    status_code   : Safe_UInt
    target_server : Safe_Str__Url
    text          : Safe_Str__Http__Text            = None                # this has 1M limit, which should be ok for all use-cases (that return text)
    timestamp     : Timestamp_Now



