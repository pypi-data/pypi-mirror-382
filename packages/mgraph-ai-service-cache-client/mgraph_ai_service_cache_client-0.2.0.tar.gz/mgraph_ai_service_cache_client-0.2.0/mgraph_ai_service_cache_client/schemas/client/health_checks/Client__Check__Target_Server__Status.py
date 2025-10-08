from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                            import Safe_Float
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now import Timestamp_Now
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url         import Safe_Str__Url


class Client__Check__Target_Server__Status(Type_Safe):
    duration     : Safe_Float
    success      : bool
    target_server: Safe_Str__Url
    timestamp    : Timestamp_Now
