from typing import Any, Optional, Dict
from osbot_utils.type_safe.Type_Safe import Type_Safe

from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Store__Strategy import Enum__Cache__Store__Strategy


class Service__Fast_API__Client__Zip(Type_Safe):
    _client: Any                                                                    # Reference to main client

    @property
    def requests(self):                                                             # Access the unified request handler
        return self._client.requests()

    def zip_create(self, namespace: str, strategy: Enum__Cache__Store__Strategy, cache_key: str, file_id: str) -> Dict:                              # Auto-generated from endpoint post__zip_create
                                                                                    # Build path
        path = f"/{{namespace}}/{{strategy}}/zip/create/{cache_key:path}/{{file_id}}"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "POST",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def zip_store(self, namespace: str, strategy: Enum__Cache__Store__Strategy, cache_key: str, file_id: str) -> Dict:                              # Auto-generated from endpoint post__zip_store
                                                                                    # Build path
        path = f"/{{namespace}}/{{strategy}}/zip/store/{cache_key:path}/{{file_id}}"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "POST",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def zip_retrieve(self, cache_id: str, namespace: str) -> Dict:                              # Auto-generated from endpoint get__zip_retrieve
                                                                                    # Build path
        path = f"/{{namespace}}/zip/{{cache_id}}/retrieve"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def zip_files_list(self, cache_id: str, namespace: str) -> Dict:                              # Auto-generated from endpoint get__zip_files_list
                                                                                    # Build path
        path = f"/{{namespace}}/zip/{{cache_id}}/files/list"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def zip_file_retrieve(self, cache_id: str, file_path: str, namespace: str) -> Dict:                              # Auto-generated from endpoint get__zip_file_retrieve
                                                                                    # Build path
        path = f"/{{namespace}}/zip/{{cache_id}}/file/retrieve/{file_path:path}"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def zip_file_add_from_bytes(self, cache_id: str, file_path: str, namespace: str) -> Dict:                              # Auto-generated from endpoint post__zip_file_add_from_bytes
                                                                                    # Build path
        path = f"/{{namespace}}/zip/{{cache_id}}/file/add/from/bytes/{file_path:path}"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "POST",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def zip_file_add_from_string(self, cache_id: str, file_path: str, namespace: str) -> Dict:                              # Auto-generated from endpoint post__zip_file_add_from_string
                                                                                    # Build path
        path = f"/{{namespace}}/zip/{{cache_id}}/file/add/from/string/{file_path:path}"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "POST",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def zip_file_delete(self, cache_id: str, file_path: str, namespace: str) -> Dict:                              # Auto-generated from endpoint delete__zip_file_delete
                                                                                    # Build path
        path = f"/{{namespace}}/zip/{{cache_id}}/file/delete/{file_path:path}"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "DELETE",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def batch_operations(self, cache_id: str, namespace: str) -> Dict:                              # Auto-generated from endpoint post__batch_operations
                                                                                    # Build path
        path = f"/{{namespace}}/zip/{{cache_id}}/batch/operations"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "POST",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text