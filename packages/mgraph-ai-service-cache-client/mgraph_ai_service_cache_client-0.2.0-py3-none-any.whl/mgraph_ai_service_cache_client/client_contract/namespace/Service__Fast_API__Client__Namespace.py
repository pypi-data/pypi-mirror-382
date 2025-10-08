from typing import Any, Optional, Dict
from osbot_utils.type_safe.Type_Safe import Type_Safe

class Service__Fast_API__Client__Namespace(Type_Safe):
    _client: Any                                                                    # Reference to main client

    @property
    def requests(self):                                                             # Access the unified request handler
        return self._client.requests()

    def file_hashes(self, namespace: str) -> Dict:                              # Auto-generated from endpoint get__file_hashes
                                                                                    # Build path
        path = f"/{{namespace}}/file-hashes"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def file_ids(self, namespace: str) -> Dict:                              # Auto-generated from endpoint get__file_ids
                                                                                    # Build path
        path = f"/{{namespace}}/file-ids"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def stats(self, namespace: str) -> Dict:                              # Auto-generated from endpoint get__stats
                                                                                    # Build path
        path = f"/{{namespace}}/stats"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text