from fred.settings import get_environ_variable


OPLOAD_BACKEND_SERVICE = get_environ_variable(
    "OPLOAD_BACKEND_SERVICE",
    default="STDLIB",
)