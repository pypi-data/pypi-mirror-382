from fred.rest.router.interface import RouterInterfaceMixin
from fred.rest.router.endpoint import RouterEndpointAnnotation


class RouterMainMixin(RouterInterfaceMixin):

    @RouterEndpointAnnotation.set(
        path="/get",
        methods=["GET"],
        summary="Get key-value",
        description="Get a value from the key-value store by its key.",
    )
    def get(self, key: str, presigned_url: bool = False, **kwargs) -> dict:
        return {
            "ok": True,
            "key": key,
            "val": self.runner_backend.keyval(key=key).get(presigned_url=presigned_url),
            **kwargs
        }

    @RouterEndpointAnnotation.set(
        path="/set",
        methods=["POST"],
        summary="Set key-value",
        description="Set a value in the key-value store by its key.",
    )
    def set(self, key: str, value: str, **kwargs) -> dict:
        self.runner_backend.keyval(key=key).set(value=value, **kwargs)
        return {
            "ok": True,
            "key": key,
            "val": value,
            **kwargs
        }
    
    @RouterEndpointAnnotation.set(
        path="/keys",
        methods=["GET"],
        summary="List keys",
        description="List keys in the key-value store matching a given pattern.",
    )
    def keys(self, pattern: str = "*", **kwargs) -> dict:
        keys = list(self.runner_backend.keyval.keys(pattern=pattern, **kwargs))
        return {
            "ok": True,
            "pattern": pattern,
            "keys": keys,
            **kwargs
        }
