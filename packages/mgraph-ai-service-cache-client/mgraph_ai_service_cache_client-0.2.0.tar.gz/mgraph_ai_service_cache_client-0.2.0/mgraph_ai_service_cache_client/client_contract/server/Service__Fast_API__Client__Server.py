from typing import Any, Optional, Dict
from osbot_utils.type_safe.Type_Safe import Type_Safe

class Service__Fast_API__Client__Server(Type_Safe):
    _client: Any                                                                    # Reference to main client

    @property
    def requests(self):                                                             # Access the unified request handler
        return self._client.requests()

    def storage__info(self) -> Dict:                              # Auto-generated from endpoint get__storage__info
                                                                                    # Build path
        path = "/server/storage/info"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def create__test_fixtures(self) -> Dict:                              # Auto-generated from endpoint get__create__test_fixtures
                                                                                    # Build path
        path = "/server/create/test-fixtures"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text