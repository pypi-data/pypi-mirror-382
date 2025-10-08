from typing                                                                    import Any, Dict
from osbot_utils.type_safe.Type_Safe                                           import Type_Safe
from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Data_Type import Enum__Cache__Data_Type


class Service__Fast_API__Client__Data__Delete(Type_Safe):
    _client: Any                                                                    # Reference to main client

    @property
    def requests(self):                                                             # Access the unified request handler
        return self._client.requests()

    def delete__all__data__files(self, cache_id: str, namespace: str) -> Dict:                              # Auto-generated from endpoint delete__delete__all__data__files
                                                                                    # Build path
        path = f"/{{namespace}}/cache/{{cache_id}}/data/delete/all"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "DELETE",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def delete__all__data__files__with__key(self, cache_id: str, namespace: str, data_key: str) -> Dict:                              # Auto-generated from endpoint delete__delete__all__data__files__with__key
                                                                                    # Build path
        path = f"/{{namespace}}/cache/{{cache_id}}/data/delete/all/{data_key:path}"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "DELETE",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def delete__data__file__with__id(self, cache_id: str, namespace: str, data_type: Enum__Cache__Data_Type, data_file_id: str) -> Dict:                              # Auto-generated from endpoint delete__delete__data__file__with__id
                                                                                    # Build path
        path = f"/{{namespace}}/cache/{{cache_id}}/data/delete/{{data_type}}/{{data_file_id}}"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "DELETE",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def delete__data__file__with__id_and_key(self, cache_id: str, namespace: str, data_type: Enum__Cache__Data_Type, data_key: str, data_file_id: str) -> Dict:                              # Auto-generated from endpoint delete__delete__data__file__with__id_and_key
                                                                                    # Build path
        path = f"/{{namespace}}/cache/{{cache_id}}/data/delete/{{data_type}}/{data_key:path}/{{data_file_id}}"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "DELETE",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text