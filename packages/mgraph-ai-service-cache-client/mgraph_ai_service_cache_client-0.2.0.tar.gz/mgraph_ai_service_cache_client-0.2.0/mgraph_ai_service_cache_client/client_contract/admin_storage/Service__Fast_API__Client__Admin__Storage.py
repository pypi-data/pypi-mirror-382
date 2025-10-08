from typing import Any, Optional, Dict
from osbot_utils.type_safe.Type_Safe import Type_Safe

class Service__Fast_API__Client__Admin__Storage(Type_Safe):
    _client: Any                                                                    # Reference to main client

    @property
    def requests(self):                                                             # Access the unified request handler
        return self._client.requests()

    def bucket_name(self) -> Dict:                              # Auto-generated from endpoint get__bucket_name
                                                                                    # Build path
        path = "/admin/storage/bucket-name"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def file__exists(self, path: Any) -> Dict:                              # Auto-generated from endpoint get__file__exists
                                                                                    # Build path
        path = f"/admin/storage/file/exists/{path:path}"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def file__bytes(self, path: Any) -> Dict:                              # Auto-generated from endpoint get__file__bytes
                                                                                    # Build path
        path = f"/admin/storage/file/bytes/{path:path}"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def file__json(self, path: Any) -> Dict:                              # Auto-generated from endpoint get__file__json
                                                                                    # Build path
        path = f"/admin/storage/file/json/{path:path}"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def files__parent_path(self, path: Optional[str] = None, return_full_path: Optional[bool] = None) -> Dict:                              # Auto-generated from endpoint get__files__parent_path
                                                                                    # Build path
        path = "/admin/storage/files/parent-path"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def files__all__path(self, path: str) -> Dict:                              # Auto-generated from endpoint get__files__all__path
                                                                                    # Build path
        path = f"/admin/storage/files/all/{path:path}"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def folders(self, path: Optional[str] = None, return_full_path: Optional[bool] = None) -> Dict:                              # Auto-generated from endpoint get__folders
                                                                                    # Build path
        path = "/admin/storage/folders"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def delete__file(self, path: str) -> Dict:                              # Auto-generated from endpoint delete__delete__file
                                                                                    # Build path
        path = f"/admin/storage/{path:path}"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "DELETE",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text