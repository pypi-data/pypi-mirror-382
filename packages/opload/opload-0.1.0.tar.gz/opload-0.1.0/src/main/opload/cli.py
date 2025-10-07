from typing import Optional

from fred.cli.interface import AbstractCLI
from fred.cli.main import CLI as FredCLI


class CLI(AbstractCLI):

    @property
    def fred(self) -> FredCLI:
        return FredCLI.default_config()

    def version(self) -> str:
        from opload.version import version
        return version.value
    
    def serve(self, classname: Optional[str] = None, classpath: Optional[str] = None, **kwargs):
        return self.fred.serve(
            classpath=classpath or "opload.router.catalog",
            classname=classname or "RouterCatalog",
            **kwargs
        )