from osbot_utils.type_safe.Type_Safe                          import Type_Safe
from osbot_utils.decorators.methods.cache_on_self             import cache_on_self
from .Service__Fast_API__Client__Config                       import Service__Fast_API__Client__Config
from .Service__Fast_API__Client__Requests                     import Service__Fast_API__Client__Requests
from .store.Service__Fast_API__Client__File__Store            import Service__Fast_API__Client__File__Store
from .retrieve.Service__Fast_API__Client__File__Retrieve      import Service__Fast_API__Client__File__Retrieve
from .exists.Service__Fast_API__Client__File__Exists          import Service__Fast_API__Client__File__Exists
from .delete.Service__Fast_API__Client__File__Delete          import Service__Fast_API__Client__File__Delete
from .data_store.Service__Fast_API__Client__Data__Store       import Service__Fast_API__Client__Data__Store
from .data.Service__Fast_API__Client__Data                    import Service__Fast_API__Client__Data
from .zip.Service__Fast_API__Client__Zip                      import Service__Fast_API__Client__Zip
from .namespace.Service__Fast_API__Client__Namespace          import Service__Fast_API__Client__Namespace
from .admin_storage.Service__Fast_API__Client__Admin__Storage import Service__Fast_API__Client__Admin__Storage
from .server.Service__Fast_API__Client__Server                import Service__Fast_API__Client__Server
from .info.Service__Fast_API__Client__Info                    import Service__Fast_API__Client__Info
#from .auth.Service__Fast_API__Client__Auth                  import Service__Fast_API__Client__Auth     # todo see why this is added here (but file is not created on disk)

class Service__Fast_API__Client(Type_Safe):
    config   : Service__Fast_API__Client__Config
    _requests: Service__Fast_API__Client__Requests = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)                                                 # Initialize request handler with config
        if not self._requests:
            self._requests = Service__Fast_API__Client__Requests(config=self.config)

    @cache_on_self
    def requests(self) -> Service__Fast_API__Client__Requests:                            # Access the unified request handler
        return self._requests

    @cache_on_self
    def store(self) -> Service__Fast_API__Client__File__Store:                               # Access store operations
        return Service__Fast_API__Client__File__Store(_client=self)

    @cache_on_self
    def retrieve(self) -> Service__Fast_API__Client__File__Retrieve:                               # Access retrieve operations
        return Service__Fast_API__Client__File__Retrieve(_client=self)

    @cache_on_self
    def exists(self) -> Service__Fast_API__Client__File__Exists:                               # Access exists operations
        return Service__Fast_API__Client__File__Exists(_client=self)

    @cache_on_self
    def delete(self) -> Service__Fast_API__Client__File__Delete:                               # Access delete operations
        return Service__Fast_API__Client__File__Delete(_client=self)

    @cache_on_self
    def data_store(self) -> Service__Fast_API__Client__Data__Store:                               # Access data_store operations
        return Service__Fast_API__Client__Data__Store(_client=self)

    @cache_on_self
    def data(self) -> Service__Fast_API__Client__Data:                               # Access data operations
        return Service__Fast_API__Client__Data(_client=self)

    @cache_on_self
    def zip(self) -> Service__Fast_API__Client__Zip:                               # Access zip operations
        return Service__Fast_API__Client__Zip(_client=self)

    @cache_on_self
    def namespace(self) -> Service__Fast_API__Client__Namespace:                               # Access namespace operations
        return Service__Fast_API__Client__Namespace(_client=self)

    @cache_on_self
    def admin_storage(self) -> Service__Fast_API__Client__Admin__Storage:                               # Access admin_storage operations
        return Service__Fast_API__Client__Admin__Storage(_client=self)

    @cache_on_self
    def server(self) -> Service__Fast_API__Client__Server:                               # Access server operations
        return Service__Fast_API__Client__Server(_client=self)

    @cache_on_self
    def info(self) -> Service__Fast_API__Client__Info:                               # Access info operations
        return Service__Fast_API__Client__Info(_client=self)

    # @cache_on_self
    # def auth(self) -> Service__Fast_API__Client__Auth:                               # Access auth operations
    #     return Service__Fast_API__Client__Auth(_client=self)