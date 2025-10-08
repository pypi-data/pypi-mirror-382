from typing                                         import Any
from osbot_utils.type_safe.Type_Safe                import Type_Safe
from osbot_utils.decorators.methods.cache_on_self   import cache_on_self
from .Service__Fast_API__Client__Data__Retrieve     import Service__Fast_API__Client__Data__Retrieve
from .Service__Fast_API__Client__Data__Delete       import Service__Fast_API__Client__Data__Delete

class Service__Fast_API__Client__Data(Type_Safe):
    _client: Any                                                                    # Reference to main client

    @cache_on_self
    def retrieve(self) -> Service__Fast_API__Client__Data__Retrieve:                                  # Access retrieve operations
        return Service__Fast_API__Client__Data__Retrieve(_client=self._client)

    @cache_on_self
    def delete(self) -> Service__Fast_API__Client__Data__Delete:                                  # Access delete operations
        return Service__Fast_API__Client__Data__Delete(_client=self._client)

