from typing import Any, Optional, Dict
from osbot_utils.type_safe.Type_Safe import Type_Safe


class Service__Fast_API__Client__Info(Type_Safe):
    _client: Any                                                                    # todo: BUG: was Any and started with _
    #client : Service__Fast_API__Client                                             # todo: BUG: fix circular dependency on Service__Fast_API__Client

    @property
    def requests(self):                                                             # Access the unified request handler
        #return self._client.requests()                                             # todo: BUG: used _client
        return self._client.requests()

    def health(self) -> Dict:                              # Auto-generated from endpoint get__health
                                                                                    # Build path
        path = "/info/health"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def server(self) -> Dict:                              # Auto-generated from endpoint get__server
                                                                                    # Build path
        path = "/info/server"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def status(self) -> Dict:                              # Auto-generated from endpoint get__status
                                                                                    # Build path
        path = "/info/status"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text

    def versions(self) -> Dict:                              # Auto-generated from endpoint get__versions
                                                                                    # Build path
        path = "/info/versions"
        body = None
                                                                                    # Execute request
        result = self.requests.execute(
            method = "GET",
            path   = path,
            body   = body
        )
                                                                                    # Return response data
        return result.json if result.json else result.text