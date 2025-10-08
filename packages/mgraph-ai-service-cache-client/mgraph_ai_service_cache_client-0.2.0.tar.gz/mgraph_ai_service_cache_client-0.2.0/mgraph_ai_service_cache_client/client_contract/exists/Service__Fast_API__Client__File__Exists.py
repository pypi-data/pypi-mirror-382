from typing import Any, Optional, Dict
from osbot_utils.type_safe.Type_Safe import Type_Safe

class Service__Fast_API__Client__File__Exists(Type_Safe):
    _client: Any                                                                    # Reference to main client

    @property
    def requests(self):                                                             # Access the unified request handler
        return self._client.requests()

    def exists__hash__cache_hash(self, cache_hash: str, namespace: str) -> Dict:                              # Auto-generated from endpoint get__exists__hash__cache_hash
                                                                                    # Build path
        path = f"/{{namespace}}/exists/hash/{{cache_hash}}"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text