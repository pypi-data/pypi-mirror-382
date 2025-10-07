import enum

from fred.rest.router.config import RouterConfig
from fred.rest.router.catalog.interface import RouterCatalogInterface

from opload.settings import OPLOAD_BACKEND_SERVICE
from opload.router._base import RouterBaseMixin
from opload.router._main import RouterMainMixin


class RouterCatalog(RouterCatalogInterface, enum.Enum):
    BASE = RouterConfig.auto(prefix="")(apply=RouterBaseMixin)
    MAIN = RouterConfig.auto(prefix="")(apply=RouterMainMixin)

    def get_kwargs(self) -> dict:
        match self:
            case RouterCatalog.MAIN:
                return {
                    "service_name": OPLOAD_BACKEND_SERVICE
                }
            case _:
                return {}