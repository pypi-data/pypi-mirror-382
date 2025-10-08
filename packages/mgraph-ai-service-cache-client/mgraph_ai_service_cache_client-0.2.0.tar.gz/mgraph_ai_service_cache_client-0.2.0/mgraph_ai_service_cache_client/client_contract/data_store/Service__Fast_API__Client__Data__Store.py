from typing  import Any, Dict
from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path   import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id     import Safe_Str__Id


class Service__Fast_API__Client__Data__Store(Type_Safe):
    _client: Any                                                                    # Reference to main client

    @property
    def requests(self):                                                             # Access the unified request handler
        return self._client.requests()

    def data__store_binary(self, cache_id: str, namespace: str, body:bytes) -> Dict:                              # Auto-generated from endpoint post__data__store_binary
                                                                                    # Build path
        path = f"/{namespace}/cache/{cache_id}/data/store/binary"
        #body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "POST",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def data__store_binary__with__id(self, cache_id: str, namespace: str, data_file_id: str, body:bytes) -> Dict:                              # Auto-generated from endpoint post__data__store_binary__with__id
                                                                                    # Build path
        path = f"/{namespace}/cache/{cache_id}/data/store/binary/{data_file_id}"
        #body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "POST",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def data__store_binary__with__id_and_key(self, cache_id: str, namespace: str, data_key: str, data_file_id: str, body:bytes) -> Dict:                              # Auto-generated from endpoint post__data__store_binary__with__id_and_key
                                                                                    # Build path
        path = f"/{namespace}/cache/{cache_id}/data/store/binary/{data_key}/{data_file_id}"
        #body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "POST",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def data__store_json(self, cache_id: str, namespace: str, body:dict) -> Dict:                              # Auto-generated from endpoint post__data__store_json
                                                                                    # Build path
        #path = f"/{{namespace}}/cache/{{cache_id}}/data/store/json"
        path = f"/{namespace}/cache/{cache_id}/data/store/json"
        #body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "POST",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def data__store_json__with__id(self, cache_id: str, namespace: str, data_file_id: str, body:dict) -> Dict:                              # Auto-generated from endpoint post__data__store_json__with__id
                                                                                    # Build path
        path = f"/{namespace}/cache/{cache_id}/data/store/json/{data_file_id}"
        #body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "POST",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def data__store_json__with__id_and_key(self, cache_id: str,
                                           namespace: str, data_key: str,
                                           data_file_id: str,
                                           body: dict) -> Dict:                              # Auto-generated from endpoint post__data__store_json__with__id_and_key
                                                                                    # Build path
        path = f"/{namespace}/cache/{cache_id}/data/store/json/{data_key}/{data_file_id}"
        #body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "POST",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    #def data__store_string(self, cache_id: str, namespace: str) -> Dict:                             # todo: BUG same as the others
    def data__store_string(self, cache_id: str, namespace: Safe_Str__Id, body:str) -> Dict:
                                                                                    # Build path
        #path = f"/{{namespace}}/cache/{{cache_id}}/data/store/string"              # BUG
        #body = None
        path = f"/{namespace}/cache/{cache_id}/data/store/string"
                                                                                    # Execute request
        result = self.requests.execute(
            method = "POST",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    #def data__store_string__with__id(self, cache_id: str, namespace: str, data_file_id: str) -> Dict:                              # Auto-generated from endpoint post__data__store_string__with__id
    def data__store_string__with__id(self, cache_id     : str,
                                           namespace    : Safe_Str__Id,
                                           data_file_id : Safe_Str__Id,
                                           body         : str
                                     ) -> Dict:                              # Auto-generated from endpoint post__data__store_string__with__id

        #path = f"/{{namespace}}/cache/{{cache_id}}/data/store/string/{{data_file_id}}"      # Build path
        path = f"/{namespace}/cache/{cache_id}/data/store/string/{data_file_id}"      # Build path
        #body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "POST",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    #def data__store_string__with__id_and_key(self, cache_id: str, namespace: str, data_key: str, data_file_id: str) -> Dict:                              # Auto-generated from endpoint post__data__store_string__with__id_and_key
    def data__store_string__with__id_and_key(self, cache_id     : str                   ,
                                                   namespace    : Safe_Str__Id          ,
                                                   data_key     : Safe_Str__File__Path  ,
                                                   data_file_id : Safe_Str__Id          ,
                                                   body: str
                                             ) -> Dict:                              # Auto-generated from endpoint post__data__store_string__with__id_and_key

        #path = f"/{{namespace}}/cache/{{cache_id}}/data/store/string/{data_key:path}/{{data_file_id}}"  # Build path
        path = f"/{namespace}/cache/{cache_id}/data/store/string/{data_key}/{data_file_id}"  # Build path
        #body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "POST",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text