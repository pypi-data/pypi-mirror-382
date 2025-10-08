from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url import Safe_Str__Url
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id
from typing import Optional

class Service__Fast_API__Client__Config(Type_Safe):
    base_url        : Safe_Str__Url = "http://localhost:8000"                      # Default to local
    api_key         : Optional[str] = None                                         # Optional API key
    api_key_header  : str           = "X-API-Key"                                  # Header name for API key
    timeout         : int           = 30                                           # Request timeout in seconds
    verify_ssl      : bool          = True                                         # Verify SSL certificates
                                                                                    # Service-specific configuration can be added here
    service_name    : Safe_Str__Id  = "Service__Fast_API"
    service_version : str           = "v0.5.67"