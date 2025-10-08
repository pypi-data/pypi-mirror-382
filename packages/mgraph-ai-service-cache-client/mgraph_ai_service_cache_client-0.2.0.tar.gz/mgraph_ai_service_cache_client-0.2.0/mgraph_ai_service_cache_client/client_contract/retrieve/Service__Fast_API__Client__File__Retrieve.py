from typing import Any, Optional, Dict
from osbot_utils.type_safe.Type_Safe import Type_Safe

class Service__Fast_API__Client__File__Retrieve(Type_Safe):
    _client: Any                                                                    # Reference to main client

    @property
    def requests(self):                                                             # Access the unified request handler
        return self._client.requests()

    def retrieve__cache_id(self, cache_id: str, namespace: str) -> Dict:                              # Auto-generated from endpoint get__retrieve__cache_id
                                                                                    # Build path
        path = f"/{{namespace}}/retrieve/{{cache_id}}"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def retrieve__cache_id__config(self, cache_id: str, namespace: str) -> Dict:                              # Auto-generated from endpoint get__retrieve__cache_id__config
                                                                                    # Build path
        path = f"/{{namespace}}/retrieve/{{cache_id}}/config"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def retrieve__cache_id__metadata(self, cache_id: str, namespace: str) -> Dict:                              # Auto-generated from endpoint get__retrieve__cache_id__metadata
                                                                                    # Build path
        path = f"/{{namespace}}/retrieve/{{cache_id}}/metadata"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def retrieve__cache_id__refs(self, cache_id: str, namespace: str) -> Dict:                              # Auto-generated from endpoint get__retrieve__cache_id__refs
                                                                                    # Build path
        path = f"/{{namespace}}/retrieve/{{cache_id}}/refs"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def retrieve__cache_id__refs__all(self, cache_id: str, namespace: str) -> Dict:                              # Auto-generated from endpoint get__retrieve__cache_id__refs__all
                                                                                    # Build path
        path = f"/{{namespace}}/retrieve/{{cache_id}}/refs/all"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def retrieve__hash__cache_hash(self, cache_hash: str, namespace: str) -> Dict:                              # Auto-generated from endpoint get__retrieve__hash__cache_hash
                                                                                    # Build path
        path = f"/{{namespace}}/retrieve/hash/{{cache_hash}}"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def retrieve__cache_id__string(self, cache_id: str, namespace: str) -> Dict:                              # Auto-generated from endpoint get__retrieve__cache_id__string
                                                                                    # Build path
        #path = f"/{{namespace}}/retrieve/{{cache_id}}/string"                      # todo: BUG: used {{
        path = f"/{namespace}/retrieve/{cache_id}/string"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def retrieve__cache_id__json(self, cache_id: str, namespace: str) -> Dict:                              # Auto-generated from endpoint get__retrieve__cache_id__json
                                                                                    # Build path
        #path = f"/{{namespace}}/retrieve/{{cache_id}}/json"                        # used {{
        path = f"/{namespace}/retrieve/{cache_id}/json"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def retrieve__cache_id__binary(self, cache_id: str, namespace: str) -> Dict:                              # Auto-generated from endpoint get__retrieve__cache_id__binary
                                                                                    # Build path
        #path = f"/{{namespace}}/retrieve/{{cache_id}}/binary"                      # todo: BUG: used {{
        path = f"/{namespace}/retrieve/{cache_id}/binary"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        #return result.json if result.json else result.text                         # todo: BUG returned this
        return result.content                                                       #       and since this is binary we need to return the result.content

    def retrieve__hash__cache_hash__string(self, cache_hash: str, namespace: str) -> Dict:                              # Auto-generated from endpoint get__retrieve__hash__cache_hash__string
                                                                                    # Build path
        path = f"/{{namespace}}/retrieve/hash/{{cache_hash}}/string"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def retrieve__hash__cache_hash__json(self, cache_hash: str, namespace: str) -> Dict:                              # Auto-generated from endpoint get__retrieve__hash__cache_hash__json
                                                                                    # Build path
        path = f"/{{namespace}}/retrieve/hash/{{cache_hash}}/json"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def retrieve__hash__cache_hash__binary(self, cache_hash: str, namespace: str) -> Dict:                              # Auto-generated from endpoint get__retrieve__hash__cache_hash__binary
                                                                                    # Build path
        path = f"/{{namespace}}/retrieve/hash/{{cache_hash}}/binary"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text