from typing import Any, Optional, Dict
from osbot_utils.type_safe.Type_Safe import Type_Safe

class Service__Fast_API__Client__Set_Cookie(Type_Safe):
    _client: Any                                                                    # Reference to main client

    @property
    def requests(self):                                                             # Access the unified request handler
        return self._client.requests()

    def set_cookie_form(self) -> Dict:                              # Auto-generated from endpoint get__set_cookie_form
                                                                                    # Build path
        path = "/auth/set-cookie-form"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def set_auth_cookie(self) -> Dict:                              # Auto-generated from endpoint post__set_auth_cookie
                                                                                    # Build path
        path = "/auth/set-auth-cookie"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "POST",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text